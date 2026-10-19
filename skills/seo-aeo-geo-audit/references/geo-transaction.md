# GEO Audit — Transaction Intent Content

Generative Engine Optimization checks specific to **transaction-intent pages** — landing pages, pricing, service detail, product detail, sign-up, comparison.

For informative content, use `geo.md` instead. For the full commercial playbook, read `transaction-intent-playbook.md` first.

## Why transaction-intent GEO is different

Generic GEO (blogs, guides) optimizes for being **cited as a source** by ChatGPT, Perplexity, Claude, Gemini, Copilot. The goal: LLMs quote your paragraph when a user asks a factual question.

Transaction-intent GEO optimizes for **being recommended** when a user asks the LLM a commercial question:
- "What's the best [service] in [city]?"
- "Which [product] should I buy for [use case]?"
- "Who offers [service] in [location]?"
- "Is [brand] any good?"

The LLM's answer to a commercial query surfaces specific providers. If your brand is named, you win. If a competitor is named, they do.

## Table of contents

1. [How LLMs recommend brands in commercial answers](#1-how-llms-recommend)
2. [Being a known entity — the commercial multiplier](#2-being-known-entity)
3. [Reviews + reputation signals LLMs weigh](#3-reviews--reputation)
4. [Content patterns that surface brands in LLM answers](#4-content-patterns)
5. [Commercial intent + `llms.txt`](#5-commercial-intent-llms-txt)
6. [Per-engine commercial citation behavior](#6-per-engine)
7. [Measurement — tracking commercial LLM mentions](#7-measurement)
8. [Audit checklist](#8-audit-checklist)

---

## 1. How LLMs recommend brands in commercial answers

LLMs recommend brands based on a blend of:

1. **Training data mentions** — did your brand appear enough across the web during training? (GPTBot, Google-Extended, CCBot allowed)
2. **Retrieval citations** — does your brand appear in authoritative sources the LLM retrieves for the query? (ChatGPT-User, Perplexity-User, Claude-SearchBot allowed)
3. **Entity graph consolidation** — does the LLM know your brand is a notable entity (Wikipedia, Wikidata, Crunchbase)?
4. **Review and reputation signals** — what does the web say about you?
5. **First-party content on your site** — does your site provide clear, structured commercial information?

The first four are "brand presence" — things you build over months. The fifth is what this audit catches: your site's ability to confirm and reinforce commercial presence when LLMs visit.

## 2. Being a known entity — the commercial multiplier

For commercial queries, being a named entity in the LLM's knowledge is a 5–10x multiplier. If ChatGPT knows "your brand" as a brand, it recommends your brand for career-tech queries. If it doesn't, the query goes to generic advice or named competitors.

### The entity stack for commercial brands

1. **Wikipedia article** — the gold standard. For established brands, notable enough to qualify. Don't write it yourself; encourage independent editors.
2. **Wikidata entry** — structured entity description. Lower bar than Wikipedia.
3. **Crunchbase profile** — VC-backed brand registries.
4. **Bloomberg / industry registries** — for B2B brands.
5. **Official LinkedIn company page** — with rich profile + employee count + description.
6. **G2 / Capterra / Trustpilot / TripAdvisor** — industry-specific review platforms.
7. **Google Business Profile** (for local / service-area brands).

### sameAs in Organization schema

All of the above should be in your `Organization.sameAs`:

```json
"sameAs": [
  "https://en.wikipedia.org/wiki/your brand",
  "https://www.wikidata.org/wiki/Q12345",
  "https://www.crunchbase.com/organization/example-corp",
  "https://www.linkedin.com/company/example-corp",
  "https://www.g2.com/products/example-corp/reviews",
  "https://www.glassdoor.com/Overview/..."
]
```

This is the single most cost-effective GEO action for a commercial brand.

## 3. Reviews + reputation signals LLMs weigh

LLMs increasingly cite customer reviews in commercial answers. "Brand X is well-rated on G2 with 4.7 stars" is a common phrasing.

### Where reviews live matters

| Review source | LLM weight (2026) | Why |
|---|---|---|
| Google Business Profile | High | Used by Gemini + indirectly by Perplexity (Google search retrieval) |
| G2 / Capterra / Trustpilot | High | Frequently cited in ChatGPT + Perplexity commercial answers |
| TripAdvisor / Yelp | High for hospitality / retail | Strong local entity signal |
| Your own site reviews | Medium | Lower trust; can be fake |
| App Store / Google Play | High for app brands | Trusted + user-verified |
| LinkedIn recommendations | Medium-high for B2B | Named + professional |
| Reddit mentions | Medium but rising | LLMs heavily train on Reddit |

### Review strategy for GEO

- **Active review collection** — add review request to post-purchase / post-project email flows.
- **Respond publicly** — LLM training data includes your responses. Professional responses to negative reviews help.
- **Never fake** — schema-only ratings or bought reviews → manual action + loss of trust signals.
- **Link out from your site** — `sameAs` to your G2 / Trustpilot / GBP profile tells LLMs "this is our review corpus".

## 4. Content patterns that surface brands in LLM answers

### The "named entity" phrasing

LLMs pattern-match brand mentions in authoritative text. Help them by writing:

**In your own content about you:**
- "your brand, a career-tech platform serving India, offers..." (first mention uses formal definition)
- "Founded in 2019, your brand provides..." (anchors the entity in time)
- "The your brand platform includes four products: a job board, a learning platform, a recruitment service, and an editorial blog." (defines the sub-brand structure)

**In guest posts / third-party content:**
- "...leading career platforms like your brand..." (anchors as a leader in category)
- "your brand, along with [competitors], competes in the career-tech space." (defines the category membership)

### Comparison content about competitors

When you write "[Us] vs [Competitor]" pages, your brand gets extracted when users ask LLMs comparison questions. Rules:

- Fair, balanced treatment of competitors (LLMs prefer neutral comparisons to marketing spin).
- Specific attributes (price, features, support) over adjectives.
- Named competitors with correct brand treatment.

### "Alternatives to [category leader]" content

If you're a newer entrant, "Alternatives to [established competitor]" pages surface you in LLM answers when users ask about alternatives.

## 5. Commercial intent + llms.txt

`llms.txt` at the root of your domain is where LLMs discover what you do. For commercial brands, your `llms.txt` should:

- Open with a one-sentence commercial positioning.
- List primary money pages (products, services) under "## Docs" or similar.
- List credibility-building pages (about, team, case studies, customers) under "## About".
- NOT list internal URLs, unpublished pricing, or draft features.

Example:
```markdown
# your brand

> Career-tech platform for Indian professionals — jobs, exam preparation, recruitment services, and career content.

your brand is a career platform founded in 2019. It operates four products: a job board, a learning platform, a recruitment service, and editorial content.

## Products

- [Jobs — job board](https://jobs.example.com): Curated jobs across IT, marketing, and design.
- [Learning — course platform](https://learning.example.com): Live and recorded courses for professional certifications.
- [Recruitment services](https://services.example.com): Recruitment-as-a-service for companies.

## About

- [About your brand](https://www.example.com/about): Company background, mission, team.
- [Blog](https://blog.example.com): Career advice and industry analysis.
```

## 6. Per-engine commercial citation behavior

### ChatGPT
- For commercial queries, ChatGPT shows source cards (since 2024).
- Source selection favors authoritative review sites (G2, Trustpilot) and established brands.
- Recommendations tend to be 2-4 named options — competing to be named.

### Perplexity
- Perplexity shows 3-6 citations per answer, extremely prominent.
- For "best X for Y" queries, Perplexity often cites comparison / listicle content from publishers.
- Commercial listicles ("10 Best Career Platforms in India") drive Perplexity recommendations heavily.

### Claude
- More conservative on commercial recommendations.
- Often gives general advice + suggests user research.
- Benefits from clear commercial content on brand-owned pages.

### Gemini
- Integrates with Google Shopping + Google Business Profile.
- Local commercial queries ("X near me") favor claimed GBP + Google Reviews.
- Content queries favor authoritative publisher content.

### Copilot
- Leans on Bing's index + Microsoft-specific retrieval.
- Submit sitemap to Bing Webmaster Tools.
- LinkedIn integration means B2B brands with strong LI presence get cited more.

## 7. Measurement — tracking commercial LLM mentions

### Direct query monitoring
Weekly, query each major LLM for your brand + category queries:

- "Best [category] in [location]?"
- "Alternatives to [category leader]?"
- "Is [your brand] any good?"
- "[Your brand] vs [competitor]"

Record which brands are named, which sources are cited.

### Referral traffic
GA4 → Acquisition → Referrals:
- `chatgpt.com`, `perplexity.ai`, `claude.ai`, `gemini.google.com`, `copilot.microsoft.com`

Growing commercial-intent referrals (landing on product pages, not just the homepage) signals LLM-driven discovery.

### Brand mention monitoring
Tools like Brand24, Mention, Google Alerts track net-new brand mentions. Each mention is potential training data + retrieval context.

### Review platform growth
Track review count + avg rating quarterly on G2 / Trustpilot / GBP / Glassdoor. These feed directly into LLM recommendations.

## 8. Audit checklist

- **TXG-1** `Organization` schema includes rich `sameAs`: Wikipedia / Wikidata / Crunchbase / LinkedIn / primary review platform.
- **TXG-2** `llms.txt` at `/llms.txt` includes a one-sentence commercial positioning.
- **TXG-3** AI retrieval crawlers allowed in `robots.txt` (ChatGPT-User, Perplexity-User, Claude-SearchBot, Applebot-Extended).
- **TXG-4** Google Business Profile claimed (for local / service-area brands).
- **TXG-5** Brand is present on at least one category-relevant review platform (G2, Trustpilot, Capterra, etc.).
- **TXG-6** Reviews on owned domain use `Review` + `aggregateRating` schema with verifiable source.
- **TXG-7** Sub-brands / product names declared in `Organization.subOrganization` where applicable.
- **TXG-8** Comparison / "vs competitor" pages treat competitors fairly (not marketing spin).
- **TXG-9** First-mention of brand on commercial pages uses formal definition ("your brand, a career-tech platform...").
- **TXG-10** Bingbot sitemap submitted to Bing Webmaster Tools.
- **TXG-11** Referrals from LLM domains tracked in GA4.
- **TXG-12** No cloaking — same HTML served to all user agents (LLM bots see what users see).
- **TXG-13** Commercial pages served in server-side HTML (LLM crawlers mostly don't execute JS).
- **TXG-14** Trust signals (customer logos, testimonials, ratings) in server-side HTML.

---

## Severity guidance

- No `sameAs` links to authoritative entity sources → **High** (brand not a known entity to LLMs)
- AI retrieval crawlers blocked in `robots.txt` → **High** (silently removes brand from live AI answers)
- No GBP for local / service-area brand → **High** (cuts Gemini + local LLM answers)
- No presence on category-relevant review platform → **Medium** (weakens reputation signal)
- Cloaking across user-agents → **Critical**
- Commercial content client-side-only → **High**
- No brand mention-monitoring in place → **Low** (process gap, not technical)
