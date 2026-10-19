---
description: Run a Visibility-to-Demand System (VDS) audit on a URL (localhost, staging, or production) or pasted code. Maps crawl presence directly to conversion, trust, and scalability/pSEO targets.
---

Run a **VDS audit** (mode = `vds`).

## What to do

1. Load the `seo-aeo-geo-audit` skill (read its `SKILL.md`).
2. Set mode = `vds`.
3. Ask the user for the target if not in `$ARGUMENTS`: URL or pasted code.
4. Follow the workflow in `SKILL.md`:
   - Gather rendered HTML, headers, robots.txt, sitemap, schema JSON-LD, headings, etc.
   - Work through the 3x3 VDS metrics layers in `references/vds-audit.md`.
   - If React / Next.js, also read `references/crawlability-react.md`.
   - Identify domain archetype (domain-discovery.md) to weight execution layers (Technical, On-Page, Off-Page) appropriately.
   - Map findings (Visibility, Demand, Scalability) showing cascade failures and write them using `references/issue-framework.md`.
   - Formulate VDS Signature leads and revenue projections, and a 5-Year VDS Recovery Roadmap.
   - Generate reports via `scripts/generate_report.py`.
5. Save reports to the user's workspace folder; share `computer://` links.
6. Summarise: what was audited, current VDS alignment rating, and top recovery opportunities.

$ARGUMENTS
