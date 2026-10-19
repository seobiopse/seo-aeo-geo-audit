# React / Next.js Architecture Profile

Site-level audit patterns specific to React and Next.js stacks. Read whenever the audit target is a production React site — especially one using Next.js (App Router, Pages Router, or a hybrid of both), or any site using frameworks built on top of React (Remix, Gatsby, Astro with React islands).

**How this differs from `crawlability-react.md`:** that file covers PAGE-level rendering rules (per-page SSR vs CSR, `'use client'` boundaries, `useEffect` anti-patterns). This file covers SITE-level architectural patterns — things that span the whole app, affect deployment, or show up in multiple components consistently.

## Table of contents

1. [When to read this](#1-when-to-read-this)
2. [Multi-route / multi-subdomain architecture](#2-multi-route--multi-subdomain-architecture)
3. [next.config.js SEO-relevant settings](#3-nextconfigjs-seo-relevant-settings)
4. [Middleware — what's safe vs risky for SEO](#4-middleware--what-s-safe-vs-risky-for-seo)
5. [ISR / revalidation strategy](#5-isr--revalidation-strategy)
6. [Environment-specific canonicals](#6-environment-specific-canonicals)
7. [Shared layout components + schema injection](#7-shared-layout-components--schema-injection)
8. [API routes + crawl considerations](#8-api-routes--crawl-considerations)
9. [next/image optimization at the site level](#9-nextimage-optimization-at-the-site-level)
10. [Font loading strategy](#10-font-loading-strategy)
11. [Edge runtime vs Node runtime](#11-edge-runtime-vs-node-runtime)
12. [Common site-level anti-patterns](#12-common-site-level-anti-patterns)
13. [Audit checklist](#13-audit-checklist)
14. [Roadmap: other stack profiles](#14-roadmap-other-stack-profiles)

---

## 1. When to read this

Load this file when the audit target's stack is:

- **Next.js** (any version 13+) — App Router, Pages Router, or both.
- **React + custom SSR setup** (e.g., Express + React DOM server) — adapt the advice but most patterns translate.
- **Remix** — the rendering model is stricter and most anti-patterns don't apply, but schema and architecture rules do.
- **Gatsby** — build-time rendering; ISR concerns don't apply but the entity-graph + shared-schema patterns do.
- **Astro with React islands** — most of this file applies to the non-React parts too; React islands behave like small Client Components.

Skip this file when the stack is pure static HTML, WordPress, Shopify, or other non-React architectures — see Section 14 for the future-work roadmap on those stacks.

## 2. Multi-route / multi-subdomain architecture

A common pattern on modern sites: one parent brand with several subdomains (marketing site + docs + app + blog + product subdomains). Each subdomain is often its own Next.js deployment.

### The Organization entity graph pattern

The parent brand's homepage declares the canonical `Organization` with a stable `@id`. Every subdomain references that `@id` instead of redeclaring.

**On the parent site (`www.example.com/`):**
```json
{
  "@type": "Organization",
  "@id": "https://www.example.com/#organization",
  "name": "your brand",
  "url": "https://www.example.com",
  "sameAs": [ /* Wikipedia, Wikidata, Crunchbase, LinkedIn, ... */ ],
  "subOrganization": [
    { "@id": "https://docs.example.com/#organization" },
    { "@id": "https://blog.example.com/#organization" }
  ]
}
```

**On a subdomain (`docs.example.com/`):**
```json
{
  "@type": "Organization",
  "@id": "https://docs.example.com/#organization",
  "name": "your brand Docs",
  "parentOrganization": {
    "@id": "https://www.example.com/#organization"
  }
}
```

### Audit checks for multi-subdomain setups

- Every subdomain declares its own `@id` using its own hostname.
- Every subdomain references the parent via `parentOrganization` with the parent's `@id`.
- `sameAs` is consistent across subdomains (same LinkedIn, same Crunchbase, etc.) — inconsistent `sameAs` fragments the entity graph.
- Logos match across subdomains.
- Contact info (email / phone / support URLs) consistent across subdomains.
- Legal policies (Privacy, Terms, Cookies) linked from every subdomain's footer, ideally pointing to a single canonical set on the parent.

### Audit checks for monorepo / single-deployment multi-route

If your site is all served from one Next.js app (routes like `/products`, `/docs`, `/blog`, `/about`), the Organization graph is simpler — one declaration on the root. But watch for:

- Inconsistent metadata API usage across route segments (some using `export const metadata`, some using old `<Head>`).
- Shared layout forgetting to pass through per-page canonicals.
- `generateMetadata` functions that fetch data from different sources with different error-handling — silent failures cause fallback-to-default metadata.

## 3. `next.config.js` SEO-relevant settings

The config file has several knobs that affect SEO. Audit them explicitly.

### `trailingSlash`
- `false` (default) — URLs are `/about`.
- `true` — URLs are `/about/`.
- Pick one and be consistent. Inconsistency (some pages with slash, some without) creates duplicate-content risk.

### `rewrites` and `redirects`
- `rewrites` — internal URL rewrites. Users see one URL; Next serves another. OK for SEO *if* the canonical tag points to the user-facing URL.
- `redirects` — HTTP redirects. Specify `permanent: true` (which is a 308 in Next — search engines treat it the same as 301 for link-equity purposes) for permanent migrations.
- `redirects` with `permanent: false` is a 307 — use only for temporary redirects.

### `headers`
- Set `Cache-Control` appropriately per route.
- Set `X-Robots-Tag: noindex, nofollow` for staging environments via env-gated headers (see Section 6).
- Set `Content-Security-Policy` — make sure it doesn't block Googlebot's structured-data extraction (rare but real).

### `images.domains` / `images.remotePatterns`
- Allows `next/image` to fetch from external hosts. Missing entries cause silent image load failures — breaking LCP and image SEO.

### `i18n`
- Built-in internationalization routing. Generates `hreflang` tags via `next/head` `<Head>` or the metadata API.
- Audit: check `hreflang` is actually being emitted per locale (it's easy to misconfigure).

### Audit command

```bash
# In the repo
cat next.config.js next.config.mjs next.config.ts 2>/dev/null | head -200
```

Look for: `trailingSlash`, `redirects`, `rewrites`, `headers`, `images`, `i18n`.

## 4. Middleware — what's safe vs risky for SEO

`middleware.ts` (or `.js`) runs on every matched request. For SEO:

### Safe middleware patterns
- **A/B testing routing** with consistent canonical tags (canonical always points to the user-facing URL, not the variant).
- **Language detection + redirect** to the right `/locale/` prefix, with `hreflang` still correct.
- **Authentication check + redirect to login** — as long as public crawlable pages aren't accidentally caught.
- **Geolocation → locale hint** via cookie, NOT via content swap.

### Risky middleware patterns
- **User-agent switching** — serving different HTML to Googlebot vs. users. This is cloaking. Google's Spam Policy treats it as a manual-action risk.
- **IP-based content swap** — similar cloaking risk.
- **Blocking unauthenticated users on public pages** — Googlebot isn't authenticated; it hits the login redirect and never sees your content.
- **Adding random query parameters for cache-busting** — changes URLs seen by crawlers, fragments indexation.

### Audit checks

- Read `middleware.ts`. Confirm no User-Agent branching.
- Check that Googlebot-UA + no-cookies + no-auth fetches return the intended public HTML.
- Verify crawler-critical paths are in the middleware `config.matcher` exclusion list if they need to bypass auth.

## 5. ISR / revalidation strategy

Incremental Static Regeneration (ISR) is Next.js's way to regenerate static pages periodically. Get this wrong and you either serve stale content to crawlers or hammer your database on every request.

### Revalidation tiers by content type

| Content | `revalidate` value | Why |
|---|---|---|
| Homepage, marketing pages | 3600 (1 hour) | Marketing copy changes rarely but homepage may show dynamic elements |
| Blog posts | 86400 (1 day) | Published articles rarely change once live |
| Product / service detail pages | 3600 | Price / availability may change |
| Programmatic pages (job detail, event detail, mentor profile) | 3600 | Real content changes regularly |
| Index / listing pages | 300 (5 min) | New items appear frequently |
| Docs / legal pages | 86400 | Change-rarely content |
| Archived content | 0 (static) | Never re-renders; rebuild on demand |

### Anti-patterns

- **`revalidate: 0`** — disables ISR; every request re-generates the page. Cache-hostile, DB-heavy. Avoid unless specifically needed.
- **`revalidate: 1`** — generates on every request effectively. Same problem.
- **No revalidate set at all** on a Server Component that reads mutable data — page serves whatever was built at deploy time; stale content for search.
- **Using `dynamic = 'force-dynamic'` everywhere** — defeats Next's SSG/ISR; every page renders on every request. Only use when you genuinely need per-request data.

### Audit commands

```bash
# Find all revalidate settings in the app
grep -rn "revalidate\s*=\|revalidate:\|revalidate(" app/ pages/ --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx"

# Find all force-dynamic exports
grep -rn "force-dynamic\|dynamic\s*=\s*['\"]force" app/ pages/
```

## 6. Environment-specific canonicals

Common bug: the canonical tag is hardcoded to the production URL, but also appears on dev / staging / PR-preview deployments. Google then indexes the production URL content served from staging — if anyone finds the staging URL.

### The right pattern

Define the canonical host as an environment variable (or via Next's built-in env handling). Different deployments get different canonical hosts.

```tsx
// lib/canonical.ts
export function canonicalBaseUrl(): string {
  return process.env.NEXT_PUBLIC_CANONICAL_ORIGIN ?? 'https://www.example.com';
}

export function canonicalUrl(path: string): string {
  return `${canonicalBaseUrl()}${path.startsWith('/') ? path : `/${path}`}`;
}

// app/about/page.tsx
import type { Metadata } from 'next';
import { canonicalUrl } from '@/lib/canonical';

export const metadata: Metadata = {
  title: 'About — your brand',
  alternates: { canonical: canonicalUrl('/about') }
};
```

### Staging / PR preview — prevent indexation

Set response headers via `next.config.js` or middleware, gated on environment:

```js
// next.config.mjs
const isProd = process.env.VERCEL_ENV === 'production';

export default {
  async headers() {
    if (isProd) return [];
    return [{
      source: '/(.*)',
      headers: [
        { key: 'X-Robots-Tag', value: 'noindex, nofollow' }
      ]
    }];
  }
};
```

### Audit checks

- Confirm `NEXT_PUBLIC_CANONICAL_ORIGIN` (or equivalent) is set in every environment.
- Confirm staging / preview deployments return `X-Robots-Tag: noindex` header.
- Confirm production returns `X-Robots-Tag: index, follow` (or no X-Robots-Tag header, which defaults to indexable).
- Confirm no hardcoded production URL in `generateMetadata` that leaks to staging.

## 7. Shared layout components + schema injection

The `app/layout.tsx` (App Router) or `pages/_app.tsx` + `pages/_document.tsx` (Pages Router) run on every page. Get them right and every page inherits correct base metadata and schema.

### Pattern: inject Organization schema at the layout level

```tsx
// app/layout.tsx — Server Component
import Script from 'next/script';

const organizationSchema = {
  '@context': 'https://schema.org',
  '@graph': [
    { '@type': 'Organization', '@id': 'https://www.example.com/#organization', /* ... */ },
    { '@type': 'WebSite', '@id': 'https://www.example.com/#website', /* ... */ }
  ]
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationSchema) }}
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
```

Now every page inherits the Organization + WebSite schema. Per-page schemas (Article, Product, etc.) get added per-route via their own `generateMetadata` or `<script>` blocks that reference the canonical `@id`.

### Audit checks

- `Organization` + `WebSite` schema present on every page (check at least 3 distinct routes).
- Canonical `@id` consistent across routes.
- No duplicate `Organization` definitions on child pages.
- `hreflang` alternates emitted correctly if the site is i18n'd.

## 8. API routes + crawl considerations

Next's API routes (`app/api/*` or `pages/api/*`) are server-side endpoints. They should NOT be indexed.

### Default recommendations

**robots.txt** — Disallow the API prefix:
```
User-agent: *
Disallow: /api/
```

**Response headers** — set `X-Robots-Tag: noindex` on API responses defensively. Shouldn't be needed in theory, but catches edge cases where the URL is accidentally shared.

```ts
// app/api/some-endpoint/route.ts
export async function GET() {
  return Response.json({ /* ... */ }, {
    headers: { 'X-Robots-Tag': 'noindex' }
  });
}
```

### Audit checks

- `robots.txt` disallows `/api/`.
- Sample API endpoints return `X-Robots-Tag: noindex` (defensive layer).
- No API endpoints are accidentally linked from crawlable pages.

## 9. `next/image` optimization at the site level

`next/image` provides automatic optimization — but misconfigured, it breaks images or tanks LCP.

### Site-level checks

- `images.domains` OR `images.remotePatterns` in `next.config.js` covers every CDN / external image host used.
- The LCP image on each major template uses `priority` prop.
- Below-the-fold images default to `loading="lazy"` (the default on `next/image` — just don't override it).
- `sizes` prop set on responsive images so Next picks the right width.
- Image alt text follows `image-optimization.md` rules (not "image" / "photo" / filename).

### Audit commands

```bash
# Find all Image imports
grep -rn "from ['\"]next/image['\"]" app/ pages/ components/

# Check for priority prop usage on likely LCP elements (hero, banner)
grep -rn "priority" app/ pages/ components/ | grep -iE 'hero|banner|cover'
```

## 10. Font loading strategy

Font loading affects LCP + CLS. Next's `next/font` package handles most of this correctly if used.

### Recommended pattern

```tsx
// app/layout.tsx
import { Inter, Playfair_Display } from 'next/font/google';

const inter = Inter({ subsets: ['latin'], display: 'swap' });
const playfair = Playfair_Display({ subsets: ['latin'], display: 'swap' });

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={`${inter.variable} ${playfair.variable}`}>
      <body>{children}</body>
    </html>
  );
}
```

### Audit checks

- Using `next/font` rather than `<link rel="stylesheet" href="https://fonts.googleapis.com/...">` directly.
- `display: 'swap'` (so text renders before fonts load — prevents FOIT).
- No multiple font variants of the same family (bloats payload).
- Fonts preloaded only when they're above the fold (Next handles this automatically if using `next/font`).

## 11. Edge runtime vs Node runtime

Next supports two runtimes per route:

- **Node (default)** — full Node.js APIs. Heavier cold starts.
- **Edge** — runs at the CDN edge. Faster response, limited APIs.

### SEO implications

Edge is faster, which helps LCP + TTFB. But:

- Database access is limited on Edge (some DB clients don't work).
- Some server-side HTML parsing libraries only work in Node.
- For programmatic-SEO pages that need DB queries + schema generation, Node is usually safer.

### Audit checks

- Per-route `export const runtime = 'edge' | 'nodejs'` decisions are explicit, not accidental.
- Routes using Edge runtime don't break because of unavailable Node APIs (test by deploying).
- Response times (TTFB) are measurably better on Edge-runtime routes (or they shouldn't be Edge).

## 12. Common site-level anti-patterns

Things to flag when you see them:

### 12.1 Hardcoded production URLs in code
Breaks staging / preview deployments. Use env vars or route-based URL derivation.

### 12.2 `generateMetadata` that silently fails
Errors in `generateMetadata` fall back to default metadata. Pages render with homepage title / description. Always `try/catch` + log errors.

### 12.3 `router.push` used for nav where `<Link>` belongs
`router.push` is client-side only. `<Link>` renders as `<a href>` in SSR (crawlable). Use `<Link>` for all navigation; use `router.push` only for programmatic navigation inside event handlers.

### 12.4 `next/script` with wrong strategy
- `strategy="beforeInteractive"` — blocks render.
- `strategy="lazyOnload"` — script loads after everything else; good for tracking pixels.
- `strategy="afterInteractive"` — default; good for non-critical scripts.
Misusing these hurts LCP.

### 12.5 Dynamic route params causing infinite variations
`/products/[slug]` where slug can be anything — if not guarded, every random URL gets generated. Use `generateStaticParams` to whitelist.

### 12.6 Missing `notFound()` on dynamic routes
When no data is found, the page should call `notFound()` to return HTTP 404. Some templates render an empty page with HTTP 200 — Google indexes the empty version.

### 12.7 Client-side `document.title` changes
React Router-style title swaps don't trigger server-side updates. Use the metadata API or `<Head>` instead.

### 12.8 Shared components importing client-only libraries
Imports cascade. A chart library in a Server Component forces the whole page to Client Component. Audit component imports carefully.

## 13. Audit checklist

- **RNJS-1** `Organization` + `WebSite` schema injected at the root layout level; every page inherits.
- **RNJS-2** Canonical URL is environment-aware (not hardcoded to production host).
- **RNJS-3** Staging / PR preview deployments return `X-Robots-Tag: noindex`.
- **RNJS-4** `robots.txt` disallows `/api/`.
- **RNJS-5** `next.config.js` `trailingSlash` is set consistently (either true everywhere or false everywhere).
- **RNJS-6** Middleware does NOT user-agent-switch or IP-switch content.
- **RNJS-7** Per-route `revalidate` values are explicit and appropriate for the content type.
- **RNJS-8** No `revalidate: 0` or `revalidate: 1` unless specifically justified.
- **RNJS-9** `force-dynamic` used only where per-request data is genuinely required.
- **RNJS-10** `next/image` uses `priority` on LCP candidates and `sizes` on responsive images.
- **RNJS-11** `next/font` used rather than direct `<link>` to Google Fonts.
- **RNJS-12** `generateMetadata` errors are caught and logged; they don't silently fall back.
- **RNJS-13** Navigation uses `<Link>` not `router.push` for all anchor-like elements.
- **RNJS-14** Dynamic routes call `notFound()` when data is missing.
- **RNJS-15** `hreflang` alternates emitted correctly on i18n sites.
- **RNJS-16** For multi-subdomain brands: every subdomain declares own `@id` + references parent via `parentOrganization`.
- **RNJS-17** `sameAs`, `logo`, and `contactPoint` consistent across subdomains of the same brand.
- **RNJS-18** No hardcoded production URLs in code outside canonical-derivation helpers.
- **RNJS-19** Edge runtime is explicitly opted into (not accidental).
- **RNJS-20** Legal policy pages linked consistently from every subdomain's footer.

---

## 14. Roadmap: other stack profiles

This file is the first architecture-specific profile. Planned additions:

### `static-html-architecture-profile.md` (static site generators)
For sites built with Eleventy (11ty), Jekyll, Hugo, Astro (non-React content), or hand-written HTML. Build-time rendering considerations, automated schema injection patterns, sitemap generation via build hooks, CDN + cache-header strategy.

### `wordpress-architecture-profile.md`
For WordPress sites. Plugin ecosystem (Yoast, Rank Math, All in One SEO), permalink structure, multisite network considerations, custom post types and taxonomy SEO, WP REST API exposure, Gutenberg vs classic editor rendering, theme hierarchy, W3 Total Cache / WP Rocket interactions.

### `shopify-architecture-profile.md`
For Shopify-hosted stores. Liquid template SEO, collection vs product URL patterns, the opinionated sitemap Shopify generates, app ecosystem impact on performance, checkout flow SEO, meta-field customisation, JSON-LD via app injection.

### `angular-architecture-profile.md`
For Angular (2+) sites. Angular Universal for SSR, route-level meta configuration, change detection + hydration, zoneless migration, standalone components vs modules, lazy-loaded routes + SEO.

### `php-architecture-profile.md`
For custom-PHP sites (Laravel, Symfony, CodeIgniter, or plain PHP). Server-rendered-everywhere baseline (usually good), common pitfalls in session handling that break crawlers, sitemap + robots generation patterns across frameworks, caching layers (Varnish, Nginx FastCGI cache).

### `wix-webflow-architecture-profile.md`
For builder-platform sites (Wix, Webflow, Framer, Squarespace). Limited control over meta / schema / sitemap, but specific knobs and custom-code escape hatches. Common issues with opaque URL structures, lack of `hreflang` in international sites, difficulty claiming per-page canonicals.

Each profile gets the same structure as this one: multi-site / architecture concerns, platform-specific anti-patterns, audit checklist.

**If you want a specific profile built for your stack, file a request via `NEW-CHECK-REQUEST-TEMPLATE.md` and route it through the governance process.**
