#!/usr/bin/env python3
"""Fan-out coverage mapper: score how well a page covers a set of related sub-queries.

The agent builds the sub-query set (see references/fanout-mapper.md) and saves it as JSON.
This script reads one page (and optionally a competitor page), scores every sub-query against
the page's passages, and writes a JSON, Markdown and HTML report with an aspect breakdown,
a sub-query heat map, missing terms, gap suggestions and an optional side-by-side "battle".

Usage:
    python3 fanout_coverage.py --fanout fanout.json --url https://example.com/page \
        [--competitor-url https://example.com/other] [--brand "acme,acme corp"] --output-dir out

    Page sources (use one per page): --url, --html FILE (saved HTML), --text FILE (pasted text;
    lines starting with '#' are headings). Same for the competitor with --competitor-*.

fanout.json:
    {"query": "what to pack on a cruise",
     "aspects": [{"name": "Follow-up questions", "queries": ["...", "..."]}, ...]}
    A flat {"query": ..., "queries": ["...", ...]} list is also accepted.

Scoring is word-overlap based (light stemming, no synonyms), computed per passage with the
section heading included. It is a content-gap heuristic, not a search-engine metric.

Exit codes: 0 ok, 1 error, 2 page needs a real browser (JavaScript shell or unreachable).
Python 3.8+, standard library only.
"""

import argparse
import html as html_mod
import json
import math
import re
import sys
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

UA = "fanout-mapper/1.0 (+https://github.com/seobiopse/seo-aeo-geo-audit)"
MAX_BYTES = 3 * 1024 * 1024
TIMEOUT = 25
COVERED, PARTIAL = 0.72, 0.45
MIN_PAGE_WORDS = 120

STOP = set("""a an the and or of to in on for with is are was were be been being it its this that these those
how what why when where which who whom do does did can could should would will you your i we they he she at by from
as about into over after before up down out if than then so vs versus there their them our my me""".split())

SKIP_TAGS = {"script", "style", "noscript", "svg", "template", "iframe", "nav", "footer", "aside", "form", "button", "select"}
BLOCK_TAGS = {"p", "li", "div", "td", "th", "tr", "blockquote", "pre", "dt", "dd", "figcaption", "summary", "section",
              "article", "ul", "ol", "table", "details", "main", "header", "br"}


# ---------- text helpers ----------

def stem(w):
    w = w.lower()
    if len(w) > 4 and w.endswith("ies"):
        w = w[:-3] + "y"
    elif len(w) > 5 and w.endswith("ing"):
        w = w[:-3]
        if len(w) > 3 and w[-1] == w[-2] and w[-1] not in "aeioulsz":
            w = w[:-1]
    elif len(w) > 5 and w.endswith("ed"):
        w = w[:-2]
        if len(w) > 3 and w[-1] == w[-2] and w[-1] not in "aeioulsz":
            w = w[:-1]
    if len(w) > 3 and w.endswith("s") and not w.endswith(("ss", "us", "is")):
        w = w[:-1]
    if len(w) > 3 and w.endswith("e"):
        w = w[:-1]
    return w


WORD = re.compile(r"[^\W_]+", re.UNICODE)


def tokens(text):
    """Stemmed, stopword-free token sequence (keeps order for bigrams)."""
    return [stem(w) for w in WORD.findall(text.lower()) if w not in STOP and len(w) > 1]


def clean(parts):
    return re.sub(r"\s+", " ", html_mod.unescape(" ".join(parts))).strip()


def esc(s):
    return html_mod.escape(str(s), quote=True)


# ---------- page extraction ----------

class Extract(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = None
        self._in_title = False
        self.skip = 0
        self.buf = []
        self.hbuf = []
        self.in_h = 0
        self.stack = []
        self.heading = ""
        self.passages = []
        self.headings = []

    def flush(self):
        text = clean(self.buf)
        self.buf = []
        if len(WORD.findall(text)) >= 2:
            self.passages.append({"heading": self.heading, "text": text, "kind": "text"})

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self._in_title = True
            self.title = ""
        if tag in SKIP_TAGS:
            self.skip += 1
            return
        if self.skip:
            return
        if re.fullmatch(r"h[1-6]", tag):
            self.flush()
            self.in_h = int(tag[1])
            self.hbuf = []
        elif tag in BLOCK_TAGS:
            self.flush()

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag in SKIP_TAGS:
            self.skip = max(0, self.skip - 1)
            return
        if self.skip:
            return
        if self.in_h and tag == f"h{self.in_h}":
            text = clean(self.hbuf)
            self.stack = self.stack[: self.in_h - 1] + [text]
            self.heading = text
            if text:
                self.headings.append(text)
                self.passages.append({"heading": text, "text": text, "kind": "heading"})
            self.in_h = 0
        elif tag in BLOCK_TAGS:
            self.flush()

    def handle_data(self, data):
        if self._in_title and self.title is not None:
            self.title += data
        if self.skip:
            return
        (self.hbuf if self.in_h else self.buf).append(data)

    def close(self):
        super().close()
        self.flush()


def parse_html(src):
    p = Extract()
    p.feed(src)
    p.close()
    return {"title": clean([p.title or ""]), "passages": p.passages, "headings": p.headings}


def parse_text(src):
    passages, headings, heading = [], [], ""
    blocks = [b.strip() for b in re.split(r"\n\s*\n", src) if b.strip()]
    for i, b in enumerate(blocks):
        first = b.splitlines()[0].strip()
        nxt = blocks[i + 1] if i + 1 < len(blocks) else ""
        is_h = first.startswith("#") or (len(b.splitlines()) == 1 and len(b) <= 90 and not re.search(r"[.?!:,;]$", b)
                                         and len(nxt) > len(b))
        if is_h:
            heading = first.lstrip("# ").strip()
            headings.append(heading)
            passages.append({"heading": heading, "text": heading, "kind": "heading"})
        else:
            for line in b.splitlines():
                line = line.strip(" -*•\t")
                if len(WORD.findall(line)) >= 2:
                    passages.append({"heading": heading, "text": line, "kind": "text"})
    return {"title": headings[0] if headings else "", "passages": passages, "headings": headings}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        raw = r.read(MAX_BYTES + 1)[:MAX_BYTES]
        enc = r.headers.get_content_charset() or "utf-8"
        return raw.decode(enc, errors="replace"), r.status


def load_page(url, html_file, text_file):
    """Return (page_dict, error_message_or_None)."""
    try:
        if url:
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            src, _ = fetch(url)
            page = parse_html(src)
            page["source"] = url
        elif html_file:
            page = parse_html(Path(html_file).read_text(encoding="utf-8-sig", errors="replace"))
            page["source"] = str(html_file)
        elif text_file:
            page = parse_text(Path(text_file).read_text(encoding="utf-8-sig", errors="replace"))
            page["source"] = str(text_file)
        else:
            return None, "no page source given"
    except (urllib.error.URLError, OSError, ValueError) as e:
        return None, f"{type(e).__name__}: {getattr(e, 'reason', e)}"
    page["words"] = sum(len(WORD.findall(p["text"])) for p in page["passages"] if p["kind"] == "text")
    page["min_words"] = 20 if text_file and not (url or html_file) else MIN_PAGE_WORDS
    return page, None


# ---------- windows (what a sub-query is scored against) ----------

def build_windows(page):
    """Each window = heading + 1 to 3 consecutive text passages of the same section."""
    wins, by_head = [], defaultdict(list)
    for p in page["passages"]:
        if p["kind"] == "text":
            by_head[p["heading"]].append(p["text"])
        else:
            wins.append({"heading": p["heading"], "text": p["text"], "heading_only": True})
    for head, texts in by_head.items():
        for i in range(len(texts)):
            for n in (1, 2, 3):
                chunk = texts[i:i + n]
                if len(chunk) < n:
                    break
                wins.append({"heading": head, "text": " ".join(chunk), "heading_only": False})
    for w in wins:
        seq = tokens(w["heading"] + " " + w["text"])
        w["seq"] = seq
        w["terms"] = set(seq)
        w["_bi"] = None
    index = defaultdict(list)
    for i, w in enumerate(wins):
        for t in w["terms"]:
            index[t].append(i)
    page_terms = set()
    for w in wins:
        page_terms |= w["terms"]
    page["windows"], page["index"], page["terms"] = wins, index, page_terms
    return page


def bigrams(seq):
    return set(zip(seq, seq[1:]))


def term_weights(fanout):
    """Rare terms carry the meaning; a word found in most sub-queries (the topic itself) counts for less."""
    df, n = Counter(), 0
    for a in fanout["aspects"]:
        for q in a["queries"]:
            n += 1
            df.update(set(tokens(q)))
    seed = set(tokens(fanout.get("query", "")))
    w = {}
    for t, d in df.items():
        w[t] = max(0.3, math.log(1 + n / d))
        if t in seed:
            w[t] = min(w[t], 0.5)
    return w


def score_query(qseq, page, weights):
    """Best window score for one sub-query. Returns (score, window or None)."""
    qset = []
    for t in qseq:
        if t not in qset:
            qset.append(t)
    if not qset:
        return 0.0, None
    tw = {t: weights.get(t, 1.0) for t in qset}
    total_w = sum(tw.values())
    hits = defaultdict(float)
    for t in qset:
        for wi in page["index"].get(t, ()):
            hits[wi] += tw[t]
    qbi = bigrams(qseq)
    best, best_w = 0.0, None
    for wi, c in hits.items():
        if c < 0.25 * total_w:
            continue
        w = page["windows"][wi]
        uni = c / total_w
        if qbi:
            if w["_bi"] is None:
                w["_bi"] = bigrams(w["seq"])
            bi = len(qbi & w["_bi"]) / len(qbi)
            s = 0.7 * uni + 0.3 * bi
        else:
            s = uni
        if s > best or (s == best and best_w is not None and len(w["text"]) < len(best_w["text"])):
            best, best_w = s, w
    return best, best_w


def classify(s, covered, partial):
    return "covered" if s >= covered else ("partial" if s >= partial else "missing")


# ---------- fan-out input ----------

def load_fanout(path, brands):
    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    aspects = data.get("aspects")
    if not aspects:
        aspects = [{"name": "Related queries", "queries": data.get("queries", [])}]
    brand_terms = [b.strip().lower() for b in brands.split(",") if b.strip()] if brands else []
    seen, out, removed_brand, removed_dupe = set(), [], 0, 0
    for a in aspects:
        name = str(a.get("name") or "Other").strip()
        qs = []
        for q in a.get("queries", []):
            q = str(q).strip()
            if not q:
                continue
            if any(re.search(r"(?<!\w)" + re.escape(b) + r"(?!\w)", q.lower()) for b in brand_terms):
                removed_brand += 1
                continue
            key = tuple(sorted(set(tokens(q))))
            if not key or key in seen:
                removed_dupe += 1
                continue
            seen.add(key)
            qs.append(q)
        if qs:
            out.append({"name": name, "queries": qs})
    return {"query": str(data.get("query", "")).strip(), "aspects": out, "sources": data.get("sources", []),
            "removed_branded": removed_brand, "removed_duplicates": removed_dupe}


# ---------- analysis ----------

def analyse(fanout, page, covered, partial):
    weights = term_weights(fanout)
    results, aspect_rows = [], []
    all_missing_terms = Counter()
    display = {}
    for a in fanout["aspects"]:
        rows = []
        for q in a["queries"]:
            qseq = tokens(q)
            for raw in WORD.findall(q.lower()):
                display.setdefault(stem(raw), raw)
            s, w = score_query(qseq, page, weights)
            status = classify(s, covered, partial)
            absent = sorted({t for t in qseq if t not in page["terms"]})
            if status != "covered":
                for t in absent:
                    all_missing_terms[t] += 1
            row = {"aspect": a["name"], "query": q, "score": round(s, 2), "status": status,
                   "heading": (w or {}).get("heading", ""), "passage": ((w or {}).get("text", "") or "")[:220],
                   "absent_terms": [display.get(t, t) for t in absent]}
            rows.append(row)
            results.append(row)
        n = len(rows)
        c = sum(r["status"] == "covered" for r in rows)
        p = sum(r["status"] == "partial" for r in rows)
        aspect_rows.append({"name": a["name"], "total": n, "covered": c, "partial": p, "missing": n - c - p,
                            "pct": round(100 * (c + 0.5 * p) / n) if n else 0})
    total = len(results)
    c = sum(r["status"] == "covered" for r in results)
    p = sum(r["status"] == "partial" for r in results)
    overall = round(100 * (c + 0.5 * p) / total) if total else 0
    gaps = []
    for r in results:
        if r["status"] == "covered":
            continue
        where = r["heading"] if r["score"] >= 0.2 and r["heading"] else ""
        gaps.append({"aspect": r["aspect"], "query": r["query"], "status": r["status"],
                     "action": "extend" if where else "add", "where": where})
    gaps.sort(key=lambda g: (g["status"] != "missing", g["aspect"]))
    missing_terms = [{"term": display.get(t, t), "queries": n} for t, n in all_missing_terms.most_common(40)]
    return {"overall": overall, "total": total, "covered": c, "partial": p, "missing": total - c - p,
            "aspects": aspect_rows, "results": results, "gaps": gaps, "missing_terms": missing_terms}


def describe_sources(fanout):
    parts = []
    for s in fanout.get("sources", []):
        t = s.get("type")
        if t == "serper_google_serp":
            parts.append(f"Google SERP features (People also ask, Related searches) via Serper on {s.get('date', '')} "
                         f"({s.get('gl', '')}/{s.get('hl', '')}, {s.get('requests', '?')} requests)")
        elif t == "pasted":
            parts.append(f"queries pasted from {s.get('label', 'another source')} on {s.get('date', '')}")
        else:
            parts.append(str(s.get("label") or t or "other source"))
    return "Sub-queries: agent-generated estimates" + (" plus " + "; ".join(parts) if parts else ", with no real-search data added") + "."


def grade(v):
    return "Strong coverage" if v >= 75 else "Partial coverage" if v >= 50 else "Thin coverage" if v >= 25 else "Minimal coverage"


def battle(a, b):
    """Compare per-query status between page A (yours) and B (competitor)."""
    bmap = {r["query"]: r for r in b["results"]}
    they_only, you_only = [], []
    for r in a["results"]:
        o = bmap.get(r["query"])
        if not o:
            continue
        rank = {"missing": 0, "partial": 1, "covered": 2}
        if rank[o["status"]] > rank[r["status"]]:
            they_only.append({"aspect": r["aspect"], "query": r["query"], "you": r["status"], "them": o["status"]})
        elif rank[r["status"]] > rank[o["status"]]:
            you_only.append({"aspect": r["aspect"], "query": r["query"], "you": r["status"], "them": o["status"]})
    aspects = []
    bas = {x["name"]: x for x in b["aspects"]}
    for x in a["aspects"]:
        aspects.append({"name": x["name"], "you": x["pct"], "them": bas.get(x["name"], {}).get("pct", 0)})
    return {"aspects": aspects, "they_cover_you_dont": they_only, "you_cover_they_dont": you_only}


def scores_block(fanout, res):
    breakdown = [{"label": a["name"], "value": a["pct"], "max": 100,
                  "note": f"{a['covered']} covered, {a['partial']} partial, {a['missing']} missing of {a['total']}"}
                 for a in res["aspects"]]
    top = []
    for a in sorted(res["aspects"], key=lambda x: x["pct"])[:3]:
        if a["pct"] < 75:
            top.append(f"Cover the '{a['name']}' sub-queries: {a['missing']} missing, {a['partial']} partial.")
    return {"page_type": "Fan-out coverage (plugin heuristic, not a search-engine metric)",
            "overall": res["overall"], "grade": grade(res["overall"]), "breakdown": breakdown, "top_improvements": top}


# ---------- output ----------

COLORS = {"covered": "var(--ok)", "partial": "var(--mid)", "missing": "var(--bad)"}


def heat(res):
    out = []
    by = defaultdict(list)
    for r in res["results"]:
        by[r["aspect"]].append(r)
    for a in res["aspects"]:
        cells = "".join(f'<i class="c {r["status"]}" title="{esc(r["query"])} ({r["status"]}, {r["score"]})"></i>'
                        for r in by[a["name"]])
        out.append(f'<div class="hrow"><span class="hl">{esc(a["name"])}</span><span class="hc">{cells}</span>'
                   f'<b>{a["pct"]}%</b></div>')
    return "".join(out)


def render_html(fanout, page, res, comp, cres, bat, today):
    def bars(res_):
        return "".join(
            f'<div class="bar"><span>{esc(a["name"])}</span><div class="track"><div class="fill" style="width:{a["pct"]}%"></div></div>'
            f'<b>{a["pct"]}%</b><small>{a["covered"]}/{a["partial"]}/{a["missing"]}</small></div>' for a in res_["aspects"])

    def details(res_):
        by = defaultdict(list)
        for r in res_["results"]:
            by[r["aspect"]].append(r)
        out = []
        for a in res_["aspects"]:
            rows = "".join(
                f'<tr class="{r["status"]}"><td>{esc(r["query"])}</td><td><span class="pill {r["status"]}">{r["status"]}</span></td>'
                f'<td>{esc(r["heading"]) or "&mdash;"}</td><td class="pas">{esc(r["passage"])}</td></tr>' for r in by[a["name"]])
            out.append(f'<details><summary>{esc(a["name"])} <b>{a["pct"]}%</b></summary>'
                       f'<table><tr><th>Sub-query</th><th>Status</th><th>Best section</th><th>Best passage</th></tr>{rows}</table></details>')
        return "".join(out)

    gaps = "".join(
        f'<li><span class="pill {g["status"]}">{g["status"]}</span> <b>{esc(g["query"])}</b> '
        f'<small>{esc(g["aspect"])} &middot; {"extend section &ldquo;" + esc(g["where"]) + "&rdquo;" if g["action"] == "extend" else "add a new section"}</small></li>'
        for g in res["gaps"][:60])
    words = "".join(f'<span class="chip">{esc(w["term"])} <small>{w["queries"]}</small></span>' for w in res["missing_terms"])
    battle_html = ""
    if bat:
        cmp_rows = "".join(
            f'<div class="bar"><span>{esc(a["name"])}</span><div class="track2"><div class="fill" style="width:{a["you"]}%"></div>'
            f'<div class="fill them" style="width:{a["them"]}%"></div></div><b>{a["you"]}% / {a["them"]}%</b></div>'
            for a in bat["aspects"])
        theirs = "".join(f'<li>{esc(x["query"])} <small>{esc(x["aspect"])} &middot; you {x["you"]}, them {x["them"]}</small></li>'
                         for x in bat["they_cover_you_dont"][:40]) or "<li>None</li>"
        yours = "".join(f'<li>{esc(x["query"])} <small>{esc(x["aspect"])}</small></li>' for x in bat["you_cover_they_dont"][:40]) or "<li>None</li>"
        battle_html = f"""<section><h2>Battle mode</h2>
<p class="sub">Your page <b>{res['overall']}%</b> vs competitor <b>{cres['overall']}%</b> ({esc(comp.get('source',''))}). Bars: <span class="key you"></span> you, <span class="key them"></span> competitor.</p>
{cmp_rows}
<div class="two"><div><h3>They cover, you don&rsquo;t</h3><ul>{theirs}</ul></div><div><h3>You cover, they don&rsquo;t</h3><ul>{yours}</ul></div></div></section>"""
    ring = f'style="--v:{res["overall"]}"'
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Fan-out coverage map</title><style>
:root{{--bg:#f7f8fa;--fg:#14213d;--card:#fff;--line:#e3e6ec;--muted:#5b6578;--ok:#2f9e6e;--mid:#e0a526;--bad:#d9534f;--acc:#3b5bdb}}
@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{--bg:#0f1420;--fg:#e8ecf5;--card:#171e2e;--line:#2a3347;--muted:#9aa5bd;--ok:#3ec28f;--mid:#f0b940;--bad:#f0706b;--acc:#7c98ff}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}}
main{{max-width:1000px;margin:0 auto;padding:24px 16px 48px}}h1{{font-size:24px;margin:0 0 4px}}h2{{font-size:18px;margin:0 0 10px}}h3{{font-size:15px;margin:12px 0 6px}}
.sub{{color:var(--muted);margin:0 0 12px;overflow-wrap:anywhere}}section{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px;margin:16px 0}}
.top{{display:flex;gap:20px;align-items:center;flex-wrap:wrap}}.ring{{--v:0;width:120px;height:120px;border-radius:50%;background:conic-gradient(var(--acc) calc(var(--v)*1%),var(--line) 0);display:grid;place-items:center;flex:none}}
.ring span{{width:92px;height:92px;border-radius:50%;background:var(--card);display:grid;place-items:center;font-size:28px;font-weight:700}}
.stats{{display:flex;gap:10px;flex-wrap:wrap}}.stat{{border:1px solid var(--line);border-radius:10px;padding:8px 14px}}.stat b{{display:block;font-size:20px}}
.bar{{display:grid;grid-template-columns:minmax(120px,220px) 1fr 70px 80px;gap:10px;align-items:center;margin:6px 0}}.bar small{{color:var(--muted)}}
.track,.track2{{background:var(--line);border-radius:6px;height:12px;overflow:hidden;position:relative}}.fill{{background:var(--acc);height:100%}}.track2 .fill{{position:absolute;left:0;top:0;height:6px}}.track2 .them{{top:6px;background:var(--mid)}}
.key{{display:inline-block;width:12px;height:8px;border-radius:2px;background:var(--acc)}}.key.them{{background:var(--mid)}}
.hrow{{display:grid;grid-template-columns:minmax(120px,220px) 1fr 50px;gap:10px;align-items:center;margin:6px 0}}.hc{{display:flex;flex-wrap:wrap;gap:3px}}
.c{{width:14px;height:14px;border-radius:3px;display:inline-block}}.c.covered,.pill.covered{{background:var(--ok)}}.c.partial,.pill.partial{{background:var(--mid)}}.c.missing,.pill.missing{{background:var(--bad)}}
.pill{{color:#fff;border-radius:999px;padding:1px 9px;font-size:12px}}table{{width:100%;border-collapse:collapse;font-size:13px;margin:8px 0}}td,th{{border-top:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}}
.pas{{color:var(--muted)}}details{{border-top:1px solid var(--line);padding:8px 0}}summary{{cursor:pointer;font-weight:600}}summary b{{float:right}}
.chip{{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:2px 10px;margin:3px;font-size:13px}}.chip small{{color:var(--muted)}}
li{{margin:6px 0}}li small{{color:var(--muted);display:block}}.two{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}
.note{{font-size:12.5px;color:var(--muted)}}@media (max-width:700px){{.bar{{grid-template-columns:1fr 60px}}.bar .track,.bar .track2,.bar small{{grid-column:1/-1}}.two{{grid-template-columns:1fr}}.hrow{{grid-template-columns:1fr 46px}}.hc{{grid-column:1/-1}}}}
</style></head><body><main>
<h1>Fan-out coverage map</h1>
<p class="sub">Query: <b>{esc(fanout['query'])}</b> &middot; Page: {esc(page.get('source',''))} &middot; {today}</p>
<section><div class="top"><div class="ring" {ring}><span>{res['overall']}%</span></div>
<div><b>{grade(res['overall'])}</b><p class="sub">{res['total']} sub-queries in {len(res['aspects'])} aspects &middot; {fanout['removed_branded']} branded and {fanout['removed_duplicates']} duplicate removed &middot; {page['words']} words on the page</p>
<p class="sub">{esc(describe_sources(fanout))}</p>
<div class="stats"><div class="stat"><b style="color:var(--ok)">{res['covered']}</b>covered</div><div class="stat"><b style="color:var(--mid)">{res['partial']}</b>partial</div><div class="stat"><b style="color:var(--bad)">{res['missing']}</b>missing</div></div></div></div></section>
<section><h2>Coverage by aspect</h2><p class="sub">Counts are covered / partial / missing. Score counts a partial as half.</p>{bars(res)}</section>
<section><h2>Heat map</h2><p class="sub">One square per sub-query. Hover for the query.</p>{heat(res)}</section>
{battle_html}
<section><h2>Gaps to close</h2><p class="sub">Missing first. Each item names the section to extend, or says to add a new one.</p><ul>{gaps or '<li>No gaps.</li>'}</ul></section>
<section><h2>Missing words</h2><p class="sub">Terms from uncovered sub-queries that do not appear anywhere on the page (number = sub-queries using it).</p>{words or '<p>None.</p>'}</section>
<section><h2>Every sub-query</h2>{details(res)}</section>
<p class="note">Plugin heuristic: word-overlap coverage of a generated sub-query set (light stemming, no synonyms), scored per passage with its heading. It is a content-gap aid, not a search-engine metric, and does not predict rankings or citations. The sub-query set is an estimate; search engines do not publish theirs.</p>
</main></body></html>"""


def render_md(fanout, page, res, comp, cres, bat, today):
    L = [f"# Fan-out coverage map", "", f"**Query:** {fanout['query']}  ", f"**Page:** {page.get('source','')}  ", f"**Date:** {today}", "",
         f"**Coverage score: {res['overall']}%** ({grade(res['overall'])}). {res['total']} sub-queries in {len(res['aspects'])} aspects: "
         f"{res['covered']} covered, {res['partial']} partial, {res['missing']} missing. "
         f"Removed {fanout['removed_branded']} branded and {fanout['removed_duplicates']} duplicate sub-queries. {describe_sources(fanout)}", "",
         "## Coverage by aspect", "", "| Aspect | Score | Covered | Partial | Missing |", "|---|---|---|---|---|"]
    L += [f"| {a['name']} | {a['pct']}% | {a['covered']} | {a['partial']} | {a['missing']} |" for a in res["aspects"]]
    if bat:
        L += ["", f"## Battle mode (you {res['overall']}% vs competitor {cres['overall']}%)", "", "| Aspect | You | Competitor |", "|---|---|---|"]
        L += [f"| {a['name']} | {a['you']}% | {a['them']}% |" for a in bat["aspects"]]
        L += ["", "**They cover, you don't:**", ""] + [f"- {x['query']} ({x['aspect']})" for x in bat["they_cover_you_dont"][:40]]
        L += ["", "**You cover, they don't:**", ""] + [f"- {x['query']} ({x['aspect']})" for x in bat["you_cover_they_dont"][:40]]
    L += ["", "## Gaps to close", ""]
    L += [f"- [{g['status']}] **{g['query']}** ({g['aspect']}): " + (f"extend section \"{g['where']}\"" if g["action"] == "extend" else "add a new section")
          for g in res["gaps"][:60]] or ["- No gaps."]
    L += ["", "## Missing words", "", ", ".join(f"{w['term']} ({w['queries']})" for w in res["missing_terms"]) or "None.", "",
          "---", "_Plugin heuristic: word-overlap coverage of a generated sub-query set. Not a search-engine metric; does not predict rankings or citations._"]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description="Score a page against a fan-out sub-query set.")
    ap.add_argument("--fanout", required=True, help="fanout.json built by the agent")
    ap.add_argument("--url"); ap.add_argument("--html"); ap.add_argument("--text")
    ap.add_argument("--competitor-url"); ap.add_argument("--competitor-html"); ap.add_argument("--competitor-text")
    ap.add_argument("--brand", help="comma-separated brand terms; sub-queries containing them are removed")
    ap.add_argument("--covered", type=float, default=COVERED); ap.add_argument("--partial", type=float, default=PARTIAL)
    ap.add_argument("--output-dir", required=True); ap.add_argument("--name")
    a = ap.parse_args()

    try:
        fanout = load_fanout(a.fanout, a.brand)
    except (OSError, ValueError) as e:
        print(json.dumps({"status": "error", "error": f"fanout file: {e}"})); return 1
    if not fanout["aspects"]:
        print(json.dumps({"status": "error", "error": "no usable sub-queries in the fanout file"})); return 1

    page, err = load_page(a.url, a.html, a.text)
    if err or page["words"] < page["min_words"]:
        why = err or (f"only {page['words']} words of text found" + (" (likely a JavaScript shell or blocked page)" if page["min_words"] > 20 else ""))
        print(json.dumps({"status": "needs_browser", "reason": why,
                          "next": "Follow references/browser-access.md: open the page in Claude in Chrome, save the rendered text or HTML to a file, and re-run with --text or --html."}))
        return 2
    build_windows(page)
    res = analyse(fanout, page, a.covered, a.partial)

    comp = cres = bat = None
    if a.competitor_url or a.competitor_html or a.competitor_text:
        comp, cerr = load_page(a.competitor_url, a.competitor_html, a.competitor_text)
        if cerr or comp["words"] < comp["min_words"]:
            print(json.dumps({"status": "needs_browser", "reason": "competitor page: " + (cerr or f"only {comp['words']} words found"),
                              "next": "Follow references/browser-access.md for the competitor page."}))
            return 2
        build_windows(comp)
        cres = analyse(fanout, comp, a.covered, a.partial)
        bat = battle(res, cres)

    today = date.today().isoformat()
    outdir = Path(a.output_dir); outdir.mkdir(parents=True, exist_ok=True)
    slug = a.name or ("fanout-map-" + re.sub(r"[^a-z0-9]+", "-", fanout["query"].lower()).strip("-")[:40] + "-" + today)
    payload = {"status": "ok", "query": fanout["query"], "page": page.get("source"), "date": today,
               "sources": fanout["sources"], "sources_text": describe_sources(fanout),
               "removed_branded": fanout["removed_branded"], "removed_duplicates": fanout["removed_duplicates"],
               "result": res, "scores_block": scores_block(fanout, res)}
    if bat:
        payload["competitor"] = {"page": comp.get("source"), "overall": cres["overall"], "aspects": cres["aspects"]}
        payload["battle"] = bat
    files = {"json": outdir / f"{slug}.json", "md": outdir / f"{slug}.md", "html": outdir / f"{slug}.html"}
    files["json"].write_text(json.dumps(payload, indent=2), encoding="utf-8")
    files["md"].write_text(render_md(fanout, page, res, comp, cres, bat, today), encoding="utf-8")
    files["html"].write_text(render_html(fanout, page, res, comp, cres, bat, today), encoding="utf-8")
    print(json.dumps({"status": "ok", "score": res["overall"], "grade": grade(res["overall"]),
                      "covered": res["covered"], "partial": res["partial"], "missing": res["missing"],
                      "competitor_score": cres["overall"] if cres else None,
                      "files": {k: str(v) for k, v in files.items()}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
