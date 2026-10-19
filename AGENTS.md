# AGENTS.md

This repo ships one portable Agent Skill: `skills/seo-aeo-geo-audit/`.

When the user asks for an SEO, AEO, GEO, AI-citation or VDS audit, a pre-ship page check, or a review of schema, crawlability, indexation, robots.txt, sitemap, llms.txt or AI search visibility:

1. Read `skills/seo-aeo-geo-audit/SKILL.md` and follow it. Do not answer from general knowledge.
2. Load only the reference files the skill tells you to, from `skills/seo-aeo-geo-audit/references/`.
3. Write findings to a `findings.json` and run `python3 skills/seo-aeo-geo-audit/scripts/generate_report.py --input findings.json --output-dir <dir>` to produce the Markdown and HTML reports. See `references/issue-framework.md` for the schema and `examples/` for a sample.

Works with any agent that reads `AGENTS.md` or Agent Skills (`SKILL.md`). See `INSTALL.md` for per-platform setup.
