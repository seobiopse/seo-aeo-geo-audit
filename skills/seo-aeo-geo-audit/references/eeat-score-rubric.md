# E-E-A-T Score Rubric

A 0–100 numeric grade of a page's E-E-A-T signals — Experience, Expertise, Authoritativeness, and Trust — based on Google's public Search Quality Rater Guidelines and the "helpful, reliable, people-first content" documentation.

Runs alongside the SEO Quality Score (see `seo-quality-score-rubric.md`). Where SEO Quality measures *how well the content is written for search*, E-E-A-T measures *whether the content is trustworthy enough to rank*. Both are scored per page; different rubrics apply to Landing/Money vs Blog/Article pages.

## The four pillars

### Experience (first-hand, lived knowledge)
Has the content author / the brand actually done the thing? First-hand screenshots, original data, case studies from real clients, photos of physical locations. Pages that are pure summary of other sites fail Experience.

### Expertise (subject-matter depth)
Does the author / brand have demonstrable expertise in the topic? Credentials, years in the field, certifications, published work, technical depth beyond the surface.

### Authoritativeness (recognized in the space)
Is the brand / author a recognized voice in the field? Backlinks from authoritative sources, mentions in industry publications, Wikipedia / Wikidata presence, named partnerships, awards.

### Trust (the reader can rely on this)
Can a reader trust this page to be accurate, safe, and transparent? Real contact information, clear policies, SSL, named author, dates, citations, no dark patterns.

Google has publicly stated that **Trust is the most important of the four** — the others feed into it. A page can have expertise and authoritativeness but still fail Trust if it's missing basic transparency signals.

## Landing / Money Page Scoring (total 100)

For pricing, service-detail, product-detail, signup, lead-capture pages.

| Pillar | Points | Signals we look for |
|---|---|---|
| **Trust** | 35 | Address + phone visible in footer; SSL valid; Privacy + Terms + Refund policies linked; real Organization schema with contactPoint; no dark patterns in CTAs or pricing; transparent pricing (no hidden fees) |
| **Experience** | 25 | Named customer logos (with permission); quantified case studies (before/after, specific outcomes); photos of physical location or team; specific project numbers (e.g., "installed 200+ enterprise fibre lines in Whitefield") |
| **Expertise** | 20 | Team credentials visible (certifications, partnerships, accreditations); years in business prominent; industry-specific depth in the copy; technical accuracy |
| **Authoritativeness** | 20 | Press mentions / "As seen in"; named partners (suppliers, certifiers, accreditors); industry awards; Organization.sameAs links to Wikipedia/Wikidata/Crunchbase/LinkedIn |

### Sub-signals per pillar — Landing/Money

**Trust (35 pts)**
- 10 pts — Address + phone + email visible in footer with `tel:` and `mailto:` links
- 8 pts — SSL valid + HSTS header + no mixed-content warnings
- 7 pts — Privacy Policy + Terms of Service + Refund/Returns Policy linked from footer
- 5 pts — Transparent pricing (visible numbers, no "contact for quote" as sole option on a pricing page)
- 3 pts — Organization schema present with contactPoint + areaServed
- 2 pts — No dark patterns (deceptive CTAs, hidden fees, forced checkboxes)

**Experience (25 pts)**
- 10 pts — Named customer logos (real, attributable, with permission)
- 8 pts — Quantified case studies / outcomes (specific numbers, named clients, timeframes)
- 4 pts — Photos of the physical location, team, or real product instances
- 3 pts — Specific operational numbers ("200+ enterprise customers," "4-hour fault response")

**Expertise (20 pts)**
- 8 pts — Team credentials visible (certifications, partnerships, accreditations displayed)
- 5 pts — Years in business + founding year prominent (more weight if > 5 years)
- 4 pts — Industry-specific depth in the copy (uses correct terminology, addresses specialist needs)
- 3 pts — Technical accuracy (no factual errors that a specialist would catch)

**Authoritativeness (20 pts)**
- 7 pts — Press mentions / "As seen in" with verifiable publisher names + links
- 5 pts — Named partnerships (suppliers, certifiers, accreditors) with logos + named relationships
- 4 pts — Organization.sameAs array links to authoritative sources (Wikipedia, Wikidata, Crunchbase, LinkedIn, Bloomberg, industry registries)
- 4 pts — Industry awards / recognitions displayed

### Grade bands for Landing/Money pages

- **90–100** Enterprise-trustable: every signal present, LLMs and users can both trust this page; ranks in competitive commercial SERPs
- **75–89** Solid: most signals present; one pillar weaker
- **60–74** Decent: core trust present; Experience or Authoritativeness thin
- **45–59** Weak: missing entire pillars; conversion suffers; LLMs don't cite
- **0–44** Failing: generic claims, no transparency, no named proof; Google's spam systems may deprioritize

## Blog / Article Page Scoring (total 100)

For blog posts, guides, explainers, editorial articles, thought-leadership pieces.

| Pillar | Points | Signals we look for |
|---|---|---|
| **Experience** | 30 | Author has personally done / measured / experienced what they're writing about; original screenshots, data, or first-hand examples; specific numbers from real work (not hypothetical) |
| **Expertise** | 30 | Named author with verifiable credentials; author bio linked to LinkedIn / published work; depth beyond summary-of-other-sites; technical accuracy |
| **Authoritativeness** | 20 | Cites primary sources (not aggregators); named experts quoted; article itself cited / referenced elsewhere; author has published on this topic before |
| **Trust** | 20 | Visible publish + last-updated dates; author bio with real photo + links; references linked; no clickbait headlines that don't match content |

### Sub-signals per pillar — Blog/Article

**Experience (30 pts)**
- 12 pts — Author has first-hand knowledge ("When we implemented X at our company..." / "I tested this on...")
- 10 pts — Original data, screenshots, or measurements present (not just third-party citations)
- 8 pts — Specific quantified examples ("47% faster build time" not "dramatically faster")

**Expertise (30 pts)**
- 10 pts — Named author with verifiable LinkedIn + bio page
- 8 pts — Author credentials relevant to topic (degree, years in field, publications, certifications)
- 7 pts — Technical depth beyond summary-of-others (unique framings, advanced angles, edge cases)
- 5 pts — Technical accuracy — no factual errors a specialist would catch

**Authoritativeness (20 pts)**
- 7 pts — Cites primary sources (Google docs, schema.org, RFCs, peer-reviewed papers) not aggregators
- 5 pts — Named experts quoted with verifiable attribution (interviews, LinkedIn-linked quotes)
- 4 pts — Author has published on this topic before (bio links to other articles)
- 4 pts — Article URL has been cited / linked by authoritative sources (verifiable backlinks)

**Trust (20 pts)**
- 7 pts — Visible publish + last-updated dates, matching `dateModified` in schema
- 6 pts — Author bio visible with photo + LinkedIn / X / ORCID links
- 4 pts — References linked to primary sources (not just "source: Google")
- 3 pts — Headline matches content (no clickbait mismatch)

### Grade bands for Blog/Article pages

- **90–100** Authoritative: cited by LLMs, ranks for the primary keyword and 10–30 related queries; author has a reputation in the topic
- **75–89** Strong: substantive and well-attributed; missing one dimension (usually original data or verified author)
- **60–74** Workable: informative but surface-level; ranks long-tail, rarely cited
- **45–59** Weak: generic, under-attributed, AI-boilerplate-feeling; Google's helpful-content systems may deprioritize
- **0–44** Failing: anonymous, thin, or re-written from other sources without value-add

## How to evaluate each signal

Evaluation is qualitative + evidence-based. For each sub-signal:

1. **Look for direct evidence** — visible on the page, in schema, or in the HTML source.
2. **Score on presence + quality** — is the signal there at all? Is it rich or token?
3. **Note what's missing** — so the report can recommend specific additions.

### Examples

**Sub-signal: "Named customer logos"**
- 0 pts — no customer logos
- 3 pts — generic "trusted by leading companies" without specific names
- 7 pts — 5+ named customer logos as `<img>` tags with proper alt text
- 10 pts — named logos + per-customer case study pages linked

**Sub-signal: "Author bio visible with LinkedIn link"**
- 0 pts — no byline
- 2 pts — "Content Team" or generic byline
- 4 pts — named author, no linked bio
- 6 pts — named author + bio page + LinkedIn in Person schema `sameAs`

## Output in the findings JSON

```json
{
  "scores": {
    "seo_quality": { ... see seo-quality-score-rubric.md },
    "eeat": {
      "page_type": "landing" | "blog",
      "overall": 62,
      "grade": "Decent",
      "breakdown": [
        {
          "pillar": "Trust",
          "value": 24,
          "max": 35,
          "sub_signals": [
            {"label": "Address/phone/email in footer", "value": 8, "max": 10, "status": "partial"},
            {"label": "SSL + HSTS", "value": 7, "max": 8, "status": "pass"},
            {"label": "Legal policies linked", "value": 5, "max": 7, "status": "partial"},
            {"label": "Transparent pricing", "value": 0, "max": 5, "status": "fail"},
            {"label": "Organization schema + contactPoint", "value": 3, "max": 3, "status": "pass"},
            {"label": "No dark patterns", "value": 1, "max": 2, "status": "partial"}
          ]
        },
        {
          "pillar": "Experience",
          "value": 14,
          "max": 25,
          "sub_signals": [ /* ... */ ]
        },
        {
          "pillar": "Expertise",
          "value": 12,
          "max": 20,
          "sub_signals": [ /* ... */ ]
        },
        {
          "pillar": "Authoritativeness",
          "value": 12,
          "max": 20,
          "sub_signals": [ /* ... */ ]
        }
      ],
      "top_improvements": [
        "Add 3 named customer logos with visible attribution — raises Experience from 14/25 to 21/25.",
        "Make pricing transparent (currently 'Contact us' only) — raises Trust from 24/35 to 29/35 AND unlocks Product/Offer schema eligibility.",
        "..."
      ]
    }
  }
}
```

## Severity-equivalent interpretation

Like SEO Quality scores, E-E-A-T scores don't replace severity. Rough correlation:

- 90–100 → no Trust / E-E-A-T critical findings expected
- 75–89 → maybe 1–2 Medium findings on one pillar
- 60–74 → 3–5 High findings across pillars
- 45–59 → multiple High + 1 Critical finding likely; brand-perception risk
- 0–44 → brand-perception crisis; Google quality systems downrank; LLMs don't cite

## Important rules

1. **Never fabricate sub-signals.** If a brand has no Wikipedia page, don't count "Wikipedia presence" as present. False scoring compounds downstream.
2. **Score on what's VISIBLE on the page**, not on what exists elsewhere. If a brand has a Crunchbase profile but it's not linked in the page's Organization schema, don't count it for Authoritativeness on that page.
3. **Score the PAGE, not the brand.** A strong brand with a weak landing page still scores the landing page on its own signals.
4. **Match page type before scoring.** A blog-page rubric applied to a pricing page gives misleading results.
5. **Trust is the foundation.** For Landing/Money pages (where Trust weighs 35/100), a page with < 20/35 on Trust cannot score above 60 overall regardless of other pillars. Flag this as a hard ceiling in the output.

## When to score

Same triggers as SEO Quality scoring (see `seo-quality-score-rubric.md`):
- `/full-audit` mode
- User explicitly requests "E-E-A-T score" / "trust score" / "credibility grade"
- One representative page per template, not every page on the site

Skip scoring when:
- `/crawl-check` mode
- Code-only audit (no live page)
- Pure utility pages (404, cookie banner)

## Page-type detection heuristics (for choosing the right rubric)

When auto-detecting whether a page is Landing/Money or Blog/Article, look for:

**Landing/Money indicators:**
- URL contains `/pricing`, `/plans`, `/enroll`, `/signup`, `/trial`, `/demo`, `/contact`, `/services/`, `/products/`
- Schema is `Product`, `Service`, `Offer`, `LocalBusiness`, `Course` with `offers`, `SoftwareApplication`
- Visible price or offer on page
- Primary CTA is conversion-oriented ("Buy", "Sign up", "Book a demo", "Get a quote")

**Blog/Article indicators:**
- URL contains `/blog/`, `/articles/`, `/posts/`, `/news/`, `/guides/`, `/learn/`, `/resources/`
- Schema is `Article`, `NewsArticle`, `BlogPosting`, `TechArticle`
- Primary visible content is text (> 800 words)
- Author byline visible

**Edge cases:**
- FAQ pages, About, Contact — score with Landing/Money rubric but note the reduced weight of Experience + Authoritativeness.
- Product + content hybrid pages (e.g., "the ultimate guide to fibre broadband" with a CTA at the bottom) — score both rubrics, average with 60/40 weighting toward Blog.
