---
description: Run a dedicated technical SEO audit on a URL (localhost, staging, production) or pasted code: crawl/indexation, redirects, sitemaps, canonicals, JavaScript/Next.js rendering, tracking-tag coverage and optional PageSpeed. Produces Markdown + HTML reports.
---

Run a **technical SEO audit** with the `technical-seo-audit` skill.

## What to do

1. Load the `technical-seo-audit` skill (read its `SKILL.md`) and follow its workflow exactly.
2. Target: use `$ARGUMENTS` (URL or pasted code). If missing, ask for it.
3. For a live site, run `scripts/tech_probe.py` to sample pages from the sitemap, then confirm its hints with `curl` or the browser.
4. Cover JavaScript rendering (raw HTML vs rendered DOM; Next.js App/Pages Router when detected) and tracking-tag coverage across the sampled pages.
5. Ask once for a PageSpeed API key. No key means skip PageSpeed and mark that item `not measured`. Treat any key as session-only: never write it to a file, report or memory.
6. Work through `references/technical-checklist.md` (TECH-01 to TECH-13). Mark anything you could not test as `not measured`.
7. Write findings and generate the reports (mode `technical`). Share links to both.
8. Summarise: pages sampled, findings by severity, top three issues, what was not measured.

$ARGUMENTS
