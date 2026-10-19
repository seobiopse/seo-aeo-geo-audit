# Wix / Webflow Architecture Profile

Site-level audit patterns for no-code / low-code builder platforms — Wix, Webflow, Framer, Squarespace, and similar hosted visual builders. Read whenever the audit target is built on a platform where the underlying code is controlled by the platform, not the client.

**Critical framing:** These platforms have hard constraints. Many best-practice SEO implementations are simply unavailable. The audit must distinguish between what CAN be fixed vs what is a **platform limitation** — and for platform limitations, flag them as strategic constraints rather than actionable findings.

## Table of contents

1. [When to read this](#1-when-to-read-this)
2. [Platform capabilities matrix](#2-capabilities-matrix)
3. [Wix — what you can and cannot control](#3-wix)
4. [Webflow — what you can and cannot control](#4-webflow)
5. [Schema injection on builder platforms](#5-schema-injection)
6. [Performance constraints on builder platforms](#6-performance)
7. [When to recommend migrating off a builder](#7-migration-signals)
8. [Common anti-patterns](#8-anti-patterns)
9. [Audit checklist](#9-audit-checklist)

---

## 1. When to read this

Load this file when:
- The site URL returns `X-Powered-By: Wix`, `x-wix-request-id`, or pages load with `wix-code` scripts.
- The site is hosted at `webflow.io` or uses Webflow's CMS (`wf-form`, `w-nav` classes, `webflow.js`).
- The source contains Squarespace's `Y-Runtime` header.
- The CMS is Framer (`framer.website` domain, `__framer__` in source).
- The site uses a visual builder and the client doesn't have access to raw HTML templates.

---

## 2. Capabilities matrix

Before auditing, set expectations. Many recommendations are not actionable on these platforms.

| SEO capability | Wix | Webflow | Framer | Squarespace |
|---|---|---|---|---|
| Custom canonical tags | ✅ | ✅ | ✅ | ✅ |
| Custom meta title / description | ✅ | ✅ | ✅ | ✅ |
| robots.txt editing | ✅ (Wix SEO) | ✅ (partial) | ⚠️ (limited) | ✅ (partial) |
| Sitemap control | ✅ auto-generated | ✅ auto-generated | ✅ auto-generated | ✅ auto-generated |
| Custom JSON-LD schema | ⚠️ (embed code) | ✅ (embed code) | ⚠️ (embed code) | ⚠️ (embed code) |
| hreflang tags | ✅ (Wix Multilingual) | ⚠️ (manual in `<head>`) | ⚠️ | ⚠️ |
| Custom URL structure | ⚠️ (no `/` changes) | ✅ | ✅ | ⚠️ |
| Server-side rendering | ✅ (Wix renders server-side) | ✅ | ⚠️ | ✅ |
| Custom `<head>` code | ✅ (Wix Head Code) | ✅ (Custom Code) | ✅ | ✅ (Code Injection) |
| Core Web Vitals control | ❌ platform-controlled | ⚠️ partial | ⚠️ partial | ❌ platform-controlled |
| Custom redirect rules | ✅ (URL redirect manager) | ✅ | ✅ | ✅ (301 redirects) |
| Custom 404 page | ✅ | ✅ | ✅ | ✅ |
| SSL/HTTPS | ✅ auto | ✅ auto | ✅ auto | ✅ auto |

---

## 3. Wix — what you can and cannot control

### What Wix handles automatically

- HTTPS certificate management.
- Mobile-responsive rendering (Wix renders server-side for crawlers).
- Automatic sitemap generation at `/sitemap.xml`.
- Basic structured data for blog posts and e-commerce products.
- robots.txt (editable via **SEO → Advanced SEO Settings → robots.txt**).

### What you control via Wix SEO tools

**Meta title and description:**
Every page has an SEO panel: **Settings → SEO (Google)** on each page. Set these explicitly — Wix defaults to the page title.

**Canonical tags:**
Wix auto-sets canonical to the page URL. If you have duplicate content (e.g., a product in multiple collections), you cannot manually override the canonical — this is a platform limitation.

**Custom head code:**
**Settings → Advanced Settings → Custom Code → Head** allows injecting `<script>`, `<meta>`, and `<link>` tags:

```html
<!-- Inject custom schema via Wix Head Code -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Example Business",
  ...
}
</script>
```

**URL structure:**
Wix prefixes URLs with section slugs (`/blog/post-title`, `/shop/product-name`). These prefixes cannot be removed.

### Wix platform limitations (flag, don't report as findings)

- Cannot change the `/blog/` or `/shop/` URL prefix.
- Cannot add `rel="prev"` / `rel="next"` for paginated content.
- Limited control over image naming (Wix CDN generates hashed filenames).
- Core Web Vitals heavily influenced by Wix's platform — third-party auditors can't fix platform JavaScript.

---

## 4. Webflow — what you can and cannot control

Webflow offers significantly more SEO control than Wix, especially on the Pro plan.

### Meta and canonical control

**Per-page SEO settings:** Settings panel → SEO tab on each page and CMS item. Supports title, description, and og:image.

**Canonical URL:**
Webflow automatically sets canonical. For CMS collections, canonical is set per item — you can reference CMS fields in the canonical: `https://example.com/products/[slug]`.

### Custom code injection

Webflow allows custom `<head>` and `<body>` code at three levels:

1. **Site-level** (Site Settings → Custom Code): loads on every page.
2. **Page-level** (Page Settings → Custom Code): loads on specific pages.
3. **CMS-level** (Collection Settings): can reference CMS fields in injected code.

CMS-level injection enables dynamic schema:

```html
<!-- In Collection Page Custom Code → Head -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "{{wf {"path":"name","type":"PlainText"} }}",
  "description": "{{wf {"path":"description","type":"PlainText"} }}",
  "offers": {
    "@type": "Offer",
    "price": "{{wf {"path":"price","type":"Number"} }}",
    "priceCurrency": "AUD"
  }
}
</script>
```

### Webflow sitemap

Auto-generated at `/sitemap.xml`. CMS items are included automatically. Exclude specific pages via **Page Settings → Search Engine Indexing → Exclude from sitemap**.

### robots.txt on Webflow

Editable at **Site Settings → SEO → robots.txt**. Add custom disallow rules, but cannot exceed Webflow's template format.

### Webflow platform limitations

- URL structure within CMS collections uses the collection slug: `/products/item-name`. The `/products/` prefix can be changed but not removed.
- Form submissions don't support `method="GET"` for filter/search (Webflow forms use POST), so faceted navigation isn't natively SEO-friendly.
- Webflow Interactions (animations) can cause CLS if not configured carefully.
- No server-side logic — all dynamic behaviour is JavaScript-based (except Webflow CMS rendering, which is server-side).

---

## 5. Schema injection on builder platforms

All builder platforms support schema injection via custom `<head>` code. The approach:

### Site-wide schema (Organization, WebSite)

Inject via site-level custom code. This loads on every page:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://example.com/#organization",
      "name": "Example Business",
      "url": "https://example.com",
      "logo": "https://example.com/logo.png",
      "sameAs": [
        "https://www.linkedin.com/company/example",
        "https://www.facebook.com/example"
      ]
    },
    {
      "@type": "WebSite",
      "@id": "https://example.com/#website",
      "url": "https://example.com",
      "name": "Example",
      "publisher": { "@id": "https://example.com/#organization" }
    }
  ]
}
</script>
```

### Page-specific schema

Inject via page-level custom code. For static pages (About, Services), hardcode the schema directly.

### CMS-dynamic schema (Webflow only)

Use Webflow's `{{wf}}` bindings to create dynamic schema per CMS item. This is the most powerful capability — avoid hardcoding schema that should vary per product/blog post.

### Verification

Always verify schema output with Rich Results Test after injecting:
1. Use the URL Test option for live pages.
2. Or paste the raw HTML if the page isn't live yet.

---

## 6. Performance constraints on builder platforms

Core Web Vitals on builder platforms are significantly harder to control than on custom-code sites. Be transparent about this in audit findings.

### What affects CWV on builders

| Factor | Wix | Webflow | Framer |
|---|---|---|---|
| Platform JavaScript | Fixed — cannot remove | Fixed — cannot remove | Fixed |
| Font loading | Can use system fonts | Can use Google Fonts with `display:swap` | Limited |
| Third-party scripts | Via custom code injection | Via custom code injection | Via custom code injection |
| Image format | Platform CDN auto-converts to WebP (Wix) | Webflow CDN — use built-in image optimizer | Auto-handled |
| LCP image preload | Cannot add `fetchpriority="high"` natively | Can inject via `<head>` custom code | Limited |

### Platform CWV benchmarks (2026)

- Wix: typical LCP 2.5–4s on mobile. Rarely achieves "Good" on CWV without significant image optimization.
- Webflow: typical LCP 1.8–3s on mobile. Achievable "Good" with careful image sizing and minimal third-party scripts.
- Squarespace: typically poor CWV scores due to platform-level JS overhead.

**Audit guidance:** Flag CWV issues on builder sites but clearly annotate which are **fixable** (image sizes, third-party scripts) vs **platform constraints** (bundle size, platform JS execution).

### Fixable on all builder platforms

- Image file sizes (ensure images are not uploaded at 4MB+ originals).
- Third-party scripts loading unnecessarily on all pages.
- Google Fonts — switch to `display=swap` parameter: `https://fonts.googleapis.com/css2?family=Poppins&display=swap`.
- Lazy-load off-screen images (available via HTML attributes in custom code).

---

## 7. Migration signals — when to recommend moving off a builder

Part of the audit is identifying when the platform is the constraint. These signals suggest a migration conversation:

- **CWV consistently "Poor" on mobile** despite all fixable optimizations implemented.
- **Organic traffic capped** despite strong content — platform limitations on URL structure, schema, or rendering may be the ceiling.
- **International SEO needed** — hreflang implementation is limited or unreliable on most builders.
- **E-commerce scaling** beyond ~500 products — Webflow's CMS limit of 10,000 items and Wix's product limits create operational constraints.
- **Technical SEO features needed** that require server-side logic (dynamic sitemaps, URL redirects at scale, custom headers).
- **AEO/GEO priority** — schema flexibility is limited on builders, which restricts answer-engine optimization.

Flag these as strategic observations, not audit failures — they're investment conversations for the client, not implementation tasks.

---

## 8. Common anti-patterns

### 8.1 Default Wix SEO titles
Wix sets the default page title to the page name. Many sites leave dozens of pages with generic titles like "Home | Site Name" or "Services". Audit every page's meta title.

### 8.2 Webflow CMS items without SEO meta filled in
Webflow CMS items have dedicated SEO fields but clients often don't fill them in, leaving meta descriptions blank. This is a data entry task, not a code task.

### 8.3 Broken links after template changes
Builder platforms allow restructuring navigation visually. Links that were manually added (not through the CMS) often break when sections are renamed.

### 8.4 Duplicate content from builder preview URLs
Webflow staging links (`.webflow.io`) and Wix preview URLs may be indexed. Verify these are blocked:
- Webflow: `webflow.io` subdomain should be blocked in robots.txt or return `X-Robots-Tag: noindex`.
- Wix: Wix handles this automatically for Editor mode.

### 8.5 Schema injected at site level when it should be page-specific
Organization schema correctly at site level. But `BlogPosting` or `Product` schema injected at site level means EVERY page claims to be a `BlogPosting`. Use page-level injection for content-type-specific schema.

### 8.6 Missing 301 redirects after URL changes
Builder platforms make it easy to change page slugs. Without adding a 301 redirect for the old URL, every past backlink and search result pointing to the old URL 404s.

### 8.7 Google Analytics injected twice
Many builder platforms have a native analytics integration AND the client adds GA manually via custom code. Result: double pageview tracking.

---

## 9. Audit checklist

**Applicable to all builder platforms:**

- **BLD-1** Every page has a unique, descriptive meta title (not platform default). Spot-check 10 pages. `curl -s https://example.com/about | grep "<title>"`.
- **BLD-2** Every page has a meta description filled in. `curl -s https://example.com/about | grep "meta name=\"description\""`.
- **BLD-3** Canonical tag present on all pages. `curl -s https://example.com/about | grep canonical` — should point to the page's own URL.
- **BLD-4** OpenGraph tags present: `og:title`, `og:description`, `og:url`, `og:image`.
- **BLD-5** HTTPS enforced. `curl -sIL http://example.com/ | head -4` shows 301 → https.
- **BLD-6** Sitemap present and submitted to GSC. `curl -sI https://example.com/sitemap.xml` returns HTTP 200.
- **BLD-7** robots.txt does not contain `Disallow: /`. AI retrieval crawlers allowed.
- **BLD-8** Organization schema injected at site level via custom code. Validate with Rich Results Test.
- **BLD-9** Page-specific schema (BlogPosting, Product, LocalBusiness) injected correctly at page/CMS level, NOT site level. Verify only one `@type` per schema block on each page.
- **BLD-10** 301 redirects in place for any changed URLs (check platform redirect manager).
- **BLD-11** Custom 404 page configured and returns HTTP 404. `curl -sI https://example.com/nonexistent | head -1`.
- **BLD-12** No duplicate `<title>` or `<meta name="description">` tags (platform conflict with custom code injection). `curl -s https://example.com/ | grep -c "<title>"` returns 1.
- **BLD-13** No double analytics tracking. Check: `curl -s https://example.com/ | grep -c "gtag\|G-"` — should not be more than 1 instance.
- **BLD-14** Builder preview/staging URLs (`.webflow.io`, Wix preview) not indexed. `curl -sI https://example-site.webflow.io/ | grep -i "x-robots\|noindex"`.
- **BLD-15** LCP image file size reasonable (≤ 200KB after platform compression). Check in Chrome DevTools Network tab.
- **BLD-16** Core Web Vitals assessed via CrUX (field data). If CWV "Poor" on mobile, annotate which issues are **platform constraints** vs **fixable**.
- **BLD-17** Google Business Profile linked from footer (for local businesses on builder sites).
- **BLD-18** `llms.txt` deployed via custom page at `/llms.txt` URL, or injected via platform's custom routes.
- **BLD-19** All CMS items (blog posts, products, team members) have SEO fields populated — not relying on auto-generated defaults.
- **BLD-20** Any international stores/languages use the platform's multilingual feature (Wix Multilingual, Webflow Localization) rather than manual translation pages, and hreflang tags are verified as present.
