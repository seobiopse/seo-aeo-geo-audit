# Google AI Overview Playbook

Google AI Overview (AIO, formerly SGE) is the AI-generated answer box that appears above organic search results for ~30% of queries. Getting cited in an AIO is a different problem from generic AEO — it has its own signal weighting that's distinct from ChatGPT / Perplexity / Claude citation (see `llm-citation-playbook.md`).

Read whenever the audit target is a page that should appear in Google search results and the team wants to be cited in AI Overviews.

## Why AIO is different from other LLM citations

| Dimension | Google AI Overview | Other LLMs (ChatGPT, Perplexity, Claude, Gemini) |
|---|---|---|
| Source | Google's Search index + Gemini generation | Varies per model (training, retrieval, browse) |
| Citation mechanism | Source card with favicon + title + snippet | Varies (inline link, footnote, "source" citation) |
| Primary ranking inputs | Classic Google ranking signals + passage indexing + knowledge panel data | Authoritative domain + content freshness + RAG retrieval match |
| Content format preferred | Structured, extractable, chunk-sized | Broad — prose, structured, lists all work |
| Primary gate | Indexed by Google + passes quality thresholds | Crawlable by the LLM's crawler + authoritative |
| Query trigger | "What is X?", "How do I Y?", "Best X for Y" (informational + commercial) | Depends on user's prompt — much broader |

The practical implication: you optimize for AIO by being a **high-ranking Google result** that also has the specific passage structure AIO likes to extract from. You optimize for other LLMs by being an **authoritative source that their crawlers can read** (see `llm-citation-playbook.md`).

## Table of contents

1. [What AIO pulls from](#1-what-aio-pulls-from)
2. [Passage Indexing — the specific unit AIO quotes](#2-passage-indexing)
3. [Content patterns AIO favors](#3-content-patterns-aio-favors)
4. [Query type → content format mapping](#4-query-type-mapping)
5. [Technical requirements (beyond general SEO)](#5-technical-requirements)
6. [Measurement: seeing your AIO presence](#6-measurement)
7. [Informative content tuning for AIO](#7-informative-tuning)
8. [Commercial content tuning for AIO](#8-commercial-tuning)
9. [Audit checklist](#9-audit-checklist)

---

## 1. What AIO pulls from

AIO generates answers by combining:

- **Top-ranking Google search results** for the query (3–8 sources typically surfaced).
- **Google's Knowledge Graph** for entities in the query.
- **Passage Indexing** — specific paragraphs from within pages, not just full pages.
- **Shopping Graph** for commercial queries.

Your page gets cited if:
1. It ranks in the top ~8 organic results for the query OR a closely related query.
2. It contains a passage that directly answers the user's question.
3. Google's quality systems rate the page as reliable.

**No ranking in top 10 = no AIO citation.** AIO doesn't rescue low-ranking pages.

## 2. Passage Indexing — the specific unit AIO quotes

Passage Indexing means Google can index and rank specific paragraphs within a long page. AIO heavily uses this: it lifts a sentence or two from page 1 of a 3,000-word article if that sentence directly answers the query.

### What makes a passage extractable

- **It's on its own.** Wrapped in a single `<p>` or `<section>`, not a paragraph that starts mid-sentence after a `<br>`.
- **It answers a question completely in < 60 words.**
- **It uses the same noun phrases as the query.** If the query is "how long does installation take", the passage should say "installation takes..." not "the deployment process spans..."
- **It's not hedged.** "It depends" / "various factors" reduces extraction odds. A direct answer wins.
- **It's preceded by a descriptive heading.** `<h2>How long does installation take?</h2>` right above the passage amplifies extraction odds.

### Anti-patterns that block passage extraction

- Answers split across multiple paragraphs ("As mentioned above..." / "...continues on").
- Answers inside tables without caption context.
- Answers behind tabs / accordions that only render when clicked.
- Answers inside conditional JS-rendered components.
- Answers that use pronouns referencing earlier content ("it" / "this" / "these").

## 3. Content patterns AIO favors

### Direct definitional answers
**Query: "What is X?"**
```html
<h2>What is fibre broadband?</h2>
<p>Fibre broadband is an internet connection that uses fibre-optic cables to transmit
data as light signals. It delivers symmetric upload and download speeds up to 1 Gbps,
far exceeding DSL or cable alternatives.</p>
```

### Numbered step-by-step
**Query: "How do I X?"**
```html
<h2>How to get fibre broadband installed</h2>
<ol>
  <li>Check coverage at your address using the provider's availability tool.</li>
  <li>Choose a plan that matches your speed and budget requirements.</li>
  <li>Schedule installation — typically takes 5 business days from order.</li>
  <li>A certified technician visits to install fibre, router, and configure the service.</li>
  <li>Run a line test and confirm activation.</li>
</ol>
```

### Comparison tables
**Query: "X vs Y" or "best X for Y"**
```html
<table>
  <caption>Fibre vs DSL vs Cable comparison</caption>
  <thead>
    <tr><th>Type</th><th>Max speed</th><th>Latency</th><th>Suitable for</th></tr>
  </thead>
  <tbody>
    <tr><td>Fibre</td><td>1 Gbps symmetric</td><td>5–15 ms</td><td>Enterprises, gamers, streamers</td></tr>
    <tr><td>Cable</td><td>500 Mbps download / 20 Mbps upload</td><td>20–40 ms</td><td>Home entertainment</td></tr>
    <tr><td>DSL</td><td>50 Mbps download / 10 Mbps upload</td><td>40–80 ms</td><td>Basic browsing</td></tr>
  </tbody>
</table>
```

### Recommendation lists
**Query: "Best X for Y"**
```html
<h2>Best fibre broadband for Whitefield businesses</h2>
<ol>
  <li><strong>GSurf Enterprise Fibre</strong> — 4-hour fault response, 5-day install.</li>
  <li><strong>[Provider 2]</strong> — lower price, longer installation window.</li>
  <li><strong>[Provider 3]</strong> — legacy provider, larger network.</li>
</ol>
```

### Definition + example combination
```html
<h2>Symmetric internet</h2>
<p>Symmetric internet is a connection where upload and download speeds are the same.
For example, 200 Mbps symmetric means 200 Mbps down AND 200 Mbps up — different from a
typical home cable plan (200 Mbps down / 20 Mbps up).</p>
```

## 4. Query type → content format mapping

Different query intents get different AIO formats. Match your content to the expected format for your target queries.

| Query pattern | AIO format | Content you need |
|---|---|---|
| "What is X" | Definition box with 1–3 sentences | Direct definition paragraph under `<h2>What is X?</h2>` |
| "How to X" | Numbered step list | `<ol>` with 3–8 concrete steps |
| "Best X for Y" | Ranked list with cards | `<ol>` of named options with short descriptions |
| "X vs Y" | Side-by-side table | Semantic `<table>` comparing 3–5 attributes |
| "X price" / "How much does X cost" | Price snippet with sources | Visible pricing + `Product` / `Offer` schema |
| "Near me" | Local Pack + map | `LocalBusiness` schema + Google Business Profile |
| "When is X" | Date / time answer | Event schema if applicable, otherwise explicit "X is scheduled for..." |
| Yes/no question | Direct "Yes," or "No," answer + explanation | Answer starts with Yes/No in bold, then explanation |

## 5. Technical requirements (beyond general SEO)

### 5.1 Content in server-side HTML

AIO's extraction runs on the rendered DOM after Googlebot's WRS pass. If your content is client-side only, Googlebot can eventually see it — but with delay. For AIO freshness-sensitive queries, this delay costs citations.

**Rule:** any content you want cited in AIO should be in the initial server response. See `crawlability-react.md`.

### 5.2 Canonical clean

AIO cites canonical URLs, never redirects. If `/page-a` 301s to `/page-b`, AIO cites `/page-b`. Broken canonicals or redirect chains confuse attribution.

### 5.3 Schema for eligibility

Not required for all AIO citations, but schema improves source-card quality:
- `Article` / `NewsArticle` — shows the author + publish date on the source card.
- `Organization` — shows your logo on the source card.
- `BreadcrumbList` — shows the category path.

### 5.4 E-E-A-T signals

AIO source selection heavily weighs E-E-A-T. Pages with strong signals (named expert authors, publisher schema, citations to primary sources) rank higher in AIO's source carousel.

### 5.5 Freshness

For queries with time-sensitive answers (pricing, "current best", latest version), AIO heavily prefers recently-updated sources. `dateModified` within the last 3 months is a strong signal.

## 6. Measurement — seeing your AIO presence

### Google Search Console
- **Performance** report — click through rate for queries where your page ranks #1–8. If CTR is lower than expected for your position, AIO may be taking the clicks.
- In 2026, GSC does NOT yet separate "AIO impression" from regular impression. Watch for "AI Overview" filter rollout.

### Manual verification
1. Search the target query in Google from the country you care about (use `&gl=IN&hl=en` parameters or a VPN).
2. Scroll up — is AIO present?
3. Is your domain in the source cards? If yes, good. If no, who is?

### Competitive analysis
- Which domains do appear in AIO for your target queries?
- What patterns do those pages share? (Usually: top-ranking organic, clear passage structure, strong E-E-A-T.)
- Use this to identify gaps.

### Position volatility
AIO source cards rotate more than organic rankings. Don't panic over daily fluctuations — measure at weekly or monthly cadence.

## 7. Informative content tuning for AIO

For blog posts, guides, explainers:

### Structure
```
<h1>Clear topic title (query-aligned)</h1>

<!-- 40-60 word TL;DR paragraph immediately under h1 — this is the AIO gold zone -->
<p>Brief, direct answer to the page's main question.</p>

<h2>Background / context</h2>
<p>Paragraph(s) explaining the setting.</p>

<h2>Question-as-heading (the actual query you're targeting)</h2>
<p>Direct answer in the first sentence. Supporting paragraph follows.</p>

<h2>Another related question-as-heading</h2>
<p>...</p>

<h2>Conclusion / next steps</h2>
```

### What helps
- Named author with `Person` schema + bio.
- Citations to primary sources.
- First-party data or experience.
- Published date + last-updated date (visible + in schema).

### What hurts
- Walls of text without question-based headings.
- Answers buried 800 words into the page.
- AI-boilerplate openers ("In today's fast-paced world...").
- Content that's 90% summary of other sites.

## 8. Commercial content tuning for AIO

For money pages, pricing, service descriptions:

### Structure for AIO
```
<h1>Service / product name — specific + differentiated</h1>
<p>30-word value prop with key differentiator</p>

<h2>What does [service] cost?</h2>
<p>Direct price answer with specifics.</p>

<h2>What's included?</h2>
<ul>Bulleted list of inclusions</ul>

<h2>How long does it take?</h2>
<p>Direct timeline answer.</p>

<h2>Do you serve [location]?</h2>
<p>Clear yes/no with coverage details.</p>
```

### AIO shopping integration
For e-commerce, the Shopping Graph is separate from AIO organic citations but equally important. Ensure:
- Google Merchant Center feed is current.
- Product schema is valid + rich (review counts, availability, price).
- Returns policy is explicit.

## 9. Audit checklist

- **AIO-1** Page targets a specific searchable query (not just a broad topic).
- **AIO-2** Page ranks (or has a realistic path to rank) in top 10 organic for that query.
- **AIO-3** TL;DR paragraph directly under `<h1>` provides a 40–60 word answer.
- **AIO-4** At least one `<h2>` is phrased as the target query.
- **AIO-5** The passage immediately below each `<h2>` answers the question in the first sentence.
- **AIO-6** Answers are in server-side HTML (not only rendered after JS hydration).
- **AIO-7** Tables use semantic `<table><thead><tbody>` with a `<caption>`.
- **AIO-8** Numbered / bulleted lists use `<ol>` / `<ul>`, not styled divs.
- **AIO-9** Canonical URL clean — no redirect chain from the URL Google indexes.
- **AIO-10** `Article` or `Organization` schema present to improve source-card appearance.
- **AIO-11** Author byline + `Person` schema (informative content).
- **AIO-12** `dateModified` recent and reflects real content changes.
- **AIO-13** No hedged language ("it depends", "various factors") in answer paragraphs.
- **AIO-14** First paragraph after `<h2>` doesn't reference earlier content ("as mentioned", "above").
- **AIO-15** Query-relevant noun phrases appear in headings AND first sentences of answer paragraphs.
- **AIO-16** Commercial pages: visible price + `Product`/`Service` + `Offer` schema.
- **AIO-17** Location-specific commercial pages: `LocalBusiness` schema + Google Business Profile claimed.

---

## Severity guidance

- Page targets a query but doesn't rank in top 20 organic → **Medium** (no AIO without ranking)
- TL;DR paragraph missing under `<h1>` → **Medium**
- Heading is not question-phrased on target-query pages → **Medium**
- Answer requires scrolling past 500 words → **Medium**
- Content rendered client-side only → **High** (`crawlability-react.md`)
- Tables used as `<div>` grids → **Medium**
- No schema present on ranking-competitive pages → **Medium**
