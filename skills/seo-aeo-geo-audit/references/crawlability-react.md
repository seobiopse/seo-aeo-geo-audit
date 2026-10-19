# Crawlability Deep-Dive for React / Next.js Sites

For any React codebase — especially mixed Next.js apps with App Router + Pages Router + client-side rendering. Explains what different crawlers see and how to fix rendering gaps without rewriting the app.

## Crawler JS-execution matrix

| Crawler | JS execution | Notes |
|---|---|---|
| Googlebot | Yes (Chromium WRS) | Renders but may delay for JS-heavy pages |
| Bingbot | Yes, limited | Occasionally times out on modern features |
| Applebot | Yes | Siri/Spotlight; quieter |
| GPTBot / OAI-SearchBot | No or minimal | Primarily raw HTML |
| ClaudeBot / anthropic-ai | No or minimal | Primarily raw HTML |
| PerplexityBot | Partial | Relies heavily on server-rendered content |
| Google-Extended | No rendering | Just reads the HTML response |
| CCBot (Common Crawl) | No | Pure HTML. Feeds most open training datasets |
| Bytespider, Meta-ExternalAgent | No or minimal | Training crawlers — raw HTML only |

**Practical consequence:** if critical content only appears after JS runs, you rank OK in Google eventually but lose most AI citation traffic. Most GEO/AEO gaps on React sites come from this single issue.

## Table of contents

1. [Rendering modes cheat sheet](#1-rendering-modes-cheat-sheet)
2. [App Router — Server vs Client Components](#2-app-router)
3. [Pages Router — data fetching](#3-pages-router)
4. [Mixed Pages + App Router codebases](#4-mixed-codebases)
5. [Metadata APIs](#5-metadata-apis)
6. [Anti-patterns and fixes](#6-anti-patterns)
7. [Testing crawlability](#7-testing-crawlability)
8. [Checklist](#8-checklist)

---

## 1. Rendering modes cheat sheet

- **SSR** — HTML generated per request. Content in raw response. All crawlers see it.
- **SSG** — HTML generated at build time. Content in raw response. All crawlers see it.
- **ISR** — SSG with periodic revalidation. Same crawler benefit as SSG.
- **RSC (Server Components, App Router)** — Rendered on server, streamed. Most content in raw HTML. Crawler-friendly.
- **CSR** — Raw HTML is near-empty shell; React fills it after hydration. Non-JS crawlers see nothing.

**Rule of thumb:** if `curl -H "User-Agent: Mozilla/5.0" <url>` doesn't return critical content in the response body, most AI crawlers will not find it.

## 2. App Router — Server Components vs Client Components

Every component is a Server Component by default. A component becomes a Client Component only when:
- It has `'use client'` at the top of the file, OR
- It's imported by another Client Component (contagious downward)

### The anti-pattern that breaks SEO

```jsx
// app/products/[id]/page.tsx
'use client'  // ❌ forces whole page into CSR

import { useEffect, useState } from 'react'

export default function Product({ params }) {
  const [data, setData] = useState(null)
  useEffect(() => {
    fetch(`/api/products/${params.id}`).then(r => r.json()).then(setData)
  }, [params.id])
  if (!data) return <div>Loading...</div>
  return <article>{data.description}</article>
}
```

Crawler sees: `<div>Loading...</div>`. Description never in raw HTML.

### The fix

```jsx
// app/products/[id]/page.tsx (Server Component — no 'use client')

async function getProduct(id) {
  const res = await fetch(`${process.env.API_URL}/products/${id}`)
  return res.json()
}

export default async function Product({ params }) {
  const data = await getProduct(params.id)
  return <article>{data.description}</article>
}
```

Isolate interactivity (e.g., "Add to cart") to small Client Components:

```jsx
// AddToCartButton.tsx — 'use client' at top
```

## 3. Pages Router

Components are implicitly client-rendered UNLESS you use a data-fetching export:
- `getStaticProps` → SSG
- `getStaticPaths` + `getStaticProps` → SSG for dynamic routes
- `getServerSideProps` → SSR per request
- None → CSR fallback (bad for crawlers)

### Common bug

```jsx
// pages/blog/[slug].jsx
export default function BlogPost() {
  const { query } = useRouter()
  const [post, setPost] = useState(null)
  useEffect(() => {
    fetch(`/api/posts/${query.slug}`).then(r => r.json()).then(setPost)
  }, [query.slug])
  if (!post) return <p>Loading...</p>
  return <article>{post.content}</article>
}
```

Raw HTML: `<p>Loading...</p>`.

### Fix with `getStaticProps`

```jsx
export async function getStaticProps({ params }) {
  const post = await fetchPostBySlug(params.slug)
  return { props: { post }, revalidate: 3600 }
}

export async function getStaticPaths() {
  const slugs = await fetchAllSlugs()
  return { paths: slugs.map(slug => ({ params: { slug } })), fallback: 'blocking' }
}

export default function BlogPost({ post }) {
  return <article>{post.content}</article>
}
```

## 4. Mixed codebases

Next.js resolves `app/` first, then falls back to `pages/`. When auditing:

1. Identify which directory resolves the URL.
2. Check the rendering mode for that specific file:
   - `app/**/page.tsx` without `'use client'` → Server Component (good)
   - `app/**/page.tsx` with `'use client'` → investigate the content
   - `pages/**.tsx` with `getStaticProps` or `getServerSideProps` → SSR/SSG (good)
   - `pages/**.tsx` without either → CSR fallback (bad)

## 5. Metadata APIs

### App Router

Use `metadata` export from a Server Component. Client Components cannot export `metadata`.

```jsx
export async function generateMetadata({ params }) {
  const post = await fetchPostBySlug(params.slug)
  return {
    title: post.title,
    description: post.excerpt,
    openGraph: { images: [post.coverImage] },
    alternates: { canonical: `https://example.com/blog/${params.slug}` },
  }
}
```

### Pages Router

```jsx
import Head from 'next/head'
<Head>
  <title>{post.title}</title>
  <meta name="description" content={post.excerpt} />
  <link rel="canonical" href={...} />
</Head>
```

**Common bug:** metadata inside a Client Component in App Router — silently ignored. Crawlers see the default title.

## 6. Anti-patterns and fixes

### 6.1 "Loading…" that never resolves for bots
Critical content behind `useEffect` with a "Loading..." fallback. → Move to `getServerSideProps` / `getStaticProps` / Server Component.

### 6.2 Infinite scroll without paginated fallback
Loads more on scroll via JS. → Expose paginated URLs (`?page=2`) crawlable via `<a href>`.

### 6.3 Tabs / accordions that only render active panel
`{activeTab === 'specs' && <Specs />}`. → Render all panels into DOM; CSS to show/hide.

### 6.4 Content via `dangerouslySetInnerHTML` from client-fetched response
→ Fetch server-side; inject during SSR.

### 6.5 JS-only navigation
`<div onClick={navigate}>Read more</div>`. → Use `<Link>` or `<a href>`.

### 6.6 User-agent-based content delivery
Middleware sends different HTML to Googlebot. → Serve same HTML to all user agents.

### 6.7 Blocking crawlers in Next.js middleware
`middleware.ts` redirects unauthenticated → `/login`, accidentally catches Googlebot. → Let Googlebot through or mark paths public.

### 6.8 Recommendations rendering script pollution
`recommendedJobs.map(j => <Link>...)` in SSR → Next.js serializes router state per item as `self.nextf.push1` scripts. 200+ KB of noise. → Move recommendations to Client Component behind `<Suspense>`. See `pseo-jobs-playbook.md` §7.

### 6.9 Hydration errors silently breaking rendering
"Hydration failed" in console, Client Components unmount as blanks. → Fix mismatches (date formatting, random IDs, authenticated content based on localStorage). Monitor hydration errors in Sentry.

### 6.10 Third-party API calls from the client (CORS)
Crunchbase / LinkedIn / salary APIs called client-side → CORS errors, content missing from SSR HTML. → Server-side proxy. See `pseo-jobs-playbook.md` §8.

## 7. Testing crawlability

### 7.1 Raw HTML test (what non-JS crawlers see)
```bash
curl -s -H "User-Agent: Mozilla/5.0 (compatible; GPTBot/1.0)" https://example.com/page | less
```
Does the critical content text appear in the response body?

### 7.2 Rendered DOM test (what Googlebot's WRS sees)
DevTools → Elements panel. Or GSC URL Inspection → "View tested page" → "HTML".

### 7.3 Compare raw vs rendered
Raw empty, rendered full → CSR-only page. #1 cause of low AI visibility.

### 7.4 Disable JS in Chrome
DevTools → Cmd/Ctrl+Shift+P → "Disable JavaScript" → reload. Page should still show critical text + navigation.

### 7.5 Rich Results Test
https://search.google.com/test/rich-results — Google's own tool.

### 7.6 Lighthouse SEO audit
`npx lighthouse <url> --only-categories=seo --view`.

### 7.7 AI-crawler policies
```bash
for ua in "GPTBot" "ClaudeBot" "PerplexityBot" "Googlebot" "CCBot"; do
  echo "=== $ua ==="
  curl -s -H "User-Agent: $ua" https://example.com/robots.txt | head -5
done
```

## 8. Checklist

- **CR-1** Raw HTML contains `<title>`, meta description, `<h1>`, first paragraph of main content.
- **CR-2** Raw HTML contains every `<a href>` link for crawling.
- **CR-3** JSON-LD `<script type="application/ld+json">` in raw HTML, not injected by CSR.
- **CR-4** App Router pages are Server Components (no `'use client'` at top of `page.tsx`).
- **CR-5** Pages Router pages export `getStaticProps` or `getServerSideProps`; no critical-data `useEffect`.
- **CR-6** `metadata` / `generateMetadata` (App Router) or `<Head>` (Pages Router) sets title + description + canonical.
- **CR-7** No user-agent-based content swapping.
- **CR-8** All AI crawlers get same `robots.txt` response as Googlebot (unless intentionally differentiated).
- **CR-9** Hydration errors in prod monitored and at steady low rate.
- **CR-10** JS-disabled render: critical text + navigation still visible.
- **CR-11** Raw HTML size reasonable (< 80 KB for detail pages; job detail pages ≤ 40 KB — see `pseo-jobs-playbook.md` §11).
- **CR-12** No `self.nextf.push1` / `__NEXT_DATA__` pollution from recommendations rendered server-side.
- **CR-13** Tabs/accordions expose all content in DOM (even inactive).
- **CR-14** Third-party API calls (Crunchbase, etc.) server-proxied — no CORS errors in console.

---

Crawlability issues are often Critical or High severity — they're the ones where the page effectively does not exist for the audience you care about.
