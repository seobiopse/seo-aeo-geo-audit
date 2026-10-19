## SEO Audit Skill for AI Agents v2.0.0: technical SEO + AEO + GEO + AI citation audits

A free, portable Agent Skill that runs a complete search-engine-ready audit on any website. It covers **technical SEO**, **answer engine optimization (AEO)**, **generative engine optimization (GEO)** and **AI citation readiness**, and produces a ticket-ready Markdown SEO audit report plus an interactive HTML report with before/after code.

### Highlights

- **Runs on multiple platforms.** One skill folder follows the open [Agent Skills spec](https://agentskills.io/specification): Claude, Claude Code, Codex/ChatGPT agents and Google Antigravity. A paste-in prompt covers Vertex AI, Gemini Gems and Custom GPTs.
- **Four audit pillars in one pass.** Technical SEO (~80 checks), AEO, GEO and AI citation readiness, plus agentic-browsing readiness and VDS mapping.
- **Three 0-100 scores.** SEO Quality, E-E-A-T and AI Citation Readiness.
- **Stack and site-type aware.** Seven stack profiles (React/Next.js, WordPress, Shopify, static HTML, Angular, PHP, Wix/Webflow) and 10 site archetypes.
- **Engineer-ready output.** Every finding has severity, evidence, broken-vs-fixed code and a verification step.

### What changed in 2.0.0

- Renamed to `seo-aeo-geo-audit` (plugin, skill and repo). Marketplace is now `seobiopse-skills`.
- `SKILL.md` frontmatter now meets the Agent Skills spec (description under 1,024 characters, name matches folder).
- Removed Claude-only wording; slash commands remain optional Claude Code shortcuts.
- Added `INSTALL.md`, `AGENTS.md`, `docs/CHAT-PROMPT.md`, `tools/package.sh` and `CITATION.cff`.
- Rewrote the README with quick facts and an FAQ on SEO audits, AEO vs SEO vs GEO, and AI search optimization.
- Fixed author-name typos.

### Install

| Platform | Command |
|---|---|
| Claude Code | `/plugin marketplace add seobiopse/seo-aeo-geo-audit` then `/plugin install seo-aeo-geo-audit@seobiopse-skills` |
| Claude (web/desktop) | Download `seo-aeo-geo-audit.zip` below, then Settings, Capabilities, Skills, Upload |
| Codex / Antigravity | Copy `skills/seo-aeo-geo-audit/` to `~/.agents/skills/` or `<project>/.agents/skills/` |

Full steps and a capability matrix are in [INSTALL.md](INSTALL.md).

### Upgrading from 1.x

Uninstall `seo-audit@seo-audit-marketplace` and install the new name above. The slash commands are unchanged.

### License

MIT + Commons Clause. Free to use, modify and self-host; no resale without a commercial license.

**Full changelog:** [CHANGELOG.md](CHANGELOG.md)
