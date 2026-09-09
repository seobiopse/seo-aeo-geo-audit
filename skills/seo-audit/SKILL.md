---
name: seo-audit
description: Run engineering-grade SEO, AEO (Answer Engine Optimization), GEO (Generative Engine Optimization), AI Citation, and VDS (Visibility-to-Demand System) audits on any web page or site — React, Next.js, WordPress, Shopify, static HTML (Eleventy, Jekyll, Hugo, Astro), Angular, PHP (Laravel, Symfony, CodeIgniter), Wix, Webflow, or any other stack. Use this skill whenever the user mentions an SEO audit, AEO, GEO, AI Citation Audit, VDS, Visibility-to-Demand System, VDS Signature, AI search visibility, chunk density / chunk score / retrievability, schema validation, Core Web Vitals, crawlability, indexation, meta tag review, robots.txt, sitemap review, structured data, llms.txt, Google AI Overviews, ChatGPT citations, Perplexity visibility, programmatic SEO, job posting schema, Google for Jobs, or asks to "check the SEO" / "audit the site" / "review this page" / "is this ready to ship" — even when they don't say the word "audit." Covers all 10 site archetypes (Marketing, Blog, E-commerce, SaaS, Job board, Staffing services, Course platform, Documentation, Multi-product conglomerate, Personal site) across all major tech stacks. Produces both a Markdown report (for tickets) and an interactive HTML report (side-by-side broken-vs-fixed code with copy buttons) engineers can action directly.
---

# SEO / AEO / GEO Engineering Audit

## What this skill does

Three layers, treated as equally important:

1. **Classic SEO** — will search engines crawl, render, index, and rank this page?
2. **AEO** — will Google AI Overviews, Bing Copilot, and similar engines pull an answer from this page?
3. **GEO** — will ChatGPT, Perplexity, Claude, and Gemini cite this page when asked a relevant question?

## When to use this skill

Trigger on any of:
- "Run an SEO / AEO / GEO / full audit on [URL or code]"
- "Check this page before we ship"
- "Is this ready to launch?"
- "Why isn't Google indexing this?"
- "Audit the schema on the product/article/job page"
- "Make sure we show up in AI Overviews / ChatGPT / Perplexity"
- "Review our Core Web Vitals"
- "Verify our robots.txt / sitemap / llms.txt"
- "Can Googlebot render this?"
- Anything mixing "engineering" + "search visibility"

If the request touches SEO/AEO/GEO even loosely, prefer this skill over answering from general knowledge. The skill produces a consistent, standardized, engineer-actionable report.

## The eight modes

| Mode | When to use | Reference | Command |
|---|---|---|---|
| **seo** | Full technical SEO: crawl, index, render, meta, schema, performance, on-page | `references/seo-audit.md` | `/seo-audit` |
| **aeo** | AI Overviews, featured snippets, voice answers | `references/aeo.md` | `/aeo-audit` |
| **geo** | ChatGPT, Perplexity, Claude, Gemini citation readiness | `references/geo.md` | `/geo-audit` |
| **ai-citation** | The three numbers that decide AI citation — chunk density, chunk relevance (n-gram + embedding), extractable units — plus Bing indexation eligibility | `references/ai-citation-audit.md` | `/ai-citation-audit` |
| **vds** | Visibility-to-Demand System (VDS) framework: review mapping crawl visibility to conversion and authority metrics | `references/vds-audit.md` | `/vds-audit` |
| **agentic-browsing** | Agentic Browsing (SXO / AXO) readiness | `references/agentic-browsing.md` | `/agentic-browsing-audit` |
| **full** | All pillars in sequence (pre-ship sign-off) | All reference guides | `/full-audit` |
| **crawl-check** | Scoped to React/Next.js/SPA rendering — what each crawler actually sees | `references/crawlability-react.md` | `/crawl-check` |

## The two input methods

### Method A: Live URL via Chrome
Use when the page is reachable (including localhost / staging / prod).
- Navigate via Chrome browser tool.
- Capture rendered HTML, raw response headers (via `read_network_requests`), Core Web Vitals, full-page screenshot.
- Use `javascript_tool` to extract: `document.title`, meta tags, canonical, hreflang, robots, schema JSON-LD, headings tree, alt-text coverage, internal link count.
- Use `get_page_text` for rendered text (for AEO/GEO analysis).
- If Ahrefs is connected, enrich with `site-audit-issues` and `site-explorer-metrics`.

### Method B: Code snippet from localhost / git
Use when the engineer pastes HTML, a component, a template, or a route-handler output.
- Analyze the code directly — no Chrome needed.
- Ask for associated `robots.txt`, `sitemap.xml`, and HTTP response headers if the mode needs them.
- For framework code (React / Next.js / Angular / Vue / Nuxt / Astro / SvelteKit / PHP / etc.), consider rendering implications. Flag any SEO-critical content that only renders client-side.

## How to run an audit

### Step 0 — Domain discovery (MANDATORY, do this FIRST every time)

**Read `references/domain-discovery.md` BEFORE loading any other reference file or starting any audit work.**

Not every domain has the same shape. A staffing subdomain has `JobPosting`. A bootcamp has `Course`. A marketing site has `Service`. A blog has `Article`. A documentation site has `TechArticle`. An e-commerce site has `Product`. Applying checks that don't fit the domain produces noise findings — flagging missing `JobPosting` schema on a blog, or missing `Course` schema on a pricing page. Noise findings erode trust in the plugin.

**Detect the domain archetype using:**
1. User intent (if they framed it — "audit my blog" vs "audit our recruitment site")
2. URL patterns (`/jobs/`, `/courses/`, `/blog/`, `/pricing`, `/docs/`, `/products/`…)
3. Schema types already present (`JobPosting` vs `Course` vs `Article` vs `Product`)
4. Homepage H1 + first paragraph content signals
5. Top-nav structure

**If you can't classify within 30 seconds, ASK the user.** A wrong archetype produces worse findings than a quick clarifying question.

**Based on the archetype, decide:**
- Which deep-dive references to LOAD
- Which deep-dive references to EXPLICITLY SKIP (and mention what you skipped in the report so the user can verify)
- Which scoring rubric applies (Landing/Money vs Blog/Article)

**Output the detected archetype prominently** in the audit's `overview` field AND as a scorecard entry in `summary.scorecard` — with a line like `"Detected archetype: Staffing services — no course/event/product checks applied"`. This transparency lets the user correct a misclassification before reading findings.

See `references/domain-discovery.md` Section 3 for the per-archetype audit-scope mapping (10 common archetypes covered: Marketing, Blog, E-commerce, SaaS, Job board, Staffing services, Course platform, Documentation, Multi-product conglomerate, Personal site).

### Step 1: Clarify scope
If mode or input method isn't specified, ask (one AskUserQuestion call).

### Step 2: Detect stack and load the relevant reference file(s)
`Read` the reference(s) that match BOTH (a) the mode the user picked AND (b) the archetype you detected in Step 0. For `full` mode, read `seo-audit.md`, `aeo.md`, `geo.md`, AND `ai-citation-audit.md` PLUS archetype-appropriate deep-dives. Always read `issue-framework.md` before writing findings.

**Detect the tech stack** from URL patterns, response headers, page source signals, and user context, then load the matching stack profile:

| Stack signals | Load |
|---|---|
| `React`, `Next.js`, App Router, `_next/`, `__NEXT_DATA__`, Remix, Gatsby | `react-nextjs-architecture-profile.md` |
| `WordPress`, `wp-content/`, `wp-json`, `WooCommerce` | `wordpress-architecture-profile.md` |
| `Shopify`, `myshopify.com`, `/collections/`, `/products/` prefix, Liquid | `shopify-architecture-profile.md` |
| Eleventy, Jekyll, Hugo, Astro, `_site/`, `public/` static output, GitHub Pages | `static-html-architecture-profile.md` |
| Angular, `ng-version`, `<app-root>`, Angular Universal | `angular-architecture-profile.md` |
| PHP, Laravel, Symfony, CodeIgniter, `composer.json`, `artisan` | `php-architecture-profile.md` |
| Wix, `x-wix-request-id`, Webflow, `.webflow.io`, Framer, Squarespace | `wix-webflow-architecture-profile.md` |

If the stack is unclear or mixed, load the most likely profile and note the uncertainty in the audit. If no stack profile matches, proceed with the universal checklist only.

Also load deep-dives when context calls for them:
- React / Next.js / SPA → `crawlability-react.md`
- Schema beyond basics → `structured-data-advanced.md`
- AI-assisted content → `ai-content-safety.md`
- Any `/jobs/` URL or job board → `pseo-playbook.md`
- AI citation readiness (chunking, n-gram overlap, extractable units, Bing indexation) → `ai-citation-audit.md` (+ `query-fanout.md`, `rag-optimization.md`)

### Step 3: Gather data
Collect what the checklists require. For live URLs, in parallel: rendered HTML + raw HTML, headers, `robots.txt`, `sitemap.xml`, `llms.txt`, screenshot, JSON-LD blocks, meta tags, OpenGraph, Twitter cards, hreflang, canonical, H1/H2/H3 tree, alt-text coverage, internal link count, page weight, request count.

### Step 4: Work through the checklist
For each item, decide `pass` / `warn` / `fail`. Every `warn` and `fail` becomes an issue. Don't invent issues outside the checklist — if you notice something real not on the list, include it as an "additional finding" but keep most findings aligned to the checklist so results are comparable across audits.

### Step 5: Write findings using the issue framework
Use `references/issue-framework.md` exactly. Each issue MUST include: severity badge (Critical/High/Medium/Low/Info), pillar tags (SEO/AEO/GEO — one to three), summary, why flagged (with standards reference), impact bullets (SEO/AEO/GEO — all three, even if "no direct impact"), benefits, broken code, fixed code, how to verify.

### Step 6: Generate both reports
Output paths (use the workspace folder the engineer shares, default to `/mnt/Core Tickets/` or the current project folder):
- `seo-audit-{mode}-{date}.md`
- `seo-audit-{mode}-{date}.html`

Preferred: call `scripts/generate_report.py --input findings.json --output-dir <dir>`.
Fallback: fill in `assets/report-template.md` and `assets/report-template.html` manually.

The HTML report includes (automatically, no configuration required):
- **Audit-group section dividers** — Traditional SEO / LLM Visibility banners when `audit_group` is set on findings.
- **Per-page context** — each finding card shows the page it applies to (via `page` or `pages_affected`).
- **Interactive checklist** — every finding has a "Mark as addressed" checkbox. Progress persists per-report in localStorage.
- **Progress bar** — sticky under the TOC, shows `X of N addressed`.
- **Re-run panel** — appears at the bottom once all findings are marked addressed, with suggested commands.
- **Signature band** — "Crafted with care by [Giriish](https://www.linkedin.com/in/girisshgk/) · Father of SEO · [For Collaboration](http://t.me/spcgbot)".

### Step 6b: Compute scores (for `/full-audit` and on explicit request)

When running `/full-audit`, also produce two numeric grades:

1. **SEO Quality Score (0–100)** — run the rubric in `seo-quality-score-rubric.md`. Detect page type (Landing/Money vs Blog/Article) from URL + schema + content. Score each of: LSI term coverage, semantic variants, named entities, content depth, sentiment alignment, keyword targeting discipline, trust signal density (for Landing/Money) OR readability (for Blog/Article).

2. **E-E-A-T Score (0–100)** — run the rubric in `eeat-score-rubric.md`. Score each pillar (Experience / Expertise / Authoritativeness / Trust) with its sub-signals. Weights differ by page type (Trust is 35/100 on Landing/Money but 20/100 on Blog/Article; Experience is 30/100 on Blog/Article but 25/100 on Landing/Money).

Both scores include a `top_improvements` list — 2–3 specific changes that would raise the score most. These are added to the JSON under `scores.seo_quality` and `scores.eeat`. The generator renders them as visual scorecards at the top of the HTML report.

On `/full-audit` and on `/ai-citation-audit`, also emit an **AI Citation Readiness score (0–100)** under `scores.ai_citation` using the rubric in `references/ai-citation-audit.md` (chunk density vs benchmark, chunk relevance on the fan-out set, extractable-unit coverage, chunk self-containment, Bing indexation). Include its own `top_improvements` list.

**Rules:**
- Score ONE representative page per template — not every page. Scoring 50 pages produces noise.
- Never fabricate sub-signals. If a signal isn't on the page, score 0.
- Score the PAGE, not the brand.
- Skip scoring on `/crawl-check` mode and on code-only audits.

### Step 7: Summarize for the user
3–6 sentences: what was audited, total findings by severity, **both scores (Quality + E-E-A-T)**, top 3 urgent issues by name, `computer://` links to both reports.

## Severity definitions

- **Critical** — Page is effectively invisible or broken (noindex shipped, robots blocking, 5xx, missing `<title>`, server content hidden from bots).
- **High** — Significant SEO/AEO/GEO value lost (missing canonical/H1, no schema on eligible page, CWV well below thresholds).
- **Medium** — Measurable but recoverable (thin meta description, missing OpenGraph, inconsistent heading hierarchy, no author schema).
- **Low** — Polish (title slightly long, minor alt-text gaps, missing favicon variants).
- **Info** — Not a defect but worth documenting.

## Things this skill should NOT do

- Don't guess rankings or traffic impact as hard numbers.
- Don't provide generic marketing advice. Fixes must be code-level where possible.
- Don't re-run crawls if the user already provided data.
- Don't skip the three-pillar impact breakdown. If a pillar isn't affected, say so.
- Don't fabricate "broken code" you didn't actually see. Mark "needs input" instead.

## Reference files

**Mandatory first read (every audit, before anything else):**
- `references/domain-discovery.md` — detect the domain's archetype (marketing / blog / e-commerce / SaaS / job board / staffing services / course platform / docs / multi-product conglomerate / personal). Determines which deep-dives apply and which to skip. Read FIRST, every time.

**Core checklists (always read for the matching mode):**
- `references/issue-framework.md` — template for every finding (read every time)
- `references/seo-audit.md` — full SEO checklist (informative + transaction both)
- `references/aeo.md` — AEO checklist for **informative** content (blogs, articles, guides)
- `references/geo.md` — GEO checklist for **informative** content
- `references/ai-citation-audit.md` — quantitative AI citation audit: Bing indexation, chunk density, chunk relevance (n-gram overlap + embedding similarity), extractable units per chunk, content-refresh playbook
- `references/vds-audit.md` — VDS (Visibility-to-Demand System) audit checklist mapping crawl presence to organic conversions
- `references/agentic-browsing.md` — Agentic Browsing (SXO / AXO) checklist
- `references/signature.md` — VDS & SEO audit mandatory signature block guide
- `references/tools-to-use.md` — browser automation, MCP tools, public URLs, and output templates guide
- `references/quality-assurance.md` — fact-checking, validation, and data integrity checklist for reports

**Stack architecture profiles (load based on detected tech stack):**
- `references/react-nextjs-architecture-profile.md` — React, Next.js (App Router, Pages Router), Remix, Gatsby
- `references/wordpress-architecture-profile.md` — WordPress, WooCommerce
- `references/shopify-architecture-profile.md` — Shopify, Shopify Plus
- `references/static-html-architecture-profile.md` — Eleventy, Jekyll, Hugo, Astro, plain HTML/CSS
- `references/angular-architecture-profile.md` — Angular (v2+), Angular Universal, Ionic
- `references/php-architecture-profile.md` — PHP, Laravel, Symfony, CodeIgniter
- `references/wix-webflow-architecture-profile.md` — Wix, Webflow, Framer, Squarespace

**Deep-dives (loaded on demand based on page type and context):**
- `references/crawlability-react.md` — React/Next.js/SPA rendering deep-dive (page-level)
- `references/agentic-browsing.md` — WCAG-based Agentic Browsing Readiness (SXO/AXO), boardroom risk rules, security guidelines
- `references/structured-data-advanced.md` — `@graph`, per-page-type recipes, Google requirements
- `references/ai-content-safety.md` — Google policies, copyright, AI-assisted content rules
- `references/image-optimization.md` — alt text/title per intent, WebP rules, srcset, LCP handling, schema image requirements
- `references/product-experience-audit.md` — non-technical product architecture checks
- `references/seo-quality-score-rubric.md` — NLP-driven 0–100 content quality score
- `references/eeat-score-rubric.md` — 0–100 E-E-A-T score (Google's Search Quality Rater Guidelines)
- `references/pseo-playbook.md` — programmatic SEO for jobs, courses, events, skill assessments, landing pages, location hubs, company hubs
- `references/transaction-intent-playbook.md` — landing pages, money pages, pricing pages
- `references/aeo-transaction.md` — AEO for commercial pages
- `references/geo-transaction.md` — GEO for commercial pages
- `references/ai-overview-playbook.md` — Google AI Overview-specific optimization
- `references/llm-citation-playbook.md` — ChatGPT, Perplexity, Claude, Gemini, Copilot citation
- `references/tracking-validation.md` — GA4, GTM, Meta Pixel, Bing UET, LinkedIn, TikTok, consent mode
- `references/robots-llms-txt-playbook.md` — robots.txt precedence, per-bot AI policies, llms.txt spec
- `references/sitemap-playbook.md` — per-type sitemaps, correct changefreq/priority/lastmod, dynamic sitemap patterns
- `references/query-fanout.md` — Query Fan-Out optimization, semantic expansions, entity clustering, and topical authority mapping
- `references/rag-optimization.md` — RAG (Retrieval-Augmented Generation) search engines, chunk-friendly formatting, and retrieval prompt-engineering optimization
- `references/rag-to-memory.md` — Stateful AI Memory systems, brand knowledge graphs, and memory-synthesizable architecture structures

**Output:**
- `assets/report-template.md`
- `assets/report-template.html`
- `scripts/generate_report.py`

### When to read which deep-dive

**Every audit starts with `domain-discovery.md` first.** Then detect the tech stack and load the matching architecture profile. The table below covers the remaining deep-dives.

| If the audit involves… | Also read |
|---|---|
| **Every single audit, before anything else** | **`domain-discovery.md`** |
| React, Next.js, Remix, Gatsby, or SPA (page-level rendering checks) | `crawlability-react.md` |
| WordPress (any) | `wordpress-architecture-profile.md` |
| Shopify | `shopify-architecture-profile.md` |
| Static HTML / Jamstack (Eleventy, Jekyll, Hugo, Astro) | `static-html-architecture-profile.md` |
| Angular | `angular-architecture-profile.md` |
| PHP (Laravel, Symfony, CodeIgniter, custom) | `php-architecture-profile.md` |
| Wix, Webflow, Framer, Squarespace | `wix-webflow-architecture-profile.md` |
| Any page with images (almost always) | `image-optimization.md` |
| Schema beyond basics (JobPosting, Product, Article, Course, Recipe, Event) | `structured-data-advanced.md` |
| AI-assisted content | `ai-content-safety.md` |
| Multi-product subdomain, mentor/author listings, event/webinar pages, paid products > ₹1L / $1K | `product-experience-audit.md` |
| `/full-audit` mode, or user asks for "quality score" / "content grade" / "E-E-A-T score" | `seo-quality-score-rubric.md` AND `eeat-score-rubric.md` |
| Programmatic page templates (jobs, courses, events, skill assessments, landing pages, location hubs, company hubs) | `pseo-playbook.md` |
| Landing page, pricing, money page, sign-up, comparison | `transaction-intent-playbook.md` + `aeo-transaction.md` + `geo-transaction.md` |
| Optimization for Google AI Overview specifically | `ai-overview-playbook.md` |
| Optimization for ChatGPT / Perplexity / Claude / Gemini / Copilot | `llm-citation-playbook.md` |
| Optimization for Agentic Browsing (SXO/AXO) or WCAG readiness | `agentic-browsing.md` |
| Site has paid media or analytics | `tracking-validation.md` |
| robots.txt / llms.txt review | `robots-llms-txt-playbook.md` |
| Sitemap review or dynamic sitemap design | `sitemap-playbook.md` |
| VDS (Visibility-to-Demand System) framework review | `vds-audit.md` |
| Setup for browser automation, MCP servers, and public analytics | `tools-to-use.md` |
| Fact-checking, QA validation, and report data integrity rules | `quality-assurance.md` |
| Query Fan-Out semantic clustering and authority audits | `query-fanout.md` |
| AI citation readiness — chunk density, n-gram overlap, extractable units, Bing indexation, content refresh | `ai-citation-audit.md` |
| RAG optimization, vector chunk-friendly text and layout layouts | `rag-optimization.md` |
| Stateful AI memory architectures, /llms.txt profiles, and SAM-C | `rag-to-memory.md` |

### Intent detection — URL-level signals (after archetype is set)

URL-level intent detection is still useful ONCE the domain archetype has been established via Step 0. These rules apply WITHIN an archetype for per-page targeting:

- **URL contains `/blog/`, `/article/`, `/guide/`, `/docs/`, `/learn/`** → informative content; load `aeo.md`, `geo.md`, `ai-overview-playbook.md`, `llm-citation-playbook.md`.
- **URL contains `/pricing`, `/plans`, or is a landing page with hero + CTA + form** → transaction content; load `transaction-intent-playbook.md`, `aeo-transaction.md`, `geo-transaction.md`.
- **URL contains `/jobs/`, `/careers/`, `/job-detail`** → PSEO jobs; load `pseo-playbook.md` Part A — **only if archetype is Job board or Staffing services**.
- **URL contains `/courses/`, `/programs/`, `/certifications/`** → PSEO courses; load `pseo-playbook.md` Part B — **only if archetype is Course platform / bootcamp**.
- **URL contains `/events/`** → PSEO events; load `pseo-playbook.md` Part C — **only if events are a real product surface**.
- **URL contains `/skill-assessments/`, `/quiz/`, `/assessments/`** → PSEO skill assessments; load `pseo-playbook.md` Part D — **only if assessments are a product surface**.
- **URL has explicit city/ICP in path (e.g., `/whitefield/`, `/schools/`)** → generated landing page; load `pseo-playbook.md` Part E.

**Critical rule:** URL patterns can be misleading. A SaaS site might have `/jobs` meaning "job to be done" rather than "job postings." The ARCHETYPE determines which rules apply. Always let Step 0 override URL-level pattern matching.

For `/full-audit`, load all relevant deep-dives based on BOTH the archetype AND the per-page URL intent.
