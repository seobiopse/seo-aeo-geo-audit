# SEO Audit Plugin for Claude Code

**Production-ready v1.9.0** — a Claude Code plugin that runs comprehensive SEO, AEO (Answer Engine Optimization), GEO (Generative Engine Optimization), and AI Citation audits on **any website, any stack**. Produces ticket-ready Markdown reports and interactive HTML reports with before/after code, confidence scores, interactive checklists, and quantitative scoring. Fully optimized for Agentic Browsing (SXO / AXO).

[![License: MIT + Commons Clause](https://img.shields.io/badge/License-MIT%20%2B%20Commons%20Clause-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.9.0-blue.svg)](CHANGELOG.md)
[![Plugin type](https://img.shields.io/badge/type-Claude%20Code%20plugin-navy.svg)](https://docs.claude.com)

---

## Why this plugin exists

SEO audits are mostly the same work, done badly, over and over, by every team. Engineers either skip SEO entirely (shipping invisible pages) or drown in 200-item checklists they can't triage. Marketing teams hand over audit spreadsheets that don't connect to code. Meanwhile, the rules have gotten more complex — Google AI Overviews, ChatGPT citations, Perplexity source cards, Claude web search, Gemini, Bing Copilot each need different signals.

This plugin fixes that by:

1. **Codifying a production-grade checklist** across 37 reference files covering every major SEO/AEO/GEO/AI-citation pillar.
2. **Adapting to YOUR site's stack and architecture** — it detects whether you're on React/Next.js, WordPress, Shopify, static HTML, Angular, PHP, Wix/Webflow, or any other platform, then loads the matching stack profile.
3. **Adapting to YOUR site's archetype** — it detects whether you're a blog, SaaS, e-commerce, job board, bootcamp, docs site, or multi-product conglomerate, and tailors the audit scope accordingly.
4. **Producing engineer-actionable reports** — every finding has confidence scores, evidence sources, broken-code-vs-fixed-code examples, and a verification step.
5. **Quantifying quality** with two 0–100 scoring models — SEO Quality (NLP-driven: LSI, semantic, entities, sentiment) and E-E-A-T (Google's Search Quality Rater Guidelines).
6. **Enforcing governance** so extensions go through review, not ad-hoc edits.

---

## Is this plugin right for you?

**Yes if:**
- Your team uses Claude Code for development.
- You have at least one web property to audit — any architecture (React / Next.js / WordPress / Shopify / Wix / Webflow / static HTML / Angular / PHP / etc.).
- You want a repeatable, standards-based SEO / AEO / GEO audit workflow.
- You want engineering to own technical SEO, and marketing to own strategy.

**Probably not if:**
- You need automated daily crawling with dashboards (use Ahrefs / Semrush / Screaming Frog for that).
- You want a drop-in audit UI for non-technical users (this one requires the Claude Code CLI).

---

## Universal stack coverage

The plugin auto-detects your tech stack and loads the matching architecture profile:

| Stack | Profile loaded |
|---|---|
| React, Next.js (App Router / Pages Router), Remix, Gatsby | `react-nextjs-architecture-profile.md` |
| WordPress, WooCommerce | `wordpress-architecture-profile.md` |
| Shopify, Shopify Plus | `shopify-architecture-profile.md` |
| Eleventy, Jekyll, Hugo, Astro, plain HTML/CSS | `static-html-architecture-profile.md` |
| Angular, Angular Universal, Ionic | `angular-architecture-profile.md` |
| PHP, Laravel, Symfony, CodeIgniter | `php-architecture-profile.md` |
| Wix, Webflow, Framer, Squarespace | `wix-webflow-architecture-profile.md` |

The core audit methodology (SEO/AEO/GEO checklists, scoring, issue framework) is stack-agnostic. Stack profiles add platform-specific checks on top.

---

## Quick start

### Installation (end users)

Pick the path that matches how you run Claude Code.

#### Claude Code user (in-session) — follow these

Run these **inside** a running Claude Code session (type `/plugin`), not in your
shell:

```bash
/plugin marketplace add seobiopse/advanced-seo-plugin-for-claude-code
/plugin install seo-audit@seo-audit-marketplace
```

Restart Claude Code when prompted.

Installing from a local clone instead (cloned with GitHub Desktop or `git clone`)?
The repo is its own marketplace — add the cloned folder as a marketplace, then
install from it. Use the full path to the folder you cloned into:

```bash
/plugin marketplace add C:/path/to/advanced-seo-plugin-for-claude-code
/plugin install seo-audit@seo-audit-marketplace
```

#### VS Code or terminal user (CLI) — follow these

Run these in your shell (VS Code integrated terminal, Windows Terminal, iTerm,
etc.):

```bash
claude plugin marketplace add seobiopse/advanced-seo-plugin-for-claude-code
claude plugin install seo-audit@seo-audit-marketplace
```

From a local clone (GitHub Desktop / `git clone`) — point `marketplace add` at the
cloned folder's full path:

```bash
claude plugin marketplace add "C:/path/to/advanced-seo-plugin-for-claude-code"
claude plugin install seo-audit@seo-audit-marketplace
```

Restart Claude Code (or start a new session) so the slash commands and skill
register. Verify with `claude plugin list` — `seo-audit@seo-audit-marketplace`
should show `Status: enabled`.

To pick up upstream changes later: pull the repo (GitHub Desktop or `git pull`),
then run `claude plugin marketplace update seo-audit-marketplace`.

**Requirements:** Claude Code installed and working (`claude` opens the prompt). If
`claude` is "not recognized", reinstall from <https://docs.claude.com/claude-code>
and open a new terminal.

### Your first audit

In Claude Code:

```
/full-audit https://your-domain.com/
```

Claude asks a few clarifying questions, detects your site's archetype and stack, and produces two files in your workspace folder:

- `seo-audit-<mode>-<date>.html` — interactive HTML report
- `seo-audit-<mode>-<date>.md` — Markdown for tickets

Open the HTML. Tick off findings as you ship fixes. A "Ready to re-run" panel appears when you've addressed every finding.

### Eight slash commands

| Command | Purpose |
|---|---|
| `/seo-audit` | Full technical SEO audit (~80 checks) |
| `/aeo-audit` | Answer-Engine Optimization (AI Overviews, featured snippets) |
| `/geo-audit` | Generative-Engine Optimization (ChatGPT, Perplexity, Claude, Gemini, Copilot) |
| `/ai-citation-audit` | The three numbers that decide AI citation — chunk density, chunk relevance, extractable units — plus Bing indexation |
| `/agentic-browsing-audit` | Agentic Browsing / SXO / AXO readiness audit (AI browser navigation) |
| `/vds-audit` | Visibility-to-Demand System — maps crawl presence to conversion + authority |
| `/full-audit` | All pillars + scoring + comprehensive deep-dives |
| `/crawl-check` | Fast 14-check rendering-only audit for React/Next.js/SPA sites |

---

## What's inside

### Plugin structure

```
advanced-seo-plugin-for-claude-code/
├── .claude-plugin/
│   ├── plugin.json                     # Plugin manifest (MUST be here, not at root)
│   └── marketplace.json                # Marketplace manifest (MUST be here, not at root)
├── README.md                           # (this file)
├── HANDOFF.md                          # Engineer-facing usage guide
├── NEW-CHECK-REQUEST-TEMPLATE.md       # Governance template for proposing extensions
├── CHANGELOG.md                        # Version history
├── CONTRIBUTING.md                     # How to contribute + governance
├── LICENSE                             # MIT + Commons Clause
├── commands/                           # 8 slash-command definitions
│   ├── seo-audit.md
│   ├── aeo-audit.md
│   ├── geo-audit.md
│   ├── ai-citation-audit.md
│   ├── agentic-browsing-audit.md
│   ├── vds-audit.md
│   ├── full-audit.md
│   └── crawl-check.md
└── skills/
    └── seo-audit/
        ├── SKILL.md                    # The skill's "brain"
        ├── assets/
        │   ├── report-template.md
        │   └── report-template.html
        ├── references/                 # 37 reference files
        │   ├── domain-discovery.md           # STEP 0 (mandatory first read)
        │   ├── issue-framework.md            # Finding schema + reporting template
        │   │
        │   ├── # Core checklists
        │   ├── seo-audit.md
        │   ├── aeo.md
        │   ├── aeo-transaction.md
        │   ├── geo.md
        │   ├── geo-transaction.md
        │   ├── ai-citation-audit.md
        │   ├── vds-audit.md
        │   │
        │   ├── # Stack architecture profiles (all 7 stacks)
        │   ├── react-nextjs-architecture-profile.md
        │   ├── wordpress-architecture-profile.md
        │   ├── shopify-architecture-profile.md
        │   ├── static-html-architecture-profile.md
        │   ├── angular-architecture-profile.md
        │   ├── php-architecture-profile.md
        │   ├── wix-webflow-architecture-profile.md
        │   │
        │   ├── # Engine-specific playbooks
        │   ├── ai-overview-playbook.md
        │   ├── llm-citation-playbook.md
        │   │
        │   ├── # Technical deep-dives
        │   ├── crawlability-react.md
        │   ├── structured-data-advanced.md
        │   ├── robots-llms-txt-playbook.md
        │   ├── sitemap-playbook.md
        │   │
        │   ├── # Content + trust
        │   ├── ai-content-safety.md
        │   ├── image-optimization.md
        │   ├── product-experience-audit.md
        │   ├── agentic-browsing.md
        │   │
        │   ├── # Programmatic + commercial
        │   ├── pseo-playbook.md
        │   ├── transaction-intent-playbook.md
        │   │
        │   ├── # Tracking
        │   ├── tracking-validation.md
        │   │
        │   ├── # Tools & Quality Assurance
        │   ├── tools-to-use.md
        │   ├── quality-assurance.md
        │   ├── signature.md
        │   │
        │   ├── # AI Overviews & RAG
        │   ├── query-fanout.md
        │   ├── rag-optimization.md
        │   ├── rag-to-memory.md
        │   │
        │   └── # Scoring
        │       ├── seo-quality-score-rubric.md
        │       └── eeat-score-rubric.md
        └── scripts/
            └── generate_report.py      # Findings JSON → MD + interactive HTML
```

---

## Architecture principles

### 1. Stack-aware, not stack-specific

The plugin detects your stack and loads the matching profile. The core methodology (crawl, index, schema, AEO, GEO) is universal — stack profiles add platform-specific checks on top, not replace the fundamentals.

### 2. Site-architecture-driven, not client-specific

The plugin reasons about domains via their architecture archetype (marketing / blog / SaaS / job board / etc.), not by name. No hardcoded rules for any specific brand.

### 3. Checklist + scoring, not opinion

Every finding is tied to a standard — Google Search Central, schema.org, RFC, web.dev, WCAG, OpenAI crawler docs, Anthropic crawler docs. Severity is calibrated against documented best practice.

### 4. Engineer-actionable

Every finding has broken-code and fixed-code examples, tied to the specific file or template they apply to. Every fix has a concrete verification step.

### 5. Governance

Engineers don't edit the plugin directly. Changes go through Marketing Director / AVP / Manager review via the `NEW-CHECK-REQUEST-TEMPLATE.md` form. Maintainer has sole commit access. See `CONTRIBUTING.md`.

---

## Version history

See [CHANGELOG.md](CHANGELOG.md) for the full history. Highlights:

- **v1.9.0 (2026-09-09)** — AI Citation Audit. New `ai-citation-audit.md` reference + `/ai-citation-audit` command measuring the three signals that decide AI citation — chunk density, chunk relevance (n-gram overlap + question→passage embedding similarity, per *"What Evidence Do Language Models Find Convincing?"*, Wan et al., ACL 2024), and extractable units per chunk — plus Bing-indexation eligibility, a 0–100 AI Citation Readiness score, and a content-refresh playbook. Folded into `/full-audit` as a fourth pillar. Marketplace manifest moved to `.claude-plugin/marketplace.json`.
- **v1.8.0 (2026-06-15)** — Quality Assurance & Data Integrity Guide. Added `quality-assurance.md` reference checklist for sub-agents to fact-check audit data and verify output layout formatting.
- **v1.7.0 (2026-06-15)** — Audit Integration Guide. Added `tools-to-use.md` reference mapping Playwright browser automation setup, MCP integration connectors (Ahrefs, Semrush, Screaming Frog), and public SEO site analytics scraping protocols.
- **v1.6.0 (2026-06-15)** — VDS Audit Integration. Added VDS (Visibility-to-Demand System) audit checklists, command hooks, examples, and updated audit templates with Telegram collaboration CTA.
- **v1.5.0 (2026-06-15)** — Agentic Browsing Readiness (SXO / AXO). Added dedicated reference profile `agentic-browsing.md` mapping WCAG 2.1/2.2 accessibility standards to autonomous AI browser navigation (e.g. Perplexity Comet, ChatGPT Atlas, Chrome Gemini Auto Browse). Integrated W3C WebMCP declarative actions, hydration progressive fallback resiliency, and robots.txt live retrieval user agent standards.
- **v1.4.0 (2026-05-19)** — Universal stack coverage. Six new architecture profiles: WordPress, Shopify, Static HTML/Jamstack, Angular, PHP, and Wix/Webflow. SKILL.md description updated to reflect universal coverage. Plugin manifest moved to correct `.claude-plugin/plugin.json` location. Full auto-detection of tech stack in the audit workflow.
- **v1.3.0 (2026-04-19)** — Universal pivot for public release. Replaced company-specific profile with generic `react-nextjs-architecture-profile.md`.
- **v1.2.0 (2026-04-19)** — Step 0 domain discovery added. Plugin now detects site archetype + tailors audit scope.
- **v1.1.0 (2026-04-19)** — SEO Quality Score (NLP-driven) + E-E-A-T Score added.
- **v1.0.0 (2026-04-19)** — First production-ready release.

---

## License

MIT License + Commons Clause. You may use, modify, and self-host the plugin
freely. You may **not** Sell it — resale, paid hosting, or paid support offered as
a product — without a commercial license. See [LICENSE](LICENSE) for full terms
and commercial-licensing contact.

---

*Crafted with care by [Giriish](https://www.linkedin.com/in/girisshgk/) · Father of SEO · [For Collaboration](http://t.me/spcgbot)*
