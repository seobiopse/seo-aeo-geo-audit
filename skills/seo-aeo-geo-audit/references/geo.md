# GEO Audit Checklist — Generative Engine Optimization

GEO is about being *cited by a generative AI* in its response — ChatGPT, Perplexity, Claude, Gemini, Microsoft Copilot, Meta AI, Grok.

Mark each `pass`, `warn`, or `fail`. Use the issue framework for findings not a pass.

## Table of contents

1. [llms.txt and AI-crawler access](#1-llmstxt-and-ai-crawler-access)
2. [Semantic HTML for retrieval](#2-semantic-html-for-retrieval)
3. [Content chunk-ability](#3-content-chunk-ability)
4. [Citation-worthy signals](#4-citation-worthy-signals)
5. [Entity & brand presence](#5-entity--brand-presence)
6. [Authority & third-party signals](#6-authority--third-party-signals)
7. [Structured data for LLMs](#7-structured-data-for-llms)
8. [Content freshness](#8-content-freshness)
9. [Prompt-realistic content](#9-prompt-realistic-content)

---

## 1. llms.txt and AI-crawler access

- **1.1** `robots.txt` at `/robots.txt` explicitly handles each major AI crawler. Decide the policy once, apply consistently:
  - **Retrieval crawlers** (important for live citation): `ChatGPT-User`, `OAI-SearchBot`, `PerplexityBot`, `Perplexity-User`, `ClaudeBot`, `Claude-SearchBot`, `Claude-Web`, `Applebot-Extended`
  - **Training crawlers** (controls inclusion in model training): `GPTBot`, `Google-Extended`, `anthropic-ai`, `CCBot`, `Bytespider`, `Meta-ExternalAgent`
- **1.2** Not accidentally disallowing retrieval crawlers — blocking these silently removes the brand from live AI answers.
- **1.3** `llms.txt` at `/llms.txt` follows the emerging spec (https://llmstxt.org/):
  ```
  # Brand name
  > One-sentence description.

  ## Docs
  - [Getting started](https://example.com/docs/start): Summary
  - [API reference](https://example.com/api): Summary
  ```
- **1.4** `llms-full.txt` at `/llms-full.txt` (optional) contains flattened Markdown of the most important content.
- **1.5** Neither `llms.txt` nor `llms-full.txt` contain secrets, internal-only URLs, or unpublished pricing.

## 2. Semantic HTML for retrieval

LLM retrieval chunkers parse HTML into blocks. Semantic tags improve chunk boundaries.

- **2.1** Uses `<main>`, `<article>`, `<section>`, `<nav>`, `<aside>`, `<header>`, `<footer>`.
- **2.2** Each distinct topic in its own `<section>` with a leading heading.
- **2.3** NOT rendered exclusively inside `<div id="root">` via CSR — retrieval chunkers often don't execute JS.
- **2.4** Code blocks use `<pre><code class="language-xxx">`.
- **2.5** Quotes use `<blockquote cite="...">` with a `cite` attribute.

## 3. Content chunk-ability

LLM retrieval chunks are typically 500–1500 tokens. Each chunk is independent.

- **3.1** Each major section is self-contained.
- **3.2** No pronouns referencing content more than a paragraph earlier. "As mentioned above" is an anti-pattern.
- **3.3** Key facts in the same paragraph as the context needed to understand them.
- **3.4** Tables/lists/code blocks not split mid-structure.
- **3.5** Sections end at natural pause points.

## 4. Citation-worthy signals

LLMs preferentially cite:

- **4.1** Unique data (original research, surveys, first-party benchmarks, proprietary datasets).
- **4.2** Specific numbers and dates ("47% of teams deploy twice a week (2024 survey of 1,200 engineers)").
- **4.3** Named quotes attributed to named people with role and organization.
- **4.4** Proper nouns — explicit company, product, person, place names.
- **4.5** Methodology statements on data presentations.
- **4.6** Direct definitions — "[Term] is [definition]" in opening paragraph of dedicated pages.

## 5. Entity & brand presence

- **5.1** Wikipedia / Wikidata entry exists (or can be created by independent editors — do NOT create conflict-of-interest edits yourself).
- **5.2** Brand named consistently across all properties.
- **5.3** `Organization` schema with `sameAs` links to Wikipedia, Wikidata, Crunchbase, Bloomberg, LinkedIn, X/Twitter, GitHub.
- **5.4** Founder/key-person pages with `Person` schema, linked to `Organization` via `founder`/`employee`.

## 6. Authority & third-party signals

- **6.1** Brand mentioned in authoritative industry publications.
- **6.2** Brand mentioned in open datasets (GitHub READMEs, Stack Overflow, Reddit, Common Crawl-indexed).
- **6.3** Linked backlinks from `.edu`, `.gov`, established industry sites; not broken.
- **6.4** No active reputation crisis on page 1 of SERPs for branded queries.
- **6.5** Team members have interviews, podcasts, or guest posts under their names.

## 7. Structured data for LLMs

Everything in the AEO schema checklist plus:

- **7.1** `Dataset` schema on pages with original data.
- **7.2** `SoftwareApplication` on software/tool pages.
- **7.3** `Course` schema on educational content.
- **7.4** `Review` schema with `author` and `reviewRating` both present.

## 8. Content freshness

- **8.1** Visible dates on time-sensitive content.
- **8.2** `dateModified` reflects real content changes only.
- **8.3** Yearly-update content (e.g., "Best X of 2026") — URL slug updated or canonical redirect set.
- **8.4** Stale content has updated `datePublished` with real revisions OR explicit "last reviewed" date.
- **8.5** Rapidly-changing topics republished with new `dateModified` within the month.

## 9. Prompt-realistic content

- **9.1** Conversational phrasings users would paste into ChatGPT.
- **9.2** Covers the full question, not just the narrow keyword.
- **9.3** Adjacent questions addressed via `<h3>` subheadings ("What about...?").
- **9.4** First-person / opinionated takes allowed and attributed.
- **9.5** No AI-generated boilerplate in first or last paragraph.

---

## Related references

- `crawlability-react.md` — most LLM bots don't run JS; foundation under every GEO signal on React sites.
- `structured-data-advanced.md` — entity graphs via `@graph` / `@id`.
- `ai-content-safety.md` — if AI-assisted, originality and attribution determine whether LLMs cite at all.

## What to do after this checklist

Use the issue framework. GEO issues tend to Medium — they're about future-proofing. But they compound.
