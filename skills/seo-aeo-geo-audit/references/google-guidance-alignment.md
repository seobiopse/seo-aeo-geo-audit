# Google guidance alignment

What Google Search Central says, checked against this plugin on **2026-11-03**. Read this before attributing any claim to Google in an audit, and before setting a severity for something Google has retired or says it does not use.

Base: `https://developers.google.com/search/docs/` (paths below are relative to it). Most pages show no "last updated" date, so treat this file as a snapshot: re-check the source page before quoting a number or a date in a client report.

## How to use this file

- A finding that cites Google (limits, "required", "no longer supported") must match the table here. If it does not, check the source page first.
- Use `Info`, not a defect, for things Google says it ignores or no longer shows.
- Separate "Google says" from "this plugin's heuristic". The plugin has heuristics (E-E-A-T score, chunk density, n-gram overlap, extractable units) that are not Google metrics. Label them as such.
- Google warns that third-party "AEO/GEO" tools and services may promise gains or claim internal Google data (`fundamentals/ai-optimization-guide`, `fundamentals/third-party-seo`). This plugin does not have Google's data. Never present its scores as Google's, and never promise rankings or citations.

## 1. Features Google no longer shows or has reduced

| Item | What Google says | Plugin treatment |
|---|---|---|
| FAQ rich results | Deprecation notice 8 May 2026: no longer shown from 7 May 2026. Documentation removed 15 Jun 2026. (Since Aug 2023 they were limited to well-known government and health sites.) Source: Search Central "latest documentation updates" changelog. | `FAQPage` is optional markup. No Google rich result. Do not recommend it as a Google fix. Absence is `Info`. If present it must match visible text. |
| HowTo rich results | Removed; documentation removed Sep 2023 (changelog). | Optional. Absence is `Info`. |
| Sitelinks search box | Removed. `nositelinkssearchbox` rule archived Nov 2024 (changelog); special-tags page lists it as a feature that no longer exists. | `WebSite` + `SearchAction` no longer produces a Google feature. Do not flag its absence. |
| Special announcement markup | Documentation removed Sep 2025 (changelog). | Not recommended. |
| Practice problems | Documentation removed; no longer shown (changelog, Jan 2026). | Not recommended. |
| ClaimReview (fact check) | Page cautions that Google is phasing out support in Search. | Only if the site publishes fact checks; low value. |
| Speakable | Beta; US users, English, news publishers (Google Assistant). | Optional, niche. Do not put in default Article recipes. |
| `data-vocabulary.org` markup | No longer eligible for rich results. | Flag as outdated if found. |
| `rel="next"` / `rel="prev"` | Google no longer uses them (other engines might). | Not an SEO requirement for Google. Use crawlable links and unique URLs. |
| Meta keywords | Not used (starter guide). | Ignore; do not recommend. |
| `noarchive`, `nocache` | Listed as not used (robots-meta-tag page). | Do not recommend for Google. |
| `crawl-delay` in robots.txt | Not supported by Google. | Bing honours it; Google does not. |
| Sitemap `priority`, `changefreq` | Ignored. | Omit; `Info` if present. |
| Image sitemap `caption`, `geo_location`, `title`, `license` | Deprecated/removed. | Do not use. |
| Video sitemap `category`, `gallery_loc`, `autoplay`, `allow_embed`, `price`, `tvshow` | Removed. | Do not use. |
| `duns`, `leiCode` on Organization | Discouraged; use `iso6523Code`. | Prefer `iso6523Code`. |
| Dynamic rendering | "A workaround and not a long-term solution"; SSR, static rendering or hydration recommended. | Do not recommend as the fix. |
| AMP | Not required; AMP pages are indexed like other pages. | Not a requirement. |

## 2. Google AI features (AI Overviews, AI Mode)

Sources: `fundamentals/ai-optimization-guide`, `appearance/ai-features`.

- Eligibility: the page is indexed and eligible to show with a snippet. `ai-features` says there are no additional technical requirements and no special optimization is necessary.
- **Not needed for Google Search:** `llms.txt`, other "AI text files", special markup or Markdown versions, special schema.org markup, "chunking" content, rewriting for AI, long-tail keyword hunting, inauthentic "mentions". Creating these for other services is fine and neither helps nor harms Search.
- Controls: `nosnippet`, `data-nosnippet`, `max-snippet`, `noindex`. Crawling is governed by `robots.txt` for Googlebot. `Google-Extended` limits use for AI training and grounding in other Google systems.
- Measurement: AI Overviews and AI Mode clicks are counted in the Search Console Performance report under the "Web" search type. `ai-optimization-guide` also describes a Generative AI performance report.
- Good practice listed: crawlable (robots.txt, CDN), internal links, page experience, important content in text, images and video, structured data that matches visible text, current Merchant Center and Business Profile data.
- Open conflict between Google pages: `ai-optimization-guide` says a site must be included in "Search generative AI features" in Search Console; `ai-features` does not mention that step. Report the Search Console setting as "stated in one Google page; verify in the property".

Plugin treatment: `llms.txt`, chunk density, n-gram overlap, extractable units and query fan-out are retrieval-readiness heuristics for non-Google LLM systems and for general content quality. They are not Google requirements. A missing `llms.txt` is `Info`. Do not describe any of them as "what AI Overviews needs".

## 3. Things Google says not to focus on (SEO starter guide)

- Meta keywords: not used. Keyword stuffing is a spam violation.
- Keywords in the domain name or URL path: hardly any effect beyond breadcrumbs.
- Content length alone is not a ranking factor; no word-count target.
- Subdomains vs subdirectories: a business choice.
- Duplicate content is not a spam violation or "penalty" (it wastes crawl resources). Copying others' content is different.
- **Heading order and count do not matter for Search.** There is no ideal number of headings. Keep headings for users and accessibility; report order/count issues as `Low`.
- **E-E-A-T is not a ranking factor** (starter guide answers "No, it's not"). Trust is described as the most important part for evaluating quality; rater data is not used directly in ranking. The plugin's E-E-A-T score is a heuristic proxy, not a Google metric.
- TLD matters only for country targeting, and then at low weight.

## 4. Titles, snippets and display

- `<title>`: no length limit; Google truncates to fit the device width. Unique, clear, concise; avoid stuffing and boilerplate; name the site with a delimiter; make the main title distinct (for example the first H1). Google may also use `og:title`, headings, anchor text and `WebSite` structured data for the title link.
- Meta description: no length limit; snippets come mostly from page content, sometimes from the meta description. Unique per page.
- "~60 and ~160 characters" are display heuristics, not Google rules. Flag only empty, duplicate, vague, stuffed or boilerplate text.
- Snippet controls: `nosnippet`, `max-snippet:[n]`, `data-nosnippet`; `max-image-preview`, `max-video-preview`, `notranslate`, `noimageindex`, `unavailable_after`, `indexifembedded` (only with noindex).

## 5. Crawling, robots.txt, sitemaps, redirects

- **Technical requirements** (`essentials/technical`): Googlebot not blocked, page returns HTTP 200, page has indexable content.
- **robots.txt** (`crawling-indexing/robots/robots_txt`): supported fields are `user-agent`, `allow`, `disallow`, `sitemap`; `*` and `$` wildcards. Size limit 500 KiB. Most specific group wins; longest rule wins; on a tie the least restrictive rule wins. `*` does not match the AdsBot crawlers. Cached up to about 24 hours; "Request a recrawl" in Search Console to refresh. Status handling: 2xx parsed; 3xx followed up to 5 hops then treated as 404; 4xx except 429 treated as no robots.txt; 5xx or network errors pause crawling for 12 hours, then the last good copy is used for up to 30 days.
- `noindex` in robots.txt is not supported. A noindexed page must not be robots-blocked, or Google never sees the tag.
- **Fetch limits:** Googlebot reads the first 2 MB of an HTML file (64 MB for a PDF). The default for Google's crawlers is 15 MB. Supports gzip, deflate, br; HTTP/2 supported.
- **Status codes for crawling:** 4xx (not 429) dropped over time; 429 and 5xx slow crawling; 503/429 can be used briefly in an emergency (about 2 days before URLs may be dropped). Googlebot follows up to 10 redirect hops.
- **Redirects** (`301-redirects`): permanent signals are 301, 308, and an instant (0 s) meta refresh or JavaScript location; temporary are 302, 303, 307 and delayed meta refresh. Server-side redirects preferred; JavaScript redirects are a last resort. Site moves: keep redirects at least a year; Change of Address only for domain/subdomain moves.
- **Canonicals** (`consolidate-duplicate-urls`): redirects are the strongest signal, then `rel="canonical"`, then sitemap inclusion (weak). Absolute URLs; self-referencing is recommended; use the link element or the HTTP header, not both; `rel="canonical"` with `hreflang`/`lang`/`media`/`type` attributes is ignored; do not use robots.txt, the removal tool or noindex to choose a canonical.
- **Sitemaps** (`sitemaps/build-sitemap`, `large-sitemaps`): 50,000 URLs or 50 MB uncompressed per file; UTF-8; absolute URLs; `lastmod` used only if consistently and verifiably accurate; `priority` and `changefreq` ignored; sitemap index up to 50,000 sitemaps. News sitemap: articles from the last 2 days, up to 1,000 per file. Image sitemap: up to 1,000 images per URL. Video sitemap required fields: thumbnail, title, description (max 2,048 chars), and content or player location. `hreflang` in sitemaps uses `xhtml:link` via the combined-extensions format.
- **Faceted navigation:** use `robots.txt` wildcards to stop crawling of filter combinations; canonical and nofollow are described as less effective long term. Avoid `#` fragments for content.
- **Pagination:** unique URLs (`?page=n`) linked with `<a href>`; do not canonicalise page 1 for the series; `rel=next/prev` not used.
- **Crawlable links:** `<a href>` only. `<a onclick>`, `<span href>`, `routerLink` without href and `javascript:` hrefs are not recommended.
- **Mobile-first indexing:** same content, robots meta, structured data, titles and descriptions on mobile and desktop; do not lazy-load primary content on interaction.
- **Valid `<head>`:** only `title`, `meta`, `link`, `script`, `style`, `base`, `noscript`, `template`. Google ignores everything after an invalid element such as `iframe` or `img`.

## 6. JavaScript

- Google renders with an evergreen headless Chromium in a separate step after crawling; pages with HTTP 200 enter the render queue. Non-200 pages may skip rendering. No numeric render timeout is published.
- JavaScript may add a canonical only if the HTML has none, and must not change an existing one. JavaScript may add or change robots meta, but a `noindex` in the HTML may stop rendering, so removing it with JavaScript can fail.
- SPAs: soft 404s should redirect to a URL that returns a real 404 or inject `noindex`. Use the History API; fragment routing is unreliable (the AJAX-crawling scheme was deprecated in 2015).
- Googlebot declines permission prompts, clears storage and cookies between page loads, and does not support WebSockets or WebRTC. Provide fallbacks.
- Lazy loading: Google does not scroll or click; do not lazy-load above-the-fold content. Infinite scroll needs a persistent unique URL per chunk.
- Structured data may be generated with JavaScript (GTM or injected `application/ld+json`); dynamically generated Product markup can make Shopping crawls less frequent and less reliable.

## 7. Core Web Vitals and page experience

- There is no single "page experience signal". Core Web Vitals are the only part of page experience that Google's ranking systems use; HTTPS, mobile display, ads and interstitials are worth improving but are not direct ranking inputs.
- Current metrics and "good" thresholds: LCP within 2.5 s, INP under 200 ms, CLS under 0.1. INP replaced FID.
- Google notes that chasing a perfect score purely for SEO may not be the best use of time.

## 8. Structured data

- JSON-LD recommended; Microdata and RDFa acceptable if valid. All required properties must be present for eligibility; complete, accurate recommended properties beat many partial ones. Never mark up content users cannot see. Markup must follow the general guidelines (`structured-data/sd-policies`).
- Required properties moved or clarified in the pages read (verify the page before relying on any):
  - Article: none required; recommended `author`, `datePublished`, `dateModified`, `headline`, `image` (16:9, 4:3, 1:1; at least 50K pixels).
  - Product snippet: `name` plus one of `review`, `aggregateRating`, `offers`. Merchant listing: `name`, `image`, `offers` with `price` (above zero) and `priceCurrency`.
  - Organization: no required properties; Google reads `name`, `logo` (at least 112x112 px), `sameAs`, `address`, `contactPoint`, `legalName`, and more.
  - LocalBusiness: `address`, `name` required.
  - Event: `location`, `name`, `startDate` required; physical events open to the public.
  - Video: `name`, `thumbnailUrl`, `uploadDate` required.
  - JobPosting: `datePosted`, `description`, `hiringOrganization`, `jobLocation`, `title` required; Indexing API recommended.
  - Course: `name`, `description` required; English only.
  - Breadcrumb: `BreadcrumbList` with at least two `ListItem`, each with `position`.
  - Review snippet: a guideline on fake and undisclosed incentivised reviews was added (changelog, Jul 2026).
  - Site names: `WebSite` with `name` and `url` on the home page (JSON-LD, RDFa or Microdata).
- Favicon: `<link rel="icon">`, square, at least 8x8 px (more than 48x48 recommended), one per hostname.
- Byline dates: visible date plus `datePublished`/`dateModified`; keep them consistent; no future dates.

## 9. Spam policies and content

- Policy names (`essentials/spam-policies`): cloaking, doorway abuse, expired domain abuse, hacked content, hidden text and link abuse, keyword stuffing, link spam, machine-generated traffic, malicious practices, misleading functionality, scaled content abuse, scraping, site reputation abuse, sneaky redirects, thin affiliation, user-generated spam. The scope also covers manipulating generative AI responses in Search.
- Scaled content abuse explicitly includes generative AI tools used to create many pages without adding value. AI use itself is not banned; purpose and value decide.
- Site reputation abuse: EEA-specific handling differs (separate categorisation instead of a manual action); outside the EEA a manual action is possible.
- Helpful content (`fundamentals/creating-helpful-content`): "Who, How, Why"; bylines encouraged; disclose automation or AI use where readers would expect it; fabricated authors (AI headshots, invented credentials) are deception.
- `fundamentals/using-gen-ai-content`: fact-check everything (titles, descriptions, alt text, structured data); Merchant Center needs IPTC `DigitalSourceType` metadata on AI-generated images and labels on AI-generated product text.
- The Helpful Content system is part of core ranking (since March 2024). Panda, Penguin and Hummingbird are retired as separate systems.

## 10. Internationalisation

- Three equivalent methods for hreflang: HTML `<link>`, HTTP `Link` header, XML sitemap. Using all three gives no benefit.
- Each version lists itself and all others (return links required; unpaired tags are ignored), uses fully qualified URLs, and includes `x-default`.
- Language ISO 639-1, region ISO 3166-1 Alpha 2, script optional (`zh-Hant`). A country code alone is invalid. `es-419` is not supported.
- Google ignores geo meta tags and the `lang` attribute for language detection; it uses visible content. Do not auto-redirect by language. Googlebot sends no `Accept-Language`; do not block it by IP location.

## 11. Pages not read (out of scope for this plugin)

AMP validation and removal pages, Web Stories (3), aggregator and supplier units, ecosystem carousel, South Africa features, package tracking, UGC fresh data program, explicit-content guidelines, malware and Safe Browsing subpages, search operators for images, bubble chart analysis, social video analysis, pause-online-business, top places list, flexible sampling, ad networks and translation. FAQ, HowTo, special announcements and sitelinks search box feature pages no longer exist; their status above comes from the changelog (parts of which are summarised, not verbatim).
