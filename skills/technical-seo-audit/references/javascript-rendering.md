# JavaScript and rendering audit (including Next.js)

Goal: find out what a crawler gets from the server alone, what it gets after JavaScript runs, and where the two differ.

## 1. Why this matters

- Googlebot fetches the HTML first and renders JavaScript later in a separate step. Content that exists only after rendering is indexed later and less reliably.
- Many other crawlers, including most AI crawlers, do not run JavaScript. Treat raw HTML as the safe baseline and verify each crawler's current documentation before claiming otherwise.
- So: anything SEO-critical (title, canonical, robots, H1, main copy, internal links, JSON-LD) should be in the server response.

## 2. Method: raw vs rendered

1. **Raw.** Run `scripts/tech_probe.py`. It reads the server HTML without running JS and reports title, meta, canonical, H1, link count, JSON-LD, visible text size and `js_shell_suspect`. Spot-check with `curl -s <url>`, and again with a bot user agent: `curl -s -A "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)" <url>`.
2. **Rendered.** In a browser tool, load the page and run this in the page context, then compare to the raw values:

   ```js
   ({
     title: document.title,
     description: document.querySelector('meta[name="description"]')?.content || null,
     canonical: document.querySelector('link[rel="canonical"]')?.href || null,
     robots: document.querySelector('meta[name="robots"]')?.content || null,
     h1: [...document.querySelectorAll('h1')].map(h => h.textContent.trim()),
     links: document.querySelectorAll('a[href]').length,
     jsonld: [...document.querySelectorAll('script[type="application/ld+json"]')].length,
     textChars: document.body.innerText.length
   })
   ```
3. **Diff.** List every field that differs. Each difference is a finding with severity by field: robots/canonical/H1/main content differences are high; JSON-LD or title only in the rendered DOM is high to medium; extra links medium.
4. **No-JS view.** If the browser allows, disable JavaScript and reload. Critical text and navigation should still be visible.

State plainly in the report which side each fact came from (raw or rendered). The probe cannot see rendered content.

## 3. Patterns to flag in any JS framework

| Pattern | Why it hurts | Fix direction |
|---|---|---|
| Empty root (`<div id="root"></div>`) and content arrives via fetch | Non-JS crawlers see nothing | SSR, SSG or prerendering |
| Title/canonical/robots set by client code (`document.title = ...`) | Server response has the default values | Set in server-rendered head |
| Navigation by `onClick` / `router.push` with no `<a href>` | No crawlable links | Real anchors (`next/link`, `<a>`) |
| Infinite scroll or "load more" only | Deep items unreachable | Paginated URLs with links |
| Tabs/accordions render only the active panel | Hidden copy never in DOM | Render all panels, hide with CSS |
| "Not found" view with HTTP 200 | Soft 404 | Return a real 404 status |
| Content or redirects differ by user agent | Cloaking risk | Same content for all agents |
| Client-fetched data behind CORS or auth that fails for bots | Blank sections | Fetch on the server |
| Hydration errors | Page may blank or re-render differently | Fix mismatch; monitor |

Dynamic rendering (serving bots a prerendered copy) is a workaround, not a recommendation. Prefer SSR/SSG.

## 4. Next.js

**Identify the router** (probe `frameworks_seen`, or grep the raw HTML):
- `self.__next_f.push` present: **App Router** (React Server Components).
- `<script id="__NEXT_DATA__">` present: **Pages Router**.
- Both can exist in one app. Audit per route.

**App Router checks**
- Page components are Server Components. `'use client'` at the top of a `page.tsx` that fetches content in `useEffect` is the classic failure: raw HTML is a shell.
- Metadata through `export const metadata` or `generateMetadata`, including `alternates.canonical`. Confirm the values appear in raw HTML for the default UA and for a Googlebot UA (streaming metadata behaviour has changed between versions: test, don't assume).
- `notFound()` is called for missing dynamic routes, so the response status is 404. A page that renders "not found" with 200 is a soft 404.
- `robots.ts`/`sitemap.ts` (or static files) exist and serve valid output. Dynamic sitemap `lastModified` comes from real data.
- `redirect()`/`permanentRedirect()` and `next.config` redirects use 308/301 as intended.
- Suspense/streaming: content inside `loading.tsx` or Suspense boundaries should still arrive in the HTML stream. Check the final raw HTML, not only the first chunk.
- Route handlers and API routes (`/api/*`) send `X-Robots-Tag: noindex` if not meant for search.

**Pages Router checks**
- Content pages use `getStaticProps` or `getServerSideProps`, not client-only data fetching.
- `<Head>` from `next/head` sets title, description and canonical on the server render.
- `__NEXT_DATA__` size: a large JSON blob inflates HTML. Compare it with visible content and trim props.

**Both routers**
- `next/link` for internal navigation, not `router.push` on clickable divs.
- `next/image`: `priority` (or `fetchpriority="high"`) on the LCP image; explicit `width`/`height`; `remotePatterns` set for external hosts.
- `next/script`: tracking tags use `strategy="afterInteractive"` (or GTM's recommended component). `beforeInteractive` blocks rendering; `lazyOnload` can miss early pageviews.
- `middleware`: no redirects loops; does not block crawlers by user agent; does not serve different content to bots; sets `noindex` on preview hosts intentionally.
- `trailingSlash`, `basePath` and `i18n` settings match the canonical URL policy.
- Preview deployments (for example `*.vercel.app`) and staging send `noindex` and are not in sitemaps or canonicals.
- Hardcoded absolute URLs (`https://localhost`, staging host) do not leak into canonicals, sitemap or JSON-LD.
- ISR/revalidation: stale or never-revalidated pages are noted if `lastmod` or content freshness matters. `export const dynamic = 'force-dynamic'` on high-traffic public pages is a TTFB risk.
- Single-page navigation: pageviews for client-side route changes need explicit handling (see `tracking-tags.md`).

If the repo is available, grep for: `'use client'` in `page.*`, `useEffect(` with fetch in page components, `router.push`, `document.title`, `dangerouslySetInnerHTML`, `generateMetadata`, `notFound(`, `revalidate`, `force-dynamic`, `beforeInteractive`.

## 5. Other frameworks (short form)

- **Nuxt/Vue:** `__NUXT__` or `/_nuxt/` present. Confirm SSR or `nuxt generate` output; SPA mode (`ssr: false`) is a shell.
- **Angular:** `<app-root>` empty in raw HTML means no Angular Universal/SSR.
- **Gatsby/Astro/static:** usually pre-rendered. Check hydration islands and client-only components for critical content.
- **Livewire/Inertia (Laravel):** Livewire renders on the server; lazy components are not in the first HTML. Inertia without SSR is a shell (`data-page` attribute only).
- **Shopify/WordPress/Wix/Webflow:** server-rendered by default. Check apps/plugins that inject content client-side.

## 6. Reporting

Put the raw-versus-rendered table in the finding (field, raw value, rendered value). Use `confidence` 95+ for what `curl` shows, 80-94 for what the rendered DOM shows, and lower for inferences from pasted code. Include a fixed-code example from the framework's own API.
