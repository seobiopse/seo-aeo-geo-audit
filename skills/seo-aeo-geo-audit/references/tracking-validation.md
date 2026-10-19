# Tracking Code Validation Reference

Audit for marketing tracking tags: presence, correct configuration, no duplicate firing, consent compliance. Broken tracking is invisible to users and to Google, but it bleeds the marketing team's ability to measure outcomes.

Read whenever an audit targets a production site with any form of paid media, analytics, or conversion tracking.

## What this audit catches

1. **Missing tags** — e.g., the page doesn't fire GA4 at all.
2. **Wrong IDs** — test / dev IDs shipped to production.
3. **Duplicate firing** — GA4 fires twice per pageview (inflated metrics, attribution breaks).
4. **Incorrect event configuration** — custom events not firing, parameters missing.
5. **Consent mode not implemented** — EU/UK/CA users tracked without consent (legal risk).
6. **Third-party scripts degrading performance** — LCP penalty, INP penalty.
7. **Broken Enhanced Conversions / Server-side tagging** — Google Ads misattribution.

## Table of contents

1. [What should fire (standard stack)](#1-standard-tracking-stack)
2. [Google Analytics 4 (GA4)](#2-ga4)
3. [Google Tag Manager (GTM)](#3-gtm)
4. [Google Ads conversion tag + Enhanced Conversions](#4-google-ads)
5. [Meta Pixel (Facebook/Instagram Ads)](#5-meta-pixel)
6. [Microsoft UET (Bing Ads)](#6-bing-uet)
7. [LinkedIn Insight Tag](#7-linkedin-insight)
8. [TikTok Pixel](#8-tiktok-pixel)
9. [Consent mode (EU/UK/CA users)](#9-consent-mode)
10. [Performance impact checks](#10-performance-impact)
11. [Audit checklist](#11-audit-checklist)

---

## 1. Standard tracking stack

Typical 2026 marketing site stack:

| Tag | Purpose | Load method | Mandatory? |
|---|---|---|---|
| GA4 | Analytics | GTM or `gtag.js` | Yes |
| GTM | Tag orchestration | Inline in `<head>` | Recommended |
| Google Ads conversion | Paid search / PMax conversions | via GTM | If running Google Ads |
| Meta Pixel | Paid social (Meta) conversions | via GTM or inline | If running Meta Ads |
| Microsoft UET | Bing Ads conversions | via GTM or inline | If running Bing Ads |
| LinkedIn Insight Tag | B2B campaigns | via GTM or inline | If running LinkedIn Ads |
| TikTok Pixel | TikTok Ads conversions | via GTM or inline | If running TikTok Ads |
| Consent banner | Cookie consent | e.g., Cookiebot, OneTrust, Klaro | Yes in EU/UK/CA |

## 2. GA4

### How to verify GA4 is firing

1. Install the **Google Analytics Debugger** Chrome extension OR open DevTools → Network → filter `collect?v=2`.
2. Load the page.
3. You should see at least ONE `https://www.google-analytics.com/g/collect?v=2&...` request on pageview.
4. If loading via GTM: also check `https://www.googletagmanager.com/gtm.js?id=GTM-XXXXXX` loads first.

### Correct basic setup (via gtag.js — if NOT using GTM)

```html
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

### Correct via GTM (preferred)

Single GTM snippet in `<head>`:

```html
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-XXXXXXX');</script>
<!-- End Google Tag Manager -->
```

Plus the `<noscript>` fallback just after `<body>`:
```html
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-XXXXXXX"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
```

Then GA4 is configured as a tag inside GTM, not inline.

### Common GA4 problems

- **Dev ID in prod** — `G-TEST123` shipped instead of production ID. Flag: check the measurement ID against what the marketing team expects.
- **GA4 fires twice** — both `gtag.js` inline AND GTM container firing GA4 = duplicate pageviews. Pick one.
- **No events beyond `page_view`** — purchases, form submits, scroll depth not configured. Audit scope: check for `purchase`, `generate_lead`, `sign_up`, `add_to_cart` events as applicable.
- **`send_page_view: false` not respected** — custom routing (SPA) without manual `page_view` events leaves analytics empty beyond the first load.
- **Cross-domain linking broken** — if traffic flows between subdomains (e.g., `www.example.com` → `product1.example.com`), configure the measurement ID to treat them as one property.

## 3. GTM

### Verify GTM is loaded

- `window.google_tag_manager` exists in console.
- Network panel shows `https://www.googletagmanager.com/gtm.js?id=GTM-XXXXXXX`.

### Common GTM problems

- **Preview / debug mode accidentally left on.** `GTM-XXXXXXX&gtm_auth=...&gtm_preview=env-X&gtm_cookies_win=x` in the URL means the site is serving debug. Real users see the GTM preview bar.
- **Container not published.** Changes staged in GTM but never clicked "Publish" → live site still serves old tags.
- **Tag sequencing broken.** Google Ads conversion tag firing before GA4 client ID is available, breaking Enhanced Conversions.
- **Built-in variables not enabled.** Common one: `Click Classes` / `Click Element` not enabled → click-based triggers silently fail.

## 4. Google Ads conversion tag + Enhanced Conversions

### Base tag (sitewide)
Fires on every page — builds the retargeting audience.

```html
<!-- Global site tag (gtag.js) - Google Ads -->
<script async src="https://www.googletagmanager.com/gtag/js?id=AW-XXXXXXXXX"></script>
<script>
  gtag('js', new Date());
  gtag('config', 'AW-XXXXXXXXX');
</script>
```

### Conversion tag (fires on conversion)
```js
gtag('event', 'conversion', {
  'send_to': 'AW-XXXXXXXXX/CONVERSION_LABEL',
  'value': 100,
  'currency': 'INR',
  'transaction_id': 'ORDER-2026-042'
});
```

### Enhanced Conversions
Hashes user-provided data (email, phone, name) before sending, for better attribution. Requires:
- User data collected at conversion (email, phone, name — usually from checkout form).
- Hashed client-side using SHA-256.
- Sent as `user_data` parameter.

### Common Google Ads problems

- **Conversion tag fires on every page** — marketing team sees pageview-equivalent conversions. Flag: ensure conversion tags fire only on the success/thank-you page.
- **Enhanced Conversions not hashed** — raw PII leaving the browser. Privacy + compliance issue.
- **Wrong conversion label** — tag configured for the wrong conversion action in Google Ads.

## 5. Meta Pixel (Facebook/Instagram Ads)

### Base code

```html
<!-- Meta Pixel Code -->
<script>
  !function(f,b,e,v,n,t,s)
  {if(f.fbq)return;n=f.fbq=function(){n.callMethod?
  n.callMethod.apply(n,arguments):n.queue.push(arguments)};
  if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
  n.queue=[];t=b.createElement(e);t.async=!0;
  t.src=v;s=b.getElementsByTagName(e)[0];
  s.parentNode.insertBefore(t,s)}(window, document,'script',
  'https://connect.facebook.net/en_US/fbevents.js');
  fbq('init', '1234567890');
  fbq('track', 'PageView');
</script>
<noscript><img height="1" width="1" style="display:none"
  src="https://www.facebook.com/tr?id=1234567890&ev=PageView&noscript=1"/></noscript>
<!-- End Meta Pixel Code -->
```

### Standard events
- `PageView` — every page
- `ViewContent` — product / detail pages
- `AddToCart`, `InitiateCheckout`, `Purchase` — e-commerce
- `Lead`, `CompleteRegistration` — lead gen

### Common Meta Pixel problems

- **`PageView` but no standard events configured** — only top-of-funnel data in Meta's reports.
- **Wrong pixel ID** — test pixel live on prod.
- **Not using Conversions API (CAPI)** in 2026 — iOS ATT + Apple Intelligent Tracking Prevention drop 30–40% of browser-side pixel events. CAPI (server-side) recovers them.
- **Duplicate firing** — if Pixel is inline + also via GTM, every event doubles.

### Meta Pixel Helper extension
Install on Chrome. It shows every event firing per page + any errors.

## 6. Microsoft UET (Bing Ads)

```html
<script>
  (function(w,d,t,r,u)
  {var f,n,i;w[u]=w[u]||[],f=function()
  {var o={ti:"12345678"}; o.q=w[u],w[u]=new UET(o),w[u].push("pageLoad")},
  n=d.createElement(t),n.src=r,n.async=1,n.onload=n.onreadystatechange=function()
  {var s=this.readyState;s&&s!=="loaded"&&s!=="complete"||(f(),n.onload=n.onreadystatechange=null)},
  i=d.getElementsByTagName(t)[0],i.parentNode.insertBefore(n,i)})
  (window,document,"script","//bat.bing.com/bat.js","uetq");
</script>
```

### UET events
- `pageLoad` — every page
- Custom events via `window.uetq.push('event', ...)` for conversions

### Verifying UET
- Install the **UET Tag Helper** Chrome extension.
- Check Bing Ads UI → Conversion Goals → last fired time.

## 7. LinkedIn Insight Tag

B2B-critical. Unique to LinkedIn in that it captures the visitor's LinkedIn company (if they're signed in), enabling account-based retargeting.

```html
<script type="text/javascript">
_linkedin_partner_id = "1234567";
window._linkedin_data_partner_ids = window._linkedin_data_partner_ids || [];
window._linkedin_data_partner_ids.push(_linkedin_partner_id);
</script><script type="text/javascript">
(function(l) {
if (!l){window.lintrk = function(a,b){window.lintrk.q.push([a,b])};
window.lintrk.q=[]}
var s = document.getElementsByTagName("script")[0];
var b = document.createElement("script");
b.type = "text/javascript";b.async = true;
b.src = "https://snap.licdn.com/li.lms-analytics/insight.min.js";
s.parentNode.insertBefore(b, s);})(window.lintrk);
</script>
```

### Verifying
- LinkedIn Campaign Manager → Insight Tag status.
- Chrome DevTools → Network → `lintrk` request on pageview.

## 8. TikTok Pixel

```html
<!-- TikTok Pixel Code Start -->
<script>
!function (w, d, t) {
  w.TiktokAnalyticsObject=t;var ttq=w[t]=w[t]||[];ttq.methods=["page","track","identify","instances","debug","on","off","once","ready","alias","group","enableCookie","disableCookie"],
  // ... etc
  ttq.load('TIKTOK_PIXEL_ID');
  ttq.page();
}(window, document, 'ttq');
</script>
<!-- TikTok Pixel Code End -->
```

## 9. Consent mode (EU/UK/CA users)

For EU/UK (GDPR) and California (CCPA/CPRA) users, tracking without consent is illegal. You MUST:

1. Show a consent banner on first visit.
2. Default tracking to OFF until consent.
3. Update tracking state when consent changes.

### Google Consent Mode v2 (required for Google Ads since March 2024)

```js
// BEFORE any tag fires, set defaults
gtag('consent', 'default', {
  'ad_storage': 'denied',
  'ad_user_data': 'denied',
  'ad_personalization': 'denied',
  'analytics_storage': 'denied',
  'functionality_storage': 'denied',
  'personalization_storage': 'denied',
  'security_storage': 'granted',
  'wait_for_update': 500
});

// After user consents:
gtag('consent', 'update', {
  'ad_storage': 'granted',
  'ad_user_data': 'granted',
  'ad_personalization': 'granted',
  'analytics_storage': 'granted'
});
```

### Verifying consent mode

- Chrome DevTools → Application → Cookies → check that no `_ga`, `_fbp`, `_uetsid` cookies exist BEFORE consent.
- After consent: those cookies appear.
- After revoking: cookies remain (until expiry) but no new events send.

### Common consent problems

- **Default state not set** — tags fire before consent → GDPR violation.
- **Banner dismissal counted as consent** — user clicks "X" to close the banner → implied consent → illegal in EU.
- **Only GDPR banner, no CPRA path** — California users need an explicit "Do Not Sell or Share" option.
- **Consent state not persisted** — every page reload re-shows the banner.

## 10. Performance impact

Marketing tags routinely cost 200–600 ms of LCP and hundreds of ms of INP. Audit checks:

- **Total tag weight** — Network panel → filter `bat.bing | connect.facebook | googletagmanager | snap.licdn | ttq`. Total KB transferred.
- **Tag blocking** — Lighthouse → "Third-party code" audit. Shows per-domain impact.
- **Consolidate via GTM** — one `gtm.js` fetch can host GA4, Ads, Meta, Bing, LinkedIn instead of six separate snippets.
- **Defer non-critical** — consent banner loads first (legal), GA4 fires on consent, Meta/LinkedIn/TikTok fire later via GTM triggers.

## 11. Audit checklist

- **TRK-1** GA4 (or primary analytics) fires on every page — verified via Network panel or GA Debugger.
- **TRK-2** Measurement ID is the production ID, not a test/dev ID.
- **TRK-3** No duplicate GA4 firing (inline gtag + GTM = duplicate).
- **TRK-4** Key conversion events fire correctly — `purchase`, `generate_lead`, `sign_up`, `add_to_cart` as applicable.
- **TRK-5** GTM container is published (not in preview mode on prod).
- **TRK-6** Google Ads conversion tag fires only on thank-you / success pages.
- **TRK-7** Enhanced Conversions: user-provided data is hashed client-side before sending.
- **TRK-8** Meta Pixel fires `PageView` site-wide + event-specific standard events on conversion pages.
- **TRK-9** Meta Pixel uses Conversions API (CAPI) for mission-critical conversions (iOS loss mitigation).
- **TRK-10** Microsoft UET fires on every page if running Bing Ads.
- **TRK-11** LinkedIn Insight Tag fires on every page if running LinkedIn Ads.
- **TRK-12** TikTok Pixel fires on every page if running TikTok Ads.
- **TRK-13** Consent banner visible for EU/UK/CA users on first visit.
- **TRK-14** Google Consent Mode v2 `default` state is "denied" for `ad_storage`, `ad_user_data`, `ad_personalization`, `analytics_storage`.
- **TRK-15** No analytics / ads cookies exist before user consent (verify in DevTools → Application → Cookies).
- **TRK-16** Consent banner dismissal (X button) does NOT count as consent.
- **TRK-17** Total tag weight ≤ 150 KB transferred on initial load.
- **TRK-18** No tracking tag causes > 300 ms INP (Lighthouse third-party audit).
- **TRK-19** No tracking-tag-related console errors on page load.

---

## Severity guidance

- Missing GA4 in production → **High** (blind marketing)
- Dev/test measurement ID in prod → **High**
- Duplicate GA4 firing → **High** (inflated conversion metrics)
- No consent mode in EU/UK/CA → **Critical** (legal risk)
- Enhanced Conversions unhashed → **High** (privacy violation)
- Third-party tags costing > 500 ms LCP → **High**
- Meta Pixel without CAPI → **Medium**
- Consent banner X-click = consent → **High** (GDPR violation)
- Google Ads conversion tag firing on every page → **Medium** (skews Google Ads metrics)
