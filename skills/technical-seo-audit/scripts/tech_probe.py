#!/usr/bin/env python3
"""Technical SEO probe: fetch a target plus a sample of its sitemap URLs and report, from the
RAW HTML and response headers, what crawlers that do not run JavaScript see.

Covers: status and redirects, headers, head metadata, JSON-LD, framework and JS-shell signals
(Next.js App/Pages router, Nuxt, Angular, Laravel, WordPress, Shopify, ...), tracking-tag
coverage across pages, robots.txt and sitemap sanity. Emits JSON, including rule-based `hints`
that the agent turns into findings.

Usage:
    python3 tech_probe.py --url https://example.com/ [--sample 15] [--urls-file urls.txt]
                          [--max-pages 25] [--output probe.json]

Limits (also written to the output): raw HTML only. Tags or content injected by JavaScript or
by Google Tag Manager are NOT visible here, so confirm those in a browser (rendered DOM and the
Network panel). Only audit sites you are authorised to test.

Safety: sitemap and redirect URLs on other hosts are never fetched (same host or its www
variant only). Python 3.8+, standard library only.
"""

import argparse
import gzip
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zlib
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser

UA = "technical-seo-audit/2.2 (+https://github.com/seobiopse/seo-aeo-geo-audit)"
MAX_BYTES = 3 * 1024 * 1024
MAX_REDIRECTS = 5
PRIVATE_PATHS = ("/cart", "/checkout", "/login", "/register", "/signup", "/account", "/dashboard", "/admin", "/wp-admin")

TRACKERS = {
    "Google Tag Manager": (r"googletagmanager\.com/(?:gtm\.js|ns\.html)", r"GTM-[A-Z0-9]{4,}"),
    "GA4": (r"googletagmanager\.com/gtag/js\?id=G-|gtag\(\s*['\"]config['\"]\s*,\s*['\"]G-", r"G-[A-Z0-9]{6,}"),
    "Universal Analytics (retired)": (r"google-analytics\.com/(?:analytics|ga)\.js|['\"]UA-\d+-\d+['\"]", r"UA-\d+-\d+"),
    "Google Ads": (r"['\"]AW-\d{6,}['\"]", r"AW-\d{6,}"),
    "Meta Pixel": (r"connect\.facebook\.net/[^\"']*/fbevents\.js|fbq\(\s*['\"]init['\"]", r"fbq\(\s*['\"]init['\"]\s*,\s*['\"](\d{6,})['\"]"),
    "Microsoft UET": (r"bat\.bing\.com", r"\bti\s*:\s*[\"'](\d{5,})[\"']"),
    "LinkedIn Insight": (r"snap\.licdn\.com/li\.lms-analytics|_linkedin_partner_id", r"_linkedin_partner_id\s*=\s*[\"'](\d+)[\"']"),
    "TikTok Pixel": (r"analytics\.tiktok\.com", r"ttq\.load\(\s*['\"]([A-Z0-9]+)['\"]"),
    "Hotjar": (r"static\.hotjar\.com|\bhjid\b", r"hjid\s*:\s*(\d+)"),
    "Microsoft Clarity": (r"clarity\.ms/tag", r"clarity\.ms/tag/([a-z0-9]+)"),
    "Segment": (r"cdn\.segment\.com", None),
    "HubSpot": (r"js\.hs-scripts\.com", r"js\.hs-scripts\.com/(\d+)"),
    "Plausible": (r"plausible\.io/js", None),
}
TRACKER_RE = {k: (re.compile(d, re.I), re.compile(i) if i else None) for k, (d, i) in TRACKERS.items()}


# ---------- fetching ----------

class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


def host_key(url):
    h = (urllib.parse.urlsplit(url).hostname or "").lower()
    return h[4:] if h.startswith("www.") else h


def same_site(a, b):
    return host_key(a) == host_key(b)


def _decode(body, enc):
    enc = (enc or "").lower()
    try:
        if "gzip" in enc:
            return gzip.decompress(body)
        if "deflate" in enc:
            return zlib.decompress(body)
    except Exception:
        pass
    return body


def fetch(url, timeout, origin):
    """GET with manual, same-site-only redirect following. Never raises."""
    chain, cur = [], url
    for _ in range(MAX_REDIRECTS + 1):
        req = urllib.request.Request(cur, headers={"User-Agent": UA, "Accept-Encoding": "gzip, deflate", "Accept": "*/*"})
        t0 = time.time()
        try:
            resp = _OPENER.open(req, timeout=timeout)
            status = resp.status
        except urllib.error.HTTPError as e:
            resp, status = e, e.code
        except Exception as e:
            return {"url": url, "final_url": cur, "status": None, "error": f"{type(e).__name__}: {e}", "chain": chain}
        ttfb = round((time.time() - t0) * 1000)
        headers = resp.headers
        if status in (301, 302, 303, 307, 308) and headers.get("Location"):
            nxt = urllib.parse.urljoin(cur, headers["Location"])
            chain.append({"from": cur, "status": status, "to": nxt})
            if not same_site(nxt, origin) or not nxt.startswith(("http://", "https://")):
                return {"url": url, "final_url": nxt, "status": status, "chain": chain, "headers": {}, "body": b"",
                        "ttfb_ms": ttfb, "note": "redirects to another site; not followed"}
            cur = nxt
            continue
        try:
            body = resp.read(MAX_BYTES + 1)
        except Exception:
            body = b""
        body = _decode(body, headers.get("Content-Encoding"))[:MAX_BYTES]
        return {"url": url, "final_url": cur, "status": status, "chain": chain, "headers": headers,
                "body": body, "ttfb_ms": ttfb}
    return {"url": url, "final_url": cur, "status": None, "error": "too many redirects", "chain": chain}


def text_of(r):
    return r.get("body", b"").decode("utf-8", errors="replace")


# ---------- HTML parsing ----------

class Head(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = None
        self._in_title = False
        self.meta = {}
        self.canonicals = []
        self.hreflang = []
        self.h1 = []
        self._h1 = None
        self.links = 0
        self.imgs = 0
        self.imgs_no_alt = 0
        self.b64_imgs = 0
        self.b64_bytes = 0
        self.jsonld = []
        self._ld = None
        self.text_len = 0
        self._skip = 0
        self.html_lang = None
        self.root_empty = False
        self._root_stack = None
        self.lazy_imgs = 0

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if tag == "html":
            self.html_lang = a.get("lang")
        elif tag == "title":
            self._in_title = True
            self.title = ""
        elif tag == "meta":
            key = (a.get("name") or a.get("property") or a.get("http-equiv") or "").lower()
            if key and key not in self.meta:
                self.meta[key] = a.get("content", "")
        elif tag == "link":
            rel = a.get("rel", "").lower().split()
            if "canonical" in rel:
                self.canonicals.append(a.get("href", ""))
            if "alternate" in rel and a.get("hreflang"):
                self.hreflang.append(a["hreflang"])
        elif tag == "a" and a.get("href"):
            self.links += 1
        elif tag == "h1":
            self._h1 = ""
        elif tag == "img":
            self.imgs += 1
            if "alt" not in a:
                self.imgs_no_alt += 1
            if a.get("loading", "").lower() == "lazy":
                self.lazy_imgs += 1
            if a.get("src", "").startswith("data:image"):
                self.b64_imgs += 1
                self.b64_bytes += len(a["src"])
        elif tag == "script":
            self._skip += 1
            if a.get("type", "").lower() == "application/ld+json":
                self._ld = ""
        elif tag in ("style", "noscript"):
            self._skip += 1
        if tag == "div" and a.get("id") in ("root", "app", "__next", "__nuxt") and self._root_stack is None:
            self._root_stack = {"id": a["id"], "text": 0}

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag == "h1" and self._h1 is not None:
            self.h1.append(self._h1.strip())
            self._h1 = None
        elif tag == "script":
            self._skip = max(0, self._skip - 1)
            if self._ld is not None:
                self.jsonld.append(self._ld)
                self._ld = None
        elif tag in ("style", "noscript"):
            self._skip = max(0, self._skip - 1)

    def handle_data(self, data):
        if self._in_title and self.title is not None:
            self.title += data
        if self._ld is not None:
            self._ld += data
        if self._h1 is not None:
            self._h1 += data
        if not self._skip:
            n = len(data.strip())
            self.text_len += n


def ld_types(blocks):
    types, bad = [], 0
    def walk(o):
        if isinstance(o, dict):
            t = o.get("@type")
            if isinstance(t, str):
                types.append(t)
            elif isinstance(t, list):
                types.extend(x for x in t if isinstance(x, str))
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    for b in blocks:
        try:
            walk(json.loads(b))
        except Exception:
            bad += 1
    return sorted(set(types)), bad


# ---------- framework signals ----------

def detect_frameworks(html, headers, cookies):
    sig = []
    low = html.lower()
    def add(name, why):
        sig.append({"framework": name, "evidence": why})
    if "/_next/static" in low or "__next_data__" in low or "self.__next_f" in low:
        router = "App Router" if "self.__next_f" in low else ("Pages Router" if "__next_data__" in low else "router unknown")
        add("Next.js", f"/_next/ assets or Next data script ({router})")
    if "__nuxt" in low or "/_nuxt/" in low:
        add("Nuxt", "__NUXT__ or /_nuxt/")
    if "___gatsby" in low:
        add("Gatsby", "___gatsby root")
    if "ng-version=" in low or "<app-root" in low:
        add("Angular", "ng-version or <app-root>")
    if "data-reactroot" in low or 'id="root"' in low:
        add("React (SPA root)", 'id="root" / data-reactroot')
    if "wp-content/" in low or "wp-includes/" in low:
        add("WordPress", "wp-content/ or wp-includes/")
    if "cdn.shopify.com" in low or "shopify.theme" in low:
        add("Shopify", "cdn.shopify.com or Shopify.theme")
    if "x-wix-request-id" in headers or "wixstatic.com" in low:
        add("Wix", "x-wix-request-id or wixstatic.com")
    if "data-wf-page" in low:
        add("Webflow", "data-wf-page")
    lv = []
    if any(c.startswith(("laravel_session", "xsrf-token")) for c in cookies):
        lv.append("laravel_session/XSRF-TOKEN cookie")
    if 'name="csrf-token"' in low:
        lv.append("csrf-token meta")
    if "/build/assets/" in low:
        lv.append("/build/assets/ (Vite)")
    if re.search(r"\bwire:[a-z]", low) or "/livewire/" in low:
        lv.append("Livewire")
    if 'data-page="' in low or "data-page='" in low:
        lv.append("Inertia data-page")
    if lv:
        add("Laravel", ", ".join(lv))
    xp = headers.get("x-powered-by", "")
    if xp:
        add("Server header", f"X-Powered-By: {xp}")
    return sig


def tracking_in(html):
    found = {}
    for name, (det, idre) in TRACKER_RE.items():
        if det.search(html):
            ids = []
            if idre:
                for m in idre.findall(html):
                    ids.append(m if isinstance(m, str) else m[0])
            found[name] = sorted(set(ids))
    return found


# ---------- per-page analysis ----------

def analyse(r, origin):
    out = {"url": r["url"], "final_url": r.get("final_url"), "status": r.get("status")}
    if r.get("error") or r.get("status") is None:
        out["error"] = r.get("error", "no response")
        return out
    h = r["headers"]
    lower = {k.lower(): v for k, v in h.items()} if h else {}
    cookies = [c.split("=")[0].strip().lower() for c in (h.get_all("Set-Cookie") or [])] if h else []
    out["redirects"] = len(r["chain"])
    out["ttfb_ms"] = r.get("ttfb_ms")
    out["bytes"] = len(r["body"])
    out["headers"] = {k: lower.get(k) for k in ("content-type", "cache-control", "x-robots-tag", "strict-transport-security",
                                                  "content-encoding", "server", "x-powered-by") if lower.get(k)}
    out["cookies"] = cookies
    ct = lower.get("content-type", "")
    if "html" not in ct and r["body"][:200].lstrip()[:1] != b"<":
        out["non_html"] = ct
        return out
    html = text_of(r)
    p = Head()
    try:
        p.feed(html)
    except Exception:
        pass
    types, bad_ld = ld_types(p.jsonld)
    canon = p.canonicals[0] if p.canonicals else None
    out.update({
        "title": (p.title or "").strip() or None,
        "meta_description": (p.meta.get("description") or "").strip() or None,
        "meta_robots": p.meta.get("robots"),
        "canonical": canon,
        "canonical_count": len(p.canonicals),
        "h1_count": len(p.h1),
        "h1": p.h1[:2],
        "links": p.links,
        "images": p.imgs, "images_no_alt": p.imgs_no_alt,
        "inline_base64_images": p.b64_imgs, "inline_base64_chars": p.b64_bytes,
        "jsonld_types": types, "jsonld_invalid_blocks": bad_ld,
        "viewport": "viewport" in p.meta,
        "lang": p.html_lang,
        "hreflang": p.hreflang,
        "visible_text_chars": p.text_len,
        "og_title": "og:title" in p.meta,
    })
    # JS-shell heuristic: little visible text and no H1/links, with an app root present
    out["js_shell_suspect"] = bool(p.text_len < 200 and p.links < 3 and not p.h1 and
                                   re.search(r'id="(root|app|__next|__nuxt)"', html))
    out["frameworks"] = detect_frameworks(html, lower, cookies)
    out["tracking"] = tracking_in(html)
    out["gtm_noscript"] = "googletagmanager.com/ns.html" in html
    return out


# ---------- site-level ----------

def parse_robots(text):
    groups, cur = defaultdict(list), []
    sitemaps = []
    prev_ua = False
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        k, v = [s.strip() for s in line.split(":", 1)]
        k = k.lower()
        if k == "user-agent":
            cur = (cur if prev_ua else []) + [v.lower()]  # consecutive User-agent lines share one group
            for ua in cur:
                groups.setdefault(ua, [])
            prev_ua = True
            continue
        prev_ua = False
        if k in ("disallow", "allow") and cur:
            for ua in cur:
                groups[ua].append((k, v))
        elif k == "sitemap":
            sitemaps.append(v)
    star = groups.get("*", [])
    return {"sitemaps": sitemaps,
            "blanket_disallow": ("disallow", "/") in star and ("allow", "/") not in star,
            "disallow_rules": [v for k, v in star if k == "disallow" and v][:20],
            "ai_bots_blocked": sorted(ua for ua in groups if ua in ("gptbot", "claudebot", "ccbot", "perplexitybot", "google-extended")
                                      and ("disallow", "/") in groups[ua])}


LOC = re.compile(r"<loc>\s*([^<\s]+)\s*</loc>", re.I)
URLBLOCK = re.compile(r"<url>(.*?)</url>", re.I | re.S)


def load_sitemap(urls, timeout, origin, cap=2000):
    """Return (list of {loc, lastmod}, info). Follows one level of sitemap index."""
    entries, info = [], {"fetched": [], "has_changefreq_or_priority": False}
    queue = list(urls)[:10]
    seen = set()
    while queue and len(entries) < cap:
        u = queue.pop(0)
        if u in seen or not same_site(u, origin):
            continue
        seen.add(u)
        r = fetch(u, timeout, origin)
        info["fetched"].append({"url": u, "status": r.get("status")})
        if r.get("status") != 200:
            continue
        txt = text_of(r)
        if "<sitemapindex" in txt.lower():
            queue.extend(LOC.findall(txt)[:10])
            continue
        if re.search(r"<(changefreq|priority)>", txt, re.I):
            info["has_changefreq_or_priority"] = True
        for blk in URLBLOCK.findall(txt):
            loc = LOC.search(blk)
            lm = re.search(r"<lastmod>\s*([^<\s]+)", blk, re.I)
            if loc and same_site(loc.group(1), origin):
                entries.append({"loc": loc.group(1), "lastmod": lm.group(1)[:10] if lm else None})
    return entries, info


def sample_urls(entries, n):
    """Spread the sample across first path segments (templates)."""
    buckets = defaultdict(list)
    for e in entries:
        seg = urllib.parse.urlsplit(e["loc"]).path.strip("/").split("/")[0]
        buckets[seg].append(e["loc"])
    out, i = [], 0
    keys = sorted(buckets, key=lambda k: -len(buckets[k]))
    while len(out) < n and any(buckets.values()):
        k = keys[i % len(keys)]
        if buckets[k]:
            out.append(buckets[k].pop(0))
        i += 1
    return out


def is_content_page(p):
    """2xx HTML pages only. Error pages and non-HTML are excluded from on-page and coverage checks."""
    return bool(p.get("status") and 200 <= p["status"] < 300 and "error" not in p and "non_html" not in p)


def build_hints(pages, robots, rtxt_status, sm_entries, sm_info, tracking_cov, origin):
    hints = []
    def hint(id_, sev, msg, urls=None, ref=None):
        hints.append({"id": id_, "severity": sev, "message": msg, "pages": (urls or [])[:15], "checklist": ref})
    ok = [p for p in pages if is_content_page(p)]

    if rtxt_status != 200:
        hint("robots-missing", "medium", f"robots.txt returned {rtxt_status}", ref="TECH-01")
    elif robots["blanket_disallow"]:
        hint("robots-blanket-disallow", "critical", "robots.txt disallows the whole site for all crawlers", ref="TECH-01")
    if rtxt_status == 200 and not robots["sitemaps"]:
        hint("robots-no-sitemap", "low", "robots.txt has no Sitemap: line", ref="TECH-03")

    for p in pages:
        if p.get("error"):
            hint("fetch-error", "high", f"Could not fetch: {p['error']}", [p["url"]], "TECH-02")
    bad = [p["url"] for p in pages if p.get("status") and p["status"] >= 400]
    if bad:
        hint("non-200", "high", "Pages returned 4xx/5xx (sitemap or crawl sample)", bad, "TECH-02")
    chains = [p["url"] for p in ok if p.get("redirects", 0) >= 2]
    if chains:
        hint("redirect-chain", "medium", "Redirect chains of 2+ hops", chains, "TECH-02")

    def missing(field, label, sev, ref):
        urls = [p["url"] for p in ok if not p.get(field)]
        if urls:
            hint(f"missing-{field}", sev, f"{label} missing in raw HTML on {len(urls)} of {len(ok)} pages", urls, ref)
    missing("title", "<title>", "high", "TECH-05")
    missing("meta_description", "Meta description", "medium", "TECH-05")
    missing("canonical", "Canonical", "high", "TECH-04")
    multi_h1 = [p["url"] for p in ok if p.get("h1_count", 0) > 1]
    none_h1 = [p["url"] for p in ok if p.get("h1_count", 0) == 0]
    if none_h1:
        hint("no-h1", "high", "No <h1> in raw HTML", none_h1, "TECH-05")
    if multi_h1:
        hint("multiple-h1", "low", "More than one <h1>", multi_h1, "TECH-05")
    noidx = [p["url"] for p in ok if "noindex" in ((p.get("meta_robots") or "") + (p.get("headers", {}).get("x-robots-tag") or "")).lower()]
    if noidx:
        hint("noindex-found", "info", "noindex on these pages. Confirm it is intended (critical if they are money/content pages)", noidx, "TECH-01")
    off_canon = []
    for p in ok:
        c = p.get("canonical")
        if c and (not c.startswith("http") or not same_site(c, origin)):
            off_canon.append(p["url"])
    if off_canon:
        hint("canonical-relative-or-offsite", "medium", "Canonical is relative or points to another site", off_canon, "TECH-04")
    nov = [p["url"] for p in ok if not p.get("viewport")]
    if nov:
        hint("no-viewport", "medium", "Missing viewport meta (mobile-first indexing)", nov, "TECH-05")
    nolang = [p["url"] for p in ok if not p.get("lang")]
    if nolang:
        hint("no-html-lang", "low", "Missing <html lang>", nolang, "TECH-05")

    shell = [p["url"] for p in ok if p.get("js_shell_suspect")]
    if shell:
        hint("js-shell", "high", "Raw HTML looks like an empty JavaScript shell (little text, no H1/links). Compare with the rendered DOM in a browser", shell, "TECH-08")
    nolinks = [p["url"] for p in ok if p.get("links", 0) < 3 and not p.get("js_shell_suspect")]
    if nolinks:
        hint("few-links-raw", "medium", "Fewer than 3 <a href> links in raw HTML. Navigation may be JS-only", nolinks, "TECH-08")
    ldbad = [p["url"] for p in ok if p.get("jsonld_invalid_blocks")]
    if ldbad:
        hint("jsonld-invalid", "high", "JSON-LD block that does not parse", ldbad, "TECH-06")
    b64 = [p["url"] for p in ok if p.get("inline_base64_chars", 0) > 50_000]
    if b64:
        hint("inline-base64", "medium", "More than ~50 KB of inline base64 images in the HTML", b64, "TECH-09")
    big = [p["url"] for p in ok if p.get("bytes", 0) > 500_000]
    if big:
        hint("large-html", "medium", "HTML document over 500 KB (uncompressed)", big, "TECH-09")
    slow = [p["url"] for p in ok if (p.get("ttfb_ms") or 0) > 800]
    if slow:
        hint("slow-ttfb", "medium", "Time to first byte over 800 ms from this location. Re-test, since one sample is noisy", slow, "TECH-09")
    if origin.startswith("https://"):
        nohsts = [p["url"] for p in ok if "strict-transport-security" not in p.get("headers", {})]
        if nohsts and len(nohsts) == len(ok):
            hint("no-hsts", "low", "No Strict-Transport-Security header", nohsts[:5], "TECH-10")
    nocache = [p["url"] for p in ok if not p.get("headers", {}).get("cache-control")]
    if nocache and len(nocache) == len(ok):
        hint("no-cache-control", "low", "No Cache-Control header on any sampled page", nocache[:5], "TECH-09")
    sess = [p["url"] for p in ok if any(c.startswith(("laravel_session", "phpsessid", "xsrf-token")) for c in p.get("cookies", []))]
    if sess:
        hint("session-cookie-public", "medium", "Session cookie set on public pages. This can defeat CDN caching", sess, "TECH-09")
    dbg = [p["url"] for p in ok if p.get("headers", {}).get("x-powered-by")]
    if dbg:
        hint("x-powered-by", "info", "X-Powered-By discloses the stack", dbg[:3], "TECH-10")

    # private paths
    priv_sm = [e["loc"] for e in sm_entries if any(urllib.parse.urlsplit(e["loc"]).path.lower().startswith(x) for x in PRIVATE_PATHS)]
    if priv_sm:
        hint("private-url-in-sitemap", "high", "Private/transactional URLs listed in the sitemap", priv_sm, "TECH-03")
    priv_idx = [p["url"] for p in ok if any(urllib.parse.urlsplit(p["url"]).path.lower().startswith(x) for x in PRIVATE_PATHS)
                and "noindex" not in ((p.get("meta_robots") or "") + (p.get("headers", {}).get("x-robots-tag") or "")).lower()]
    if priv_idx:
        hint("private-url-indexable", "high", "Private/transactional pages without noindex", priv_idx, "TECH-01")

    # sitemap sanity
    lm = [e["lastmod"] for e in sm_entries if e.get("lastmod")]
    if len(lm) >= 10:
        top, n = Counter(lm).most_common(1)[0]
        if n / len(lm) >= 0.8:
            hint("sitemap-lastmod-uniform", "low", f"{n} of {len(lm)} sitemap entries share lastmod {top}. It is probably generation time, not content change", ref="TECH-03")
    if sm_info.get("has_changefreq_or_priority"):
        hint("sitemap-changefreq-priority", "info", "Sitemap uses changefreq/priority. Google ignores both", ref="TECH-03")
    if robots.get("sitemaps") and not sm_entries:
        hint("sitemap-empty", "high", "Sitemap listed but no usable URLs found (not fetched, empty, or other host)", ref="TECH-03")

    # tracking
    n = len(ok)
    if n:
        if not tracking_cov:
            hint("no-tracking-raw", "info", "No tracking tags found in raw HTML. They may be injected by JS/GTM, so check the Network panel", ref="TECH-11")
        for name, c in tracking_cov.items():
            if 0 < c["pages_with"] < n and c["pages_with"] / n >= 0.5:
                hint("tracking-inconsistent", "high", f"{name} present on {c['pages_with']} of {n} sampled pages", c["missing_urls"], "TECH-11")
            if len(c["ids"]) > 1:
                hint("tracking-multiple-ids", "medium", f"{name} has multiple IDs: {', '.join(c['ids'])}. Confirm that is intended", ref="TECH-11")
        if "Universal Analytics (retired)" in tracking_cov:
            hint("ua-retired", "medium", "Universal Analytics (UA-) code is still present. UA stopped processing data in 2023", ref="TECH-11")
        if "GA4" in tracking_cov and "Google Tag Manager" in tracking_cov:
            hint("ga4-and-gtm", "low", "GA4 gtag.js and GTM both present. Check GTM is not also firing GA4 (duplicate pageviews)", ref="TECH-11")
        gtm_pages = [p for p in ok if "Google Tag Manager" in p.get("tracking", {})]
        no_ns = [p["url"] for p in gtm_pages if not p.get("gtm_noscript")]
        if no_ns and len(no_ns) == len(gtm_pages):
            hint("gtm-noscript-missing", "low", "GTM <noscript> iframe not found in raw HTML", no_ns[:5], "TECH-11")
    return hints


def main():
    ap = argparse.ArgumentParser(description="Technical SEO probe (raw HTML, headers, tracking coverage).")
    ap.add_argument("--url", required=True)
    ap.add_argument("--sample", type=int, default=15, help="URLs to sample from the sitemap (default 15)")
    ap.add_argument("--urls-file", help="File with extra URLs, one per line (same site only)")
    ap.add_argument("--max-pages", type=int, default=25, help="Hard cap on pages fetched (default 25, max 50)")
    ap.add_argument("--timeout", type=int, default=20)
    ap.add_argument("--output")
    a = ap.parse_args()

    target = a.url if "://" in a.url else "https://" + a.url
    sp = urllib.parse.urlsplit(target)
    if sp.scheme not in ("http", "https") or not sp.hostname:
        print(json.dumps({"status": "error", "error": "URL must be http(s)"}))
        return 1
    origin = f"{sp.scheme}://{sp.netloc}"
    cap = max(1, min(a.max_pages, 50))

    rr = fetch(origin + "/robots.txt", a.timeout, origin)
    rtxt_status = rr.get("status")
    robots = parse_robots(text_of(rr)) if rtxt_status == 200 else {"sitemaps": [], "blanket_disallow": False, "disallow_rules": [], "ai_bots_blocked": []}
    sm_urls = robots["sitemaps"] or [origin + "/sitemap.xml"]
    entries, sm_info = load_sitemap(sm_urls, a.timeout, origin)

    urls = [target]
    urls += sample_urls(entries, a.sample)
    if a.urls_file:
        with open(a.urls_file, encoding="utf-8") as f:
            urls += [u.strip() for u in f if u.strip() and same_site(u.strip(), origin)]
    seen, plan = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            plan.append(u)
    plan = plan[:cap]

    with ThreadPoolExecutor(max_workers=4) as ex:
        results = list(ex.map(lambda u: analyse(fetch(u, a.timeout, origin), origin), plan))

    ok = [p for p in results if is_content_page(p)]
    cov = {}
    for p in ok:
        for name, ids in p.get("tracking", {}).items():
            c = cov.setdefault(name, {"pages_with": 0, "ids": set(), "missing_urls": []})
            c["pages_with"] += 1
            c["ids"].update(ids)
    for name, c in cov.items():
        c["missing_urls"] = [p["url"] for p in ok if name not in p.get("tracking", {})][:15]
        c["ids"] = sorted(c["ids"])
        c["pages_total"] = len(ok)

    fw = Counter(s["framework"] for p in ok for s in p.get("frameworks", []))
    result = {
        "status": "ok",
        "target": target,
        "pages_fetched": len(results),
        "sitemap_urls_found": len(entries),
        "frameworks_seen": [{"framework": k, "pages": v} for k, v in fw.most_common()],
        "robots": {"status": rtxt_status, **robots},
        "sitemap": sm_info,
        "tracking_coverage": cov,
        "hints": build_hints(results, robots, rtxt_status, entries, sm_info, cov, origin),
        "pages": results,
        "limits": [
            "Raw HTML only: content, links, schema and tags added by JavaScript or Google Tag Manager are not visible here.",
            "Confirm JS-dependent items in a browser (rendered DOM, Network panel).",
            "One request per page from one location; TTFB and headers can differ by region and CDN state.",
            f"Sampled {len(results)} pages; coverage statements apply to the sample, not the whole site.",
        ],
    }
    text = json.dumps(result, indent=2)
    if a.output:
        with open(a.output, "w", encoding="utf-8") as f:
            f.write(text + "\n")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
