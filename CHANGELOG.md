# Changelog

All notable changes to the SEO Audit Plugin are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.9.0] — 2026-09-09

### Added

- **AI Citation Audit mode & reference guide (`references/ai-citation-audit.md`)** — A quantitative audit for AI citation readiness, built from published retrieval research and field data:
  - **The three numbers** — chunk density (chunks per 1,000 words), chunk relevance score (n-gram overlap + question→passage embedding similarity, per *"What Evidence Do Language Models Find Convincing?"*, Wan et al., ACL 2024), and extractable units per chunk (statistic / attributed quotation / cited source; ~+41% citation lift for a quotation, ~−8% for keyword stuffing per the GEO research line).
  - **Prerequisite: indexation, not ranking** — Bing Webmaster vs GSC indexed-count comparison; rank and AI citation are close to statistically independent.
  - **0–100 AI Citation Readiness score** — emitted under `scores.ai_citation` on `/full-audit` and `/ai-citation-audit`.
  - **Content-refresh playbook** — the 7-step per-page loop (add ~3 H2 sections, rewrite weak sections for n-gram/relevance, add FAQ, update title/meta, add 3–5 internal links, cut fluff) and the ~10-week effect-lag / model-rollout-volatility expectations.
  - **AIC-1 … AIC-16 checklist.**
- **AI Citation Audit command (`commands/ai-citation-audit.md`)** — Registered `/ai-citation-audit` (mode = `ai-citation`).

### Changed

- **`commands/full-audit.md`** — AI Citation is now a fourth pillar of the full audit: reads `ai-citation-audit.md`, gathers raw (no-JS) HTML + Bing/Google indexed counts, and includes the per-chunk table and readiness roll-up. Summary rollup is now SEO / AEO / GEO / AI Citation.
- **`SKILL.md`** — "seven modes" → "eight modes" (new `ai-citation` row); `full` mode now also reads `ai-citation-audit.md`; registered `ai-citation-audit.md` in the reference catalog, the deep-dive load list, and the "When to read which deep-dive" table; Step 6b now documents the `scores.ai_citation` grader; frontmatter description updated with AI Citation / chunk-score triggers.
- **`README.md`** — Version → `1.9.0`; "Six slash commands" → "Eight slash commands" (added `/ai-citation-audit` and the previously-unlisted `/vds-audit`); reference count 35 → 37; plugin file tree updated; installation section corrected to `/plugin install seo-audit@seo-audit-marketplace` with a Requirements note.
- **Marketplace manifest moved to `.claude-plugin/marketplace.json`** (was at repo root, where Claude Code does not look) and expanded to the full schema (`owner`, `metadata`). Version bumped to reference plugin `1.9.0`.
- **`.claude-plugin/plugin.json`** — Version bump to `1.9.0`; added `ai-citation`, `chunk-score`, `retrievability`, `extractable-units`, `bing-indexation` keywords.

---

## [1.8.0] — 2026-06-15

### Added

- **Quality Assurance & Data Integrity Guide (`references/quality-assurance.md`)** — Documented verification rules, anti-hallucination policies, and HTML/Markdown templates layout checking guidelines for audit sub-agents.

### Changed

- **`SKILL.md` reference files list** — Registered `quality-assurance.md` in the skill's reference catalog.
- **`README.md` details** — Updated version to `1.8.0` and version history highlights.
- **`.claude-plugin/plugin.json` & `marketplace.json` manifest version bump** — Incremented package version to `1.8.0`.

---

## [1.7.0] — 2026-06-15

### Added

- **Audit Integration Guide (`references/tools-to-use.md`)** — Outlined setup instructions for Playwright browser automation, MCP servers (Ahrefs, Semrush, Screaming Frog), public overview URLs, and report template standardization.

### Changed

- **`SKILL.md` reference files list** — Registered `tools-to-use.md` in the skill's reference catalog.
- **`README.md` details** — Updated version to `1.7.0` and version history highlights.
- **`.claude-plugin/plugin.json` & `marketplace.json` manifest version bump** — Incremented package version to `1.7.0`.

---

## [1.6.0] — 2026-06-15

### Added

- **VDS (Visibility-to-Demand System) Audit Mode & Reference Guide (`references/vds-audit.md`)** — Added full VDS audit mode mapping search visibility to conversion metrics.
- **VDS Audit Example (`examples/vds-audit-example.md`)** — Included a real case-study VDS audit report for reference.
- **VDS Audit Command (`commands/vds-audit.md`)** — Registered `/vds-audit` to automate framework checks.
- **Mandatory Audit Signature Guide (`references/signature.md` & `SIGNATURE.md`)** — Introduced a standardized signature block template for VDS and SEO audits.

### Changed

- **`SKILL.md` reference files list** — Registered `vds-audit.md` and `signature.md` in the skill's reference catalog.
- **`README.md` details** — Updated version to `1.6.0` and updated footer signature/CTA.
- **`.claude-plugin/plugin.json` & `marketplace.json` manifest version bump** — Incremented package version to `1.6.0`.
- **`generate_report.py` signature** — Updated generated HTML report footer signature to Giriish and added Telegram CTA link.

---

## [1.5.0] — 2026-06-15

### Added

- **Agentic Browsing Readiness (SXO / AXO) & WCAG Reference Profile (`references/agentic-browsing.md`)** — A comprehensive deep-dive linking accessibility baselines to model capabilities:
  - **WCAG Baseline:** Details how `lang` attributes, document outlines (single H1), image alt text, and semantic form labels are interpreted by programmatic AI crawlers.
  - **Risk Rules & Governance:** Explores sandbox environments, indirect prompt injection protection, cryptographic model signing, and human-in-the-loop (HITL) transaction boundaries.
  - **2026 Browser Landscape:** Documents autonomous browser agents (Perplexity Comet, ChatGPT Atlas, Chrome Gemini Auto Browse) and modern W3C WebMCP integration protocols.
  - **AXO-1.1 to AXO-1.8 Checklist:** Provides a structured checklist mapping technical readiness parameters.

### Changed

- **`SKILL.md` reference files list** — Registered `agentic-browsing.md` in the skill's reference catalog.
- **`README.md` details** — Updated version badges and documented `agentic-browsing.md` in the plugin codebase layout.
- **`.claude-plugin/plugin.json` & `marketplace.json` manifest version bump** — Incremented package version to `1.5.0` and added agentic keywords (`agentic-browsing`, `axo`, `sxo`, `webmcp`).

---

## [1.4.0] — 2026-05-19

### Added

- **Six new stack architecture profiles** — the plugin now covers all major tech stacks, not just React/Next.js:
  - **`references/wordpress-architecture-profile.md`** — WordPress and WooCommerce. Covers: permalink structure, SEO plugin ecosystem (Yoast, Rank Math, AIOSEO), duplicate content from taxonomy/archive pages, canonical issues, schema via Yoast filters, WooCommerce product schema, faceted navigation, Core Web Vitals offenders (render-blocking scripts, unoptimised images, emoji scripts), and a 22-item checklist.
  - **`references/shopify-architecture-profile.md`** — Shopify and Shopify Plus. Covers: fixed URL prefixes, duplicate product URLs via collection paths, Liquid template meta/canonical/OG patterns, Product schema via Liquid, `/collections/all` handling, sitemap auto-generation, robots.txt via `robots.txt.liquid`, CWV constraints, Shopify Markets / hreflang, and a 20-item checklist.
  - **`references/static-html-architecture-profile.md`** — Eleventy, Jekyll, Hugo, Astro, plain HTML/CSS, and Jamstack. Covers: build-time SEO validation, trailing slash consistency, template-level meta/schema injection, sitemap generation with real `<lastmod>` from git dates, robots.txt at build time, CDN/hosting SEO (cache headers, HTTPS, 404 handling), URL migration redirects, build-time image processing, and a 20-item checklist.
  - **`references/angular-architecture-profile.md`** — Angular (v2+), Angular Universal, Ionic. Covers: CSR vs SSR vs prerendering detection, Angular Universal setup audit, `Title` and `Meta` service patterns, canonical tag injection via `DOCUMENT`, route-level SEO configuration, server-safe schema injection, lazy loading and crawlability, Transfer State for avoiding double API calls, and a 20-item checklist.
  - **`references/php-architecture-profile.md`** — Laravel, Symfony, CodeIgniter, and custom PHP. Covers: clean URL routing (index.php removal, .htaccess/Nginx config), session-based URL duplicate content, meta/schema injection in Blade/Twig, caching layer SEO (Varnish, FastCGI), N+1 query TTFB impact, Laravel sitemap generation, Symfony HTTP cache headers, and a 20-item checklist.
  - **`references/wix-webflow-architecture-profile.md`** — Wix, Webflow, Framer, Squarespace. Covers: platform capabilities matrix (what each platform can/cannot do), per-platform SEO control walkthrough, schema injection via custom head code, CWV constraints (platform vs fixable), Webflow CMS dynamic schema with `{{wf}}` bindings, Wix URL prefix constraints, migration signals (when to recommend moving off a builder), and a 20-item checklist.

- **Stack auto-detection in SKILL.md** — the skill now detects the tech stack from URL patterns, response headers, and page source signals, then automatically loads the matching architecture profile. Detection table covers all 7 stacks.

- **Updated `plugin.json` manifest** — moved to `.claude-plugin/plugin.json` (correct location per Claude Code spec). Updated `description` to reflect universal stack coverage. Updated `author.name` to full name. Added `homepage` and `repository` fields. Added new stack keywords.

### Changed

- **`SKILL.md` description frontmatter** — replaced "Tailored for React / Next.js codebases with App Router, Pages Router, and client-side rendering" with a universal description covering all major stacks and all 10 site archetypes.
- **`SKILL.md` reference files section** — added all 6 new stack architecture profiles to the reference list and the "When to read which deep-dive" table.
- **`SKILL.md` Step 2** — now includes explicit stack detection logic with a signal → profile mapping table.
- **`plugin.json` location** — moved from repo root to `.claude-plugin/plugin.json` per the Claude Code plugin specification.
- **Version bump** — 1.3.0 → 1.4.0 (minor: new reference files, new stack coverage, manifest fix).

### Rationale

v1.3 made the methodology universal but the SKILL.md description still said "Tailored for React / Next.js." v1.4 closes that gap: the plugin now has genuine stack-specific guidance for every major platform, and Claude will correctly load the matching profile regardless of which stack it encounters.

---

## [1.3.0] — 2026-04-19

### Added
- **`references/react-nextjs-architecture-profile.md`** — new universal architecture profile for React + Next.js projects. 14 sections covering multi-subdomain architecture, `next.config.js` SEO settings, middleware patterns, ISR strategy, environment-aware canonicals, shared layout + schema injection, API routes, `next/image`, font loading, edge runtime, common anti-patterns, and an audit checklist (RNJS-1 through RNJS-20).
- **Stack-profile roadmap** — the architecture profile explicitly names planned future profiles: Static HTML, WordPress, Shopify, Angular, PHP, Wix/Webflow. Forks can add their own profile for any stack by following the same 14-section template.

### Changed
- **Sanitized the plugin for public GitHub release.** All company-exclusive references, internal subdomain names, and domain-specific placeholders have been replaced with universal architecture-based examples (`example.com`, `jobs.example.com`, `learn.example.com`, etc.). The plugin is now safe to publish openly without leaking any specific employer / client context.
- Removed the former brand-specific architecture profile and replaced it with `react-nextjs-architecture-profile.md` — the same shape, but framed around stack architecture rather than any one brand.
- Refreshed every worked example in `geo-transaction.md`, `pseo-playbook.md`, `domain-discovery.md` to use generic product names (job board, learning platform, recruitment service) instead of any company's specific product names.

### Rationale
A plugin distributed publicly must not carry any employer / client-specific identity. v1.3 completes the universal pivot: anyone can clone, read, and audit any site — React, WordPress, Shopify, Angular — without tripping on leftover brand references.

---

## [1.2.0] — 2026-04-19

### Added
- **`references/domain-discovery.md`** — new mandatory Step 0 of every audit. Detects site archetype (10 common types: Marketing, Blog, E-commerce, SaaS, Job board, Staffing services, Course platform, Documentation, Multi-product conglomerate, Personal site) and tailors audit scope accordingly.
- Per-archetype Apply/Skip lists for all 20 reference files.
- Transparent "explicitly not audited" reporting in every audit output so users can verify the archetype was detected correctly.

### Changed
- `SKILL.md` now requires Step 0 domain discovery before loading any other reference file.
- `HANDOFF.md` — new Section 1a explains to engineers that the plugin tailors itself to the site's architecture.
- URL-level intent detection rules now defer to archetype classification (a SaaS site with `/jobs` meaning "jobs-to-be-done" no longer gets job-board treatment).
- `react-nextjs-architecture-profile.md` reframed as a worked example with an explicit instructional preamble — forks can delete it or adapt it to their own brand.

### Rationale
The v1.1 plugin risked producing noise findings when applied to a domain archetype it didn't understand (e.g. flagging missing `JobPosting` schema on a marketing page). Step 0 prevents that structurally.

---

## [1.1.0] — 2026-04-19

### Added
- **`references/seo-quality-score-rubric.md`** — 0–100 NLP-driven content quality score covering LSI terms, semantic variants, named entities, sentiment analysis, content depth, keyword targeting discipline, and trust-signal density. Separate rubrics for Landing/Money pages vs Blog/Article pages.
- **`references/eeat-score-rubric.md`** — 0–100 E-E-A-T score (Experience + Expertise + Authoritativeness + Trust) aligned with Google's Search Quality Rater Guidelines. Separate rubrics for Landing/Money vs Blog/Article with distinct weight distributions (Trust 35/100 on commercial; Experience 30/100 on editorial).
- Visual Scorecards section at the top of every `/full-audit` HTML report with per-dimension progress bars, color-coded sub-signals (green/amber/red pass/partial/fail), and a "Top improvements" list.
- `scores` field in findings JSON schema.

### Changed
- `SKILL.md` adds a new Step 6b: Compute scores whenever running `/full-audit` or on explicit user request.
- `issue-framework.md` documents the `scores` schema.
- Generator's `render_scores_block` + CSS added.

---

## [1.0.0] — 2026-04-19

### Added — first production-ready release

- **16 reference files** codifying a production-grade SEO / AEO / GEO audit methodology.
- **5 slash commands**: `/seo-audit`, `/aeo-audit`, `/geo-audit`, `/full-audit`, `/crawl-check`
- **Interactive HTML reports** with navy + Playfair Display premium visual design, two audit-group banners, per-finding cards, syntax highlighting, copy-to-clipboard buttons, interactive "Mark as addressed" checkboxes with localStorage persistence, sticky progress bar, re-run panel, signature band, and print-friendly layout.
- **Confidence scoring** (0–100) with evidence source on every finding.
- **Per-page context** — each finding shows the specific URL(s) it applies to.
- **Governance process** — engineers don't edit the plugin directly. Extensions go through `NEW-CHECK-REQUEST-TEMPLATE.md` → Marketing Director/AVP/Manager review → Maintainer implementation.
- **`HANDOFF.md`** — engineer-facing usage guide.
- Python 3 standalone report generator (`scripts/generate_report.py`).

---

## Release policy

- **Major** (x.0.0) — breaking changes to findings schema or reference-file structure.
- **Minor** (1.x.0) — new reference files, new scoring models, new commands, significant UI changes.
- **Patch** (1.0.x) — bug fixes, clarifications in existing references, version-bumps of dependencies.

Maintainer (Girish Kumar G) is sole commit authority. Extension requests route through the governance process in `CONTRIBUTING.md`.
