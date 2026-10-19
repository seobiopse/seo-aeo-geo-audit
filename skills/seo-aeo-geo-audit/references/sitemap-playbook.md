# Sitemap Playbook

Proper sitemap strategy. Most teams ship a single `sitemap.xml` with `<changefreq>weekly</changefreq>` and `<priority>0.8</priority>` on every URL — that's worse than no sitemap, because Google learns to ignore the hints.

Read whenever an audit targets a site with a sitemap (every site should have one).

## The point of a sitemap

A sitemap is NOT an indexing guarantee. It's a discovery signal + freshness signal. Specifically:

1. **Discovery** — Google finds URLs it hasn't crawled yet.
2. **Freshness** — `<lastmod>` tells Google which URLs changed recently, so crawl budget focuses on those.
3. **Completeness** — helps Google build a mental model of your site's structure.

If your sitemap isn't doing all three, it's noise.

## Table of contents

1. [Sitemap types](#1-sitemap-types)
2. [When to split into multiple sitemaps](#2-when-to-split)
3. [`<lastmod>` — the only freshness signal that matters](#3-lastmod)
4. [`<changefreq>` — when to use, when to skip](#4-changefreq)
5. [`<priority>` — mostly ignored, use sparingly](#5-priority)
6. [Dynamic sitemap patterns](#6-dynamic-sitemap-patterns)
7. [Specialised sitemaps (image, video, news)](#7-specialised-sitemaps)
8. [Sitemap index (`sitemap_index.xml`)](#8-sitemap-index)
9. [Validation + Search Console submission](#9-validation--gsc-submission)
10. [Audit checklist](#10-audit-checklist)

---

## 1. Sitemap types

- **Main sitemap** (`/sitemap.xml`) — for sites under 50K URLs. Single file, all canonical URLs.
- **Sitemap index** (`/sitemap.xml` as an index) — for sites over 50K URLs or with distinct content types.
- **Per-content sitemaps** (`/sitemap-jobs.xml`, `/sitemap-articles.xml`, `/sitemap-products.xml`) — referenced by the index.
- **Image sitemap** — extensions to URLs that declare their images.
- **Video sitemap** — same, for video content.
- **News sitemap** — for publishers approved for Google News.

## 2. When to split

Split into multiple sitemaps when any of:

- You have > 50,000 URLs (Google's hard limit per sitemap).
- You have > 50 MB uncompressed (Google's other hard limit).
- You have distinct content types with different update cadences (e.g., jobs change daily, evergreen articles don't).
- You want per-section diagnostics in GSC (each sitemap shows its own index rate).

### Recommended split for a typical content-rich site

```
/sitemap.xml                    ← index, references the below
/sitemap-main.xml               ← homepage + top-level marketing pages
/sitemap-articles.xml           ← blog posts
/sitemap-categories.xml         ← hub / category pages
/sitemap-products.xml           ← product / service detail pages
/sitemap-jobs.xml               ← job-posting pages (dynamic)
/sitemap-courses.xml            ← course-detail pages (dynamic)
/sitemap-authors.xml            ← author bio pages
/sitemap-images.xml             ← image sitemap
```

## 3. `<lastmod>` — the only freshness signal that matters

`<lastmod>` is the single most important field in a sitemap entry. Google literally documents that `<lastmod>` is the primary freshness signal and that `<changefreq>` and `<priority>` are secondary.

### Rules

1. **Use ISO 8601 with timezone.**
   - ✅ `2026-04-18T09:00:00+05:30`
   - ✅ `2026-04-18` (date-only is accepted, but less informative)
   - ❌ `18/04/2026`

2. **Only update on real content changes.** The temptation is to bump `<lastmod>` on every build. DON'T. If you do, Google learns to ignore `<lastmod>` because it's always "today" for your site.

3. **Consequences of abused `<lastmod>`:** Google's crawl systems detect the pattern. They start downweighting the signal site-wide. You lose the ability to tell Google "these 30 URLs changed today, crawl them first." Eventually your sitemap is ignored for prioritization.

4. **What counts as a real change:**
   - Article body edited
   - Product price or availability changed
   - Job status flipped (active → inactive)
   - Schema updated
   - New image, new paragraph, corrected fact
   
   What does NOT count:
   - Redeploy with no content change
   - Cache rebuild
   - CSS/JS change
   - Dependency update

5. **Implementation:** track `updated_at` or `dateModified` in your database, and only bump it when content changes. Your sitemap generator reads `updated_at` for `<lastmod>`.

### Example (correct)

```xml
<url>
  <loc>https://example.com/blog/post-slug</loc>
  <lastmod>2026-03-15T14:22:00+05:30</lastmod>
</url>
```

### Example (wrong — don't do this)

```xml
<url>
  <loc>https://example.com/blog/post-slug</loc>
  <lastmod>2026-04-18T06:00:00Z</lastmod>  <!-- same for every URL, updated nightly -->
</url>
```

## 4. `<changefreq>` — when to use, when to skip

Google has explicitly stated that `<changefreq>` is mostly ignored. Crawl frequency is determined by observed behavior (how often pages actually change) + signal from `<lastmod>`.

### Our recommendation

**Skip `<changefreq>` entirely for most pages.** Exception: use it only when the values below would be *factually correct* and help a newer crawler calibrate:

| Value | Appropriate use |
|---|---|
| `always` | Never use — this is for pages that change on every request (live stock tickers). Your marketing site isn't one. |
| `hourly` | Real-time news or stock sites only. |
| `daily` | Active job boards, events, news sections. |
| `weekly` | Blog posts that may be updated, product category pages. |
| `monthly` | Evergreen guides, docs. |
| `yearly` | Policies, about-us, non-updating content. |
| `never` | Archived content that will never change. Pair with `lastmod` set to the archive date. |

### The freshness risk

If `<changefreq>weekly</changefreq>` is set on every URL and 90% don't change weekly, Google detects the inflation and ignores `<changefreq>` from your sitemap. You've damaged a signal for no gain.

**Safer default: omit `<changefreq>` entirely.** Let `<lastmod>` do the work.

## 5. `<priority>` — mostly ignored, use sparingly

`<priority>` (0.0 – 1.0) is Google's least-weighted sitemap signal. Google has publicly said they mostly ignore it.

### When `<priority>` is actually useful

When your site has a clear importance hierarchy and you want to communicate it ONCE:

- Homepage: `1.0`
- Top-level category hubs: `0.8`
- Individual articles / products: `0.5`
- Author pages / tag pages: `0.3`
- Legal / policies: `0.2`

If every URL has `priority 0.8`, you've said nothing. If you use `priority` at all, make sure it's MEANINGFUL (different values for different page types).

### Safer default

Omit `<priority>` entirely if you're not going to use meaningful values. The field existing with `0.5` on everything is worse than not having the field.

## 6. Dynamic sitemap patterns

Programmatic and large content sites MUST use dynamic sitemaps. Static `sitemap.xml` goes stale within hours on a job board, product site, or news site.

### Pattern: dynamic Next.js sitemap route (App Router)

```typescript
// app/sitemap-jobs.xml/route.ts
import { NextResponse } from 'next/server';

export async function GET() {
  const jobs = await db.jobs.findMany({
    where: { status: 1 },                     // active only
    orderBy: { updated_at: 'desc' },
    select: { slug: true, updated_at: true, location: true, company: true }
  });

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${jobs.map(j => `  <url>
    <loc>https://example.com/jobs/${j.location}/${j.company}/${j.slug}</loc>
    <lastmod>${j.updated_at.toISOString()}</lastmod>
  </url>`).join('\n')}
</urlset>`;

  return new NextResponse(xml, {
    headers: {
      'Content-Type': 'application/xml',
      'Cache-Control': 'public, s-maxage=3600, stale-while-revalidate=86400'
    }
  });
}
```

### Caching strategy

- **Edge cache: 1 hour hard (`s-maxage=3600`) + 24 hour soft (`stale-while-revalidate=86400`).**
- Most bots re-fetch the sitemap every few hours. 1-hour cache is fresh enough for them without hammering your database every request.
- Regenerate on content change events (cron, webhook, or on-demand revalidation).

### Database query for correctness

```sql
-- Include ONLY:
SELECT slug, updated_at, ... FROM content
WHERE status = 'published'        -- not drafts
  AND noindex = false              -- not marked noindex
  AND canonical_url IS NULL        -- not canonicalised to something else
ORDER BY updated_at DESC
LIMIT 50000;                       -- split into multiple sitemaps past this
```

### What to EXCLUDE from your sitemap

- `noindex` pages
- Pages canonicalised to a different URL
- Pages behind auth
- Duplicate / filtered URLs (facets, sorts)
- 301/302/404 URLs
- Drafts / internal staging URLs
- Search result pages

Listing any of these in your sitemap is a negative quality signal to Google.

## 7. Specialised sitemaps (image, video, news)

### Image sitemap extension
Declares images that live on each URL. Helps Google Images discover them.

```xml
<url>
  <loc>https://example.com/product/widget</loc>
  <lastmod>2026-04-18</lastmod>
  <image:image xmlns:image="http://www.google.com/schemas/sitemaps-image/1.1">
    <image:loc>https://example.com/img/widget-1200.webp</image:loc>
    <image:caption>Widget product photo on white background</image:caption>
  </image:image>
</url>
```

Useful when images drive traffic (e-commerce, photography, real estate).

### Video sitemap extension

```xml
<url>
  <loc>https://example.com/video/demo</loc>
  <video:video xmlns:video="http://www.google.com/schemas/sitemaps-video/1.1">
    <video:thumbnail_loc>https://example.com/img/demo-thumb.jpg</video:thumbnail_loc>
    <video:title>Product demo walkthrough</video:title>
    <video:description>3-minute overview of the widget</video:description>
    <video:content_loc>https://example.com/video/demo.mp4</video:content_loc>
    <video:duration>180</video:duration>
  </video:video>
</url>
```

### News sitemap (Google News only)

Only for publishers approved in Google News. Different schema, 2-day rolling window.

## 8. Sitemap index

For sites with > 50K URLs or multiple content types:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://example.com/sitemap-main.xml</loc>
    <lastmod>2026-04-18</lastmod>
  </sitemap>
  <sitemap>
    <loc>https://example.com/sitemap-articles.xml</loc>
    <lastmod>2026-04-18</lastmod>
  </sitemap>
  <sitemap>
    <loc>https://example.com/sitemap-jobs.xml</loc>
    <lastmod>2026-04-18</lastmod>
  </sitemap>
</sitemapindex>
```

### Rules
- The index itself can list up to 50,000 sitemaps.
- Each listed sitemap can have up to 50,000 URLs.
- The index's `<lastmod>` should be the most recent `<lastmod>` of any URL in the referenced sitemap.
- Reference the INDEX in your `robots.txt`: `Sitemap: https://example.com/sitemap.xml` — Google follows the chain.

## 9. Validation + GSC submission

### Validate locally
```bash
# XML well-formed?
xmllint --noout https://example.com/sitemap.xml

# Check URL count
curl -s https://example.com/sitemap.xml | grep -c '<url>'

# Check lastmod formatting
curl -s https://example.com/sitemap.xml | grep -oP '<lastmod>[^<]+' | head -5
```

### Submit to Google Search Console
1. Search Console → your property → Sitemaps (left nav).
2. Enter the path (e.g., `sitemap.xml` or `sitemap-jobs.xml`).
3. Submit. Wait 24–48 hours.
4. Check "Success" status. Check "Discovered URLs" count matches your expectation.

If `<lastmod>` is broken, GSC flags "couldn't fetch lastmod" or "invalid date".

### Submit to Bing Webmaster Tools
Same flow, separate tool. Sites that want GEO citations from Copilot / Bing AI should submit here too.

### Direct ping (legacy)
```
# Google (deprecated June 2023 — don't bother)
# Bing:
https://www.bing.com/ping?sitemap=https://example.com/sitemap.xml
```

Google dropped the ping endpoint. They discover sitemaps via `robots.txt` or GSC submission.

## 10. Audit checklist

- **SM-1** `/sitemap.xml` returns HTTP 200 with `Content-Type: application/xml`.
- **SM-2** Sitemap is well-formed XML (passes `xmllint`).
- **SM-3** Every `<loc>` is an absolute URL with `https://` (no relative paths).
- **SM-4** Every `<loc>` resolves to HTTP 200 (not 301/302/404/5xx). Spot-check 10 random URLs.
- **SM-5** No `noindex` URLs in the sitemap.
- **SM-6** No canonicalised-away URLs in the sitemap (each URL is its own canonical).
- **SM-7** `<lastmod>` uses ISO 8601 format.
- **SM-8** `<lastmod>` reflects real content changes (spot-check: compare to `dateModified` in schema or the page's visible "Last updated" date).
- **SM-9** `<lastmod>` is NOT identical across all URLs (indicates "bumped on rebuild" anti-pattern).
- **SM-10** `<changefreq>` either omitted, or present with meaningfully different values per URL type.
- **SM-11** `<priority>` either omitted, or present with meaningfully different values (not `0.8` on everything).
- **SM-12** Sitemap size ≤ 50 MB and URL count ≤ 50,000. Split via sitemap index if exceeded.
- **SM-13** `robots.txt` references the sitemap (`Sitemap: https://...`).
- **SM-14** Sitemap submitted to GSC (and Bing WMT for GEO-critical sites).
- **SM-15** For programmatic sites, sitemap is dynamically generated from the database — not a static file.
- **SM-16** Dynamic sitemap is cached appropriately (edge cache, 1h hard + 24h soft).
- **SM-17** Dynamic sitemap queries exclude inactive / unpublished / noindexed / canonicalised-away content.
- **SM-18** For multi-content sites, a sitemap index (`/sitemap.xml` as index) references per-type sitemaps.

---

## Severity guidance

- Sitemap missing or unreachable → **High**
- Sitemap full of 404s or redirects → **High**
- `<lastmod>` identical across all URLs (nightly rebuild) → **High** (damages a global signal)
- `noindex` URLs in sitemap → **Medium**
- `<changefreq>weekly</changefreq>` on every URL regardless of reality → **Medium**
- Missing `<lastmod>` entirely → **Medium**
- Sitemap not submitted to GSC → **Low**
- No image/video sitemaps when images/videos drive traffic → **Low**
