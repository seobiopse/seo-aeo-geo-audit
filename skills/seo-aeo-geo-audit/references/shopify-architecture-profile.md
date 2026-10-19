# Shopify Architecture Profile

Site-level audit patterns specific to Shopify — the hosted e-commerce platform. Read whenever the audit target is a Shopify store, Shopify Plus merchant, or a headless Shopify implementation.

**Key constraint:** Shopify is a hosted platform. Unlike WordPress or custom code, many structural SEO decisions are locked — URL prefixes, sitemap generation, and robots.txt format cannot be fully controlled. The audit must identify what CAN be fixed vs what is a platform constraint.

## Table of contents

1. [When to read this](#1-when-to-read-this)
2. [URL structure — what you can and cannot change](#2-url-structure)
3. [Duplicate content — the Shopify trap](#3-duplicate-content)
4. [Liquid template SEO patterns](#4-liquid-template-seo)
5. [Schema for Shopify products](#5-schema)
6. [Shopify sitemap and robots.txt](#6-sitemap-and-robots)
7. [Core Web Vitals on Shopify](#7-core-web-vitals)
8. [Shopify Markets and international SEO](#8-international)
9. [Common anti-patterns](#9-anti-patterns)
10. [Audit checklist](#10-audit-checklist)

---

## 1. When to read this

Load this file when:
- The target URL contains `/collections/`, `/products/`, or `myshopify.com`.
- The site uses Shopify's admin at `store.myshopify.com`.
- The store uses headless Shopify with Hydrogen/Oxygen (also load the relevant frontend stack profile).

---

## 2. URL structure — what you can and cannot change

### Fixed URL prefixes (cannot be changed on standard Shopify)

| Content type | Fixed prefix | Example |
|---|---|---|
| Products | `/products/` | `/products/blue-widget` |
| Collections | `/collections/` | `/collections/widgets` |
| Blog posts | `/blogs/news/` | `/blogs/news/post-title` |
| Pages | `/pages/` | `/pages/about` |

These prefixes are hardcoded into Shopify. You cannot move products to `/shop/` or collections to `/category/` without going headless.

### What you CAN change

- **Handle (slug):** the part after the prefix. Keep it short, keyword-rich, hyphen-separated.
- **Product title:** influences the default handle but can be customised.
- Custom domain mapping (your domain instead of `myshopify.com`).

### The handle rule

Good: `/products/blue-widget-100ml`
Bad: `/products/blue-widget-100ml-1` (Shopify appends `-1` when a handle conflicts — a signal of duplicate or renamed products)

Audit for handles with `-1`, `-2` suffixes — these indicate unresolved duplicates.

---

## 3. Duplicate content — the Shopify trap

Shopify creates duplicate product URLs at the collection level. This is the most significant SEO issue on Shopify stores.

### The core problem

Every product is accessible at:
1. `/products/blue-widget` — the canonical URL
2. `/collections/widgets/products/blue-widget` — a collection-scoped URL
3. `/collections/all/products/blue-widget` — Shopify's auto-generated "all" collection

All three serve the same content with different URLs.

### Shopify's built-in canonical tag

Shopify themes (Dawn and most modern themes) automatically add a canonical tag pointing to `/products/blue-widget` for all three URL variants. Verify this is working:

```bash
curl -s https://example.com/collections/widgets/products/blue-widget | grep canonical
# Should return: <link rel="canonical" href="https://example.com/products/blue-widget">
```

### The `/collections/all` page

Shopify auto-generates `/collections/all` which lists every product. This page is often thin (just a product grid), competes with category pages, and is frequently a crawl-budget waste.

**Fix:** Add `<meta name="robots" content="noindex, follow">` to the `collection.all` template in Liquid, OR block it in robots.txt.

### Pagination duplicate content

Shopify paginates collections at `?page=2`. Ensure paginated pages have:
1. Self-referencing canonical (not canonical → page 1)
2. `rel="prev"` / `rel="next"` links (deprecated but still used by some crawlers)

---

## 4. Liquid template SEO patterns

Shopify uses Liquid templating. SEO is injected into templates.

### Title and meta description

In `theme.liquid` or `layout/theme.liquid`:

```liquid
<title>
  {%- if template == 'index' -%}
    {{ shop.name }} — {{ shop.description }}
  {%- elsif template == 'product' -%}
    {{ product.title }} — {{ shop.name }}
  {%- elsif template == 'collection' -%}
    {{ collection.title }} — {{ shop.name }}
  {%- else -%}
    {{ page_title }} — {{ shop.name }}
  {%- endif -%}
</title>
<meta name="description" content="{{ page_description | escape }}">
```

Audit: confirm `page_description` is populated for all product and collection pages. Empty meta descriptions are a common Shopify issue — merchants fill in product descriptions but skip the SEO description field.

### Canonical tag

In `layout/theme.liquid`:
```liquid
<link rel="canonical" href="{{ canonical_url }}">
```

Shopify's `canonical_url` object resolves correctly for product/collection duplication. Verify it's present and using the correct variable (not a hardcoded URL).

### OpenGraph tags

```liquid
<meta property="og:title" content="{{ page_title | escape }}">
<meta property="og:description" content="{{ page_description | escape }}">
<meta property="og:url" content="{{ canonical_url }}">
<meta property="og:image" content="{{ product.featured_image | img_url: '1200x630' }}">
<meta property="og:type" content="{% if template == 'product' %}product{% else %}website{% endif %}">
```

Common issue: Shopify's `img_url` filter crops to exact dimensions, potentially distorting non-square images. Use `img_url: '1200x630', crop: 'center'` for OG images.

---

## 5. Schema for Shopify products

Shopify themes inject basic `Product` schema automatically in recent versions. Verify completeness.

### Minimum viable Product schema for Shopify

```json
{
  "@context": "https://schema.org/",
  "@type": "Product",
  "name": "Blue Widget 100ml",
  "url": "https://example.com/products/blue-widget-100ml",
  "image": [ "https://cdn.shopify.com/s/files/..." ],
  "description": "Product description here.",
  "sku": "BW-100ML",
  "brand": { "@type": "Brand", "name": "Example Brand" },
  "offers": {
    "@type": "Offer",
    "url": "https://example.com/products/blue-widget-100ml",
    "priceCurrency": "AUD",
    "price": "29.95",
    "availability": "https://schema.org/InStock",
    "itemCondition": "https://schema.org/NewCondition"
  }
}
```

### Injecting schema via Liquid

In `product.liquid` or `sections/main-product.liquid`:

```liquid
<script type="application/ld+json">
{
  "@context": "https://schema.org/",
  "@type": "Product",
  "name": {{ product.title | json }},
  "url": {{ canonical_url | json }},
  "image": [
    {%- for image in product.images -%}
      {{ image.src | img_url: '1200x1200' | json }}{% unless forloop.last %},{% endunless %}
    {%- endfor -%}
  ],
  "description": {{ product.description | strip_html | json }},
  "sku": {{ product.selected_or_first_available_variant.sku | json }},
  "offers": {
    "@type": "Offer",
    "url": {{ canonical_url | json }},
    "priceCurrency": {{ shop.currency | json }},
    "price": {{ product.price | money_without_currency | json }},
    "availability": "https://schema.org/{% if product.available %}InStock{% else %}OutOfStock{% endif %}"
  }
}
</script>
```

### Shopify Reviews apps and aggregateRating

Shopify's built-in Product Reviews app or Judge.me / Okendo / Stamped inject review data. Verify:
1. `aggregateRating` is present in the Product schema.
2. The rating value and review count match the visible review section.
3. Individual `Review` schema items are present (or at minimum `aggregateRating`).

---

## 6. Shopify sitemap and robots.txt

### Sitemap

Shopify auto-generates `/sitemap.xml` — a sitemap index with:
- `/sitemap_products_1.xml`
- `/sitemap_pages_1.xml`
- `/sitemap_collections_1.xml`
- `/sitemap_blogs_1.xml`

**You cannot edit this sitemap.** Key audit checks:
- Submit to GSC and Bing WMT.
- Verify it excludes noindexed pages.
- Product count in sitemap matches expected active product count.
- No 404 URLs in the sitemap (common after product deletions).

### robots.txt

Shopify auto-generates `robots.txt`. Since Shopify 2021, you CAN customise it via the `robots.txt.liquid` template:

```liquid
{% comment %} robots.txt.liquid {% endcomment %}
{% for group in robots.default_groups %}
  {{- group.user_agent -}}
  {% for rule in group.rules %}
    {{- rule -}}
  {% endfor %}
  {% if group.sitemap %}
    {{- group.sitemap -}}
  {% endif %}
{% endfor %}

{% comment %} Custom additions: {% endcomment %}
User-agent: *
Disallow: /collections/all
Disallow: /search
```

If the store hasn't updated to Shopify Online Store 2.0, `robots.txt.liquid` may not be available — flag this.

---

## 7. Core Web Vitals on Shopify

Shopify stores commonly score poorly on mobile CWV. Main offenders:

### Theme JavaScript

Heavy themes (especially page-builder themes like PageFly, GemPages) load 200–500KB of JS. Audit:

```bash
curl -s https://example.com/ | grep -oP 'src="[^"]*\.js[^"]*"' | wc -l
```

More than 15–20 JS files is a performance red flag.

### Third-party app scripts

Every Shopify app installs a script tag that loads on every page. Common offenders: chat widgets, loyalty apps, review widgets, exit-intent popups. Each adds 20–200ms of LCP.

Audit: Chrome DevTools → Network → filter by third-party domains. Identify scripts that load above the fold on product pages.

### Shopify CDN image serving

Shopify serves images from `cdn.shopify.com`. The `img_url` filter controls sizing:

```liquid
{{ product.featured_image | img_url: '800x800' }}        {%- # generates /800x800/ cropped -%}
{{ product.featured_image | img_url: 'master' }}         {%- # original, potentially huge -%}
{{ product.featured_image | img_url: '800x', crop: 'center' }}  {%- # 800px wide, proportional -%}
```

**Always specify a maximum size.** Never use `master` for above-the-fold images.

### LCP image preload on Shopify

The hero/featured image needs `fetchpriority="high"` and ideally a `<link rel="preload">`:

```liquid
{%- if section.index == 1 -%}
  <link rel="preload" as="image" href="{{ section.settings.image | img_url: '1200x' }}" fetchpriority="high">
{%- endif -%}
```

---

## 8. International SEO with Shopify Markets

Shopify Markets (released 2021) handles multi-currency, multi-language, multi-country selling.

### URL structure for international

- Subdomain: `fr.example.com` (recommended)
- Subfolder: `example.com/fr` (available on some plans)
- Top-level domain: `example.fr` (advanced setup)

### hreflang

Shopify Markets auto-generates `hreflang` tags. Verify:
1. Each locale has a self-referencing `hreflang`.
2. `x-default` points to the default market.
3. All hreflang URLs are absolute and return HTTP 200.

```bash
curl -s https://example.com/ | grep hreflang
```

### Currency not in URL

Shopify serves different currency prices to the same URL based on IP/cookie. This is NOT duplicate content — currency display doesn't create separate indexable URLs. The canonical URL is currency-neutral.

---

## 9. Common anti-patterns

### 9.1 Password-protected store indexed after launch
Shopify stores launch in password-protected mode. After going live, the password protection must be explicitly removed. Googlebot cannot crawl a password-protected store.

**Check:** `curl -sI https://example.com/` — should NOT return `X-Shopify-Stage: password`.

### 9.2 Duplicate products from variants
Large variant lists (e.g., 100 colour/size combinations) don't create URL duplicates in standard Shopify — variants share the parent product URL with `?variant=123` appended. These should canonicalise to the parent URL. Verify:

```bash
curl -s "https://example.com/products/widget?variant=12345" | grep canonical
# Should return the base product URL without ?variant=
```

### 9.3 App conflicts creating extra `<title>` tags
Some Shopify apps inject their own meta tags. Check for duplicate `<title>` tags:

```bash
curl -s https://example.com/products/widget | grep -c "<title>"
# Should return 1
```

### 9.4 Missing product descriptions
Shopify stores commonly have products with no description — just a title and image. This produces thin pages that struggle to rank. Flag: `product.description` empty on more than 20% of products.

### 9.5 Navigation breadcrumbs missing schema
Most Shopify themes render breadcrumbs visually but without `BreadcrumbList` schema. This is a quick win — add schema to the breadcrumb snippet.

### 9.6 Blog section underutilised
Shopify's built-in `/blogs/` section is often ignored. When used, it commonly lacks `Article` schema and author attribution.

---

## 10. Audit checklist

- **SF-1** Custom domain mapped (not `store.myshopify.com`). HTTPS active. `curl -sIL http://example.com/` returns `301 → https://`.
- **SF-2** Password protection removed. `curl -sI https://example.com/` does NOT return `X-Shopify-Stage: password`.
- **SF-3** Canonical tags correct on collection-scoped product URLs: `curl -s https://example.com/collections/all/products/widget | grep canonical` → base `/products/widget` URL.
- **SF-4** `/collections/all` is noindexed or blocked in robots.txt.
- **SF-5** `page_description` populated on product and collection pages. Spot-check 5 products: `curl -s https://example.com/products/widget | grep "meta name=\"description\""`.
- **SF-6** OpenGraph `og:image` ≥ 1200×630. Check with LinkedIn Post Inspector.
- **SF-7** Product schema present and passes Rich Results Test. Required: `name`, `image`, `offers.price`, `offers.availability`.
- **SF-8** `aggregateRating` present only if reviews actually exist on the page and count matches.
- **SF-9** Sitemap submitted to GSC + Bing WMT. Product count in sitemap reasonable vs store size.
- **SF-10** No 404 URLs in sitemap (common after product deletions). Test 10 random sitemap URLs.
- **SF-11** `robots.txt` customised to block `/collections/all` and `/?*` facet URLs if applicable.
- **SF-12** LCP image size reasonable (≤ 200KB). NOT loaded with `img_url: 'master'`. Has `fetchpriority="high"`.
- **SF-13** Third-party app script count ≤ 10. Identify any chat/loyalty/review scripts loading above the fold unnecessarily.
- **SF-14** Duplicate `<title>` tags absent. `curl -s https://example.com/ | grep -c "<title>"` returns 1.
- **SF-15** Product handles contain no `-1`, `-2` suffixes (indicates unresolved duplicates).
- **SF-16** Breadcrumbs have `BreadcrumbList` schema (not just visual breadcrumbs).
- **SF-17** Blog posts (if used): `Article` schema with `author`, `datePublished`, `dateModified`.
- **SF-18** Shopify Markets (if used): `hreflang` tags present with `x-default` and self-referencing locale tags.
- **SF-19** Paginated collection pages (`?page=2`) have self-referencing canonical (not canonical → page 1).
- **SF-20** `BreadcrumbList` schema on product pages shows full path: Home → Collection → Product.
