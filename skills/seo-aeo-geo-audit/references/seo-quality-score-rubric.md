# SEO Quality Score Rubric

A 0–100 numeric grade of a page's content quality from an NLP-and-intent-aware perspective. Scored on four content signals plus topical coverage, with distinct rubrics for **Landing / Money pages** and **Blog / Article pages**.

Read whenever the audit mode is `/full-audit` or the user explicitly asks for a "quality score" / "content grade" / "NLP audit". The scoring sits on top of the checklist audit — it's not a replacement, it's the summary.

## The four NLP signals

### 1. LSI terms (Latent Semantic Indexing)
Related keywords and phrases that co-occur naturally with the target keyword across the web. If a page targets "fibre broadband Whitefield" and doesn't mention ISP, bandwidth, SLA, uplink, router, downtime, or enterprise — Google assumes the content is thin.

**How to evaluate:**
- Identify the page's 1–2 primary target keywords (from H1, title, meta description).
- List 10–20 LSI terms that an expert writer on this topic would naturally include.
- Count how many actually appear on the page.
- Score = (matches / 20) × pillar weight.

### 2. Semantic terms
Synonyms, morphological variants, and alternative phrasings of the target keywords. A page that says "fibre broadband" five times and never says "fiber optic internet," "dedicated fibre," or "leased-line" reads as keyword-stuffed, not topically expert.

**How to evaluate:**
- For each primary keyword, derive 5–8 natural semantic variants.
- Count distinct variants used on the page (at least once each).
- Penalise repetition: using the same keyword 10× while skipping synonyms is worse than using 10 different phrasings.
- Score = variant coverage, adjusted for keyword density balance.

### 3. Entity terms
Named entities that Google's Knowledge Graph expects on a topically-complete page: organisations (competitors, suppliers, partners), people (experts, named customers), places (locations served, city landmarks), products (specific named offerings), technologies (standards, protocols, tools).

**How to evaluate:**
- Extract all capitalised multi-word terms + proper nouns from the page body.
- For Landing/Money pages: expect 5–15 entities (brand + key offerings + target locations).
- For Blog/Article pages: expect 10–30 entities (broader topical coverage required).
- Check entities resolve to real Knowledge Graph entries — a page mentioning "Cisco" + "Juniper" + "Google Fiber" scores higher than a page mentioning "leading vendors."

### 4. Page sentiment score
Tone of the content relative to intent. A landing page should be confident and action-oriented (not aggressive). A blog should be educational and balanced (not preachy). An informational FAQ should be neutral and factual.

**How to evaluate:**
- Run qualitative sentiment on the body text: classify each paragraph as Confident / Neutral / Cautious / Aggressive / Defensive.
- For Landing/Money pages: expected distribution is ~60% Confident, ~30% Neutral, ~10% Cautious. Aggressive or Defensive tones tank the score.
- For Blog/Article pages: expected distribution is ~20% Confident, ~60% Neutral, ~20% Cautious. Too much Confident sounds like marketing spin.
- Score based on alignment with expected distribution for the page type.

## Landing / Money Page Scoring (total 100)

For pricing, service-detail, product-detail, signup, landing-page-for-paid-campaign pages.

| Dimension | Points | What it measures |
|---|---|---|
| LSI term coverage | 20 | Depth of topically-related vocabulary (industry terminology, technical terms, product-category terms) |
| Semantic variants | 20 | Breadth of phrasings for target keywords (synonyms, morphological variants, localized forms) |
| Named entities | 15 | Concrete named things (competitors, partners, locations served, product names) |
| Content depth | 20 | Word count + unique content ratio + section structure (headers per 500 words) |
| Sentiment alignment | 10 | Confident / neutral / cautious distribution matches commercial-intent expectations |
| Keyword targeting discipline | 10 | Primary keyword used 3–8× (not stuffed); H1 + title + meta description aligned |
| Trust signal density | 5 | Named testimonials + real reviews + customer logos present in body text |
| **Total** | **100** | |

### Grade bands for Landing/Money pages

- **90–100** Exceptional: comprehensive, trust-signal-rich, semantically deep. Competes for featured snippets on commercial queries.
- **75–89** Strong: most signals present; some dimension is weaker (often entities or semantics).
- **60–74** Workable: core message lands, but thin on depth or missing entities. Ranks but doesn't dominate.
- **45–59** Weak: underweight on most signals. Ranks only for low-competition queries.
- **0–44** Failing: generic, thin, or keyword-stuffed. Google's helpful-content systems will deprioritize.

### Common failure modes on Landing/Money pages

- Hero copy of 30 words + bullet list of features + "Contact us" — fails LSI, semantics, entities, depth.
- Generic claims ("leading provider," "best-in-class") without named entities — fails entity + trust.
- Aggressive CTA density (6 "Book now" buttons above the fold) — fails sentiment.
- Missing the target location or industry terminology — fails LSI.

## Blog / Article Page Scoring (total 100)

For blog posts, guides, explainers, news articles, editorial content.

| Dimension | Points | What it measures |
|---|---|---|
| LSI term coverage | 15 | Topically-related vocabulary for the article's subject |
| Semantic variants | 20 | Natural phrasings of core concepts; avoids keyword stuffing |
| Named entities | 25 | Specific people, companies, products, standards, tools mentioned |
| Content depth | 20 | Word count (typically 1,200–3,500 for strong ranking), heading structure, paragraph variety |
| Sentiment alignment | 10 | Educational / neutral / balanced tone; avoids marketing spin |
| Readability | 10 | Flesch-Kincaid-ish balance: ~60–70 for most audiences; 40–60 for technical topics |
| **Total** | **100** | |

### Grade bands for Blog/Article pages

- **90–100** Exceptional: authoritative, entity-rich, comprehensive. Ranks for the primary keyword + 10–30 related queries; cited by LLMs.
- **75–89** Strong: substantive, well-structured; missing one dimension (usually entities or depth).
- **60–74** Workable: informative but surface-level. Ranks for long-tail; rarely cited by LLMs.
- **45–59** Weak: thin, generic, or AI-boilerplate-feeling. Ranks only for low-competition queries.
- **0–44** Failing: shallow or off-topic; risk of Google's helpful-content downranking.

### Common failure modes on Blog/Article pages

- 500-word articles that try to cover broad topics — fails LSI, entities, depth.
- "5 tips" style with generic tips and no named tools/companies — fails entities.
- Aggressive CTA mid-article ("Book a demo of our product!") — fails sentiment for educational intent.
- Summary of other sites without original data or named sources — fails entities + fails the AI-content-safety check (see `ai-content-safety.md`).

## How to output the score

Every quality score produced by this rubric must include:

1. **Page type classification** — Landing/Money OR Blog/Article (auto-detected from URL pattern + H1 + schema type)
2. **Overall score** (0–100)
3. **Sub-scores per dimension** (each dimension's contribution to the total)
4. **Identified LSI terms present / missing** — as specific word lists
5. **Identified entities present / missing** — as named-entity lists
6. **Sentiment distribution** — percentages of each tone
7. **Grade band interpretation** — human-readable assessment
8. **Three highest-impact improvements** — which dimension to address first, what to add

### Output in the findings JSON

Add a top-level `scores` object to the audit JSON:

```json
{
  "audit": { ... },
  "summary": { ... },
  "scores": {
    "seo_quality": {
      "page_type": "landing" | "blog",
      "overall": 68,
      "grade": "Workable",
      "breakdown": [
        {"label": "LSI coverage", "value": 14, "max": 20, "note": "..."},
        {"label": "Semantic variants", "value": 16, "max": 20, "note": "..."},
        {"label": "Named entities", "value": 8, "max": 15, "note": "..."},
        {"label": "Content depth", "value": 14, "max": 20, "note": "..."},
        {"label": "Sentiment alignment", "value": 7, "max": 10, "note": "..."},
        {"label": "Keyword targeting discipline", "value": 6, "max": 10, "note": "..."},
        {"label": "Trust signal density", "value": 3, "max": 5, "note": "..."}
      ],
      "lsi_terms_present": ["..."],
      "lsi_terms_missing": ["..."],
      "entities_present": ["..."],
      "entities_missing": ["..."],
      "sentiment_distribution": {"confident": 0.55, "neutral": 0.30, "cautious": 0.10, "aggressive": 0.05},
      "top_improvements": [
        "Add 3-5 named entities from the local ISP market (specific street names, pincodes, competitor providers) — raises entity score from 8/15 to 12-14/15.",
        "..."
      ]
    },
    "eeat": { ... see eeat-score-rubric.md }
  },
  "findings": [ ... ]
}
```

The generator renders this as a visual scorecard section at the top of the HTML report, with bar charts for each breakdown dimension.

## When to score

Run the scoring automatically whenever:
- Mode is `/full-audit`
- User explicitly asks for "content quality score," "SEO score," "grade this page"
- Auditing a single representative page (scoring 50 pages is noise; score one representative page per template)

Skip scoring when:
- Mode is `/crawl-check` (scope doesn't include content quality)
- The target is code-only (no live URL to analyze)
- The page is a pure utility page (404 page, cookie banner, etc.)

## Severity-equivalent interpretation

Scores don't replace severity — they summarize. But rough correlation:
- 90–100 → no Critical content findings expected
- 75–89 → maybe 1–2 Medium findings
- 60–74 → expect 3–5 Medium + 1–2 High findings
- 45–59 → expect several High + 1 Critical finding
- 0–44 → likely multiple Critical findings + page is a candidate for rewriting rather than patching

The score is communicated alongside findings, not as a substitute. A 95/100 page with one Critical finding is still not shippable — fix the Critical first.
