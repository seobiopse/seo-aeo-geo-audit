---
description: Run an AEO (Answer Engine Optimization) audit — checks readiness for Google AI Overviews, Bing Copilot, and featured snippets.
---

Run an **AEO audit** (mode = `aeo`).

## What to do

1. Load the `seo-aeo-geo-audit` skill.
2. Set mode = `aeo`.
3. Ask for target (URL or code) if not in `$ARGUMENTS`.
4. Follow SKILL.md workflow:
   - Gather rendered HTML, JSON-LD, author bylines, visible dates.
   - Work through `references/aeo.md`.
   - Also consult `references/structured-data-advanced.md` for FAQPage / HowTo / SpeakableSpecification recipes.
   - If AI-assisted content, read `references/ai-content-safety.md`.
   - Use `references/issue-framework.md` for findings.
   - Generate both reports via `scripts/generate_report.py`.
5. Save reports; share `computer://` links.
6. Summarise top issues.

$ARGUMENTS
