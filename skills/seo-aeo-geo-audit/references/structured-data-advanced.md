# Advanced Structured Data Reference

Use when an audit goes beyond basic `<meta>` tags into entity-level structured data. Goal: make content machine-readable for search engines AND LLMs, using `@graph` so entities connect across pages and subdomains.

Google recommends JSON-LD; Microdata and RDFa are equally acceptable if valid. JSON-LD is decoupled from HTML, renders cleanly from Server Components and supports `@graph`. Google states that no special structured data is needed to appear in its AI features (see `google-guidance-alignment.md`); structured data is for rich results and entity clarity.

## Table of contents

1. [The `@graph` pattern](#1-the-graph-pattern)
2. [`@id` cross-references](#2-id-cross-references)
3. [Per-page-type schema recipes](#3-per-page-type-recipes)
4. [Google-specific requirements](#4-google-required-properties)
5. [Validation & common mistakes](#5-validation--common-mistakes)
6. [How structured data helps LLM citation](#6-how-structured-data-helps-llm-citation)

---

## 1. The `@graph` pattern

Put multiple related entities in a single `@graph` array instead of one object per page.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://example.com/#organization",
      "name": "your brand",
      "url": "https://example.com",
      "logo": "https://example.com/logo.png",
      "sameAs": [
        "https://www.linkedin.com/company/example",
        "https://twitter.com/example",
        "https://www.wikidata.org/wiki/Q12345"
      ]
    },
    {
      "@type": "WebSite",
      "@id": "https://example.com/#website",
      "url": "https://example.com",
      "name": "Example",
      "publisher": { "@id": "https://example.com/#organization" },
      "potentialAction": {
        "@type": "SearchAction",
        "target": "https://example.com/search?q={search_term_string}",
        "query-input": "required name=search_term_string"
      }
    },
    {
      "@type": "Article",
      "@id": "https://example.com/blog/post-slug/#article",
      "headline": "Post title",
      "datePublished": "2026-04-01",
      "dateModified": "2026-04-18",
      "author": { "@id": "https://example.com/authors/jane/#person" },
      "publisher": { "@id": "https://example.com/#organization" },
      "isPartOf": { "@id": "https://example.com/#website" },
      "mainEntityOfPage": "https://example.com/blog/post-slug/"
    },
    {
      "@type": "Person",
      "@id": "https://example.com/authors/jane/#person",
      "name": "Jane Doe",
      "jobTitle": "Senior Editor",
      "worksFor": { "@id": "https://example.com/#organization" },
      "url": "https://example.com/authors/jane/",
      "sameAs": [
        "https://www.linkedin.com/in/janedoe",
        "https://twitter.com/janedoe"
      ]
    }
  ]
}
</script>
```

Search engines and LLMs parse the relationships (Article → Author → Organization) in one read.

## 2. `@id` cross-references

Every entity referenced from another page should have an absolute `@id`. Convention: `<canonical-url>#<entity-type>`.

- Organization: `https://example.com/#organization`
- WebSite: `https://example.com/#website`
- Authors: `https://example.com/authors/<slug>/#person`
- Articles: `https://example.com/blog/<slug>/#article`
- Products: `https://example.com/products/<slug>/#product`

### Cross-subdomain / cross-domain pattern

Declare the Organization ONCE with its canonical `@id` (usually on the main domain). Every other property references it:

```json
{ "@type": "Article", "publisher": { "@id": "https://main.example.com/#organization" } }
```

This is the difference between five unrelated subdomains and one coherent entity.

### `sameAs` priority order

1. Wikipedia article
2. Wikidata entry
3. Crunchbase profile
4. Official LinkedIn company page
5. Official X/Twitter
6. GitHub organization (for tech)
7. Bloomberg, Forbes, industry-specific registries

Curate to authoritative sources; avoid listing every social profile.

## 3. Per-page-type schema recipes

### 3.1 Homepage — Organization + WebSite

`WebSite` with `name`, optional `alternateName` and `url` on the home page drives Google site names (one name per domain or subdomain). Google reads these `Organization` properties: `name`, `logo` (at least 112x112 px), `sameAs`, `address`, `contactPoint`, `legalName`. **The Sitelinks Search Box was removed from Google Search, so `SearchAction` no longer produces a Google feature.** It is harmless to keep for on-site search consumers; do not flag its absence.

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://example.com/#organization",
      "name": "your brand",
      "alternateName": "Example",
      "url": "https://example.com",
      "logo": { "@type": "ImageObject", "url": "...", "width": 512, "height": 512 },
      "description": "...",
      "foundingDate": "2018-01-01",
      "sameAs": [ "..." ],
      "contactPoint": {
        "@type": "ContactPoint",
        "contactType": "customer support",
        "email": "support@example.com",
        "areaServed": "IN"
      }
    },
    {
      "@type": "WebSite",
      "@id": "https://example.com/#website",
      "url": "https://example.com",
      "name": "Example",
      "publisher": { "@id": "https://example.com/#organization" },
      "potentialAction": {
        "@type": "SearchAction",
        "target": "https://example.com/search?q={search_term_string}",
        "query-input": "required name=search_term_string"
      }
    }
  ]
}
```

### 3.2 Article / Blog post

```json
{
  "@type": "Article",
  "headline": "Concise title (Google sets no required length)",
  "description": "155-char summary.",
  "image": [ "https://example.com/hero-1200x630.jpg" ],
  "datePublished": "2026-04-01T09:00:00+05:30",
  "dateModified": "2026-04-18T14:00:00+05:30",
  "author": { "@type": "Person", "@id": "...", "name": "..." },
  "publisher": { "@id": "https://example.com/#organization" },
  "mainEntityOfPage": "https://example.com/blog/slug/"
}
```

Google lists no required properties for Article. Recommended: `author` (with `name` and `url`), `datePublished`, `dateModified`, `headline`, `image` (16:9, 4:3 and 1:1 versions, at least 50K pixels each). Use ISO 8601 dates with a timezone. `speakable` is beta (US, English, Google Assistant news) and is intentionally left out of the default recipe.

### 3.3 JobPosting

For programmatic job boards see `pseo-jobs-playbook.md`.

```json
{
  "@type": "JobPosting",
  "title": "Senior React Developer",
  "description": "<p>Full HTML description...</p>",
  "datePosted": "2026-04-15",
  "validThrough": "2026-06-15T23:59:00+05:30",
  "employmentType": ["FULL_TIME"],
  "hiringOrganization": {
    "@type": "Organization",
    "name": "your brand",
    "sameAs": "https://example.com",
    "logo": "https://example.com/logo.png"
  },
  "jobLocation": {
    "@type": "Place",
    "address": {
      "@type": "PostalAddress",
      "addressLocality": "Bengaluru",
      "addressCountry": "IN"
    }
  },
  "baseSalary": {
    "@type": "MonetaryAmount",
    "currency": "INR",
    "value": { "@type": "QuantitativeValue", "minValue": 1500000, "maxValue": 2500000, "unitText": "YEAR" }
  },
  "directApply": true
}
```

Required: `title`, `description`, `datePosted`, `hiringOrganization`, and either `jobLocation` or `applicantLocationRequirements`.

### 3.4 Course (LearningResource)

```json
{
  "@type": "Course",
  "name": "JEE Advanced Physics",
  "description": "16-week course covering JEE Advanced Physics syllabus.",
  "provider": { "@id": "https://example.com/#organization" },
  "hasCourseInstance": [{
    "@type": "CourseInstance",
    "courseMode": "online",
    "startDate": "2026-06-01",
    "endDate": "2026-09-21",
    "instructor": { "@type": "Person", "name": "Dr Priya Iyer" }
  }],
  "offers": { "@type": "Offer", "price": "15000", "priceCurrency": "INR" }
}
```

Required: `name`, `description`, `provider`, `hasCourseInstance` with `courseMode` and `startDate`.

### 3.5 Product

```json
{
  "@type": "Product",
  "name": "Product name",
  "image": [ "..." ],
  "description": "...",
  "sku": "ABC-123",
  "brand": { "@type": "Brand", "name": "Example" },
  "offers": {
    "@type": "Offer",
    "url": "https://example.com/product/abc-123",
    "priceCurrency": "INR",
    "price": "1499.00",
    "availability": "https://schema.org/InStock"
  }
}
```

### 3.6 FAQPage — no longer a Google rich result (optional)

Every Q/A in schema must also appear visibly on the page.

```json
{
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is X?",
      "acceptedAnswer": { "@type": "Answer", "text": "X is Y. Matches visible page text." }
    }
  ]
}
```

Google stopped showing FAQ rich results (deprecation notice May 2026, documentation removed June 2026; since Aug 2023 they were limited to government and health sites). `FAQPage` is still valid schema.org markup, but it earns no Google rich result and Google says special markup is not needed for its AI features. Keep it only when it mirrors visible Q&A. Do not recommend it as a Google visibility fix, and report its absence at most as `Info`.

### 3.7 HowTo — rich result retired (optional)

Google removed the HowTo rich result (documentation removed Sep 2023). Valid schema.org markup, no Google feature. Every step must appear on the page. Absence is `Info`.

```json
{
  "@type": "HowTo",
  "name": "How to set up X",
  "step": [
    {
      "@type": "HowToStep",
      "name": "Step 1",
      "text": "Full step description visible on the page.",
      "url": "https://example.com/how-to#step-1"
    }
  ]
}
```

### 3.8 BreadcrumbList

On every non-homepage page.

```json
{
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://example.com" },
    { "@type": "ListItem", "position": 2, "name": "Blog", "item": "https://example.com/blog" },
    { "@type": "ListItem", "position": 3, "name": "Post title" }
  ]
}
```

Final item (current page) omits `item`.

### 3.9 VideoObject

```json
{
  "@type": "VideoObject",
  "name": "Video title",
  "description": "Description ≥ 160 chars.",
  "thumbnailUrl": [ "..." ],
  "uploadDate": "2026-04-01T09:00:00+05:30",
  "duration": "PT3M45S",
  "contentUrl": "...",
  "embedUrl": "..."
}
```

## 4. Google-required properties

| Type | Google-required |
|---|---|
| Article | none required. Recommended: `author`, `datePublished`, `dateModified`, `headline`, `image` |
| JobPosting | `title`, `description`, `datePosted`, `hiringOrganization`, `jobLocation` (Indexing API recommended) |
| Product snippet | `name` + one of `review`, `aggregateRating`, `offers` |
| Merchant listing | `name`, `image`, `offers` with `price` (above zero) + `priceCurrency` |
| Course | `name`, `description` (English only; `provider` recommended) |
| Event | `name`, `startDate`, `location` with `address` (physical, public events) |
| Recipe | `name`, `image` (`recipeIngredient`, `recipeInstructions` recommended) |
| LocalBusiness | `name`, `address` (others recommended) |
| Organization | none required (see 3.1 for the properties Google reads) |
| VideoObject | `name`, `thumbnailUrl`, `uploadDate` (`description` recommended) |
| HowTo | retired: no Google rich result |
| FAQPage | retired: no Google rich result |

Requirements change; confirm the feature page before quoting (see `google-guidance-alignment.md` section 8).

Validate with https://search.google.com/test/rich-results before shipping.

## 5. Validation & common mistakes

- **Relative URLs** in `@id`, `sameAs`, `image` — must be absolute (`https://...`).
- **Dates without timezone** — use ISO 8601: `2026-04-18T14:00:00+05:30`.
- **`@graph` entries without `@id`** — entity is page-local, can't be referenced.
- **Duplicate schema types for the same entity** — consolidate.
- **Schema doesn't match visible content** — manual-action trigger.
- **`dateModified` bumped on every build** — only update on real content changes.
- **Author as string instead of Person object** — lose entity-graph benefits.
- **`offers.price` as `"₹1,499"`** — wrong. Use `"price": "1499", "priceCurrency": "INR"`.
- **Missing `inLanguage` on multilingual sites**.

## 6. How structured data helps LLM citation

Possible effects. Google does not document these for its own AI features, so treat them as hypotheses to test, not guarantees:

1. **Entity disambiguation** — `sameAs` to Wikipedia/Wikidata tells LLMs this is a known entity. More confident citations.
2. **Authorship clarity** — typed `Person` with `sameAs` lets LLMs cite "according to Jane Doe of your brand".
3. **Freshness signals** — `dateModified` helps retrieval filter for recent sources.
4. **Content structure** — Q&A and step blocks give retrieval chunks clean boundaries in non-Google retrieval systems. Google says no "chunking" is needed for its AI features.
5. **Trust scoring** — consistent, valid, connected schema weighted more heavily in retrieval.

---

## Severity guidance

- Missing Organization/WebSite on homepage → High
- Missing schema on Google-rich-result-eligible page (Article, JobPosting, Course, Product) → High
- Invalid required field → High or Critical
- Missing optional property that improves LLM entity linking (`sameAs`) → Medium
- Wrong format (relative URL, missing timezone) → Medium
