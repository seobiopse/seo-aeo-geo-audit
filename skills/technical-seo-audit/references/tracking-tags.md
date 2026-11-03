# Tracking tag validation across pages

Goal: confirm the right tags are on every page that needs them, with the right IDs, firing once, and not breaking performance or consent. A tag missing from a template silently loses data, so check coverage by sampling templates, not only the homepage.

## 1. What the probe can and cannot see

`scripts/tech_probe.py` reads the raw HTML of a sample of pages and reports, per tag: how many pages have it, which IDs, and which pages lack it (`tracking_coverage`).

It can detect: Google Tag Manager, GA4, Universal Analytics (retired), Google Ads, Meta Pixel, Microsoft UET, LinkedIn Insight, TikTok Pixel, Hotjar, Microsoft Clarity, Segment, HubSpot, Plausible.

It cannot see:
- Tags that Google Tag Manager (or another tag manager) loads after page load. If GTM is present, the individual tags inside the container are invisible to the probe. Verify them in the browser.
- Tags injected by client-side JavaScript or consent platforms after the user accepts.
- Whether a hit was actually sent, or sent with the right parameters.

So: "not found in raw HTML" is `info` when a tag manager is present, and a finding only when you have also checked the browser.

## 2. Sample the right pages

Cover each template, not just many URLs of one kind: home, category/listing, detail (product, job, article), search results, form/lead, cart/checkout, thank-you/confirmation, 404, and any subdomain or microsite that shares the property. The probe spreads its sample across sitemap path prefixes. Add missing templates with `--urls-file`. Thank-you and checkout pages are often not in the sitemap, so add them by hand.

For a small site (under about 30 pages), sample all of them.

## 3. Browser verification (rendered)

Run on at least the home page, one detail page and one conversion page.

1. **Network panel.** Reload and filter for: `collect` or `g/collect` (GA4), `gtm.js`, `tr/?id=` or `facebook.com/tr` (Meta), `bat.bing.com` (UET), `px.ads.linkedin.com` (LinkedIn), `analytics.tiktok.com`. Record the ID in each request.
2. **Console snippets.**

   ```js
   ({
     dataLayerLen: (window.dataLayer || []).length,
     gtmContainers: Object.keys(window.google_tag_manager || {}),
     hasFbq: typeof window.fbq === 'function',
     hasGtag: typeof window.gtag === 'function'
   })
   ```
3. **Route changes (SPAs, Next.js App Router).** Click an internal link without a full reload and check that a new `page_view` hit fires. Frameworks do not send it automatically unless GTM's History Change trigger or an explicit router listener is set up. Missing route-change pageviews undercount traffic.
4. **Consent.** Load with a clean profile and no consent: confirm no analytics/ad cookies and no ad/analytics hits before consent where required. Check Consent Mode v2 defaults (`ad_storage`, `ad_user_data`, `ad_personalization`, `analytics_storage` = denied). Dismissing the banner is not consent.
5. **Conversion events.** Trigger one conversion in a test environment; confirm the event fires once, on the right page only.

## 4. How to judge the results

| Observation | Finding | Severity |
|---|---|---|
| Primary analytics tag missing on a template that gets traffic | Data loss on that template | High |
| Tag present on most sampled pages but not all (probe `tracking-inconsistent`) | Inconsistent deployment | High |
| Different IDs for the same tag across pages, or a test/staging ID in production | Data split or polluted | High |
| GA4 `gtag.js` inline plus GTM also configured to fire GA4 | Probable duplicate pageviews | Medium |
| Two GTM containers or two GA4 IDs without a reason | Double counting or orphaned config | Medium |
| `UA-` code still present | Dead code adding weight | Medium |
| Pixel on all pages, but conversion event also on all pages | Inflated conversions | High |
| GTM `<noscript>` iframe missing | Minor gap for no-JS users | Low |
| No tags in raw HTML and no tag manager | Either none installed or all JS-injected: check the browser | Info until verified |
| Heavy tag weight or long tasks from third-party scripts (PageSpeed/Lighthouse third-party summary) | Performance cost | Medium |

If the site has a staging environment, confirm staging does not report into production IDs.

## 5. Placement and loading (Next.js and similar)

- Put the GTM/GA snippet in the root layout so every route gets it, not per page.
- Next.js: use the framework's script component with `afterInteractive` (or the official GTM/GA component). `beforeInteractive` blocks rendering. `lazyOnload` can miss quick-bounce pageviews.
- Keep tags out of components that only mount on some routes.

## 6. Reporting

- Include a coverage table in the report: tag, pages with it / pages sampled, IDs, missing URLs.
- State the sample size and the templates covered. Coverage claims apply to the sample.
- Never include secret values. Tag IDs (GTM-, G-, pixel IDs) are public and fine to list; API keys and tokens are not.
- For deeper per-platform setup (events, Enhanced Conversions, CAPI, consent), use `seo-aeo-geo-audit/references/tracking-validation.md` (TRK-1 to TRK-19) when that skill is installed.
