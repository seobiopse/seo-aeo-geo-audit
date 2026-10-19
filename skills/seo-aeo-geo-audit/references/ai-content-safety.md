# AI Content Safety Reference

For any audit where the target uses AI to research, draft, paraphrase, or rewrite content. Goal: keep content on the right side of Google's policies, copyright, and LLM citation quality — not to evade detection.

## Core framing

Two ways to use AI in content:

1. **Research / drafting tool** — summarising sources, outlining, headline proposals, grammar, first drafts a human expert rewrites with their own experience and data.
2. **Scaled-publishing shortcut** — generating/rewriting content at volume, primarily to capture search traffic.

Google's March 2024 guidelines allow #1 and explicitly target #2 as "scaled content abuse." Copyright law draws a similar line. LLMs are increasingly good at identifying their own patterns — evasion is a losing game.

This reference focuses on making #1 safe and effective.

## Table of contents

1. [What Google's policies actually say](#1-google-policies)
2. [Copyright basics](#2-copyright-basics)
3. [The four originality add-ons](#3-four-originality-add-ons)
4. [Attribution patterns](#4-attribution-patterns)
5. [When AI assistance is OK](#5-when-ok)
6. [When AI content is not OK](#6-when-not-ok)
7. [Pre-publish checklist](#7-pre-publish-checklist)
8. [Safe workflow patterns](#8-safe-workflows)

---

## 1. Google policies

### 1.1 Scaled content abuse (March 2024)

Google takes action against sites producing large volumes of content primarily to manipulate rankings, regardless of production method. Threshold is *intent and scale*, not AI use.

100 AI-assisted articles/month targeting keywords with no unique expertise → demoted. 20 AI-assisted articles/month each reviewed by an expert with first-hand experience → fine.

### 1.2 Site reputation abuse (May 2024)

High-authority domains hosting third-party content unrelated to the host's editorial focus get demoted. Killed many news sites' coupon and gambling "guest post" sections.

### 1.3 Helpful content guidance (Aug 2022)

Ranking weighted toward "people-first content" — content written for a real audience with real expertise. Signals: first-hand experience, goes beyond obvious, trust signals (author bio, citations, dates), not primarily summarising other sites.

### 1.4 Google on AI-generated specifically

Public stance: AI content isn't banned. Content quality and purpose are what Google evaluates. Low-quality AI → demoted. High-quality AI-assisted → ranked normally.

Spam systems are tuned to detect low-effort AI patterns (generic openers, predictable structure, no specific details, no first-hand claims).

## 2. Copyright basics

### 2.1 Paraphrasing is not a defense

Copyright covers substantially similar expression, not just verbatim text. A rewrite preserving structure, order of arguments, and specific examples can still be infringing derivative work.

Practical test: if you closed the source and wrote from scratch, would your version look like the source? If yes, you've copied expression.

### 2.2 Facts aren't copyrightable — expression is

Learn facts from any source; reuse freely. Can't reuse the author's chosen words, sentence structure, worked examples, or analogies.

### 2.3 Fair use isn't a license

Fair use is a defense raised in court. Commercial sites using source material at scale typically don't qualify.

### 2.4 AI output has its own legal questions

US Copyright Office: purely AI-generated content isn't eligible for copyright protection without meaningful human authorship. If you want to enforce copyright on your content, the human contribution must be substantial.

### 2.5 Never include verbatim source text

More than ~15 words copied from another site = infringement risk. Quote briefly, attribute clearly, link to source.

## 3. The four originality add-ons

Every AI-assisted piece needs at least three of these four before publishing.

### 3.1 First-party experience

Something you or your team actually did, tested, measured. Not "studies show" — "when we implemented this on our product, we saw X."

Examples: screenshots of your dashboard, numbers from your analytics, interview transcripts, your A/B test results, photos of your physical location.

### 3.2 Expert byline with verifiable credentials

The author is a real person the reader can Google:
- Real name and photo
- Bio linking to LinkedIn / X / published work
- Credentials relevant to the topic
- `Person` schema with `sameAs` links

"Content Team" byline fails this test.

### 3.3 Original data or quotes

Data only available from you:
- Survey of your customers or industry
- Benchmark from your tools or product
- Direct interview quote from a named expert
- Publicly-scraped data analysed uniquely

One paragraph of original data in a 2,000-word article makes the whole piece citable.

### 3.4 Unique analysis or opinion

A take only a human with your perspective could write. Not "here are pros and cons" — "here's why industry consensus on this is wrong, and what we're doing differently."

LLMs average training data; clear, specific, defensible opinions differentiate.

---

**None of the above:** scaled-content-abuse candidate.
**One:** borderline.
**Three or four:** strong piece.

## 4. Attribution patterns

### 4.1 Link to primary sources, not aggregators
"According to a 2024 Statista report, ..." > "According to a 2024 study, ..." Better still, link directly.

### 4.2 Quote sparingly, verbatim
Short quotes, quotation marks, linked source. Don't clean up the quote.

### 4.3 Name the expert, not "studies show"
"A 2025 NIH study of 1,200 patients (Smith et al.) showed X" > "Studies show X". Also closer to how LLMs cite, raising your odds of being cited.

### 4.4 Separate "facts we learned" from "our take"
Make it clear which sentences report existing information and which are yours.

### 4.5 Disclose AI assistance where relevant
For editorial journalism, research reports — brief disclosure improves trust. Most marketing content doesn't need this, but if the reader would feel misled, disclose.

## 5. When AI assistance is OK

- Generating outlines a human expert rewrites
- Summarising long docs for internal use
- Proposing headline variations
- Grammar and style editing
- Translating content the team authored
- Generating code examples in tutorials (with human review)
- First drafts of product descriptions from structured data
- Rewording for different audiences or reading levels
- Researching adjacent topics

Common thread: AI does what a junior assistant might do; a human expert takes responsibility for the final output.

## 6. When AI content is not OK

- Feeding competitor articles into a rewriter and publishing
- Generating hundreds of location-page variants
- AI-written "expert opinion" under a fictional byline
- AI "reviews" of products the team hasn't used
- AI-generated "news" from press releases without additional reporting
- Rewriting Wikipedia for SEO traffic
- Content for subdomains/subdirectories that don't match host's editorial focus (site reputation abuse)
- FAQ schema filled with AI-generated Q/As matching search queries rather than actual user questions

Common thread: content exists primarily to capture search traffic, not to serve an audience.

## 7. Pre-publish checklist

Hold the piece if three or more are "no":

- **1** Byline names a real verifiable person?
- **2** At least one paragraph of first-party experience, data, or quotes?
- **3** At least one original analysis or opinion paragraph?
- **4** All sources named and linked to primary source?
- **5** Edited by a human who'd stake their reputation on it?
- **6** No verbatim passages > 15 words from any source?
- **7** `Person` schema on author page with real external `sameAs` links?
- **8** Answers a real question the audience is actually asking (not just a keyword)?
- **9** Part of a series? Each entry meaningfully different (not templated)?
- **10** Still useful if search didn't exist (to a reader arriving from a newsletter)?

## 8. Safe workflows

### 8.1 Expert-first, AI-assisted
Expert outlines + decides thesis. AI fills structure, grammar, boilerplate. Expert rewrites key passages in their voice + adds first-hand examples. Expert signs off.

### 8.2 Research-then-write
AI summarises sources into an internal research brief. Human writes the public piece from scratch, without referring back to source text. Sources cited, not rewritten.

### 8.3 Interview-to-article
Human conducts 30-min interview with named expert. AI transcribes + summarises. Human editor rewrites. Attributed to interviewer + interviewee.

### 8.4 Data-driven content
Start with proprietary dataset. AI describes the data. Unique data is the defensible contribution.

### 8.5 Opinion / editorial
Human writes first-person position piece. AI only for grammar + alternate phrasing. Thesis entirely human.

---

## Severity guidance

- **Critical** — Verbatim paraphrasing of identifiable source articles at scale
- **High** — AI content with no first-party experience, data, or named author
- **Medium** — Missing author schema / bio / credentials on AI-assisted pieces
- **Low** — Style-level issues on pieces that otherwise pass
- **Info** — Opportunities to strengthen already-safe pieces
