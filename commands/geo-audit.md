---
description: Run a GEO (Generative Engine Optimization) audit — checks whether ChatGPT, Perplexity, Claude, and Gemini can access, chunk, and cite this page.
---

Run a **GEO audit** (mode = `geo`).

## What to do

1. Load the `seo-aeo-geo-audit` skill.
2. Set mode = `geo`.
3. Ask for target, plus `robots.txt` and `llms.txt` if available.
4. Follow SKILL.md workflow:
   - Gather `robots.txt`, `llms.txt`, rendered HTML, Organization schema, entity references.
   - Work through `references/geo.md`.
   - Also read `references/crawlability-react.md` (most LLM bots don't run JS — critical for React sites).
   - Also consult `references/structured-data-advanced.md` for entity-graph patterns (`@graph`, `@id`, `sameAs`).
   - If AI-assisted content, read `references/ai-content-safety.md`.
   - Use `references/issue-framework.md` for findings.
   - Generate both reports.
5. Save reports; share `computer://` links.
6. Summarise top issues.

$ARGUMENTS
