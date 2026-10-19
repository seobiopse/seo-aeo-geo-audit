# SEO Audit Checklist (Engineering Definition-of-Done)

Use any time an engineer is working on a page — during dev on localhost, on a PR preview or staging URL, or on production after deploy. Every page shipped should pass this list.

Mark each item `pass`, `warn`, or `fail`. Use the issue framework for anything not a pass.

## Table of contents

1. [Crawl & indexation controls](#1-crawl--indexation-controls)
2. [URL structure & redirects](#2-url-structure--redirects)
3. [Rendering & JS dependency](#3-rendering--js-dependency)
4. [`<head>` metadata](#4-head-metadata)
5. [Structured data](#5-structured-data)
6. [Content & heading hierarchy](#6-content--heading-hierarchy)
7. [Internationalization](#7-internationalization)
8. [Images & media](#8-images--media)
9. [Performance & Core Web Vitals](#9-performance--core-web-vitals)
10. [Security & accessibility basics](#10-security--accessibility-basics)
11. [Sitemaps & robots](#11-sitemaps--robots)

---

## 1. Crawl & indexation controls

- **1.1** `robots.txt` does NOT contain `User-agent: * \n Disallow: /` (unless site is intentionally private).
- **1.2** No page meant to rank has `<meta name="robots" content="noindex">`.
- **1.3** No page returns `X-Robots-Tag: noindex` in HTTP headers.
- **1.4** Staging-only noindex directives are REMOVED before prod deploy.
- **1.5** `<meta name="googlebot">` and `<meta name="bingbot">` are intentional if present.
- **1.6** Pages return HTTP 200, not 301/302/307/308/404/410/5xx.
- **1.7** No `Disallow: /` for critical bot user-agents (Googlebot, Bingbot, DuckDuckBot).

## 2. URL structure & redirects

- **2.1** URLs lowercase, hyphen-separated, no query strings for canonical content.
- **2.2** Trailing-slash policy consistent (all or none).
- **2.3** `www` vs `non-www` redirects to one canonical host.
- **2.4** `http://` 301-redirects to `https://`.
- **2.5** No redirect chains of more than one hop.
- **2.6** No internal links point to redirected URLs.
- **2.7** 404 page returns HTTP 404 (not 200 with a "not found" body).

## 3. Rendering & JS dependency

For React / Next.js codebases, also read `crawlability-react.md` for framework-specific checks.

- **3.1** Raw HTML (view-source) contains critical content — not only the rendered DOM.
- **3.2** `fetch('<url>')` from a browser console shows all critical text, canonical, structured data.
- **3.3** No critical content inside a `<noscript>` fallback only.
- **3.4** With JS disabled in Chrome DevTools, the page still shows critical text and navigation.
- **3.5** No User-Agent-based content swapping ("cloaking") — same URL returns same content for humans and bots.

## 4. `<head>` metadata

- **4.1** `<title>` present, unique per page, 30–60 chars.
- **4.2** `<meta name="description">` present, 110–160 chars, distinct from title.
- **4.3** `<link rel="canonical" href="...">` absolute self-URL for unique pages.
- **4.4** `<meta charset="utf-8">` within the first 1024 bytes.
- **4.5** `<meta name="viewport" content="width=device-width, initial-scale=1">` present.
- **4.6** OpenGraph: `og:title`, `og:description`, `og:url`, `og:image`, `og:type`.
- **4.7** Twitter Card: `twitter:card`, `twitter:title`, `twitter:description`, `twitter:image`.
- **4.8** Favicon link(s) — PNG + Apple touch.
- **4.9** No duplicate tags in `<head>`.
- **4.10** `<html lang="xx">` set correctly.

## 5. Structured data

For depth on `@graph`, `@id` cross-references, and per-page-type recipes, also read `structured-data-advanced.md`. For job-detail pages specifically, read `pseo-jobs-playbook.md`.

- **5.1** JSON-LD used (preferred over microdata/RDFa).
- **5.2** Homepage has `Organization` or `LocalBusiness` with name, logo, URL, `sameAs`.
- **5.3** Article/blog pages have `Article` or `NewsArticle` with `headline`, `image`, `datePublished`, `dateModified`, `author` (typed `Person`), `publisher`.
- **5.4** Product pages have `Product` with `name`, `image`, `description`, `sku`, `brand`, `offers`.
- **5.5** FAQ pages have `FAQPage` — visibility requirement (every Q/A visible on the page).
- **5.6** `BreadcrumbList` on pages with visible breadcrumbs.
- **5.7** Schema passes https://search.google.com/test/rich-results with no errors.
- **5.8** All `@id` values are absolute URLs.
- **5.9** No duplicate schema types for the same entity.

## 6. Content & heading hierarchy

- **6.1** Exactly one `<h1>` per page.
- **6.2** Heading levels don't skip.
- **6.3** Headings are semantic `<h1>`–`<h6>`, never `<div class="text-2xl font-bold">` used as a heading.
- **6.4** Main content in `<main>` / `<article>`.
- **6.5** Content above the fold answers the user's question within the first 100 words where possible.

## 7. Internationalization

Only if the site has multiple languages/regions.

- **7.1** `hreflang` includes every variant + self-referencing tag.
- **7.2** `x-default` hreflang present.
- **7.3** ISO 639-1 language codes; ISO 3166-1 region codes.
- **7.4** Hreflang URLs return HTTP 200.
- **7.5** `og:locale` matches `<html lang>`.

## 8. Images & media

- **8.1** All non-decorative images have descriptive `alt`.
- **8.2** Decorative images have `alt=""` (not missing `alt`).
- **8.3** Modern formats (`webp`, `avif`) with fallbacks.
- **8.4** `<img width>` and `height` set to prevent CLS.
- **8.5** `loading="lazy"` on below-the-fold images.
- **8.6** `og:image` ≥ 1200×630 absolute URL.
- **8.7** `VideoObject` schema on primary-content videos.

## 9. Performance & Core Web Vitals

- **9.1** LCP ≤ 2.5s mobile 4G throttled.
- **9.2** CLS ≤ 0.1.
- **9.3** INP ≤ 200ms.
- **9.4** FCP ≤ 1.8s.
- **9.5** Total page weight under ~1.5 MB where feasible.
- **9.6** Critical render-blocking resources minimised.
- **9.7** Fonts use `font-display: swap` and `<link rel="preload">`.
- **9.8** Third-party scripts audited.

## 10. Security & accessibility basics

- **10.1** HTTPS enforced. No mixed content.
- **10.2** HSTS header set.
- **10.3** CSP doesn't block Googlebot's inline scripts for structured data.
- **10.4** Color contrast ≥ 4.5:1 for body text; focusable elements keyboard-navigable.

## 11. Sitemaps & robots

- **11.1** `sitemap.xml` at `/sitemap.xml` (or index for large sites).
- **11.2** Only canonical, indexable URLs (no 404s, 301s, noindexed pages).
- **11.3** Absolute `https://` URLs.
- **11.4** `<lastmod>` accurate.
- **11.5** `robots.txt` references the sitemap.
- **11.6** `robots.txt` reachable, HTTP 200.
- **11.7** AI-crawler policies explicit (GPTBot, ClaudeBot, Google-Extended, PerplexityBot, CCBot) — allow if pursuing GEO, disallow if deliberately opting out.

---

## What to do after this checklist

Use the issue framework for every `warn`/`fail`. See SKILL.md Step 6 for report generation.
