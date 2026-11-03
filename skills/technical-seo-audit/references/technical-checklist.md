# Technical SEO checklist

Scope: what engineers can fix in code, config or infrastructure. Content quality, E-E-A-T, AEO, GEO, AI citation and VDS belong to the `seo-aeo-geo-audit` skill.

Google-sourced limits, retired features and thresholds in this checklist were re-checked on 2026-11-03 against Search Central; sources are in `../seo-aeo-geo-audit/references/google-guidance-alignment.md` (when that skill is installed) and on the pages it cites. Re-check the source page before quoting a number in a client report.

Every item ends as `pass`, `warn`, `fail` or `not measured`. Never guess. If you could not test an item, mark it `not measured` and say why. `warn` and `fail` become findings.

`scripts/tech_probe.py` gives raw-HTML evidence for most items (its hints cite the `TECH-xx` ids below). Items marked **(browser)** need a rendered page or the Network panel.

---

## TECH-07. Stack and architecture (do this first)

Identify the stack from live evidence, record the evidence and a confidence level (hint, likely, unknown). Do not infer a stack from URL shapes alone (`/dashboard`, `/product/<slug>` exist on every stack).

- **07.1** Stack named with evidence (probe `frameworks_seen`, response headers, cookies, asset paths, meta tags).
- **07.2** Matching profile loaded from `seo-aeo-geo-audit/references/` if that skill is installed (React/Next.js, WordPress, Shopify, static, Angular, PHP/Laravel, Wix/Webflow). Otherwise apply this checklist only and say so.
- **07.3** Environment noted: production, staging, localhost, preview deploy. Staging and preview hosts must not be indexable.

## TECH-01. Crawl and indexation controls

- **01.1** `robots.txt` returns 200 (a 4xx is treated as "no robots.txt"; a 5xx pauses Google's crawling), is under 500 KiB, has no blanket `Disallow: /` for `*`, lists the sitemap, and uses only supported fields (`user-agent`, `allow`, `disallow`, `sitemap`). `crawl-delay` and `noindex` lines are not supported by Google.
- **01.2** No important section is blocked in `robots.txt`. CSS/JS needed for rendering are not blocked.
- **01.3** `noindex` (meta robots or `X-Robots-Tag`) is on private and thin pages and absent from money and content pages. Check the sample: every `noindex` found is intended. A noindexed URL must not be blocked in `robots.txt`, or Google never sees the tag.
- **01.4** Private and transactional URLs (`/cart`, `/checkout`, `/login`, `/register`, `/account`, `/dashboard`) are `noindex` or disallowed and are not in the sitemap. Note `Disallow` stops crawling, not indexing.
- **01.5** Staging, preview and development hosts return `noindex` or are behind auth.
- **01.6** AI-crawler policy in `robots.txt` is intentional (GPTBot, ClaudeBot, PerplexityBot, CCBot, Google-Extended). Report what is blocked, not whether it should be.
- **01.7** Non-HTML endpoints (`/api/`, JSON, feeds) send `X-Robots-Tag: noindex` where they should not be indexed.

## TECH-02. Status codes and redirects

- **02.1** Sampled URLs return 200. Sitemap URLs returning 3xx/4xx/5xx are listed.
- **02.2** Missing pages return a real 404/410 (not a 200 "not found" page, i.e. a soft 404).
- **02.3** Redirects are 301/308 for permanent moves, one hop where possible, no chains or loops. Googlebot follows up to 10 hops (robots.txt: 5), but fewer is better. JavaScript and meta-refresh redirects are a last resort.
- **02.4** One canonical host: HTTP to HTTPS, and www vs non-www, each a single 301.
- **02.5** Trailing-slash policy is consistent and redirected.
- **02.6** No 5xx under normal load on the sample.

## TECH-03. Sitemaps

- **03.1** Sitemap is valid XML, referenced in `robots.txt`, and reachable.
- **03.2** Every listed URL is canonical, indexable, 200, and on the same host.
- **03.3** `lastmod` reflects real content changes. If most entries share one date it is probably the generation time.
- **03.4** `changefreq` and `priority` are ignored by Google. Report as `info`, not as a defect. `lastmod` counts only if consistently accurate.
- **03.5** Sitemap index and size limits respected (50,000 URLs or 50 MB uncompressed per file).
- **03.6** No private, parameterised, redirected or noindex URLs listed.

## TECH-04. Canonicals and duplicate URLs

- **04.1** Every indexable page has exactly one self-referencing absolute canonical on the final URL, set with the link element or the HTTP header (not both). Canonicals are a hint, not a rule; redirects are the stronger signal.
- **04.2** Canonical host and protocol match the preferred host.
- **04.3** Parameter variants (`?sort=`, `?page=`, UTM, session IDs) canonicalise to the clean URL or are blocked from crawl.
- **04.4** Faceted navigation does not generate unlimited crawlable combinations.
- **04.5** Pagination uses crawlable links (`<a href>`), not only JS "load more".
- **04.6** Old IDs and alternate slugs 301 to the canonical slug.

## TECH-05. Document head and basics

- **05.1** One `<title>` and one meta description per page, unique across the sample. Google sets no length limit (it truncates to device width), so flag empty, duplicate, vague, stuffed or boilerplate text, not a character count.
- **05.2** An `<h1>` is present in raw HTML. Google does not require exactly one and says heading order and count do not matter for Search: multiple H1s or skipped levels are `Low`, a missing H1 is `Medium`.
- **05.3** `<meta name="viewport">` present. `<html lang>` set.
- **05.4** Open Graph and Twitter tags on shareable pages (`info`/`low`).
- **05.5** `charset` declared early. No `<head>` content after `<body>` starts (breaks parsers).

## TECH-06. Structured data (technical validity)

- **06.1** JSON-LD is in the raw HTML (not injected after load) and parses without errors.
- **06.2** `@type` matches the page type; required properties are present (check with Rich Results Test).
- **06.3** Ratings, prices and availability in markup match what is visible on the page.
- **06.4** `Organization`/`WebSite` once at layout level; `BreadcrumbList` on deep pages.
- **06.5** Markup for features Google no longer shows (FAQ and HowTo rich results, sitelinks search box `SearchAction`, special announcements, practice problems) is `Info` when present and is never reported as missing. `Speakable` is beta and niche. `data-vocabulary.org` markup is outdated.

## TECH-08. JavaScript and rendering

See `javascript-rendering.md` for the method and the Next.js specifics.

- **08.1** Raw HTML contains the title, meta description, canonical, H1 and the main content (`js_shell_suspect` is false).
- **08.2** Raw HTML contains real `<a href>` links for navigation and pagination (not only click handlers).
- **08.3** JSON-LD and meta tags are in the server response, not added by client code.
- **08.4** **(browser)** Rendered DOM matches raw HTML for title, canonical, H1, robots and main content. List every difference.
- **08.5** Content hidden behind tabs, accordions, infinite scroll or "load more" is present in the DOM or reachable by crawlable URL.
- **08.6** No user-agent-based content or redirect differences (compare default UA with Googlebot UA).
- **08.7** Soft 404s: client-rendered "not found" views return a real 404 status.
- **08.8** Hydration errors and failed script/API calls in the console are absent on sampled pages. **(browser)**
- **08.9** Next.js: router type identified, page components are server-rendered, metadata is set through the framework API, `notFound()` is used, `next/link` is used for navigation.
- **08.10** Raw HTML size is reasonable and framework payload (for example `__NEXT_DATA__`) is not bloated. Googlebot processes only the first 2 MB of an HTML file, so critical content and links must sit within it.
- **08.11** JavaScript does not change a canonical or robots meta that the HTML already sets (Google may keep the HTML value, and a `noindex` in the HTML can stop rendering). Dynamic rendering is a workaround, not a fix.
- **08.12** **(browser)** Nothing critical depends on permission prompts, cookies or storage that persist between loads, WebSockets or WebRTC (Googlebot declines prompts, clears storage and does not support those transports).

## TECH-09. Performance and delivery

- **09.1** Google has no single "page experience signal"; Core Web Vitals are the only part its ranking systems use. If a PageSpeed API key was provided: mobile and desktop scores recorded, with field data (CrUX) preferred over lab data. LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1 at the 75th percentile. Without a key, mark `not measured`.
- **09.2** TTFB under about 800 ms on the sample (single request, one location: re-test before reporting).
- **09.3** Compression (`gzip`/`br`) enabled. HTML under about 500 KB uncompressed.
- **09.4** `Cache-Control` set sensibly: long-lived hashed assets, revalidation for HTML. Public pages are not `no-store` without reason.
- **09.5** Session cookies are not set on cacheable public pages (they can defeat CDN caching).
- **09.6** LCP image is a real file with `fetchpriority="high"`, not lazy-loaded, not an inline base64 `data:` URI.
- **09.7** No large inline base64 images (over ~50 KB in total in the HTML).
- **09.8** Images have `width`/`height` (prevents layout shift) and below-the-fold images are lazy.
- **09.9** Render-blocking CSS/JS minimised; third-party scripts deferred/async; fonts use `font-display`.

## TECH-10. Security and server hygiene

- **10.1** HTTPS everywhere, valid certificate, no mixed content.
- **10.2** HSTS header present on HTTPS sites (`low`).
- **10.3** Debug mode off in production: error pages show no stack traces (Laravel `APP_DEBUG`, framework dev overlays).
- **10.4** `X-Powered-By`/`Server` do not disclose versions (`info`).
- **10.5** Admin and login paths are not indexable and not linked from public pages.

## TECH-11. Tracking tags

See `tracking-tags.md`. Evidence comes from the probe's `tracking_coverage` plus browser checks.

- **11.1** The primary analytics tag (GA4 or equivalent) is present on every sampled template: home, listing, detail, article, form, thank-you, 404 where relevant.
- **11.2** Tag manager container (GTM) present on every page, with the `<noscript>` iframe right after `<body>`.
- **11.3** Ad and marketing pixels (Google Ads, Meta, Microsoft UET, LinkedIn, TikTok) present on all pages where those channels run, and conversion events only on conversion pages.
- **11.4** One ID per tag type unless intentional. IDs are the production IDs (not test, dev or staging).
- **11.5** No duplicate firing (inline `gtag.js` plus GTM sending the same GA4 hit; two containers).
- **11.6** Retired Universal Analytics (`UA-`) code removed.
- **11.7** **(browser)** The tag actually fires: hit visible in the Network panel on first load and on client-side route changes (SPAs).
- **11.8** **(browser)** Consent behaviour: no ad/analytics cookies before consent where required; Consent Mode v2 defaults set.
- **11.9** Tag weight and impact on INP/TBT noted (Lighthouse third-party audit, or PageSpeed output).

## TECH-12. International (only if the site has multiple languages or regions)

- **12.1** `hreflang` annotations are reciprocal, use valid codes, include `x-default`, and point to 200 canonical URLs.
- **12.2** Each language version has a self-referencing canonical.
- **12.3** Language switching uses crawlable links, not geo-redirects that block crawlers.

## TECH-13. Images and media (technical only)

- **13.1** Modern formats (WebP/AVIF) with a fallback where needed, responsive `srcset`/`sizes`.
- **13.2** Images are on crawlable URLs, not blocked in `robots.txt`, and have a successful response.
- **13.3** `alt` attribute present (probe: `images_no_alt`). Alt quality is a content matter.
