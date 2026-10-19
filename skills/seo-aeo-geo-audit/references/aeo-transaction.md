# AEO Audit — Transaction Intent Content

Answer Engine Optimization checks specific to **transaction-intent pages** — landing pages, pricing, service detail, product detail, sign-up, comparison.

For informative / editorial content (blog posts, guides, how-to articles), use `aeo.md` instead. For the full commercial playbook (trust signals, E-E-T-T, structured data stack for money pages), read `transaction-intent-playbook.md` first — this file is the AEO-specific subset.

## Why transaction-intent AEO is different

Generic AEO (blogs, articles) optimizes for **definitional and how-to** extraction. Answer engines quote a paragraph that defines or explains.

Transaction-intent AEO optimizes for **commercial decision extraction**. Answer engines quote:
- Pricing answers ("How much does X cost?")
- Comparison answers ("X vs Y, which is better?")
- Availability answers ("Do you serve Y?")
- Qualification answers ("Is X free? Is there a trial?")
- Feature-match answers ("Does X include Y?")

The content structure is different. The schema is different. And Google's Shopping Graph integration matters in addition to organic AIO.

## Table of contents

1. [Commercial query types AIO answers](#1-commercial-query-types)
2. [Pricing pages — AEO-first design](#2-pricing-pages)
3. [Comparison pages — AEO-first design](#3-comparison-pages)
4. [Service area pages — AEO for location queries](#4-service-area-pages)
5. [FAQ schema on money pages](#5-faq-schema-on-money-pages)
6. [Product schema for AIO Shopping](#6-product-schema-for-aio-shopping)
7. [Review + aggregateRating signals](#7-review--aggregaterating)
8. [E-E-T-T signals AIO weighs on commercial pages](#8-e-e-t-t-signals)
9. [Audit checklist](#9-audit-checklist)

---

## 1. Commercial query types AIO answers

| Query pattern | AIO surface format | What your page needs |
|---|---|---|
| "How much does X cost" | Price snippet with source cards | Visible pricing + `Product` or `Service` schema with `offers.price` |
| "Is X free" | Direct yes/no + explanation | H2 "Is X free?" + first-sentence yes/no answer |
| "X vs Y" | Side-by-side comparison box | Semantic `<table>` with 3-5 comparison attributes |
| "Best X for Y" | Ranked list with source cards | H2 "Best X for Y" + `<ol>` of named options with short descriptions |
| "X near me" | Local Pack + map + AIO summary | `LocalBusiness` schema + Google Business Profile claimed + `areaServed` specified |
| "Does X include Y" | Direct yes/no from feature list | Features listed in semantic `<ul>` OR `Product.hasFeature` in schema |
| "X alternatives" | Ranked list of competitors | H2 "Alternatives to X" + explicit named alternatives list |
| "How do I cancel X" | How-to from your help docs | `HowTo` schema on the cancellation guide |

Note: AIO surfaces commercial answers more cautiously than informative ones — but when it does, the clicks it drives have very high buying intent.

## 2. Pricing pages — AEO-first design

### Structure for AEO

```html
<h1>[Service/product] pricing</h1>
<p>One-sentence positioning — "Plans from ₹1,999/month for businesses in [City]."</p>

<h2>How much does [service] cost?</h2>
<p>Direct answer: "Plans start at ₹1,999/month for the Starter tier, ₹4,999 for Pro, and custom pricing for Enterprise. All plans include 24/7 support."</p>

<h2>What's included in each plan?</h2>
<!-- semantic table -->
<table>
  <caption>Plan comparison</caption>
  <thead>
    <tr><th>Feature</th><th>Starter</th><th>Pro</th><th>Enterprise</th></tr>
  </thead>
  <tbody>
    <tr><td>Speed</td><td>100 Mbps</td><td>300 Mbps</td><td>1 Gbps</td></tr>
    <!-- etc. -->
  </tbody>
</table>

<h2>Is there a setup fee?</h2>
<p>No. Setup is included in all plans. Hardware installation is free; we retain ownership of the router.</p>

<h2>Can I cancel anytime?</h2>
<p>Yes. All plans are month-to-month with no lock-in after the first 30 days.</p>

<h2>Do you serve [location]?</h2>
<p>Yes. We cover Whitefield (560066), Brookefield (560037), ITPL (560048), Mahadevapura (560016), and nearby areas in East Bangalore.</p>
```

The pattern: **commercial question as H2 → direct answer in first sentence → supporting context after.**

Extractors lift the first-sentence answer. Users skim the H2s.

## 3. Comparison pages — AEO-first design

Comparison pages ("Us vs Competitor", "X vs Y vs Z") are high-CTR AIO candidates. Google surfaces comparison tables directly in AIO.

### Rules

- Use semantic `<table>` with `<thead>`, `<tbody>`, `<caption>`.
- Compare 3-5 specific attributes (features, price, speed, support, location, etc.).
- Be specific and honest — "Starter plan at ₹1,999" not "affordable pricing".
- Include a winner summary above the table: "For most small teams, X offers the best balance of price and speed. Y is better if you need enterprise SLA guarantees."

### Schema

Comparison pages don't have a dedicated schema type, but you can use:
- `Article` with `about: [array of competitors]` for editorial comparisons
- `ItemList` wrapping the ranked alternatives
- `FAQPage` for "which is better for X?" questions

## 4. Service area pages — AEO for location queries

For "does X serve [location]" queries, AIO needs:

- `LocalBusiness` schema with `areaServed` specific to the location.
- H2 "Do you serve [location]?" with direct yes/no answer.
- Coverage list on the page (pincodes, neighbourhoods) rendered server-side.
- Consistent NAP (Name, Address, Phone) across sub-pages.

For multi-city operators, create a hub per city (see `pseo-playbook.md` §F Location Hubs) OR a single page with explicit coverage list. Don't leave it as "contact us for coverage" — that doesn't extract.

## 5. FAQ schema on money pages

FAQPage schema on pricing / service pages is particularly valuable for AEO despite Google's 2023 restriction of FAQ rich results for most sites. Even without rich-result eligibility:

- Answer engines STILL extract from FAQPage schema for AIO and other LLMs.
- Organic CTR on commercial pages benefits when questions match user intent.
- Converts browsers to buyers by addressing objections upfront.

### Commercial FAQ design

Every FAQ on a money page should:
1. Phrase the question as a buyer would ask it ("Is there a setup fee?" not "About setup charges").
2. Answer YES/NO/A SPECIFIC NUMBER in the first 10 words.
3. Match the visible page (Google guideline — every Q/A in schema must appear visibly).

### Example

```json
{
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Is there a setup fee for Enterprise Fibre?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "No setup fee for standard installations. Custom deployments (e.g., multiple buildings) may incur a site-survey fee quoted upfront."
      }
    },
    {
      "@type": "Question",
      "name": "Can I cancel anytime?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes, all plans are month-to-month after the first 30 days. No termination fee."
      }
    }
  ]
}
```

## 6. Product schema for AIO Shopping

For e-commerce pages, Google's Shopping Graph surfaces products directly in AIO for "buy X" / "best X for Y" queries.

### Required fields for shopping rich result

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Widget 3000",
  "image": ["https://.../widget-1200x1200.webp"],
  "description": "...",
  "sku": "W3000-BLK",
  "gtin13": "1234567890123",
  "brand": { "@type": "Brand", "name": "Example" },
  "aggregateRating": { /* only if verifiable */ },
  "review": [ /* individual reviews */ ],
  "offers": {
    "@type": "Offer",
    "url": "https://example.com/product/widget-3000",
    "priceCurrency": "INR",
    "price": "4999",
    "priceValidUntil": "2026-12-31",
    "availability": "https://schema.org/InStock",
    "itemCondition": "https://schema.org/NewCondition",
    "shippingDetails": {
      "@type": "OfferShippingDetails",
      "shippingRate": { "@type": "MonetaryAmount", "value": "0", "currency": "INR" },
      "shippingDestination": { "@type": "DefinedRegion", "addressCountry": "IN" }
    },
    "hasMerchantReturnPolicy": {
      "@type": "MerchantReturnPolicy",
      "returnPolicyCategory": "https://schema.org/MerchantReturnFiniteReturnWindow",
      "merchantReturnDays": 7
    }
  }
}
```

Note: Google's rich results for ecommerce REQUIRE `shippingDetails` + `hasMerchantReturnPolicy` since 2023. Missing these = no rich result.

## 7. Review + aggregateRating signals

Critical rules:

- **Real reviews only.** Fabricated reviews or schema-only ratings (no visible source) are a manual-action trigger.
- **Source must be visible.** If schema says `aggregateRating.ratingCount: 127`, the page must show "127 reviews" or similar.
- **Match schema to visible content.** If schema says 4.8 and page shows 4.5, Google flags.

### First-party reviews on your own page

```json
{
  "@type": "Review",
  "author": { "@type": "Person", "name": "Priya K." },
  "datePublished": "2026-03-15",
  "reviewRating": { "@type": "Rating", "ratingValue": "5" },
  "reviewBody": "Installation was fast and support has been prompt..."
}
```

### Third-party reviews
If reviews live on Google Business Profile, Trustpilot, G2, Capterra — don't duplicate them into your schema unless you have permission. Instead, link out to those profiles via `sameAs` in your Organization schema.

## 8. E-E-T-T signals AIO weighs on commercial pages

Google's AIO source selection for commercial queries weighs:

- **Trust** — valid SSL, visible address/phone, Terms/Privacy/Refund policies linked.
- **Experience** — years in business visible, volume / customer count.
- **Expertise** — credentials, certifications, partner logos.
- **Transactional proof** — real reviews, customer logos, case studies.

Low-E-E-T-T pages (e.g., affiliate / doorway pages) rarely appear in AIO source cards even if they rank in top 10 organic. AIO seems to apply a higher quality bar to commercial queries than to informational ones.

## 9. Audit checklist

- **TXA-1** Commercial query-intent headings phrased as user would ask (H2 "Is X free?", "How much does X cost?", "Do you serve Y?").
- **TXA-2** First sentence under each H2 gives the direct answer (yes/no/specific number).
- **TXA-3** Pricing visible on pricing pages. Not "Contact us" alone.
- **TXA-4** Comparison uses semantic `<table>` with `<caption>`.
- **TXA-5** FAQPage schema present with every Q/A matching visible page text.
- **TXA-6** `LocalBusiness` + `areaServed` schema on service-area pages.
- **TXA-7** `Product` schema with required shopping fields (price, availability, shipping, return policy) on ecommerce pages.
- **TXA-8** `aggregateRating` only if verifiable + matches visible page.
- **TXA-9** Customer logos / testimonials rendered in server-side HTML.
- **TXA-10** Trust footer visible: address, phone, SSL, policies.
- **TXA-11** For "best X for Y" content: `<ol>` of named options (not just paragraphs).
- **TXA-12** For "X vs Y": side-by-side comparison table with specific attributes.
- **TXA-13** For "near me" queries: Google Business Profile claimed + linked.

---

## Severity guidance

- Missing pricing on a pricing page → **High** (blocks commercial AIO)
- Comparison rendered as div-grid not `<table>` → **Medium**
- Commercial FAQ missing or not schema-marked → **Medium**
- `Product` schema without shipping + return fields → **High** (no rich result)
- `aggregateRating` without visible source on page → **Critical** (manual-action risk)
- Trust signals only in client-rendered JS → **High**
- No `areaServed` on service-area pages → **Medium**
