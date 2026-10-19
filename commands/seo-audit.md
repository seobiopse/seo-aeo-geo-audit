---
description: Run a technical SEO audit on a URL (localhost, staging, or production) or pasted code. Produces Markdown + HTML reports with broken-vs-fixed code.
---

Run an **SEO audit** (mode = `seo`).

## What to do

1. Load the `seo-aeo-geo-audit` skill (read its `SKILL.md`).
2. Set mode = `seo`.
3. Ask the user for the target if not in `$ARGUMENTS`: URL or pasted code.
4. Follow the workflow in `SKILL.md`:
   - Gather rendered HTML, headers, robots.txt, sitemap, schema JSON-LD, headings, etc.
   - Work through `references/seo-audit.md`.
   - If React / Next.js, also read `references/crawlability-react.md`.
   - If the audit involves job pages, also read `references/pseo-jobs-playbook.md`.
   - Use `references/issue-framework.md` for every finding.
   - Generate both reports via `scripts/generate_report.py`.
5. Save reports to the user's workspace folder; share `computer://` links.
6. Summarise: what was audited, findings by severity, top 3 issues by name.

$ARGUMENTS
