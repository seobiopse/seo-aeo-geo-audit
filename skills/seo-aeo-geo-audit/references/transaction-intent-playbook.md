# Transaction-Intent Content Playbook

Landing pages, money pages, pricing pages, sign-up pages, product/service detail pages — everything where the primary goal is **conversion**, not **education**.

Transaction-intent pages have different SEO/AEO/GEO rules than informative content (blogs, articles, guides). The general `aeo.md` and `geo.md` references assume informative intent. This playbook covers the commercial half.

Read whenever the audit target is:
- A landing page (PPC destination or organic lead-capture)
- A pricing page
- A product / service detail page that's not part of a programmatic template
- A "compare plans" / "compare us vs competitor" page
- A signup / "start free trial" / "book a demo" page
- A city/neighbourhood page with commercial intent

For programmatic patterns (jobs, courses, events, bulk location pages), see `pseo-playbook.md` instead. For content + commerce together (e.g., blog posts that link to a product), audit each section with its own intent.

## The rule that changes everything

Informative content wins on **E-E-A-T** (experience, expertise, authoritativeness, trust). Transaction content wins on **E-E-T-T** — experience, expertise, **trust signals**, and **transactional proof**.

The shift: you're no longer asking "is this writer credible?" — you're asking "is this business legitimate enough to take my money or my email?"

## Table of contents

1. [What Google treats as a money page (YMYL + commercial intent)](#1-what-google-treats-as-a-money-page)
2. [E-E-T-T signals](#2-e-e-t-t-signals)
3. [Structured data for commercial pages](#3-structured-data-for-commercial-pages)
4. [On-page patterns that convert AND rank](#4-on-page-patterns)
5. [Pricing page specifics](#5-pricing-page)
6. [FAQ on money pages — AEO-first design](#6-faq-on-money-pages)
7. [Trust-signal placement (SEO-visible vs JS-only)](#7-trust-signals)
8. [CTA-SEO interplay](#8-cta-seo)
9. [Internal linking for commercial pages](#9-internal-linking)
10. [Audit checklist](#10-audit-checklist)

---

## 1. What Google treats as a money page

Google's guidelines have a concept of YMYL ("Your Money, Your Life") — pages that can affect financial, health, legal, or safety outcomes. These get extra quality scrutiny.

Money pages are a broader category: ANY page where the user might spend money, give an email for outreach, or commit to a service. Google scrutinises these more than informative content:

- Pricing / plans
- Buy / purchase / checkout
- Product detail (commercial)
- Service detail (e.g., "web design Bangalore")
- "Contact us for quote" / lead capture
- Sign up / create account / start trial
- Comparison ("Us vs competitor")
- Location-specific commercial ("Broadband Whitefield")

These pages must pass stricter quality thresholds to rank.

## 2. E-E-T-T signals

Transaction content needs to answer four questions for a user-to-be-converted AND for a ranking algorithm evaluating the page:

### Experience (same as informative, but commercial)
"Has this business actually done this kind of work?"
- Case studies with named clients.
- Before/after metrics from actual projects.
- Years in business + volume delivered.

### Expertise
"Does the team have the qualifications to do this?"
- Team bios with credentials + LinkedIn links.
- Certifications (Google Partner, Meta Business Partner, industry-specific certs).
- Awards.

### Trust
"Is this a real business that will follow through?"
- Physical address visible in footer (real address, not a P.O. box for regulated industries).
- Phone number (visible + `tel:` link).
- Email.
- Registration / licensing / regulatory info as applicable.
- SSL certificate valid + HTTPS enforced.
- Privacy policy + terms of service linked from footer.
- Return / refund policy for e-commerce.
- GST / business registration for India (or equivalent).

### Transactional proof
"Have other customers bought from this business and been OK?"
- Real, verifiable customer reviews (Google Business Profile, Trustpilot, G2, Capterra, industry-specific).
- Star ratings visible + matching schema.
- Customer logos (with permission — don't use logos without consent).
- Testimonial quotes with name + company + photo (photo matters).
- Case studies with outcomes.

## 3. Structured data for commercial pages

### Minimum viable schema stack

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "LocalBusiness",
      "@id": "https://example.com/#localbusiness",
      "name": "...",
      "image": "https://example.com/logo.jpg",
      "url": "https://example.com",
      "telephone": "+91-...",
      "email": "sales@example.com",
      "address": {
        "@type": "PostalAddress",
        "streetAddress": "...",
        "addressLocality": "Whitefield",
        "addressRegion": "Karnataka",
        "postalCode": "560066",
        "addressCountry": "IN"
      },
      "geo": {
        "@type": "GeoCoordinates",
        "latitude": 12.9698,
        "longitude": 77.75
      },
      "openingHoursSpecification": [{
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],
        "opens": "09:00",
        "closes": "20:00"
      }],
      "priceRange": "₹₹",
      "aggregateRating": {
        "@type": "AggregateRating",
        "ratingValue": "4.8",
        "reviewCount": "127"
      },
      "sameAs": [
        "https://www.linkedin.com/company/...",
        "https://www.google.com/maps/place/...",
        "https://g.co/..."
      ]
    },
    {
      "@type": "Service",
      "@id": "https://example.com/service/#service",
      "name": "Enterprise Fibre Broadband",
      "serviceType": "Internet service",
      "provider": { "@id": "https://example.com/#localbusiness" },
      "areaServed": [...],
      "offers": {
        "@type": "Offer",
        "priceCurrency": "INR",
        "priceSpecification": {
          "@type": "UnitPriceSpecification",
          "priceCurrency": "INR",
          "price": "1999",
          "unitText": "MONTH"
        }
      }
    },
    {
      "@type": "FAQPage",
      "mainEntity": [ /* FAQ items — see §6 */ ]
    },
    {
      "@type": "BreadcrumbList",
      "itemListElement": [ /* ... */ ]
    }
  ]
}
```

### What EACH of these does

- **LocalBusiness** (or `Organization` if not local) — identity. Lets Google place you on the map + understand who the business is.
- **Service** or **Product** — what you sell. Enables rich results for pricing / availability.
- **aggregateRating** — star ratings in SERPs. ONLY if ratings are real + verifiable. Fake ratings = manual action.
- **FAQPage** — covers questions users have BEFORE converting. See §6.
- **BreadcrumbList** — path from homepage → category → this page. Helps Google understand site structure.
- **Review** (individual reviews) — schema for each visible customer review. Ties into aggregateRating.

### Product vs Service vs LocalBusiness — which applies?

- **Product** — physical or digital goods sold. Has SKU, price, availability.
- **Service** — work provided to customers. Has provider, areaServed, maybe offers.
- **LocalBusiness** — a physical or service-area business. Often combined with Product or Service for subpages.

For a site like "Enterprise Broadband Whitefield":
- Homepage → `LocalBusiness` + `Organization`
- `/whitefield` → `LocalBusiness` scoped to that location
- `/enterprise-plans` → `Service` with `offers`
- `/compare-plans` → comparison page, no schema required

## 4. On-page patterns that convert AND rank

Commercial content should follow a specific sequence above the fold:

```
┌─────────────────────────────────────────────────┐
│ <h1> — What you do + who it's for + location │
│ (fibre broadband for Whitefield businesses) │
├─────────────────────────────────────────────────┤
│ One-sentence value prop → the promise │
│ (4-hour fault response, 5-day install) │
├─────────────────────────────────────────────────┤
│ Primary CTA (high-contrast, explicit action) │
│ [Get a quote] or [Check coverage] │
├─────────────────────────────────────────────────┤
│ Trust indicators (logos, star rating, # customers) │
│ As seen in • 200+ active customers • 4.8 ★ │
└─────────────────────────────────────────────────┘
```

Everything below the fold: detailed value prop, social proof (reviews/case studies), features, pricing, FAQ, secondary CTA.

### Rules for the above-the-fold block

- **`<h1>` is specific + unique per page.** "Fibre broadband" ❌ → "Fibre broadband for Whitefield businesses" ✅
- **Value prop uses numbers, not adjectives.** "Fast" ❌ → "200 Mbps symmetric, 4-hour fault response" ✅
- **Primary CTA copy is the user's next action, not generic.** "Submit" ❌ → "Check coverage at my address" ✅
- **Trust indicators are real.** "Trusted by industry leaders" ❌ → "4.8 ★ on Google, 127 reviews" ✅ (if true)

### The commercial-page content skeleton (good for SEO + conversion)

1. **Hero** — h1 + value prop + CTA (above)
2. **Social proof row** — logos or rating or customer count
3. **Problem statement** — "Most Whitefield ISPs have 2–3 day installation delays..."
4. **Solution** — "We install in 5 days guaranteed, or the first month is free"
5. **Features / differentiators** — specific, numbered, not generic
6. **Pricing or "How it works"** — transparent
7. **Social proof deep** — 2–3 detailed customer quotes + named company
8. **FAQ** — 5–8 questions users actually have. Answer first, supporting paragraph second. Marked up as FAQPage schema.
9. **Secondary CTA** — repeat the primary ask with different copy ("Get started in 5 days")
10. **Footer trust** — address, phone, email, registration

Each section is a semantic `<section>` with a `<h2>`. Headings help both SEO and skimmers.

## 5. Pricing page

Pricing pages are high-intent money pages. Google and LLMs both use them as primary evidence for commercial queries ("how much does X cost").

### Must-haves

- **Explicit prices** (not "contact us for pricing"). Pages without visible prices miss the high-intent queries entirely. "Contact us for pricing" is an acceptable CTA ON a pricing page, but the page must show *something* numerical ("plans from ₹1,999/month").
- **Structured `PriceSpecification` in schema.** Enables rich result eligibility.
- **Currency + unit clear.** "₹1,999/month" — not just "1,999".
- **Comparison table.** Google rewards structured comparison tables with featured-snippet placement for "X vs Y pricing" queries. Use semantic `<table>`.
- **FAQs addressing pricing objections.** "Is there a setup fee?" "Can I cancel anytime?" "What's included?" These answer the unspoken objections that kill conversion.

### Avoid

- **Price hidden behind JS.** If the pricing table is rendered client-side only, crawlers and LLMs see "contact us" instead of the numbers.
- **Price images.** Prices as `<img>` screenshots defeat schema and hide from crawlers.
- **Dark patterns.** Hidden fees, confusing pricing tiers, dishonest "from" prices (where the actual tier is much higher) trigger Google's spam systems.

## 6. FAQ on money pages — AEO-first design

FAQ sections on money pages are uniquely valuable. They:
1. Answer objections that silently kill conversion.
2. Feed Google AI Overviews for commercial queries.
3. Give LLMs structured Q/A to cite.
4. Get indexed as `FAQPage` schema (rich result eligibility — though Google narrowed this in 2023).

### Money-page FAQ pattern

Each question should be phrased as a user would ask it + answer first + supporting context after.

**Example (bad):**
> **Setup & Installation:** Our standard installation takes 5 business days from order. A certified technician will visit your premises with all necessary equipment. After installation, we do a complete line test and network handover.

**Example (good):**
> **How long does installation take?** Five business days from order — we install at your premises with a certified technician, then run a full line test and hand over. Faster options available for time-critical deployments.

The good version answers the question in the first 10 words. Extractors can lift the answer cleanly.

### Question categories for money pages

- **Pricing** — "Is there a setup fee? What's the minimum contract?"
- **Delivery** — "How long does installation take? How do I get started?"
- **Features** — "Do you offer X? Is Y included?"
- **Comparison** — "How is this different from [competitor]?"
- **Trust** — "Do you serve [location]? How many customers do you have?"
- **Support** — "What if I have problems? Can I cancel?"
- **Refund / cancellation** — these are trust signals, not just objections.

5–8 FAQ questions is the sweet spot. More than 12 starts to feel padded.

### FAQPage schema with visibility

```json
{
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "How long does installation take?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Five business days from order — we install at your premises with a certified technician, then run a full line test and hand over."
      }
    }
  ]
}
```

Every Q/A in schema MUST appear visibly on the page (Google guideline). Hiding schema Q/A while showing different text to users = manual-action trigger.

## 7. Trust signals — SEO-visible vs JS-only

Trust signals lose half their SEO value when loaded only client-side.

### Render trust signals in the initial HTML

- ✅ Customer logo row with `<img alt="Customer logo: Beta Consulting">` directly in the SSR response.
- ❌ `<div id="logo-slider">` that hydrates a Swiper carousel after JS loads — empty to crawlers.

### Same applies to:

- Star ratings (render the text "4.8 out of 5 (127 reviews)" server-side, even if the star visuals are CSS).
- Testimonial quotes.
- Award badges.
- "As seen in" publisher logos.
- Customer counts ("200+ businesses served").

### Schema + visible content must match

`aggregateRating.ratingValue: 4.8` in schema → visible "4.8 stars" on page.
`aggregateRating.reviewCount: 127` in schema → visible "127 reviews" on page.

If schema says 4.8 and page shows 4.5, Google flags.

## 8. CTA-SEO interplay

CTAs and SEO don't usually interact, with one exception: **CTA anchor text**.

The clickable text on your primary CTA is crawlable. It signals the page's transactional intent to Google.

### Good CTA anchor text
- "Check coverage at my address"
- "Book a 30-minute demo"
- "Start my free trial"
- "Get a quote for my team"

### Weak CTA anchor text (doesn't help SEO)
- "Submit"
- "Click here"
- "Learn more" (this can be OK on educational CTAs, not commercial)
- "→" (arrow-only)

### On CTAs: ONE primary per viewport

Multiple competing CTAs reduce conversion AND confuse search intent. Each screen should have one clear primary action + secondary options below.

## 9. Internal linking for commercial pages

Money pages need link equity flowing INTO them from informative content + from the homepage.

### Good patterns

- Homepage links to primary category hubs (`/enterprise`, `/home-broadband`) with descriptive anchor text.
- Each category hub links to individual product/service pages AND to relevant blog posts.
- Blog posts link back to relevant money pages ("Related guide: Enterprise Broadband Plans").
- Breadcrumb navigation visible + schema-marked.

### Bad patterns

- Deep money pages linked only from the footer sitemap.
- Blog posts with no links back to relevant commercial pages (all link equity stays in /blog/).
- All internal links use generic anchor text ("click here" for 20 different destinations).

## 10. Audit checklist

Transaction-intent-specific checks. Run in addition to the regular SEO/AEO/GEO checklists.

- **TX-1** `<h1>` is specific + commercial — includes what + who + where (if local).
- **TX-2** Primary CTA is above the fold with descriptive anchor text (not "Submit" / "Click here").
- **TX-3** At least 3 trust signals above the fold (logos / rating / customer count / address).
- **TX-4** All trust signals render in server-side HTML, not only after JS hydration.
- **TX-5** Visible prices on pricing pages (not only "contact us"). At minimum a "from ₹X" + clear tier structure.
- **TX-6** `LocalBusiness` or `Organization` schema present with full address + phone + sameAs.
- **TX-7** `Service` or `Product` schema with `offers` (price + currency + availability).
- **TX-8** `aggregateRating` in schema ONLY if verifiable ratings exist. Values match what's visible on page.
- **TX-9** `FAQPage` schema present on pricing / product detail pages. Every Q/A matches visible text.
- **TX-10** Semantic `<table>` used for pricing comparisons (not div-based).
- **TX-11** Address, phone, email visible in footer as text + `tel:` / `mailto:` links.
- **TX-12** Privacy policy + Terms of Service + Refund Policy (if e-commerce) linked from footer.
- **TX-13** SSL valid; no mixed-content warnings; HSTS header set.
- **TX-14** Customer testimonials include name + company + photo (real testimonials, not stock).
- **TX-15** Customer logos displayed have permission or are licensed for display.
- **TX-16** Breadcrumb navigation visible on the page AND marked up with `BreadcrumbList` schema.
- **TX-17** Commercial content has clear internal links from informative content (blog posts).
- **TX-18** CTA anchor text is descriptive + specific — not "Submit" / "Click here".
- **TX-19** For location-specific money pages, `addressLocality` + `geo` coordinates in schema match the targeted city.
- **TX-20** "Return / Refund Policy" link visible on product/checkout pages.

---

## Severity guidance

- Missing LocalBusiness/Organization schema on a money page → **High**
- No visible pricing on pricing page → **High**
- `aggregateRating` in schema without verifiable source → **Critical** (manual-action trigger)
- Trust signals only in client-rendered JS → **High**
- No FAQ on pricing / product detail → **Medium**
- Generic CTA anchor text ("Submit") → **Medium**
- No breadcrumbs on deep commercial pages → **Medium**
- Missing phone/address on contact page → **Medium**
- Customer testimonials without attribution (name/company) → **Low** (looks fake even if real)
