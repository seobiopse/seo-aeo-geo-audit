#!/usr/bin/env python3
"""Run the fan-out coverage scorer over several pages and write one roll-up report.

The agent prepares, for each page, a fanout.json (see references/fanout-mapper.md) and lists the pages in a
manifest. This script scores every page and writes the per-page reports plus a combined JSON, Markdown and HTML
roll-up: pages ranked by Search Console opportunity (or by lowest coverage), the biggest gaps per page, the aspects
that are weak across pages, and pages that need a real browser.

Usage:
    python3 fanout_batch.py --manifest batch.json --output-dir out [--covered 0.72] [--partial 0.45]

batch.json:
    {"period": "last 28 days", "brand": "acme",
     "pages": [{"url": "https://example.com/a", "seed": "what to pack on a cruise",
                "fanout": "fanout/a/fanout.json",
                "html": null, "text": null,
                "metrics": {"impressions": 4200, "clicks": 12, "ctr": 0.0029, "position": 6.4,
                            "opportunity_clicks": 86.1, "reasons": ["low_ctr_for_position ..."]}}]}
Per page use "url" (fetched), or "html" / "text" (saved or pasted content; "url" is then only a label).

Exit codes: 0 ok (some pages may need a browser, listed in the report), 1 error. Python 3.8+, standard library only.
"""

import argparse
import html as html_mod
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fanout_coverage as fc  # noqa: E402


def esc(s):
    return html_mod.escape(str(s), quote=True)


def slugify(url, used):
    s = re.sub(r"^https?://(www\.)?", "", url or "page").lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:50] or "page"
    base, n = s, 2
    while s in used:
        s = f"{base}-{n}"; n += 1
    used.add(s)
    return s


def top_gaps(res, n=3):
    miss = [r for r in res["results"] if r["status"] == "missing"]
    miss.sort(key=lambda r: r["score"])
    return [r["query"] for r in miss[:n]]


def main():
    ap = argparse.ArgumentParser(description="Score several pages against their fan-out sets and write a roll-up.")
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--covered", type=float, default=fc.COVERED)
    ap.add_argument("--partial", type=float, default=fc.PARTIAL)
    a = ap.parse_args()
    try:
        man = json.loads(Path(a.manifest).read_text(encoding="utf-8-sig"))
        pages = man["pages"]
    except (OSError, ValueError, KeyError) as e:
        print(json.dumps({"status": "error", "error": f"manifest: {e}"})); return 1
    if not pages:
        print(json.dumps({"status": "error", "error": "manifest has no pages"})); return 1
    out = Path(a.output_dir); out.mkdir(parents=True, exist_ok=True)
    base = Path(a.manifest).resolve().parent
    brand, used = man.get("brand"), set()
    done, failed = [], []

    for pg in pages:
        slug = slugify(pg.get("url"), used)
        fan = Path(pg.get("fanout", ""))
        if not fan.is_absolute() and not fan.exists():
            fan = base / fan
        pdir = out / "pages" / slug
        code, r = fc.run(str(fan), brand, pg.get("url") if not (pg.get("html") or pg.get("text")) else None,
                         pg.get("html"), pg.get("text"), None, None, None, a.covered, a.partial, str(pdir), "fanout-map")
        entry = {"url": pg.get("url"), "seed": pg.get("seed", ""), "metrics": pg.get("metrics") or {}, "slug": slug}
        if code == 0:
            payload = r["payload"]
            entry.update({"score": r["score"], "grade": r["grade"], "covered": r["covered"], "partial": r["partial"],
                          "missing": r["missing"], "gaps": top_gaps(payload["result"]), "aspects": payload["result"]["aspects"],
                          "missing_terms": payload["result"]["missing_terms"], "sources_text": payload["sources_text"],
                          "report": f"pages/{slug}/fanout-map.html"})
            done.append(entry)
        else:
            entry.update({"status": r.get("status"), "reason": r.get("reason") or r.get("error"), "next": r.get("next", "")})
            failed.append(entry)

    # ranking: Search Console opportunity first when present, else lowest coverage first
    has_opp = any(e["metrics"].get("opportunity_clicks") is not None for e in done)
    done.sort(key=lambda e: (-(e["metrics"].get("opportunity_clicks") or 0), e["score"]) if has_opp else (e["score"],))

    aspect_scores = defaultdict(list)
    terms = Counter()
    for e in done:
        for asp in e["aspects"]:
            aspect_scores[asp["name"]].append(asp["pct"])
        for t in e["missing_terms"]:
            terms[t["term"]] += t["queries"]
    common_aspects = sorted(((n, round(sum(v) / len(v)), len(v)) for n, v in aspect_scores.items() if len(v) >= 2), key=lambda x: x[1])
    avg = round(sum(e["score"] for e in done) / len(done)) if done else None
    today = date.today().isoformat()
    summary = {"status": "ok", "date": today, "period": man.get("period", ""), "pages_total": len(pages),
               "pages_scored": len(done), "pages_need_browser": len(failed), "average_score": avg,
               "pages": [{k: v for k, v in e.items() if k not in ("aspects", "missing_terms")} for e in done],
               "needs_browser": failed, "weak_aspects": [{"aspect": n, "avg_pct": p, "pages": c} for n, p, c in common_aspects[:8]],
               "common_missing_terms": [{"term": t, "queries": c} for t, c in terms.most_common(25)]}
    files = {"json": out / f"fanout-batch-{today}.json", "md": out / f"fanout-batch-{today}.md", "html": out / f"fanout-batch-{today}.html"}
    files["json"].write_text(json.dumps(summary, indent=2), encoding="utf-8")
    files["md"].write_text(render_md(summary), encoding="utf-8")
    files["html"].write_text(render_html(summary), encoding="utf-8")
    print(json.dumps({"status": "ok", "pages_scored": len(done), "pages_need_browser": len(failed), "average_score": avg,
                      "files": {k: str(v) for k, v in files.items()}}))
    return 0


def metrics_cell(m):
    if not m:
        return "&mdash;"
    bits = []
    if m.get("impressions") is not None:
        bits.append(f"{int(m['impressions']):,} impr.")
    if m.get("ctr") is not None:
        bits.append(f"CTR {m['ctr']*100:.1f}%" + (f" (typical {m['typical_ctr_at_position']*100:.1f}%)" if m.get("typical_ctr_at_position") else ""))
    if m.get("position") is not None:
        bits.append(f"pos {m['position']}")
    if m.get("opportunity_clicks") is not None:
        bits.append(f"~{m['opportunity_clicks']:.0f} clicks vs your curve")
    return "<br>".join(esc(b) if "&" not in b else b for b in bits) or "&mdash;"


def render_md(s):
    L = ["# Fan-out content-gap roll-up", "", f"**Date:** {s['date']}  ", f"**Search Console period:** {s['period'] or 'not given'}  ",
         f"**Pages scored:** {s['pages_scored']} of {s['pages_total']}"
         + (f" (average coverage {s['average_score']}%)" if s["average_score"] is not None else "")
         + (f"; {s['pages_need_browser']} need a browser" if s["pages_need_browser"] else ""), "",
         "| Page | Seed query | Search Console | Coverage | Biggest gaps |", "|---|---|---|---|---|"]
    for e in s["pages"]:
        m = e["metrics"]
        gsc = "; ".join(x for x in [f"{int(m['impressions']):,} impr." if m.get("impressions") is not None else "",
                                     f"CTR {m['ctr']*100:.1f}%" if m.get("ctr") is not None else "",
                                     f"pos {m['position']}" if m.get("position") is not None else ""] if x) or "-"
        L.append(f"| [{e['url']}]({e['report']}) | {e['seed'] or '-'} | {gsc} | {e['score']}% ({e['grade']}) | {'; '.join(e['gaps']) or '-'} |")
    if s["weak_aspects"]:
        L += ["", "## Aspects that are weak across pages", "", "| Aspect | Average | Pages |", "|---|---|---|"]
        L += [f"| {a['aspect']} | {a['avg_pct']}% | {a['pages']} |" for a in s["weak_aspects"]]
    if s["common_missing_terms"]:
        L += ["", "## Words missing across pages", "", ", ".join(f"{t['term']} ({t['queries']})" for t in s["common_missing_terms"])]
    if s["needs_browser"]:
        L += ["", "## Pages that need a browser", ""] + [f"- {e['url']}: {e['reason']}" for e in s["needs_browser"]]
    L += ["", "---", "_Plugin heuristic: word-overlap coverage of generated sub-query sets, not a search-engine metric. It does not predict rankings, clicks or citations. Opportunity clicks compare each page with this site's own CTR-by-position curve._"]
    return "\n".join(L) + "\n"


def render_html(s):
    rows = []
    for e in s["pages"]:
        gaps = "".join(f"<li>{esc(g)}</li>" for g in e["gaps"]) or "<li>None</li>"
        rows.append(f'<tr><td><a href="{esc(e["report"])}">{esc(e["url"])}</a><div class="sm">{esc(e["seed"])}</div></td>'
                    f'<td>{metrics_cell(e["metrics"])}</td>'
                    f'<td><div class="track"><div class="fill" style="width:{e["score"]}%"></div></div><b>{e["score"]}%</b> '
                    f'<span class="sm">{esc(e["grade"])}<br>{e["covered"]} / {e["partial"]} / {e["missing"]}</span></td>'
                    f'<td><ul class="g">{gaps}</ul></td></tr>')
    weak = "".join(f'<div class="bar"><span>{esc(a["aspect"])}</span><div class="track"><div class="fill" style="width:{a["avg_pct"]}%"></div></div><b>{a["avg_pct"]}%</b><small>{a["pages"]} pages</small></div>'
                   for a in s["weak_aspects"]) or "<p>Not enough shared aspects.</p>"
    words = "".join(f'<span class="chip">{esc(t["term"])} <small>{t["queries"]}</small></span>' for t in s["common_missing_terms"]) or "<p>None.</p>"
    nb = "".join(f"<li><b>{esc(e['url'])}</b>: {esc(e['reason'])}<br><small>{esc(e['next'])}</small></li>" for e in s["needs_browser"])
    nb_html = f'<section><h2>Pages that need a browser</h2><ul>{nb}</ul></section>' if nb else ""
    avg = f"{s['average_score']}%" if s["average_score"] is not None else "n/a"
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Fan-out roll-up</title><style>
:root{{--bg:#f7f8fa;--fg:#14213d;--card:#fff;--line:#e3e6ec;--muted:#5b6578;--acc:#3b5bdb}}
@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{--bg:#0f1420;--fg:#e8ecf5;--card:#171e2e;--line:#2a3347;--muted:#9aa5bd;--acc:#7c98ff}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}}
main{{max-width:1100px;margin:0 auto;padding:24px 16px 48px}}h1{{font-size:24px;margin:0 0 4px}}h2{{font-size:18px;margin:0 0 10px}}
.sub{{color:var(--muted);margin:0 0 12px}}section{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px;margin:16px 0;overflow-x:auto}}
table{{width:100%;min-width:680px;border-collapse:collapse;font-size:14px}}td,th{{border-top:1px solid var(--line);padding:8px;text-align:left;vertical-align:top}}th{{border-top:0;color:var(--muted);font-weight:600}}
a{{color:var(--acc);overflow-wrap:anywhere}}.sm,small{{color:var(--muted);font-size:12.5px}}.track{{background:var(--line);border-radius:6px;height:10px;width:130px;overflow:hidden;display:inline-block;vertical-align:middle;margin-right:6px}}
.fill{{background:var(--acc);height:100%}}ul.g{{margin:0;padding-left:18px}}.bar{{display:grid;grid-template-columns:minmax(120px,240px) 140px 50px 80px;gap:10px;align-items:center;margin:6px 0}}
.chip{{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:2px 10px;margin:3px;font-size:13px}}.note{{font-size:12.5px;color:var(--muted)}}
</style></head><body><main>
<h1>Fan-out content-gap roll-up</h1>
<p class="sub">{s['date']} &middot; Search Console period: {esc(s['period'] or 'not given')} &middot; {s['pages_scored']} of {s['pages_total']} pages scored &middot; average coverage {avg}</p>
<section><h2>Pages</h2><p class="sub">Ranked by estimated clicks below your own CTR-by-position curve when Search Console data was given, otherwise by lowest coverage. Counts are covered / partial / missing. Open a page for its heat map.</p>
<table><tr><th>Page and seed query</th><th>Search Console</th><th>Coverage</th><th>Biggest gaps</th></tr>{''.join(rows)}</table></section>
<section><h2>Aspects that are weak across pages</h2>{weak}</section>
<section><h2>Words missing across pages</h2><p class="sub">Terms from uncovered sub-queries that appear nowhere on the page (number = sub-queries using them).</p>{words}</section>
{nb_html}
<p class="note">Plugin heuristic: word-overlap coverage of generated sub-query sets, not a search-engine metric. It does not predict rankings, clicks or citations. Opportunity clicks compare each page with this site's own CTR-by-position curve and are estimates.</p>
</main></body></html>"""


if __name__ == "__main__":
    sys.exit(main())
