# AEO Audit Checklist — Answer Engine Optimization

AEO is about being *the extracted answer* in an answer-engine result: Google AI Overviews, Featured Snippets, Bing Copilot, voice assistants.

Mark each `pass`, `warn`, or `fail`. Use the issue framework for findings not a pass.

## Table of contents

1. [Answer-first structure](#1-answer-first-structure)
2. [Question-led headings](#2-question-led-headings)
3. [Schema for extraction](#3-schema-for-extraction)
4. [Content format for extractors](#4-content-format-for-extractors)
5. [E-E-A-T signals](#5-e-e-a-t-signals)
6. [Technical accessibility for AI crawlers](#6-technical-accessibility-for-ai-crawlers)
7. [Freshness](#7-freshness)
8. [Entity clarity](#8-entity-clarity)

---

## 1. Answer-first structure

Extractors lift the first clean, direct answer they find.

- **1.1** Primary question answered in first 1–2 sentences of main content, within 40–60 words.
- **1.2** Answer paragraph is self-contained. Remove pronouns referencing earlier paragraphs.
- **1.3** Definition answers follow: `[Subject] is [direct definition]. [1–2 sentences of elaboration].`
- **1.4** How-to answers lead with numbered list or tight paragraph summary.
- **1.5** Comparison answers state the winner/verdict up front.

## 2. Question-led headings

Extractors scan `<h2>` and `<h3>` for question patterns.

- **2.1** At least one heading phrased as a question users actually ask.
- **2.2** Each question-heading immediately followed by a self-contained answer (< 60 words).
- **2.3** Multiple related questions each get their own `<h2>`/`<h3>` + answer.
- **2.4** Heading phrasing matches what users search (check autocomplete, "People also ask").

## 3. Schema for extraction

For schema recipes, read `structured-data-advanced.md`.

- **3.1** `FAQPage` schema where FAQ visible — every Q/A matches visible text.
- **3.2** `HowTo` schema on step-by-step content; steps match visible page.
- **3.3** `Article`/`NewsArticle` with typed `author`, `datePublished`, `dateModified`, `publisher`.
- **3.4** `SpeakableSpecification` inside `Article` pointing to the answer-first paragraph.
- **3.5** `QAPage` if the page is a single-question Q&A.
- **3.6** All schema passes Google's Rich Results Test with no errors.

## 4. Content format for extractors

- **4.1** Paragraph answer (40–60 words, self-contained) for definition queries.
- **4.2** Numbered list for "how to" queries. Each step short.
- **4.3** Bulleted list for "list of" / "types of" queries. Each bullet a complete phrase.
- **4.4** Proper `<table><thead><tbody>` markup for comparison queries (not divs).
- **4.5** Tables include `<caption>`.
- **4.6** Lists/tables appear *before* long-form explanation.

## 5. E-E-A-T signals

- **5.1** Author byline linking to a real author page.
- **5.2** Author page has real name, photo, bio with credentials, links to profiles.
- **5.3** Author markup uses `Person` schema with `jobTitle`, `worksFor`, `sameAs`.
- **5.4** `Organization` schema on homepage with `foundingDate`, `address`, `telephone`, `sameAs`, `logo`.
- **5.5** For YMYL topics (health, finance, legal), prominent citations + reviewer byline where appropriate.
- **5.6** Citations are real links to authoritative sources.
- **5.7** Originality signals: original research, data, first-hand quotes.

## 6. Technical accessibility for AI crawlers

- **6.1** Main content in server-rendered HTML (most answer-engine crawlers don't run JS).
- **6.2** `robots.txt` explicitly allows Googlebot, Bingbot, Google-Extended (if opting in).
- **6.3** No rate-limiting/WAF rule accidentally blocking legitimate crawlers.
- **6.4** No mandatory JS interaction (accordions, tabs) hiding the answer.
- **6.5** GET-based pagination, not POST-required.

## 7. Freshness

- **7.1** Visible "Last updated" date matching `dateModified` in schema.
- **7.2** `dateModified` reflects real content changes, not rebuilds.
- **7.3** Evergreen content reviewed annually — "Reviewed [date] by [author]".
- **7.4** Time-sensitive claims (prices, stats, versions) either current or explicitly dated.

## 8. Entity clarity

- **8.1** Primary entity named consistently throughout.
- **8.2** `about` or `mentions` schema linking to Wikidata / Wikipedia URL where one exists.
- **8.3** Brand `sameAs` links to Wikipedia, Crunchbase, primary social profiles.
- **8.4** URL slug contains the primary entity name.
- **8.5** First mention uses the full formal name.

---

## Related references

- `structured-data-advanced.md` — FAQPage, HowTo, SpeakableSpecification, Article schema.
- `ai-content-safety.md` — if content is AI-assisted, AEO engines increasingly down-weight low-effort AI content.

## What to do after this checklist

Use the issue framework. AEO issues tend to cluster on Medium/High.
