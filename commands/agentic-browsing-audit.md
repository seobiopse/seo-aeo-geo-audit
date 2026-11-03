---
description: Run an Agentic Browsing (SXO / AXO) audit — checks whether autonomous AI search and action agents can crawl, render, navigate, and interact with the page.
---

Run an **Agentic Browsing audit** (mode = `agentic-browsing`).

## What to do

1. Load the `seo-aeo-geo-audit` skill.
2. Set mode = `agentic-browsing`.
3. Ask for the target URL or templates.
4. Follow the SKILL.md workflow:
   - Gather `robots.txt`, `llms.txt` / `llms-full.txt`, and rendered HTML structure.
   - Work through `references/agentic-browsing.md`.
   - Also read `references/crawlability-react.md` (for JS-grid rendering verification).
   - Use `references/issue-framework.md` for findings.
   - Generate both reports.
5. Save reports; share `computer://` links.
6. Summarise top issues.

If the in-app browser or fetch tool cannot reach the site, follow `references/browser-access.md` in the skill you loaded: tell the user what failed, switch to Claude in Chrome, and if the extension is not installed give the install steps and wait.

$ARGUMENTS
