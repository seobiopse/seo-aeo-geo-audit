#!/usr/bin/env python3
"""Find pages worth a fan-out content-gap check from Google Search Console data.

Reads a Search Console Performance export (Pages tab, CSV) or the same rows as JSON, and ranks pages by two
signals that are easy to misread on their own:

  1. Low CTR FOR ITS POSITION. CTR falls naturally as position falls, so a low CTR alone mostly finds pages
     ranking at position 12. Instead this builds YOUR site's own CTR-by-position curve (impression-weighted)
     and compares each page with it:  opportunity_clicks = impressions x max(0, typical CTR at that position - page CTR).
  2. Striking distance: average position 5 to 20 with high impressions (visible, not yet winning).

Optionally reads a page+query export to pick a seed query per page (the highest-impression non-brand query).

Usage:
    python3 gsc_opportunities.py --pages Pages.csv [--page-queries PageQueries.csv] [--brand "acme,acme corp"]
        [--min-impressions 100] [--limit 10] [--domain example.com] [--exclude "regex"] [--period "last 28 days"]
        [--output opportunities.json]
    python3 gsc_opportunities.py --json rows.json     # rows: [{"page","clicks","impressions","ctr","position"}, ...]

Which period? Search Console presets are 7 days, 28 days and 3 months (the API accepts any range). Use 28 days by
default: it smooths weekday swings and is recent. Use 3 months when pages get only tens of impressions in 28 days.
Use 7 days only to check a recent change. Search Console data lags by about two days, and average position is an
average over many queries, so treat it as a guide.

Python 3.8+, standard library only. Reads local files only.
"""

import argparse
import csv
import json
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

PAGE_KEYS = ("top pages", "pages", "page", "landing page", "url", "page url")
QUERY_KEYS = ("top queries", "queries", "query", "search query")
CLICK_KEYS = ("clicks",)
IMPR_KEYS = ("impressions",)
CTR_KEYS = ("ctr", "click-through rate", "click through rate")
POS_KEYS = ("position", "average position", "avg. position", "avg position")


def num(v):
    if v is None:
        return None
    s = str(v).strip().replace(",", "").replace(" ", "")
    if not s or s in ("-", "--"):
        return None
    pct = s.endswith("%")
    try:
        x = float(s.rstrip("%"))
    except ValueError:
        return None
    return x / 100 if pct else x


def find_col(headers, keys):
    low = {h.strip().lower(): h for h in headers}
    for k in keys:
        if k in low:
            return low[k]
    for h in headers:                      # tolerant match for localised or prefixed headers
        hl = h.strip().lower()
        if any(k in hl for k in keys):
            return h
    return None


def read_rows(path, kind):
    p = Path(path)
    if p.suffix.lower() == ".json":
        rows = json.loads(p.read_text(encoding="utf-8-sig"))
        return [normalise_json(r) for r in rows]
    text = p.read_text(encoding="utf-8-sig", errors="replace")
    try:
        dialect = csv.Sniffer().sniff(text[:2000], delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel
    rdr = csv.DictReader(text.splitlines(), dialect=dialect)
    h = rdr.fieldnames or []
    cols = {"page": find_col(h, PAGE_KEYS), "query": find_col(h, QUERY_KEYS), "clicks": find_col(h, CLICK_KEYS),
            "impressions": find_col(h, IMPR_KEYS), "ctr": find_col(h, CTR_KEYS), "position": find_col(h, POS_KEYS)}
    need = ["page", "impressions"] if kind == "pages" else ["page", "query", "impressions"]
    missing = [n for n in need if not cols[n]]
    if missing:
        raise ValueError(f"{path}: could not find column(s) {missing}. Found headers: {h}")
    out = []
    for r in rdr:
        row = {k: (r.get(c) if c else None) for k, c in cols.items()}
        out.append(normalise_row(row))
    return [r for r in out if r["page"]]


def normalise_json(r):
    return normalise_row({"page": r.get("page") or r.get("url") or r.get("top_pages"), "query": r.get("query"),
                          "clicks": r.get("clicks"), "impressions": r.get("impressions"), "ctr": r.get("ctr"),
                          "position": r.get("position")})


def normalise_row(r):
    clicks, impr, ctr, pos = num(r.get("clicks")), num(r.get("impressions")), num(r.get("ctr")), num(r.get("position"))
    if ctr is not None and ctr > 1:        # a bare "2.5" means percent
        ctr /= 100
    if ctr is None and impr:
        ctr = (clicks or 0) / impr
    return {"page": (r.get("page") or "").strip(), "query": (r.get("query") or "").strip(),
            "clicks": clicks or 0, "impressions": impr or 0, "ctr": ctr or 0.0, "position": pos}


def bucket(pos):
    if pos is None:
        return None
    p = int(round(pos))
    if p <= 10:
        return max(1, p)
    return 15 if p <= 15 else 20 if p <= 20 else 25


def build_curve(rows):
    """Site-specific CTR by position band.

    Fine position buckets (1..10, 15, 20, 25) are merged into bands that each hold at least 3 pages, the
    impression-weighted CTR is taken per band, and the result is forced to be non-increasing as position worsens
    (a worse position never expects a higher CTR). Returns (bands, overall_ctr, confidence)."""
    agg = defaultdict(lambda: [0.0, 0.0, 0])
    tot_c = tot_i = 0.0
    for r in rows:
        b = bucket(r["position"])
        if b is None or r["impressions"] <= 0:
            continue
        c = r["clicks"] or r["ctr"] * r["impressions"]
        a = agg[b]
        a[0] += c; a[1] += r["impressions"]; a[2] += 1
        tot_c += c; tot_i += r["impressions"]
    overall = tot_c / tot_i if tot_i else 0.0
    bands, cur = [], None
    for b in sorted(agg):
        c, i, n = agg[b]
        if cur is None:
            cur = {"from": b, "to": b, "c": c, "i": i, "n": n}
        else:
            cur["to"] = b; cur["c"] += c; cur["i"] += i; cur["n"] += n
        if cur["n"] >= 3:
            bands.append(cur); cur = None
    if cur is not None:                      # leftover with fewer than 3 pages: fold into the previous band
        if bands:
            bands[-1]["to"] = cur["to"]; bands[-1]["c"] += cur["c"]; bands[-1]["i"] += cur["i"]; bands[-1]["n"] += cur["n"]
        else:
            bands.append(cur)
    for b in bands:
        b["ctr"] = b["c"] / b["i"] if b["i"] else 0.0
    # pool adjacent violators: expected CTR may not rise as position worsens
    k = 0
    while k < len(bands) - 1:
        if bands[k + 1]["ctr"] > bands[k]["ctr"]:
            a, b = bands[k], bands[k + 1]
            m = {"from": a["from"], "to": b["to"], "c": a["c"] + b["c"], "i": a["i"] + b["i"], "n": a["n"] + b["n"]}
            m["ctr"] = m["c"] / m["i"] if m["i"] else 0.0
            bands[k:k + 2] = [m]
            k = max(0, k - 1)
        else:
            k += 1
    total_pages = sum(v[2] for v in agg.values())
    confidence = "ok" if (total_pages >= 12 and len(bands) >= 3) else "low"
    return bands, overall, confidence


def expected_ctr(pos, bands, overall):
    b = bucket(pos)
    if b is None or not bands:
        return overall
    for band in bands:
        if band["from"] <= b <= band["to"]:
            return band["ctr"]
    if b < bands[0]["from"]:
        return bands[0]["ctr"]
    if b > bands[-1]["to"]:
        return bands[-1]["ctr"]
    for k in range(len(bands) - 1):         # between two bands: take the worse one (conservative)
        if bands[k]["to"] < b < bands[k + 1]["from"]:
            return bands[k + 1]["ctr"]
    return overall

def pick_seeds(pq_rows, brands):
    by_page = defaultdict(list)
    bre = [re.compile(r"(?<!\w)" + re.escape(b.strip().lower()) + r"(?!\w)") for b in (brands or "").split(",") if b.strip()]
    for r in pq_rows:
        if not r["query"] or any(b.search(r["query"].lower()) for b in bre):
            continue
        by_page[r["page"]].append(r)
    seeds = {}
    for page, rs in by_page.items():
        rs.sort(key=lambda x: -x["impressions"])
        seeds[page] = [x["query"] for x in rs[:3]]
    return seeds


def main():
    ap = argparse.ArgumentParser(description="Rank pages from Search Console data for a fan-out content-gap check.")
    ap.add_argument("--pages", help="Search Console Pages export (CSV or JSON)")
    ap.add_argument("--json", dest="json_rows", help="rows as JSON: page, clicks, impressions, ctr, position")
    ap.add_argument("--page-queries", help="optional page+query export (CSV or JSON) used to pick a seed query per page")
    ap.add_argument("--brand", help="comma-separated brand terms; branded queries are never used as seeds")
    ap.add_argument("--min-impressions", type=int, default=100, help="ignore pages with fewer impressions in the period")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--domain", help="keep only URLs on this domain")
    ap.add_argument("--exclude", help="regex of URLs to ignore (for example /tag/|/page/\\d+)")
    ap.add_argument("--period", default="", help="label for the report, e.g. 'last 28 days'")
    ap.add_argument("--output", help="write the ranked result as JSON")
    a = ap.parse_args()
    src = a.pages or a.json_rows
    if not src:
        print(json.dumps({"status": "error", "error": "give --pages FILE (CSV or JSON) or --json FILE"})); return 1
    try:
        rows = read_rows(src, "pages")
        pq = read_rows(a.page_queries, "page-queries") if a.page_queries else []
    except (OSError, ValueError) as e:
        print(json.dumps({"status": "error", "error": str(e)})); return 1

    if a.domain:
        d = a.domain.lower().removeprefix("www.")
        rows = [r for r in rows if d in r["page"].lower()]
    ex = re.compile(a.exclude) if a.exclude else None
    if ex:
        rows = [r for r in rows if not ex.search(r["page"])]
    if not rows:
        print(json.dumps({"status": "error", "error": "no rows left after filtering"})); return 1

    bands, overall, confidence = build_curve(rows)
    seeds = pick_seeds(pq, a.brand)
    cands = []
    for r in rows:
        if r["impressions"] < a.min_impressions or r["position"] is None:
            continue
        exp = expected_ctr(r["position"], bands, overall)
        lost = r["impressions"] * max(0.0, exp - r["ctr"])
        reasons = []
        if confidence == "ok" and exp > 0 and r["ctr"] < 0.8 * exp and lost >= 3:
            reasons.append(f"low_ctr_for_position (page {r['ctr']*100:.1f}% vs your typical {exp*100:.1f}% at position ~{r['position']:.0f})")
        if 5 <= r["position"] <= 20:
            reasons.append(f"striking_distance (average position {r['position']:.1f}, {int(r['impressions'])} impressions)")
        if not reasons:
            continue
        s = seeds.get(r["page"], [])
        cands.append({"url": r["page"], "impressions": int(r["impressions"]), "clicks": int(r["clicks"]),
                      "ctr": round(r["ctr"], 4), "position": round(r["position"], 1), "typical_ctr_at_position": round(exp, 4),
                      "opportunity_clicks": round(lost, 1), "reasons": reasons,
                      "seed": s[0] if s else "", "other_seeds": s[1:], "seed_source": "gsc" if s else "none (use the page's main topic)"})
    cands.sort(key=lambda c: (not any(x.startswith("low_ctr") for x in c["reasons"]), -c["opportunity_clicks"], -c["impressions"]))
    out = {"status": "ok", "period": a.period, "pages_read": len(rows), "pages_over_threshold": sum(1 for r in rows if r["impressions"] >= a.min_impressions),
           "min_impressions": a.min_impressions, "candidates": cands[: a.limit], "candidates_total": len(cands),
           "ctr_bands": [{"positions": f"{b['from']}-{b['to']}", "ctr": round(b["ctr"], 4), "pages": b["n"]} for b in bands], "curve_confidence": confidence, "site_ctr": round(overall, 4),
           "notes": ["opportunity_clicks is an estimate against this site's own CTR curve, not a forecast.",
                     "Average position is an average over many queries. Check the query-level data before acting.",
                     "Search Console data lags by about two days."]}
    if confidence == "low":
        out["notes"].insert(0, "Too few pages to build a reliable CTR-by-position curve (needs about 12 pages across 3 position bands). The low-CTR test is switched off; candidates are striking-distance pages ranked by impressions.")
    if a.output:
        Path(a.output).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
