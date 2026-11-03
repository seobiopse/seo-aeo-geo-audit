---
description: Run the full audit — SEO + AEO + GEO + AI Citation in one pass. Use before shipping a page to production.
---

Run a **full audit** (mode = `full`) — all pillars in sequence.

Use when the user says "full audit", "pre-launch check", "is this ready to ship", or anything comprehensive.

## What to do

1. Load the `seo-aeo-geo-audit` skill.
2. Set mode = `full`.
3. Ask for target if not in `$ARGUMENTS`.
4. Follow SKILL.md workflow:
   - Gather ALL data: rendered HTML, raw (no-JS) HTML, headers, robots.txt, sitemap.xml, llms.txt, schema JSON-LD, author/org data, headings, Bing vs Google indexed counts, etc.
   - For a live public URL, ask for the PageSpeed API key in your FIRST message, together with the target, and wait for the answer (the user may say "skip"; never skip on your own and never say PageSpeed is "not available"). Follow `references/pagespeed.md`; include `scores.pagespeed` in the combined report.
   - Work through `references/seo-audit.md`, `references/aeo.md`, `references/geo.md`, AND `references/ai-citation-audit.md`.
   - Load relevant deep-dives: `crawlability-react.md`, `structured-data-advanced.md`, `ai-content-safety.md`, `query-fanout.md`, `rag-optimization.md`, `pseo-playbook.md` (if jobs), `react-nextjs-architecture-profile.md` (for React / Next.js sites).
   - Use `references/issue-framework.md` for every finding. Tag each with every pillar it affects.
   - For the AI Citation pass, include the per-chunk table and the AI Citation Readiness roll-up from `references/ai-citation-audit.md`.
   - Generate ONE combined report via `scripts/generate_report.py` with `mode=full`.
5. Save reports; share `computer://` links.
6. Summarise: findings-by-severity rollups per pillar (SEO / AEO / GEO / AI Citation) + the top issues blocking ship.

## After the report is ready: optional fan-out content-gap check

Once both reports are generated and summarised, offer this. Never start it without a yes.

1. Ask: "Want a fan-out content-gap check on your pages with high impressions but low clicks? It needs your Search Console data."
2. If yes, follow "Batch mode: pages from Search Console" in `references/fanout-mapper.md`: ask for the Search Console Pages export (28 days recommended; 3 months for low-traffic sites), run `scripts/gsc_opportunities.py` to rank pages by CTR below the site's own CTR-by-position curve plus striking-distance pages, and let the user choose pages (default the top 5) and confirm seed queries.
3. Credit rules: with a Serper key, run a sample of the top 5 pages and ask before running more. With a connected Semrush, Ahrefs or OpenRush (permission first, with the expected call count), run all the pages the user submitted. With neither, run the top 5 with agent-generated sub-queries and offer the rest.
4. Run `scripts/fanout_batch.py`, share the roll-up and per-page reports, and explain the findings and the limits of the score. If `fanout.json` files were created, the AI citation pass can reuse them.
If the in-app browser or fetch tool cannot reach the site, follow `references/browser-access.md` in the skill you loaded: tell the user what failed, switch to Claude in Chrome, and if the extension is not installed give the install steps and wait.

$ARGUMENTS
