# WordPress Architecture Profile

Site-level audit patterns specific to WordPress — the CMS powering ~43% of the web. Read whenever the audit target runs on WordPress, WooCommerce, or any WordPress-based platform (Elementor, Divi, Beaver Builder, etc.).

**How this differs from `crawlability-react.md`:** WordPress is server-rendered by default, so crawlability is rarely the problem. The issues here are structural — permalink configuration, plugin conflicts, duplicate content from taxonomy/archive pages, and schema injection patterns.

## Table of contents

1. [When to read this](#1-when-to-read-this)
2. [Permalink structure](#2-permalink-structure)
3. [SEO plugin ecosystem](#3-seo-plugin-ecosystem)
4. [Duplicate content — the WordPress trap](#4-duplicate-content)
5. [Schema injection patterns](#5-schema-injection)
6. [Core Web Vitals — common WordPress offenders](#6-core-web-vitals)
7. [WooCommerce-specific SEO](#7-woocommerce)
8. [robots.txt and sitemap via plugins](#8-robots-and-sitemap)
9. [Common anti-patterns](#9-anti-patterns)
10. [Audit checklist](#10-audit-checklist)

---

## 1. When to read this

Load this file when the audit target is:
- WordPress (any version)
- WooCommerce
- Any site with `/wp-admin/`, `/wp-content/`, or `wp-json` in the URL structure
- Headless WordPress (WordPress as CMS, decoupled frontend — also load the frontend's stack profile)

Skip for non-WordPress PHP (use `php-architecture-profile.md`) or React-based frontends consuming WordPress via API (use `react-nextjs-architecture-profile.md` for the frontend layer).

---

## 2. Permalink structure

WordPress ships with `?p=123` URLs by default. This is the worst setting for SEO.

### The correct setting

**Settings → Permalinks → Post name:** `/sample-post/`

This produces clean, keyword-rich URLs that match user intent and search patterns.

### Common permalink structures and their SEO implications

| Structure | Example | SEO verdict |
|---|---|---|
| Plain (default) | `/?p=123` | ❌ Terrible — opaque, no keywords |
| Day and name | `/2026/04/18/post-name/` | ⚠️ Date in URL ages content prematurely |
| Month and name | `/2026/04/post-name/` | ⚠️ Same issue |
| Numeric | `/archives/123` | ❌ Opaque, no improvement over default |
| Post name | `/post-name/` | ✅ Best for most sites |
| Custom structure | `/category/%postname%/` | ✅ Good for large blogs with strong categories |

### Changing permalinks on an existing site

Never change permalink structure on a live site without a redirect strategy. Every existing URL changes — without 301 redirects, you lose all link equity and SERP positions. Use the **Redirection** plugin or server-side rewrite rules.

### Audit command

```bash
curl -sI https://example.com/?p=1 | grep -i location
# If it redirects to /sample-post/, permalinks are set correctly.
# If it serves the page directly, ?p=123 is live.
```

---

## 3. SEO plugin ecosystem

Most WordPress SEO is handled by one of three plugins. Each has its own schema output, sitemap format, and meta-tag injection.

### Yoast SEO (most common)

- Meta tags: injected in `<head>` via `wp_head` hook.
- Schema: `@graph`-based JSON-LD on every page. Highly configurable.
- Sitemap: `/sitemap_index.xml` with sub-sitemaps per post type.
- robots.txt: editable via **SEO → Tools → File Editor**.
- Key setting: **SEO → Search Appearance → Content Types** — ensure `noindex` isn't accidentally set on Posts or Pages.

### Rank Math

- Meta tags: injected similarly to Yoast.
- Schema: rich schema builder with 20+ schema types per page.
- Sitemap: `/sitemap_index.xml`.
- Advantage over Yoast: per-page schema type selection in the block editor sidebar.

### All in One SEO (AIOSEO)

- Older plugin, still widely used.
- Sitemap: `/sitemap.xml`.
- Less sophisticated schema output than Yoast/Rank Math.

### Audit checks for SEO plugins

- Confirm only ONE SEO plugin is active. Two SEO plugins = double `<title>` tags, double schema, double og:tags.
- Confirm the active plugin is not set to `noindex` site-wide (common after migrations or staging clones).
- Confirm schema output passes Rich Results Test.
- Confirm sitemap is reachable and populated.

---

## 4. Duplicate content — the WordPress trap

This is the single biggest SEO issue on WordPress sites. WordPress generates multiple archive pages for every piece of content:

| Archive type | Example URL | Default behaviour |
|---|---|---|
| Category archive | `/category/seo/` | Indexed |
| Tag archive | `/tag/technical-seo/` | Indexed |
| Author archive | `/author/girish/` | Indexed |
| Date archive | `/2026/04/` | Indexed |
| Post format archive | `/type/video/` | Indexed |
| Attachment pages | `/post-name/image-file/` | Indexed |
| Search results | `/?s=query` | Indexed (MUST noindex) |
| Paginated archives | `/?paged=2` | Indexed (canonicalise) |

Most of these dilute crawl budget and create thin/duplicate content at scale.

### Recommended settings (Yoast)

- **SEO → Search Appearance → Taxonomies:** noindex tag archives if they have < 10 posts each.
- **SEO → Search Appearance → Archives:** noindex author archives unless the site is author-driven.
- **SEO → Search Appearance → Archives:** noindex date archives (almost always).
- **SEO → Search Appearance → Media:** noindex attachment pages (always — they serve almost no SEO value).

### Search results

`/?s=query` pages MUST be noindexed. They're thin, session-specific, and burn crawl budget:

```php
// functions.php — force noindex on search
add_action('wp_head', function() {
  if (is_search()) {
    echo '<meta name="robots" content="noindex, follow">';
  }
}, 1);
```

### Canonical for paginated archives

WordPress paginates archives at `?paged=2`. Self-canonicalise paginated pages:

```php
// functions.php
add_action('wp_head', function() {
  if (is_paged()) {
    echo '<link rel="canonical" href="' . get_pagenum_link(get_query_var('paged')) . '">';
  }
});
```

Most SEO plugins handle this automatically — verify it's working.

### The www / non-www and HTTP / HTTPS redirects

WordPress stores the site URL in the database. Both must be canonical:

1. **Settings → General:** both `WordPress Address (URL)` and `Site Address (URL)` must use `https://` and consistent `www`/non-www.
2. Confirm `.htaccess` or Nginx config redirects the non-canonical variant.
3. `wp-config.php` should NOT hardcode HTTP: `define('WP_HOME', 'https://example.com')`.

---

## 5. Schema injection patterns

WordPress/Yoast outputs a `@graph`-based schema that's robust — don't override it unless you need to extend it.

### The Yoast @graph structure (auto-generated)

```json
{
  "@context": "https://schema.org",
  "@graph": [
    { "@type": "WebPage", "@id": "https://example.com/post/#webpage" },
    { "@type": "Article", "@id": "https://example.com/post/#article" },
    { "@type": "Person", "@id": "https://example.com/#/schema/person/HASH" },
    { "@type": "WebSite", "@id": "https://example.com/#website" },
    { "@type": "Organization", "@id": "https://example.com/#organization" }
  ]
}
```

### Extending schema without breaking Yoast

Use the `wpseo_schema_graph` filter to add types:

```php
add_filter('wpseo_schema_graph', function($graph, $context) {
  if (is_singular('post')) {
    $graph[] = [
      '@type' => 'FAQPage',
      '@id' => $context->canonical . '#faqpage',
      'mainEntity' => [ /* your FAQs */ ]
    ];
  }
  return $graph;
}, 11, 2);
```

### Schema for Custom Post Types (CPTs)

Yoast doesn't automatically add schema for CPTs. Either:
1. Use Rank Math's per-CPT schema templates.
2. Add schema manually via `wp_head` action.
3. Use a plugin like Schema Pro for CPT schema.

### WooCommerce Product schema

WooCommerce + Yoast outputs `Product` schema automatically. Verify:
- `aggregateRating` is populated (requires a review plugin like WooCommerce Reviews or Trustpilot).
- `offers.price` reflects the current price (not the cached price from a previous session).
- `offers.availability` reflects actual stock status.

---

## 6. Core Web Vitals — common WordPress offenders

WordPress sites notoriously score poorly on Core Web Vitals. The usual suspects:

### Render-blocking resources

Most WordPress themes enqueue CSS and JS in `<head>` without `defer` or `async`. Audit:

```bash
curl -s https://example.com/ | grep -oP '<script[^>]*src="[^"]*"[^>]*>' | head -20
```

Look for `<script src="...">` without `async` or `defer`. These block rendering.

**Fix:** Use a caching plugin (WP Rocket, LiteSpeed Cache, W3 Total Cache) with "Defer JS execution" enabled.

### Unoptimised images

WordPress generates multiple image sizes on upload but doesn't serve WebP by default. Check:
- Are images served as WebP? (Check response headers: `Content-Type: image/webp`)
- Is `srcset` populated with appropriate sizes?
- Is the LCP image lazy-loaded? (It must NOT be.)

**Fix:** Plugins like Imagify, ShortPixel, or Smush for WebP conversion + automatic resizing.

### Excessive plugins

Every active plugin adds PHP execution time + potentially JS/CSS. Audit:
- How many plugins are active? > 20 is a yellow flag; > 40 is a red flag.
- Any plugin loading JS on every page that only needs to load on specific pages?
- Any abandoned plugins (last updated > 2 years ago)?

### Unoptimised database

Years of revisions, transient data, and spam comments bloat the database → slow queries → slow TTFB.

```sql
-- Check table sizes
SELECT table_name, ROUND(data_length/1024/1024, 2) AS size_mb
FROM information_schema.tables
WHERE table_schema = 'your_database'
ORDER BY data_length DESC;
```

Common tables to clean: `wp_postmeta`, `wp_options` (transients), `wp_revisions`.

### Caching

Every production WordPress site needs page caching. Without it, every request executes PHP + DB queries:

- **Shared hosting:** WP Super Cache or W3 Total Cache
- **Managed hosting:** Usually built-in (WP Engine, Kinsta, Cloudways)
- **Self-hosted:** WP Rocket (best overall) or LiteSpeed Cache (on LiteSpeed servers)

---

## 7. WooCommerce-specific SEO

WooCommerce adds several SEO considerations beyond standard WordPress.

### URL structure for products

Default WooCommerce URLs:
- Products: `/product/product-name/`
- Shop: `/shop/`
- Category: `/product-category/category-name/`

The `/product/` base can be removed for cleaner URLs but requires a redirect strategy.

### Duplicate content in WooCommerce

- `/shop/` and `/product-category/all/` often serve near-identical content.
- Product variations create multiple URLs if not handled. Use canonical to point variations to the parent product.
- Out-of-stock products: keep the page live with `<meta name="robots" content="noindex">` — removing it causes crawl errors.

### Product schema validation

WooCommerce + Yoast auto-generates `Product` schema. Verify all required fields:

```bash
curl -s https://example.com/product/widget/ | python3 -c "
import sys, json, re
html = sys.stdin.read()
schemas = re.findall(r'<script type=\"application/ld\+json\">(.*?)</script>', html, re.DOTALL)
for s in schemas:
    try:
        data = json.loads(s)
        if isinstance(data, dict) and data.get('@type') == 'Product':
            print(json.dumps(data, indent=2))
    except: pass
"
```

Required: `name`, `image`, `description`, `offers.price`, `offers.priceCurrency`, `offers.availability`.

### Faceted navigation

WooCommerce filter plugins (YITH, FacetWP) create URLs like `?color=red&size=large`. Without canonical tags, these create thousands of duplicate product listing pages.

**Fix:** Ensure the SEO plugin canonicalises all filter URLs to the base category URL.

---

## 8. robots.txt and sitemap via plugins

### robots.txt

WordPress doesn't have a physical `robots.txt` file by default — it's generated dynamically by WordPress/Yoast.

**Check:** `curl https://example.com/robots.txt`

Default Yoast `robots.txt`:
```
User-agent: *
Disallow: /wp-admin/
Allow: /wp-admin/admin-ajax.php

Sitemap: https://example.com/sitemap_index.xml
```

**Common issues:**
- Staging sites often have `Disallow: /` — this must be removed before production launch.
- `/wp-content/uploads/` should NOT be disallowed (blocks image indexing).
- The `Sitemap:` directive should point to the correct sitemap URL.

### Sitemap

Yoast generates `/sitemap_index.xml` referencing sub-sitemaps:
- `/post-sitemap.xml` — blog posts
- `/page-sitemap.xml` — pages
- `/product-sitemap.xml` — WooCommerce products
- `/category-sitemap.xml` — categories (only if indexed)

**Audit checks:**
- All sitemap URLs return HTTP 200.
- No `noindex` URLs appear in the sitemap.
- `<lastmod>` values reflect actual content modification dates (not server rebuild dates).
- Product sitemap updates when product prices/availability change.

---

## 9. Common anti-patterns

### 9.1 Staging site indexed accidentally
After migrating from staging to production, `Settings → Reading → Search Engine Visibility` checkbox is left ticked ("Discourage search engines"). This adds `<meta name="robots" content="noindex,follow">` to every page.

**Check:** `curl -s https://example.com/ | grep -i "noindex"`

### 9.2 Theme overriding SEO plugin output
Some themes output their own `<title>` tag or `og:tags` in `header.php`, conflicting with the SEO plugin. Result: duplicate meta tags.

**Check:** `curl -s https://example.com/ | grep -i "<title>"` — should return exactly one `<title>` tag.

### 9.3 WP-REST API leaking user data
`/wp-json/wp/v2/users` exposes all author usernames by default — a security + SEO anti-pattern (exposes login names to brute-force attacks).

**Fix:**
```php
// functions.php
add_filter('rest_endpoints', function($endpoints) {
  if (isset($endpoints['/wp/v2/users'])) {
    unset($endpoints['/wp/v2/users']);
  }
  return $endpoints;
});
```

### 9.4 wp-json indexed
`/wp-json/` endpoints should be disallowed in robots.txt:
```
Disallow: /wp-json/
```

### 9.5 Author archives exposing usernames
`/author/admin/` archives expose the WordPress admin username. Either disable author archives (noindex) or create a non-admin author account for all public posts.

### 9.6 Attachment pages indexed
`/post-name/image-file/` attachment pages are thin pages with a single image. Always noindex in Yoast: **SEO → Search Appearance → Media → Show Media in search results → No**.

### 9.7 Broken emoji script
WordPress loads a `wp-emoji-release.min.js` script and inline SVG sprite that adds ~10KB of render-blocking overhead on every page.

**Fix:**
```php
// functions.php
remove_action('wp_head', 'print_emoji_detection_script', 7);
remove_action('wp_print_styles', 'print_emoji_styles');
```

---

## 10. Audit checklist

- **WP-1** Permalink structure set to "Post name" (not plain/numeric/date-based). Verify: `curl -sI https://example.com/?p=1` returns 301 to slug.
- **WP-2** Exactly ONE SEO plugin active (Yoast OR Rank Math OR AIOSEO — never two).
- **WP-3** Active SEO plugin not set to noindex site-wide. Check: `curl -s https://example.com/ | grep noindex`.
- **WP-4** `Settings → General`: both WordPress Address and Site Address use `https://` + consistent www/non-www.
- **WP-5** HTTP → HTTPS redirect confirmed: `curl -sIL http://example.com/` returns `301` with `https://` Location.
- **WP-6** Tag archives: noindex (unless each tag page has ≥ 10 substantial posts).
- **WP-7** Author archives: noindex (unless author-driven editorial site).
- **WP-8** Date archives: noindex (almost always).
- **WP-9** Attachment pages: noindex (always — `Show Media in search results → No`).
- **WP-10** Search results (`/?s=`): noindex confirmed. `curl -s "https://example.com/?s=test" | grep noindex`.
- **WP-11** `robots.txt` does NOT contain `Disallow: /` or `Disallow: /wp-content/uploads/`.
- **WP-12** Sitemap index reachable at `/sitemap_index.xml` (Yoast/Rank Math) or `/sitemap.xml` (AIOSEO). All sub-sitemaps return HTTP 200.
- **WP-13** No noindex URLs appear in any sub-sitemap. Spot-check 5 URLs from sitemap → confirm they're indexable.
- **WP-14** `<title>` appears exactly once in `<head>`. No theme/plugin conflict.
- **WP-15** Schema passes Rich Results Test with no errors on at least 3 representative page types (Home, Post, Product/Service).
- **WP-16** LCP image NOT lazy-loaded. Check: `curl -s https://example.com/ | grep -i "loading="` — hero image should have `loading="eager"` or no loading attribute.
- **WP-17** Images served as WebP. Check response headers: `curl -sI https://example.com/wp-content/uploads/hero.jpg -H "Accept: image/webp"`.
- **WP-18** Page caching active. Check: `curl -sI https://example.com/ | grep -i "x-cache\|cf-cache\|x-wp-cache"`.
- **WP-19** `/wp-json/wp/v2/users` returns 404 or empty (user enumeration blocked).
- **WP-20** `wp-emoji-release.min.js` not loaded (performance + unnecessary request). Check: `curl -s https://example.com/ | grep emoji`.
- **WP-21** WooCommerce (if applicable): Product schema passes Rich Results Test with `offers.price`, `offers.availability`, and (if collected) `aggregateRating`.
- **WP-22** Faceted navigation (if applicable): all filter URLs canonicalise to base category URL. Check: `curl -s "https://example.com/shop/?filter_color=red" | grep canonical`.
