#!/usr/bin/env python3
"""Add real-search data to a fan-out set (the input of fanout_coverage.py).

Two sources:
  --provider serper   Google "People also ask" and "Related searches" for a seed query, through the
                      Serper SERP API (https://serper.dev). Needs the user's own API key.
  --provider import   Queries the user pasted from somewhere else (one per line), with a label.

The key is optional for the skill as a whole: with no key (--key-stdin, SERPER_API_KEY or --key) the
serper provider prints a "skipped" result and exits 0, so the workflow continues without it.

Usage:
    printf '%s' "$KEY" | python3 fanout_enrich.py --provider serper --key-stdin \
        --query "what to pack on a cruise" [--gl us] [--hl en] [--max-requests 6] \
        [--exclude-domain example.com] [--brand "acme,acme corp"] \
        [--merge fanout.json] [--output observed.json]
    python3 fanout_enrich.py --provider import --import queries.txt --label "ChatGPT (pasted)" --merge fanout.json
    Add --dry-run to print the plan (requests and estimated credits) without calling the API.

--merge adds aspects to fanout.json ("People also ask (Google)", "Related searches (Google)" or
"Observed: <label>") and records the source under "sources". Re-running replaces those aspects.

What is sent: only the seed query and a few related queries, to the provider. Do not use confidential
text as the seed. The key is held in memory only: it is never printed, written to a file or put in
an error message. Python 3.8+, standard library only.
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

SERPER_ENDPOINT = "https://google.serper.dev/search"
TEST_ENDPOINT_ENV = "FANOUT_ENRICH_TEST_ENDPOINT"   # tests only; must point at localhost
UA = "fanout-enrich/1.0 (+https://github.com/seobiopse/seo-aeo-geo-audit)"
TIMEOUT = 30
WORD = re.compile(r"[^\W_]+", re.UNICODE)

ASPECT_PAA = "People also ask (Google)"
ASPECT_REL = "Related searches (Google)"


def norm(q):
    return " ".join(WORD.findall(q.lower()))


def token_set(q):
    return set(WORD.findall(q.lower()))


def jaccard(a, b):
    return len(a & b) / len(a | b) if (a or b) else 1.0


def endpoint():
    ov = os.environ.get(TEST_ENDPOINT_ENV)
    if not ov:
        return SERPER_ENDPOINT
    host = (urllib.parse.urlsplit(ov).hostname or "").lower()
    if host not in ("127.0.0.1", "localhost", "::1"):
        raise SystemExit(json.dumps({"status": "error", "error": f"{TEST_ENDPOINT_ENV} must point at localhost"}))
    return ov


def get_key(args):
    raw = ""
    if args.key_stdin:
        raw = sys.stdin.readline()
    raw = raw or args.key or os.environ.get("SERPER_API_KEY") or ""
    # Keep printable ASCII only: Windows PowerShell prepends a hidden BOM (U+FEFF) to piped text, which corrupts a key.
    return re.sub(r"[^\x21-\x7e]", "", raw)


def serper(query, key, gl, hl, num):
    body = json.dumps({"q": query, "gl": gl, "hl": hl, "num": num}).encode()
    req = urllib.request.Request(endpoint(), data=body, method="POST",
                                 headers={"X-API-KEY": key, "Content-Type": "application/json", "User-Agent": UA})
    last = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            try:
                msg = json.load(e).get("message", "")
            except Exception:
                msg = ""
            last = (e.code, msg or e.reason)
            if e.code not in (429, 500, 502, 503, 504):
                break
        except (urllib.error.URLError, TimeoutError, ValueError) as e:
            last = (0, f"network error: {getattr(e, 'reason', e)}")
        time.sleep(2 * (attempt + 1))
    code, msg = last
    raise RuntimeError(f"{code}: {msg}".replace(key, "***"))


def parse(resp):
    paa = [str(i.get("question", "")).strip() for i in (resp.get("peopleAlsoAsk") or []) if isinstance(i, dict)]
    rel = [str(i.get("query", "")).strip() for i in (resp.get("relatedSearches") or []) if isinstance(i, dict)]
    org = []
    for i in (resp.get("organic") or []):
        if isinstance(i, dict) and i.get("link"):
            org.append({"position": i.get("position"), "title": i.get("title", ""), "link": i["link"],
                        "domain": (urllib.parse.urlsplit(i["link"]).hostname or "").lower().removeprefix("www."),
                        "snippet": i.get("snippet", "")})
    credits = resp.get("credits")
    return [q for q in paa if q], [q for q in rel if q], org, credits if isinstance(credits, (int, float)) else None


def collect(args, key):
    seed = args.query.strip()
    brands = [b.strip().lower() for b in (args.brand or "").split(",") if b.strip()]
    seen = {norm(seed)}
    paa_out, rel_out, top, requests, credits = [], [], [], 0, 0
    follow_pool, chosen_sets = [], [token_set(seed)]

    def keep(q, bucket, origin):
        n = norm(q)
        if not n or n in seen:
            return
        if any(re.search(r"(?<!\w)" + re.escape(b) + r"(?!\w)", q.lower()) for b in brands):
            return
        seen.add(n)
        bucket.append({"query": q, "from": origin})

    resp = serper(seed, key, args.gl, args.hl, args.num)
    requests += 1
    paa, rel, org, cr = parse(resp)
    credits += cr or 1
    top = org
    for q in rel:
        keep(q, rel_out, seed)
    for q in paa:
        keep(q, paa_out, seed)
    # second level: expand a few distinct related searches, then questions, to widen the set
    for q in [x["query"] for x in rel_out] + [x["query"] for x in paa_out]:
        ts = token_set(q)
        if all(jaccard(ts, c) < 0.7 for c in chosen_sets):
            follow_pool.append(q)
            chosen_sets.append(ts)
    for q in follow_pool[: max(0, args.max_requests - 1)]:
        time.sleep(0.3)
        resp = serper(q, key, args.gl, args.hl, args.num)
        requests += 1
        p2, r2, _, cr = parse(resp)
        credits += cr or 1
        for x in r2:
            keep(x, rel_out, q)
        for x in p2:
            keep(x, paa_out, q)
    return {"paa": paa_out, "related": rel_out, "top": top, "requests": requests, "credits": credits}


def competitor_candidates(top, exclude):
    ex = (exclude or "").lower().removeprefix("www.")
    seen, out = set(), []
    for r in top:
        d = r["domain"]
        if not d or d == ex or d.endswith("." + ex) and ex or d in seen:
            continue
        seen.add(d)
        out.append({"domain": d, "title": r["title"], "url": r["link"], "position": r["position"]})
    return out[:8]


def merge(path, new_aspects, source):
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8-sig")) if p.exists() else {"query": "", "aspects": []}
    names = {a["name"] for a in new_aspects}
    data["aspects"] = [a for a in data.get("aspects", []) if a.get("name") not in names] + new_aspects
    srcs = [s for s in data.get("sources", []) if not (s.get("type") == source["type"] and s.get("label") == source.get("label"))]
    data["sources"] = srcs + [source]
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Add real-search data to a fan-out set.")
    ap.add_argument("--provider", choices=["serper", "import"], required=True)
    ap.add_argument("--query", help="seed query (serper)")
    ap.add_argument("--key", help="Serper API key. Discouraged: visible in process lists and shell history. Prefer --key-stdin or SERPER_API_KEY.")
    ap.add_argument("--key-stdin", action="store_true", help="read the key from the first line of stdin")
    ap.add_argument("--gl", default="us", help="country code (default us)")
    ap.add_argument("--hl", default="en", help="language code (default en)")
    ap.add_argument("--num", type=int, default=10)
    ap.add_argument("--max-requests", type=int, default=6, help="API requests to spend (default 6, max 15)")
    ap.add_argument("--exclude-domain", help="the user's own domain, left out of competitor candidates")
    ap.add_argument("--brand", help="comma-separated brand terms to drop")
    ap.add_argument("--import", dest="import_file", help="text file with one query per line (provider import)")
    ap.add_argument("--label", help="source label for imported queries, e.g. 'ChatGPT (pasted)'")
    ap.add_argument("--merge", help="fanout.json to add the aspects to")
    ap.add_argument("--output", help="write the observed data here as JSON")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    args.max_requests = max(1, min(args.max_requests, 15))
    today = date.today().isoformat()

    if args.provider == "import":
        if not args.import_file or not args.label:
            print(json.dumps({"status": "error", "error": "--import FILE and --label are required"})); return 1
        lines = [l.strip(" -*•\t") for l in Path(args.import_file).read_text(encoding="utf-8-sig").splitlines()]
        seen, qs = set(), []
        for l in lines:
            if l and norm(l) not in seen:
                seen.add(norm(l)); qs.append(l)
        aspect = {"name": f"Observed: {args.label}", "queries": qs}
        if args.merge:
            merge(args.merge, [aspect], {"type": "pasted", "label": args.label, "date": today})
        print(json.dumps({"status": "ok", "provider": "import", "queries": len(qs), "merged_into": args.merge}))
        return 0

    if not args.query:
        print(json.dumps({"status": "error", "error": "--query is required for the serper provider"})); return 1
    if args.dry_run:
        print(json.dumps({"status": "dry-run", "provider": "serper", "query": args.query, "requests": args.max_requests,
                          "estimated_credits": f"about {args.max_requests} (1 per request; confirm in your Serper dashboard)",
                          "sends": "the seed query and up to %d related queries" % (args.max_requests - 1)}))
        return 0
    key = get_key(args)
    if not key:
        print(json.dumps({"status": "skipped", "provider": "serper",
                          "reason": "No Serper API key provided; real-search enrichment skipped."}))
        return 0
    try:
        res = collect(args, key)
    except RuntimeError as e:
        msg = str(e)
        hint = ""
        if msg.startswith(("401", "403")):
            hint = "The key was rejected. Check it at https://serper.dev (dashboard)."
        elif msg.startswith(("402", "429")):
            hint = "Out of credits or rate limited. Check the Serper dashboard; try again later or reduce --max-requests."
        print(json.dumps({"status": "error", "provider": "serper", "error": msg, "hint": hint}))
        return 1

    observed = {"source": "serper-google-serp", "date": today, "query": args.query, "gl": args.gl, "hl": args.hl,
                "requests": res["requests"], "credits_used": res["credits"],
                "people_also_ask": res["paa"], "related_searches": res["related"], "top_results": res["top"]}
    if args.output:
        Path(args.output).write_text(json.dumps(observed, indent=2, ensure_ascii=False), encoding="utf-8")
    if args.merge:
        aspects = []
        if res["paa"]:
            aspects.append({"name": ASPECT_PAA, "queries": [x["query"] for x in res["paa"]]})
        if res["related"]:
            aspects.append({"name": ASPECT_REL, "queries": [x["query"] for x in res["related"]]})
        if aspects:
            merge(args.merge, aspects, {"type": "serper_google_serp", "label": "Google SERP via Serper", "date": today,
                                        "gl": args.gl, "hl": args.hl, "requests": res["requests"]})
    print(json.dumps({"status": "ok", "provider": "serper", "requests": res["requests"], "credits_used": res["credits"],
                      "people_also_ask": len(res["paa"]), "related_searches": len(res["related"]),
                      "competitor_candidates": competitor_candidates(res["top"], args.exclude_domain),
                      "merged_into": args.merge if (args.merge and (res["paa"] or res["related"])) else None,
                      "output": args.output}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
