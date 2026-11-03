# AGENTS.md

This repo ships two portable Agent Skills: `skills/seo-aeo-geo-audit/` (full SEO/AEO/GEO suite) and `skills/technical-seo-audit/` (technical-only audit).

When the user asks for an SEO, AEO, GEO, AI-citation or VDS audit, a pre-ship page check, or a review of schema, crawlability, indexation, robots.txt, sitemap, llms.txt or AI search visibility:

1. Read `skills/seo-aeo-geo-audit/SKILL.md` and follow it. Do not answer from general knowledge.
2. Load only the reference files the skill tells you to, from `skills/seo-aeo-geo-audit/references/`.
3. Write findings to a `findings.json` and run `python3 skills/seo-aeo-geo-audit/scripts/generate_report.py --input findings.json --output-dir <dir>` to produce the Markdown and HTML reports. See `references/issue-framework.md` for the schema and `examples/` for a sample.

For a technical-only request (technical SEO audit, indexation or crawl problems, JavaScript/Next.js SEO, redirects, sitemaps, canonicals, tracking-tag coverage), read `skills/technical-seo-audit/SKILL.md` instead and follow it. It uses `skills/technical-seo-audit/scripts/tech_probe.py` for sampled page checks and, when present, the first skill's report generator.

For `seo`, `full` and `technical` audits of a live public URL, ask the user for a PageSpeed API key in your first message (they can say "skip"; never skip on your own). If the browser or fetch tool cannot reach the site, follow `references/browser-access.md` in the skill you are using: switch to Claude in Chrome, or give the user the install steps.

For a fan-out or content-gap request ("what content is this page missing for <topic>", compare with a competitor page), read `skills/seo-aeo-geo-audit/references/fanout-mapper.md` and run `skills/seo-aeo-geo-audit/scripts/fanout_coverage.py` as it describes.

Works with any agent that reads `AGENTS.md` or Agent Skills (`SKILL.md`). See `INSTALL.md` for per-platform setup.
