---
description: Run an AI Citation Audit — measures the three numbers that decide if ChatGPT, Perplexity, Claude, Gemini, and Copilot cite this page (chunk density, chunk relevance, extractable units) plus Bing indexation eligibility.
---

Run an **AI Citation Audit** (mode = `ai-citation`).

## What to do

1. Load the `seo-audit` skill (read its `SKILL.md`).
2. Set mode = `ai-citation`.
3. Ask for the target if not in `$ARGUMENTS`: URL(s) or pasted content, plus the
   target root query if the user has one.
4. Follow the SKILL.md workflow:
   - Gather rendered text AND raw (no-JS) text, Bing Webmaster vs GSC indexed
     counts (ask the user if not provided), and 3–5 benchmark pages currently
     cited for the target query.
   - Derive the fan-out sub-query set (8–20) using `references/query-fanout.md`.
   - Work through `references/ai-citation-audit.md` — measure chunk density,
     per-sub-query chunk relevance (n-gram overlap + first-sentence answer), and
     extractable units per chunk.
   - Also read `references/rag-optimization.md` (chunk-friendly HTML) and
     `references/crawlability-react.md` (most citation crawlers do not run JS).
   - Use `references/issue-framework.md` for every finding. Include the per-chunk
     table and the AI Citation Readiness roll-up described in the reference.
   - Generate both reports via `scripts/generate_report.py`.
5. Save reports; share `computer://` links.
6. Summarise: indexation gap, chunk-density band vs benchmark, % chunks with an
   extractable unit, and the top 3 fixes.

$ARGUMENTS
