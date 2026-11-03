#!/usr/bin/env python3
"""Run a PageSpeed Insights (API v5) test for a URL and emit a compact JSON summary.

The API key is optional for the skill as a whole: with no key (--key or the
PAGESPEED_API_KEY environment variable) this script prints a "skipped" result and
exits 0, so the audit continues without PageSpeed data.

Usage:
    python3 pagespeed.py --url https://example.com/ [--key KEY] [--strategy both]
                         [--output pagespeed.json]

Output (stdout, or --output file):
    {"status": "ok" | "skipped" | "error", "url": ..., "results": {"mobile": {...}, "desktop": {...}},
     "scores_block": {...}}   # drop into findings.json under scores.pagespeed

Docs: https://developers.google.com/speed/docs/insights/v5/get-started
Python 3.8+, standard library only. The key is held in memory only: it is never written
to the output, to a file, or into error messages.
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ENDPOINT = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
CATEGORIES = ["performance", "accessibility", "best-practices", "seo"]
CATEGORY_LABELS = {
    "performance": "Performance",
    "accessibility": "Accessibility",
    "best-practices": "Best Practices",
    "seo": "SEO",
}
# Lighthouse lab metrics: audit id -> label
LAB_METRICS = {
    "first-contentful-paint": "FCP",
    "largest-contentful-paint": "LCP",
    "total-blocking-time": "TBT",
    "cumulative-layout-shift": "CLS",
    "speed-index": "Speed Index",
    "interactive": "TTI",
}
TIMEOUT_S = 120  # PSI runs a real Lighthouse test; it is slow


def grade(score):
    if score >= 90:
        return "Good"
    if score >= 50:
        return "Needs improvement"
    return "Poor"


def call_api(url, key, strategy):
    params = [("url", url), ("strategy", strategy), ("key", key)]
    params += [("category", c) for c in CATEGORIES]  # repeat the parameter per category
    req_url = ENDPOINT + "?" + urllib.parse.urlencode(params)
    last_err = None
    for attempt in range(2):
        try:
            with urllib.request.urlopen(req_url, timeout=TIMEOUT_S) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            try:
                msg = json.load(e).get("error", {}).get("message", "")
            except Exception:
                msg = ""
            last_err = f"HTTP {e.code}: {msg or e.reason}"
            if e.code not in (429, 500, 502, 503, 504):
                break
        except (urllib.error.URLError, TimeoutError) as e:
            last_err = f"Network error: {getattr(e, 'reason', e)}"
        time.sleep(3)
    raise RuntimeError(last_err.replace(key, "***"))


def summarise_field(block):
    """CrUX field data from loadingExperience / originLoadingExperience."""
    if not block or not block.get("metrics"):
        return None
    metrics = {}
    for name, m in block["metrics"].items():
        metrics[name] = {"percentile": m.get("percentile"), "category": m.get("category")}
    return {
        "overall_category": block.get("overall_category"),
        "metrics": metrics,
        "fallback_to_origin": bool(block.get("origin_fallback")),
    }


def summarise(data):
    lh = data.get("lighthouseResult", {})
    audits = lh.get("audits", {})
    out = {"scores": {}, "lab": {}, "opportunities": [], "field": {}}

    for cat in CATEGORIES:
        c = lh.get("categories", {}).get(cat)
        if c and c.get("score") is not None:
            out["scores"][cat] = round(c["score"] * 100)

    for aid, label in LAB_METRICS.items():
        a = audits.get(aid)
        if a:
            out["lab"][label] = {
                "display": a.get("displayValue"),
                "value": a.get("numericValue"),
                "score": a.get("score"),
            }

    perf_refs = {r["id"] for r in lh.get("categories", {}).get("performance", {}).get("auditRefs", [])}
    for aid, a in audits.items():
        if aid not in perf_refs or a.get("score") is None or a["score"] >= 0.9:
            continue
        if a.get("scoreDisplayMode") not in ("numeric", "binary", "metricSavings"):
            continue
        if aid in LAB_METRICS:
            continue
        details = a.get("details") or {}
        out["opportunities"].append({
            "id": aid,
            "title": a.get("title"),
            "display": a.get("displayValue"),
            "score": a.get("score"),
            "savings_ms": details.get("overallSavingsMs"),
            "savings_bytes": details.get("overallSavingsBytes"),
        })
    out["opportunities"].sort(key=lambda o: (-(o["savings_ms"] or 0), o["score"]))
    out["opportunities"] = out["opportunities"][:10]

    out["field"]["page"] = summarise_field(data.get("loadingExperience"))
    out["field"]["origin"] = summarise_field(data.get("originLoadingExperience"))
    out["final_url"] = lh.get("finalUrl") or lh.get("finalDisplayedUrl")
    out["analysed_at"] = data.get("analysisUTCTimestamp")
    return out


def build_scores_block(results):
    """Shape for findings.json -> scores.pagespeed (rendered by generate_report.py)."""
    primary = results.get("mobile") or results.get("desktop")
    if not primary:
        return None
    breakdown = []
    for strategy in ("mobile", "desktop"):
        r = results.get(strategy)
        if not r:
            continue
        for cat, score in r["scores"].items():
            note = ""
            if cat == "performance" and r["lab"]:
                note = ", ".join(f"{k} {v['display']}" for k, v in r["lab"].items() if v.get("display"))
            breakdown.append({
                "label": f"{strategy.capitalize()} · {CATEGORY_LABELS[cat]}",
                "value": score,
                "max": 100,
                "note": note,
            })
    overall = primary["scores"].get("performance", 0)
    improvements = [
        f"{o['title']}" + (f" ({o['display']})" if o.get("display") else "")
        for o in primary["opportunities"][:3]
    ]
    return {
        "page_type": "Lighthouse via PageSpeed Insights (mobile headline)" if results.get("mobile")
        else "Lighthouse via PageSpeed Insights (desktop)",
        "overall": overall,
        "grade": grade(overall),
        "breakdown": breakdown,
        "top_improvements": improvements,
    }


def main():
    p = argparse.ArgumentParser(description="PageSpeed Insights v5 test with optional API key.")
    p.add_argument("--url", required=True)
    p.add_argument("--key", help="PageSpeed API key. Discouraged: visible in process lists and shell "
                   "history. Prefer --key-stdin or the PAGESPEED_API_KEY environment variable.")
    p.add_argument("--key-stdin", action="store_true", help="Read the API key from the first line of stdin")
    p.add_argument("--strategy", choices=["mobile", "desktop", "both"], default="both")
    p.add_argument("--output", help="Write JSON here instead of stdout")
    args = p.parse_args()

    stdin_key = sys.stdin.readline() if args.key_stdin else ""
    key = (stdin_key or args.key or os.environ.get("PAGESPEED_API_KEY") or "").strip()
    if not key:
        result = {
            "status": "skipped",
            "url": args.url,
            "reason": "No PageSpeed API key provided; PageSpeed test skipped.",
        }
    else:
        strategies = ["mobile", "desktop"] if args.strategy == "both" else [args.strategy]
        results, errors = {}, {}
        for s in strategies:
            try:
                results[s] = summarise(call_api(args.url, key, s))
            except Exception as e:  # keep going so one failed strategy doesn't lose the other
                errors[s] = str(e)
        result = {
            "status": "ok" if results else "error",
            "url": args.url,
            "results": results,
        }
        if errors:
            result["errors"] = errors
        block = build_scores_block(results) if results else None
        if block:
            result["scores_block"] = block

    text = json.dumps(result, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text + "\n")
    else:
        print(text)
    return 0 if result["status"] != "error" else 1


if __name__ == "__main__":
    sys.exit(main())
