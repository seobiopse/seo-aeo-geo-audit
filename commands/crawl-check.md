---
description: Fast rendering-only audit (14 checks, 1-2 minutes) for React / Next.js / SPA sites. Scoped subset of /seo-audit — for a full audit, use /seo-audit or /full-audit instead.
---

Run a **fast crawlability check** — scoped subset of `/seo-audit` that ONLY runs the 14 rendering/crawlability checks from `references/crawlability-react.md`. Useful during active development when engineers want a quick sanity check after changing a component or route, without waiting for a full audit.

**If you want the full technical SEO audit (all 80+ on-page + crawl + schema checks), use `/seo-audit` — it includes these 14 rendering checks as part of its scope.**

## What this command does

1. Load the `seo-aeo-geo-audit` skill (read its `SKILL.md`).
2. Set mode = `crawl-check`.
3. Read `references/crawlability-react.md` — the 14 CR-* checks.
4. Ask for the target (URL strongly preferred for this check):
   - Live URL (localhost / staging / production)
   - If code, also ask for `robots.txt` and the framework being used
5. Run ONLY the crawlability-specific audit:
   - Fetch raw HTML without JS execution
   - Compare raw HTML vs rendered DOM
   - Simulate each major crawler: Googlebot, GPTBot, ClaudeBot, PerplexityBot, CCBot, Bingbot
   - Check robots.txt policy for each AI crawler
   - Identify React anti-patterns (Section 6 of `crawlability-react.md`)
   - Check metadata API usage (App Router: Server Components only; Pages Router: `next/head`)
6. Use `references/issue-framework.md` for every finding. Expect 2–5 findings typically.
7. Generate a concise report via `scripts/generate_report.py`.
8. Summary line: "Critical content visible to: [Googlebot ✓ / GPTBot ✗ / ClaudeBot ✗ / PerplexityBot ✓]"

## When to use `/crawl-check` vs `/seo-audit`

- `/crawl-check` — single component change, routing change, testing SSR vs CSR, quick sanity check during dev
- `/seo-audit` — before merging a PR, before shipping a feature, as part of a real audit

## Arguments

$ARGUMENTS
