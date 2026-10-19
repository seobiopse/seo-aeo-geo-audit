# Programmatic SEO Playbook (Jobs, Courses, Events, Skill Assessments, Location Pages)

Reference for auditing or building programmatic SEO (PSEO) pages at scale — any page type generated from a database with hundreds or thousands of instances sharing a template.

Read whenever the audit target is any of:
- **Job detail / listing pages** (see [Part A](#part-a-jobs))
- **Course / learning program detail pages** (see [Part B](#part-b-courses))
- **Event detail pages** (see [Part C](#part-c-events))
- **Skill assessment / quiz detail pages** (see [Part D](#part-d-skill-assessments))
- **Landing pages generated per city / per ICP / per keyword combination** (see [Part E](#part-e-generated-landing-pages))
- **Location hub pages** (city / pincode / neighbourhood — see [Part F](#part-f-location-hubs))
- **Company / provider hub pages** (see [Part G](#part-g-company-hubs))

## Shared fundamentals (apply to every PSEO page type)

All PSEO page types share these foundational rules regardless of content:

1. **Scale** — you audit the TEMPLATE, not the instance. Fix once, ship thousands.
2. **Lifecycle** — data changes; stale URLs turn into 404s. Every page type needs a "what happens when the record changes/expires" policy.
3. **Crawl budget** — finite per domain. Template efficiency and dynamic sitemaps matter more than on static sites.
4. **Dynamic sitemap** — static `sitemap.xml` goes stale within hours on PSEO sites. See `sitemap-playbook.md`.
5. **Hero SSR + auxiliary CSR** — critical content server-rendered; recommendations / related content behind Suspense. See [§A.7](#a7-rendering-strategy--hero-ssr--recs-csr) for the definitive pattern (written for jobs but applies to every type).
6. **Schema per instance** — exactly one primary schema block per page, rendered server-side.
7. **Canonical URL discipline** — slugs are stable; URL migrations use 301 redirects; no client-side navigation that skips server rendering.
8. **Crawlability** — see `crawlability-react.md` for React/Next.js rendering requirements.

For file format / alt text / image rules, see `image-optimization.md`. For tracking validation, see `tracking-validation.md`.

---

# Part A: Jobs

Reference for job-detail and job-listing pages. Based on the your brand PSEO-101 initiative.

## Table of contents (Part A — Jobs)

1. [Why job pages are different](#a1-why-job-pages-are-different)
2. [URL structure — hierarchical vs flat](#a2-url-structure--hierarchical-vs-flat)
3. [Slug generation rules](#a3-slug-generation-rules)
4. [Job lifecycle automation](#a4-job-lifecycle-automation)
5. [Dynamic sitemap generation](#a5-dynamic-sitemap-generation)
6. [301 redirect strategy for URL migrations](#a6-301-redirect-strategy-for-url-migrations)
7. [Rendering strategy — Hero SSR + Recs CSR](#a7-rendering-strategy--hero-ssr--recs-csr)
8. [CORS-safe API proxy pattern](#a8-cors-safe-api-proxy-pattern)
9. [JobPosting schema recipe](#a9-jobposting-schema-recipe)
10. [Semantic HTML + heading hierarchy](#a10-semantic-html--heading-hierarchy)
11. [Performance budget](#a11-performance-budget)
12. [Google for Jobs checklist](#a12-google-for-jobs-checklist)
13. [Audit checklist for any job detail page](#a13-audit-checklist-for-any-job-detail-page)

---

## 1. Why job pages are different

Three realities make job boards a different kind of SEO problem from a marketing site:

- **Scale.** A job board with 10,000 active listings has 10,000+ detail URLs. Typical audit patterns (manual review, per-URL optimization) don't scale — you audit the *template*, not the instance.
- **Ephemerality.** Jobs close. A listing alive today is closed in 30 days and purged in 120. If the template doesn't handle lifecycle cleanly, the index fills with 404s and soft-404s, crawl budget leaks, and Google for Jobs eligibility drops.
- **Crawl-budget pressure.** Googlebot has a finite budget per domain. If 40% of that budget crawls dead listings, fresh jobs wait days or weeks for discovery. On a marketplace where time-to-index is measured in hours, this kills the product.

Design every job-page feature (URL structure, sitemap, schema, rendering) with these three realities front of mind.

## 2. URL structure — hierarchical vs flat

Two patterns you'll see in the wild:

### Hierarchical (recommended for new builds)
```
/jobs/[location]/[company]/[title-slug]-[uuid]

Example:
/jobs/pune/beta-consulting/walk-in-drive-back-office-fresher-pune-apprentice-wfo-d96ab9e2
```

### Flat
```
/jobs/job-detail-[title]-[company]-[loc]-[id]

Example:
/jobs/job-detail-seo-specialist-amazon-chennai-9asdWFEQW
```

### How to choose

Hierarchical wins in every dimension a serious job board cares about:

- **Location clusters** — `/jobs/pune/` can become a crawlable hub page listing all Pune jobs. `/jobs/pune/beta-consulting/` clusters by company within location. Google's ranking systems reward clean entity hierarchies.
- **Google for Jobs alignment** — Google Jobs groups listings by location + company, so URL hierarchy reflects how Google's knowledge graph already groups the data.
- **Breadcrumb SEO** — hierarchical URLs generate natural breadcrumbs: Home > Jobs > Pune > Beta Consulting > [Job Title]. Flat URLs can't.
- **Entity extraction for LLMs** — LLMs parse URL paths as entity signals. `/jobs/pune/beta-consulting/` tells Claude/ChatGPT "this site has Beta Consulting content in the Pune location cluster."

Flat wins on exactly one axis: simpler routing logic. That's not enough.

**Recommendation:** use hierarchical for greenfield. If you're migrating from flat to hierarchical, do it once — the 301s from a second migration compound redirect chains and bleed link equity.

### Multi-location handling

Same job posted in multiple cities — avoid duplicate content.

- Single location: use the real location slug.
- Remote: use `remote` as the location slug.
- Multi-location: use `multi` as the location slug and list all cities on the page with `jobLocation` as an array in schema.

```
/jobs/remote/amazon/seo-specialist-amazon-remote-9asdWFEQW
/jobs/multi/amazon/senior-seo-manager-amazon-multi-9asdWFEQW
```

## 3. Slug generation rules

Slug quality affects crawlability, click-through rate, and human readability.

- Lowercase only.
- Words separated by hyphens (`-`), never underscores.
- Strip all non-alphanumeric characters before hyphenation.
- Include the primary keyword early (job title).
- Include brand/company name (high search intent).
- Include location or `remote`/`multi`.
- Append a **short UUID prefix** (8 chars is enough for uniqueness at reasonable scale) or the full UUID if your traffic/collision risk needs it.
- Max length: 80 characters excluding the UUID. Long URLs get truncated in SERPs.
- Stable once published — slug changes cost SEO equity. If the title changes, keep the old slug and add a redirect from it.

Reference implementation (from PSEO-101):

```typescript
// utils/slugs.ts
import slugify from 'slugify';

export function generateJobSlug(job: {
  title: string;
  company: string;
  location: string;
  uuid: string;
}) {
  return {
    location: slugify(job.location, { lower: true, strict: true }),
    company: slugify(job.company, { lower: true, strict: true }),
    title: `${slugify(job.title, { lower: true, strict: true }).slice(0, 72)}-${job.uuid.slice(0, 8)}`
  };
}

export function validateSlug(params: { location: string; company: string; title: string }, job: any): boolean {
  const expected = generateJobSlug(job);
  return params.location === expected.location &&
         params.company === expected.company &&
         params.title === expected.title;
}
```

Store the generated slug(s) on the job record. Re-compute and compare on page load — if the request's slug doesn't match the stored one, 301 to the canonical.

## 4. Job lifecycle automation

Every job has a lifecycle:

```
Day 0 → Day 31:      Active      (status=1, index,follow, in sitemap)
Day 32 → Day 121:   Inactive     (status=2, noindex, 200 OK, "Job closed" banner, removed from sitemap)
Day 122+:            Purged      (job + candidate data deleted, 301 to search)
```

Rationale:

- **31 days active** — matches Google for Jobs freshness expectations and typical candidate application timelines.
- **90 days noindex** — keeps the URL resolvable (so search crawlers see the `noindex` and drop it cleanly) and preserves the page for users who clicked a link from email, LinkedIn, etc. An "expired but 200" page is much better UX than a hard 404.
- **Purge at day 122** — data retention hygiene (PII in applications) and storage cost reduction. Old slugs redirect to search so referring links don't break.

### Database schema

```
jobs.status           (1 = Active, 2 = Inactive)
jobs.posted_at        (timestamp)
jobs.inactivated_at   (timestamp, set on Day 32 transition)
jobs.purged_at        (timestamp, set on Day 122 transition)
jobs.slug             (string, stable after first publish)
```

### Daily cron

Runs once per day (e.g., 02:00 IST to avoid peak traffic).

1. Find all jobs where `status = 1 AND posted_at < NOW() - INTERVAL 31 DAY` → set `status = 2, inactivated_at = NOW()`.
2. Find all jobs where `status = 2 AND inactivated_at < NOW() - INTERVAL 90 DAY` → DELETE job + applications. Before deleting, cache the job's `title` and `location` in a lightweight "purged-slug" table so the 301 destination can still reconstruct the search URL.
3. Regenerate / invalidate the sitemap cache.

### URL behavior by status

| Status | HTTP | Robots | Content |
|---|---|---|---|
| Active (`status=1`) | 200 | `index, follow` | Full job detail page |
| Inactive (`status=2`) | 200 | `noindex` | Job details + "This position has been closed" banner + similar jobs |
| Purged | 301 | — | Redirect to `/jobs?title={cached_title}&location={cached_location}` |

### Apply gating

The Apply button / endpoint must reject `status=2` jobs — even if the URL is still reachable, applications shouldn't be accepted on closed roles. Error message: "This role is no longer accepting applications. Browse similar roles."

## 5. Dynamic sitemap generation

Never ship a static sitemap for a programmatic site. It goes stale within hours.

### Structure

Main sitemap index at `/sitemap.xml` references specialised sitemaps:

```xml
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap><loc>https://www.example.com/sitemap-main.xml</loc></sitemap>
  <sitemap>
    <loc>https://www.example.com/sitemap-jobs.xml</loc>
    <lastmod>2026-04-18</lastmod>
  </sitemap>
  <sitemap><loc>https://www.example.com/sitemap-companies.xml</loc></sitemap>
</sitemapindex>
```

### `sitemap-jobs.xml`

Generated on-demand from the database. Key rules:

- Include **only** `status=1` (active) jobs. Inactive jobs have `noindex` — listing them in the sitemap contradicts the `noindex` signal and confuses Googlebot.
- Use absolute canonical URLs in the new semantic format.
- `<lastmod>` = `job.updated_at` as ISO 8601 with timezone.
- `<changefreq>` and `<priority>` are advisory only; set them consistently but don't over-optimise.
- Cache the response aggressively: `Cache-Control: public, s-maxage=3600, stale-while-revalidate=86400` (1h hard, 24h soft).
- Split into `sitemap-jobs-1.xml`, `sitemap-jobs-2.xml`, etc. once you cross 50,000 URLs per sitemap (Google's limit is 50K URLs or 50 MB uncompressed).

### Implementation (Next.js App Router)

```typescript
// app/sitemap-jobs.xml/route.ts
import { NextResponse } from 'next/server';

export async function GET() {
  const jobs = await db.jobs.findMany({
    where: { status: 1 },
    orderBy: { updated_at: 'desc' },
    select: { id: true, slug: true, location_slug: true, company_slug: true, updated_at: true }
  });

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${jobs.map(j => `  <url>
    <loc>https://www.example.com/jobs/${j.location_slug}/${j.company_slug}/${j.slug}</loc>
    <lastmod>${j.updated_at.toISOString()}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
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

Submit to Google Search Console as a separate property (the subdomain or the section). Monitor the "Discovered" → "Indexed" progression weekly.

## 6. 301 redirect strategy for URL migrations

Migrating from one URL pattern to another is routine for PSEO sites. Done badly, it vaporises traffic for months. Done right, equity transfers within weeks.

### Core principles

- **301 always, never 302.** 302 is temporary — Google won't transfer link equity.
- **Single-hop redirects.** Don't chain `/old` → `/intermediate` → `/new`. Each hop loses equity.
- **Server-side, not client-side.** Do it in Next.js middleware, a Next.js route handler returning `redirect()`, or CDN rules. Never with `window.location =`.
- **No blanket homepage redirects.** A deleted job should 404 (or 301 to search with the cached metadata, never to `/`). Blanket-redirecting anything-missing to the homepage tells Google your old URLs are soft-404s.
- **Preserve redirects forever.** Once deployed, don't remove them. Removing a 301 after link equity has flowed through means the receiving URL loses that equity.

### Pattern: legacy UUID URL → new semantic URL

```typescript
// app/jobs/job-[jobId]/page.tsx
import { redirect, notFound } from 'next/navigation';

export default async function LegacyJobPage({ params }: { params: { jobId: string } }) {
  const job = await getJobById(params.jobId);
  if (!job) notFound();

  const slugs = generateJobSlug(job);
  redirect(`/jobs/${slugs.location}/${slugs.company}/${slugs.title}`);
}
```

### Pattern: slug drift (title changed)

If a job's title or company is edited after publish, the canonical slug changes. The old slug should 301 to the new one:

```typescript
// app/jobs/[location]/[company]/[title]/page.tsx
const job = await getJobByUuid(extractUuidFromTitle(params.title));
if (!validateSlug(params, job)) {
  const slugs = generateJobSlug(job);
  redirect(`/jobs/${slugs.location}/${slugs.company}/${slugs.title}`);
}
```

### Testing redirects

- Staging: `curl -I https://staging.example.com/jobs/job-<UUID>` → expect `HTTP/2 301` and correct `Location:` header.
- Production canary: deploy for one job, monitor Vercel/New Relic for 5xx spikes.
- SEO validation: Screaming Frog crawl → filter by "Redirect chains" → expect zero chains for the new URL set.
- Google Search Console: URL Inspection on the old URL → "Page with redirect" → follow the redirect → check canonical.

## 7. Rendering strategy — Hero SSR + Recs CSR

The single highest-ROI pattern on a programmatic job page.

### The problem this solves

A typical React/Next.js job page has two kinds of content:

1. **Hero content** (job title, description, requirements, apply button) — every crawler and LLM must see this in the raw HTML.
2. **Recommendations sidebar** (similar jobs) — nice for users, zero SEO value. If anything, it *hurts* SEO: when `recommendedJobs.map(j => <Link>...)` renders in SSR, Next.js serializes router state per item into `self.nextf.push1` scripts. With 15 recs, the page balloons from 40 KB to 200+ KB of duplicate inline scripts and bot-confusing phantom content.

### The fix

Render the hero server-side (SSR or ISR), wrap recommendations in `<Suspense>` with a client-side boundary that fetches after hydration:

```tsx
// app/jobs/[location]/[company]/[title]/page.tsx
import { Suspense } from 'react';
import { notFound } from 'next/navigation';
import { JobHero } from './JobHero';
import { Recommendations } from './Recommendations';
import { RecommendationsSkeleton } from './RecommendationsSkeleton';

export const revalidate = 3600;  // ISR: 1 hour

export default async function JobDetailPage({ params }) {
  const job = await getJobBySlug(params);
  if (!job || job.status !== 1) notFound();  // active only

  return (
    <>
      <article itemScope itemType="https://schema.org/JobPosting">
        <JobHero job={job} />
      </article>

      <script type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(generateJobSchema(job)) }}
      />

      <Suspense fallback={<RecommendationsSkeleton />}>
        <Recommendations slug={params.title} />
      </Suspense>
    </>
  );
}
```

```tsx
// Recommendations.tsx
'use client';
export default function Recommendations({ slug }) {
  const [recs, setRecs] = useState([]);
  useEffect(() => {
    fetch(`/api/jobs/recommendations?slug=${slug}`).then(r => r.json()).then(setRecs);
  }, [slug]);
  return recs.map(r => <RecCard key={r.id} job={r} />);
}
```

### What crawlers see

| Crawler | Hero | Recommendations |
|---|---|---|
| Googlebot | ✅ SSR | ✅ (renders later, but noise is contained) |
| Bingbot | ✅ SSR | ❌ — doesn't run fetch |
| GPTBot / ClaudeBot / CCBot | ✅ SSR | ❌ — no JS execution |
| PerplexityBot | ✅ SSR | ❌ or minimal |

This is exactly the outcome you want. Hero = SEO-critical = always visible. Recs = UX-only = invisible to bots and doesn't dilute entity extraction.

### Common anti-patterns to flag in an audit

- `'use client'` at the top of the page file — forces the entire page into CSR mode; hero loses crawlability.
- `useEffect` fetching the job's own data — the core content isn't in SSR HTML. Non-JS crawlers see `<div>Loading...</div>`.
- `recommendedJobs.map(j => <Link href={`/jobs/${j.slug}`}>...)` rendered server-side — produces `self.nextf.push1` script pollution. Move the `.map()` into a Client Component behind Suspense.
- Third-party embeds (chat widgets, analytics, A/B test snippets) rendered above the fold — delay LCP, bloat HTML.
- `<script>` tags with inline data blobs (`__NEXT_DATA__` bloat, etc.) duplicated per recommendation item.

### Page weight target

40 KB HTML for a job detail page is achievable and should be the budget. Anything above 80 KB warrants investigation.

## 8. CORS-safe API proxy pattern

A frequent GSC / Lighthouse complaint on React job pages: CORS errors from client-side third-party API calls (Crunchbase, LinkedIn, salary providers, etc.).

### Why this breaks SEO

- Googlebot's rendering service sees the CORS error in the console. It logs it. Page quality score drops.
- Client-side-injected content (company logo, salary range) never makes it into the SSR HTML → crawlers see empty placeholders.
- API keys embedded in client code get scraped and abused.

### Fix: server-side proxy

```typescript
// app/api/proxy/crunchbase/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(req: NextRequest) {
  const query = new URL(req.url).searchParams.get('query') ?? '';

  const res = await fetch(
    `https://crunchbase-crunchbase-v1.p.rapidapi.com/autocompletes?collection_ids=organizations&query=${encodeURIComponent(query)}`,
    {
      headers: {
        'X-RapidAPI-Key': process.env.RAPIDAPI_KEY!,
        'X-RapidAPI-Host': 'crunchbase-crunchbase-v1.p.rapidapi.com'
      },
      cache: 'force-cache',  // ISR-friendly; refresh at revalidate boundary
      next: { revalidate: 3600 }
    }
  );

  if (!res.ok) return NextResponse.json({ error: 'upstream failed' }, { status: 502 });
  return NextResponse.json(await res.json());
}
```

Then call it from the page's Server Component during render:

```tsx
const companyRes = await fetch(
  `${process.env.NEXT_PUBLIC_BASE_URL}/api/proxy/crunchbase?query=${job.company}`,
  { next: { revalidate: 3600 } }
);
const companyData = await companyRes.json();
```

Key properties:

- API keys stay server-side.
- Response cached at the edge.
- No CORS — same origin.
- Company data is in the SSR HTML for every crawler.

## 9. JobPosting schema recipe

Google for Jobs eligibility requires schema. Here's the fully-populated example the plugin expects to see on a job detail page:

```json
{
  "@context": "https://schema.org",
  "@type": "JobPosting",
  "title": "Senior React Developer",
  "description": "<p>Full HTML description of the role, verbatim from the visible page body...</p>",
  "identifier": {
    "@type": "PropertyValue",
    "name": "your brand",
    "value": "JOB-2026-042"
  },
  "datePosted": "2026-04-15T09:00:00+05:30",
  "validThrough": "2026-05-16T23:59:00+05:30",
  "employmentType": ["FULL_TIME"],
  "hiringOrganization": {
    "@type": "Organization",
    "name": "Beta Consulting",
    "sameAs": "https://www.crunchbase.com/organization/beta-consulting",
    "logo": "https://cdn.example.com/logos/beta-consulting.png"
  },
  "jobLocation": {
    "@type": "Place",
    "address": {
      "@type": "PostalAddress",
      "addressLocality": "Pune",
      "addressRegion": "MH",
      "postalCode": "411001",
      "addressCountry": "IN"
    }
  },
  "jobLocationType": "TELECOMMUTE",
  "applicantLocationRequirements": { "@type": "Country", "name": "India" },
  "baseSalary": {
    "@type": "MonetaryAmount",
    "currency": "INR",
    "value": {
      "@type": "QuantitativeValue",
      "minValue": 1500000,
      "maxValue": 2500000,
      "unitText": "YEAR"
    }
  },
  "directApply": true,
  "skills": "React, TypeScript, Next.js, GraphQL",
  "qualifications": "B.Tech / B.E. in Computer Science or equivalent; 5+ years experience"
}
```

### Rules

- **`datePosted` and `validThrough` must be real.** `datePosted` = `posted_at`, `validThrough` = `posted_at + 31 days` (or whatever matches your lifecycle). Google removes listings with `validThrough` in the past — this is what drives your active/inactive transition to be reflected in Google Jobs within 48 hours of the cron running.
- **One JobPosting per page.** Never emit multiple `<script type="application/ld+json">` JobPosting blocks (common bug with recommendations rendering their own schema). Only the hero gets schema.
- **`hiringOrganization.sameAs`** — link to Crunchbase, LinkedIn, or the official company website. Strongest entity signal for LLMs.
- **`baseSalary` is optional but powerful.** In India, job boards that include salary see significantly higher CTR in Google Jobs. If you have the data, publish it. Use `MonetaryAmount` with `unitText` ("YEAR" / "MONTH" / "HOUR").
- **`directApply: true`** signals that candidates can apply without leaving your site. Google promotes direct-apply jobs in Jobs carousel.
- **Description must match visible content.** The description in schema must be the same job description shown to users. Don't schema-pad for keywords.
- **Test every deploy.** Run one URL through https://search.google.com/test/rich-results — any error → fix before merging.

### What to render it next to

The JSON-LD `<script>` goes inside the `<article>` element that contains the visible job. Server-side rendered. Never client-side-injected.

## 10. Semantic HTML + heading hierarchy

A job detail page should be scannable both by humans and by retrieval chunkers. Use semantic tags, not `<div>` soup.

### Required structure

```html
<article itemScope itemType="https://schema.org/JobPosting">
  <header>
    <h1 itemProp="title">Senior React Developer</h1>
    <div itemProp="hiringOrganization" itemScope itemType="https://schema.org/Organization">
      <h2 itemProp="name">Beta Consulting</h2>
    </div>
  </header>

  <section itemProp="jobLocation" itemScope itemType="https://schema.org/Place">
    <h3>Location</h3>
    <p><span itemProp="addressLocality">Pune</span>, India</p>
  </section>

  <section>
    <h2>About the job</h2>
    <section>
      <h3>Summary</h3>
      <div itemProp="description">...</div>
    </section>
    <section>
      <h3>Key Responsibilities</h3>
      <ul>...</ul>
    </section>
    <section>
      <h3>Qualifications / Requirements</h3>
      <ul itemProp="qualifications">...</ul>
    </section>
    <section>
      <h3>Preferred Skills / Attributes</h3>
      <ul>...</ul>
    </section>
  </section>
</article>

<aside aria-label="Similar jobs">
  <h2>Similar jobs</h2>
  <!-- rendered client-side via Suspense -->
</aside>
```

### Heading rules

- Exactly one `<h1>` per page — the job title.
- `<h2>` for: company name, "About the job", "Similar jobs" sidebar heading.
- `<h3>` under "About the job": Summary, Key Responsibilities, Qualifications, Preferred Skills.
- No level skipping (no `<h2>` followed directly by `<h4>`).
- Styled headings — never `<div class="text-2xl font-bold">` for things that are semantically headings. This is the single biggest regression I'd flag from the current your brand HTML.

### Microdata `itemProp` + JSON-LD both

Including `itemProp` attributes alongside JSON-LD schema is belt-and-braces — doesn't hurt SEO and gives older / simpler parsers an alternate path. JSON-LD remains primary.

## 11. Performance budget

For a job detail page, aim for:

| Metric | Budget | Stretch |
|---|---|---|
| HTML size (`curl` response) | < 80 KB | < 40 KB |
| Total transferred (network) | < 700 KB | < 400 KB |
| LCP (mobile, 4G throttled) | < 2.5 s | < 1.5 s |
| INP | < 200 ms | < 100 ms |
| CLS | < 0.1 | < 0.05 |
| TTFB | < 500 ms | < 200 ms |
| Lighthouse Performance (mobile) | ≥ 75 | ≥ 90 |
| Lighthouse SEO | ≥ 95 | 100 |

If the page is under 40 KB HTML with proper ISR caching, sub-500ms TTFB is routine.

## 12. Google for Jobs checklist

Google for Jobs is the job-specific equivalent of an AI Overview — a rich results box at the top of the SERP for `"<role> jobs"` queries. Eligibility rules:

- Every job has valid `JobPosting` schema (see §9).
- `datePosted`, `validThrough`, `employmentType`, `hiringOrganization`, and either `jobLocation` or `applicantLocationRequirements` are present.
- Schema is visible to Googlebot (rendered server-side).
- Page returns HTTP 200 (not 301/302).
- Page is not `noindex`.
- Page is reachable from `sitemap-jobs.xml`.
- Same site also provides a `ListItem` schema on listing pages (category, search results) so Google understands how jobs are grouped.
- Indexing API (recommended): for time-sensitive pages, use the Google Indexing API's `URL_UPDATED` endpoint when a job is posted, and `URL_DELETED` when it's closed. Jobs API is specifically allowed to use the Indexing API (most site types aren't). This is the fastest way to ensure new jobs appear in Google Jobs within hours instead of days.

### Monitoring

In Search Console → Enhancements → Job Postings → count of valid items. Should match your `status=1` count within ±5%. Any consistent gap means schema is failing validation somewhere.

## 13. Audit checklist for any job detail page

Mark each `pass`, `warn`, or `fail`. Use the issue framework for findings. On a full audit, include every `fail` and `warn` in the report.

- **PJ-1** Raw HTML (`curl` without JS) contains the job title (`<h1>`), company name (`<h2>`), full job description text, and all skills/requirements.
- **PJ-2** Raw HTML contains exactly one `<script type="application/ld+json">` block with valid `JobPosting` schema.
- **PJ-3** No `self.nextf.push1` / `__NEXT_DATA__` pollution from recommendations rendered server-side. Count of occurrences in raw HTML ≤ 1.
- **PJ-4** Raw HTML size ≤ 80 KB (strict: ≤ 40 KB).
- **PJ-5** Page returns HTTP 200 with `Content-Type: text/html; charset=utf-8`.
- **PJ-6** `<meta name="robots">` absent or set to `index, follow` for active jobs; `noindex` for inactive; page entirely absent (redirect) for purged.
- **PJ-7** URL follows the agreed pattern (hierarchical recommended: `/jobs/[location]/[company]/[title-slug]-[uuid]`).
- **PJ-8** Legacy UUID-only URL (`/jobs/job-<UUID>`) returns HTTP 301 to the canonical new URL.
- **PJ-9** Slug mismatch (e.g., stale slug from an old link) returns HTTP 301 to the canonical slug, not 200.
- **PJ-10** JobPosting schema passes https://search.google.com/test/rich-results with zero errors.
- **PJ-11** `datePosted` is a real ISO 8601 timestamp with timezone; `validThrough` is ≥ 1 day in the future.
- **PJ-12** Every heading level is semantic (`<h1>`, `<h2>`, `<h3>`) — no `<div>` styled as headings.
- **PJ-13** `<article itemScope itemType="https://schema.org/JobPosting">` wraps the hero content.
- **PJ-14** No CORS errors in the console on page load (server-side proxy for all third-party data).
- **PJ-15** Recommendations sidebar is inside a `<Suspense>` boundary (or equivalent CSR pattern), not rendered in the initial SSR HTML.
- **PJ-16** No duplicate JobPosting schema (exactly one per page, for the hero job only).
- **PJ-17** `sitemap-jobs.xml` contains this URL if the job is `status=1`; does NOT contain it if `status=2` or purged.
- **PJ-18** Cron lifecycle rules (31d → inactive, 90d → purge) are implemented and verified on sample data.
- **PJ-19** Mobile Core Web Vitals: LCP ≤ 2.5 s, CLS ≤ 0.1, INP ≤ 200 ms (field data from GSC / CrUX).
- **PJ-20** Lighthouse Performance ≥ 75 mobile, ≥ 90 desktop. Lighthouse SEO ≥ 95.

---

## Related references in this plugin

- `crawlability-react.md` — deeper treatment of the Next.js App Router / Pages Router rendering mechanics that underpin §7.
- `structured-data-advanced.md` — general structured-data patterns; §3.3 has the JobPosting recipe at a glance.
- `seo-audit.md` — the main SEO checklist all job pages should still pass.
- `react-nextjs-architecture-profile.md` — React / Next.js-specific guidance including the cross-subdomain Organization graph that every JobPosting's `hiringOrganization` / `publisher` should reference.

## What to do after running this checklist

Use the issue framework in `issue-framework.md` for every `warn`/`fail`. On job detail pages, severities tend to cluster on Critical/High because any single failure can exclude the page from Google for Jobs — which is the primary distribution channel. When in doubt, err toward Critical for schema and rendering issues.

---

# Part B: Courses

Reference for course / learning program detail pages (e.g., a learning subdomain like `learn.example.com` or `courses.example.com`).

## B.1 Why course pages are different

- **Decisional content** — users compare multiple courses before enrolling. Pages compete in "best X course" queries.
- **Authority signals matter more than on jobs** — who teaches it, outcome data, certifications.
- **Longer commitment** — higher bar for trust signals than a blog post.
- **Schema ROI is huge** — `Course` rich results show pricing, ratings, and instructor directly in SERPs.

## B.2 URL structure

Recommended hierarchy for course pages:

```
/courses/[category]/[course-slug]
e.g. /courses/jee/jee-advanced-physics-advanced-2026
      /courses/digital-marketing/digital-marketing-ai-100-days
```

Why hierarchical by category:
- `/courses/jee/` becomes a crawlable hub listing all JEE courses (category page)
- `/courses/` top-level hub lists all categories
- Breadcrumbs map naturally: Home › Courses › JEE › [Course Title]

Avoid:
- `/course-[id]` (opaque)
- `/courses/[course-id]-[slug]` (ID-first slugs look low-quality to users)
- Date in URL (`/courses/2026/...`) unless you version annually

## B.3 Slug generation for courses

```
[course-name-slug]-[version-or-year-if-applicable]

examples:
jee-advanced-physics-complete-course
digital-marketing-ai-100-days-2026
```

- Include the exam/subject/primary keyword in the slug
- Year / version only if you run annual editions (and then redirect old editions)
- Max 80 chars

## B.4 Course page content structure

```
<h1>[Course name]</h1>
<p>One-sentence value proposition with outcome</p>

<section aria-label="Course summary">
  <dl>
    <dt>Duration</dt><dd>16 weeks</dd>
    <dt>Mode</dt><dd>Live + recorded</dd>
    <dt>Level</dt><dd>Advanced</dd>
    <dt>Instructor</dt><dd>Dr Priya Iyer</dd>
    <dt>Price</dt><dd>₹15,000</dd>
  </dl>
  <button>Enroll now</button>
</section>

<section>
  <h2>What you'll learn</h2>
  <ul>...</ul>
</section>

<section>
  <h2>Syllabus</h2>
  <!-- week-by-week or module breakdown -->
</section>

<section>
  <h2>Instructor</h2>
  <!-- Person schema with bio -->
</section>

<section>
  <h2>Student outcomes</h2>
  <!-- verifiable outcomes, not vanity stats -->
</section>

<section>
  <h2>Reviews</h2>
  <!-- real reviews marked up with Review schema -->
</section>

<section>
  <h2>FAQs</h2>
  <!-- FAQPage schema -->
</section>
```

## B.5 Course schema recipe

```json
{
  "@context": "https://schema.org",
  "@type": "Course",
  "name": "JEE Advanced Physics — Complete Course",
  "description": "16-week live course covering JEE Advanced Physics syllabus, taught by Dr Priya Iyer.",
  "provider": {
    "@type": "Organization",
    "@id": "https://learning.example.com/#organization"
  },
  "hasCourseInstance": [{
    "@type": "CourseInstance",
    "courseMode": "online",
    "startDate": "2026-06-01",
    "endDate": "2026-09-21",
    "courseWorkload": "PT12H",
    "instructor": {
      "@type": "Person",
      "name": "Dr Priya Iyer",
      "jobTitle": "Senior Physics Faculty",
      "url": "https://learning.example.com/instructors/priya-iyer"
    }
  }],
  "offers": {
    "@type": "Offer",
    "category": "Paid",
    "price": "15000",
    "priceCurrency": "INR",
    "availability": "https://schema.org/InStock"
  },
  "educationalLevel": "Advanced",
  "teaches": "JEE Advanced Physics concepts and problem-solving",
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "ratingCount": "412"
  },
  "review": [ /* individual reviews */ ]
}
```

### Google requirements
- Required: `name`, `description`, `provider`, `hasCourseInstance` with `courseMode` and either `startDate` or `repeatFrequency`.
- `aggregateRating` ONLY if ratings are real + verifiable. Fabricated ratings = manual-action risk.
- `offers.price` in the local currency.

## B.6 Course lifecycle considerations

Different from jobs — courses don't expire in 31 days. But cohorts do:

- **Current cohort** (status: OPEN_FOR_ENROLLMENT) → indexable + in sitemap + `validThrough` = enrollment close date
- **Past cohort** (status: CLOSED) → EITHER keep indexable with "next cohort" CTA, OR 301 to the upcoming cohort's page
- **Retired course** (never running again) → 301 to the closest replacement OR category page
- **New cohort** → new URL per cohort if curriculum changes significantly; reuse URL if same curriculum

## B.7 Audit checklist for course pages

- **CO-1** `Course` + `CourseInstance` schema present with required Google fields.
- **CO-2** `Offer` includes price + currency + availability.
- **CO-3** Instructor is a real `Person` with `url` to a bio page.
- **CO-4** `aggregateRating` only if ratings are verifiable.
- **CO-5** FAQ section covering common pre-enrollment questions with `FAQPage` schema.
- **CO-6** Syllabus visible on the page (not behind "download PDF").
- **CO-7** Outcomes / testimonials with real attribution (name + role, photo where permitted).
- **CO-8** `BreadcrumbList` schema: Home › Courses › [Category] › [Course Title].
- **CO-9** Video preview (if exists) uses `VideoObject` schema.
- **CO-10** Course lifecycle handled (current/past/retired — see B.6).
- **CO-11** Price rendered in server-side HTML, not injected client-side.
- **CO-12** Instructor schema has `sameAs` → LinkedIn / published credentials.

---

# Part C: Events

Reference for event detail pages (conferences, webinars, career fairs, workshops).

## C.1 Why event pages are different

- **Time-sensitive** — relevance has a hard expiry (event date).
- **Geography-sensitive** — in-person events rank best for location-specific queries.
- **Post-event lifecycle** — what do you do with the page AFTER the event?

## C.2 URL structure

```
/events/[year]/[city or slug]/[event-slug]
  /events/2026/mumbai/career-summit
  /events/2026/online/webinar-react-performance

For recurring series, keep the base slug:
  /events/career-summit  (canonical hub)
  /events/career-summit/2026  (instance)
  /events/career-summit/2025  (past instance)
```

## C.3 Event schema recipe

```json
{
  "@context": "https://schema.org",
  "@type": "Event",
  "name": "your-event-name 2026",
  "description": "...",
  "startDate": "2026-11-15T09:00:00+05:30",
  "endDate": "2026-11-15T18:00:00+05:30",
  "eventStatus": "https://schema.org/EventScheduled",
  "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
  "location": {
    "@type": "Place",
    "name": "Jio World Convention Centre",
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "...",
      "addressLocality": "Mumbai",
      "addressRegion": "MH",
      "postalCode": "400051",
      "addressCountry": "IN"
    }
  },
  "image": ["https://.../event-hero.webp"],
  "organizer": {
    "@type": "Organization",
    "@id": "https://www.example.com/#organization"
  },
  "offers": [{
    "@type": "Offer",
    "url": "https://www.example.com/events/2026/mumbai/career-summit",
    "price": "2499",
    "priceCurrency": "INR",
    "availability": "https://schema.org/InStock",
    "validFrom": "2026-08-01"
  }],
  "performer": [ /* speakers as Person entities */ ]
}
```

### Google requirements for Event rich result
- `name`, `startDate`, `location`, `offers` (if ticketed).
- `eventAttendanceMode` specifies online / offline / hybrid. Critical for "events near me" vs "online webinars" queries.
- `eventStatus` — `EventScheduled`, `EventCancelled`, `EventPostponed`, `EventRescheduled`, `EventMovedOnline`. Update promptly if any changes.

## C.4 Event lifecycle

```
Pre-event (> 3 months out):      Active, indexed, in sitemap, promoted
Pre-event (< 30 days):           Active, indexed, boosted internal linking
Post-event (first 30 days):      Keep page live with recap content (photos, recordings, highlights) — this is the GEO gold window
Post-event (ongoing):            Keep live as an archive; ensure `eventStatus` + `endDate` both past
Year change:                     If running annually, create /events/YYYY+1/... early; link old to new via visible "see our 2027 edition"
```

**Don't 404 past events.** They accumulate backlinks, get cited for speaker bios, and rank for "what happened at [event]" queries.

## C.5 Audit checklist for event pages

- **EV-1** `Event` schema with required Google fields.
- **EV-2** `eventAttendanceMode` set (online/offline/hybrid).
- **EV-3** `eventStatus` accurate and updated if event status changes.
- **EV-4** `startDate` + `endDate` in ISO 8601 with timezone.
- **EV-5** Location: full `PostalAddress` for offline, `VirtualLocation` for online.
- **EV-6** `offers` with price + currency + availability.
- **EV-7** Speakers listed with `Person` schema, each with bio page.
- **EV-8** Post-event: page kept live with recap, not 404'd.
- **EV-9** `image` is absolute URL ≥ 696×696 per Google's Event rich result spec.
- **EV-10** Timezone-aware dates display (don't just say "10am" — say "10:00 IST").

---

# Part D: Skill Assessments

Reference for skill test / quiz / assessment detail pages (e.g., your brand skill assessments).

## D.1 Why skill assessment pages are different

- **Outcome-focused** — users want the test + their score, not educational content.
- **High bounce risk** — if the test isn't immediately startable, users leave.
- **Schema hybrid** — mixes `Quiz` (schema.org) with `EducationalOccupationalCredential` or `Course`.

## D.2 URL structure

```
/skill-assessments/[category]/[skill-slug]
  /skill-assessments/coding/react-intermediate
  /skill-assessments/aptitude/quantitative-reasoning
```

## D.3 Page structure

```
<h1>[Skill] — [Level] Assessment</h1>
<p>One-sentence description of what this test evaluates</p>

<section aria-label="Test metadata">
  <dl>
    <dt>Duration</dt><dd>30 minutes</dd>
    <dt>Questions</dt><dd>25 (multiple choice)</dd>
    <dt>Difficulty</dt><dd>Intermediate</dd>
    <dt>Score returned</dt><dd>Percentile + skills breakdown</dd>
  </dl>
  <button>Start test</button>
</section>

<section>
  <h2>What this test covers</h2>
  <ul>
    <li>React hooks and state management (8 questions)</li>
    <li>Component architecture (7 questions)</li>
    <li>Performance optimization (5 questions)</li>
    <li>Testing patterns (5 questions)</li>
  </ul>
</section>

<section>
  <h2>Who should take this</h2>
  <ul>...</ul>
</section>

<section>
  <h2>Sample questions</h2>
  <!-- 2-3 example questions (NOT the real test questions) -->
</section>

<section>
  <h2>FAQs</h2>
  <!-- FAQPage schema -->
</section>
```

## D.4 Schema for skill assessments

No exact schema.org type for assessments — use a combination:

```json
{
  "@context": "https://schema.org",
  "@type": "Quiz",
  "name": "React Intermediate Assessment",
  "description": "30-minute assessment covering React hooks, component architecture, performance optimization, and testing patterns.",
  "educationalLevel": "Intermediate",
  "timeRequired": "PT30M",
  "about": {
    "@type": "DefinedTerm",
    "name": "React",
    "inDefinedTermSet": "https://en.wikipedia.org/wiki/React_(software)"
  },
  "provider": {
    "@type": "Organization",
    "@id": "https://www.example.com/#organization"
  },
  "educationalCredentialAwarded": {
    "@type": "EducationalOccupationalCredential",
    "credentialCategory": "Skill Assessment Certificate",
    "recognizedBy": { "@id": "https://www.example.com/#organization" }
  },
  "hasPart": [
    { "@type": "Question", "name": "Sample question 1...", "acceptedAnswer": { "@type": "Answer", "text": "..." }}
  ]
}
```

### Note
`Quiz` schema is under-documented compared to `Course` or `JobPosting`. Rich results for quizzes are limited. The main SEO benefit is entity clarity + FAQ rich results for sample questions.

## D.5 Audit checklist for skill assessment pages

- **SA-1** `Quiz` schema OR combined `Course` + `EducationalOccupationalCredential` schema present.
- **SA-2** Duration, question count, difficulty visible on page.
- **SA-3** Start button above the fold.
- **SA-4** "What this test covers" section with topic breakdown.
- **SA-5** FAQ section with `FAQPage` schema answering common pre-test questions.
- **SA-6** Sample questions visible (2-3 examples — NOT the real test questions).
- **SA-7** `about` property in schema links to the skill's Wikipedia/Wikidata entity where possible.
- **SA-8** If certificate awarded, `educationalCredentialAwarded` present.
- **SA-9** Price (or "free") clearly stated.
- **SA-10** Retake / cooldown policy mentioned if applicable.

---

# Part E: Generated Landing Pages (per-city / per-ICP)

Reference for landing pages generated from combinations (e.g., per-city, per-industry, per-ICP). This is the highest-risk PSEO category because it's adjacent to "doorway pages" which Google penalises.

## E.1 The doorway risk

Google penalises "doorway pages" — pages whose primary purpose is to rank for keyword variants, not serve users. Signs of doorway:
- Near-duplicate templates with only the city/industry name swapped.
- No meaningfully different content per variant.
- Internal linking designed only to funnel bots to a shared conversion page.

To differentiate YOUR city/ICP pages from doorways:
- **Real content per variant** — specific to the location or ICP (not generic).
- **Different imagery** where possible.
- **Local proof** — customer logos, testimonials, case studies from that city/ICP.
- **Different FAQ content** — locale-specific questions.
- **Linked from navigation** — not orphaned.

## E.2 URL structure

```
/[service-or-product]/[city-or-icp-slug]
  /enterprise-broadband/whitefield
  /fibre/schools
  /recruitment/healthcare

Or hierarchical:
  /solutions/schools/fibre-broadband
  /cities/whitefield/enterprise-broadband
```

## E.3 Content rules per variant

Each variant page must have:

1. **Unique `<h1>`** — includes the city/ICP + the service + the location.
2. **Unique meta description** — not templated.
3. **Meaningfully different body content** — at least 40% variation from sister pages.
4. **Local proof** — a customer name, a testimonial, a neighbourhood reference.
5. **Structured data appropriate to the variant** — e.g., `LocalBusiness` with `areaServed` + `geo` specific to the city.

## E.4 Schema for city/ICP landing pages

Combination of:

```json
{
  "@graph": [
    {
      "@type": "LocalBusiness",
      "@id": "https://example.com/#localbusiness",
      "name": "...",
      "areaServed": {
        "@type": "Place",
        "name": "Whitefield, Bangalore",
        "address": {
          "@type": "PostalAddress",
          "addressLocality": "Whitefield",
          "addressRegion": "Karnataka",
          "postalCode": "560066",
          "addressCountry": "IN"
        }
      }
    },
    {
      "@type": "Service",
      "name": "Enterprise Fibre Broadband in Whitefield",
      "areaServed": { "@type": "Place", "name": "Whitefield, Bangalore" },
      "provider": { "@id": "https://example.com/#localbusiness" }
    },
    {
      "@type": "FAQPage",
      "mainEntity": [ /* city-specific FAQs */ ]
    }
  ]
}
```

## E.5 Audit checklist for generated landing pages

- **GLP-1** `<h1>` unique per variant, includes the variant dimension (city / ICP).
- **GLP-2** Meta description unique per variant (not templated).
- **GLP-3** Body content has meaningful per-variant substance (at least 40% variation).
- **GLP-4** Local proof present — customer logo / testimonial / case study specific to the variant.
- **GLP-5** `LocalBusiness` or `Service` schema with `areaServed` matching the variant.
- **GLP-6** FAQ section includes at least 2 variant-specific questions.
- **GLP-7** Page linked from navigation / sister pages — not orphaned.
- **GLP-8** Internal linking goes both ways (sister pages link to each other via a geographic hub).
- **GLP-9** No "Copy A with city name swapped" — Google detects template reuse.
- **GLP-10** Variant-specific images where feasible (not the same hero on 50 pages).

For broader transaction-intent rules on these pages, cross-reference `transaction-intent-playbook.md`.

---

# Part F: Location Hubs

Reference for location / city / pincode / neighbourhood hub pages (e.g., `/cities/whitefield/`).

## F.1 Purpose

A location hub is a page that:
- Ranks for generic location queries ("broadband Whitefield").
- Lists products/services/providers relevant to that location.
- Funnels users to individual detail pages.
- Consolidates topical authority for the location.

## F.2 URL structure

```
/cities/[city-slug]
  /cities/whitefield
  /cities/560066  (by pincode — for hyper-local)

Or combined with service:
  /[service]/[city]
    /fibre-broadband/whitefield
```

## F.3 Content structure

```
<h1>[Service] in [City] — [Differentiator]</h1>

<section>
  <!-- Brief overview of the service in this location -->
</section>

<section>
  <h2>Coverage in [City]</h2>
  <!-- Map or list of sub-areas -->
</section>

<section>
  <h2>Plans / pricing for [City]</h2>
  <!-- Location-specific pricing if it varies -->
</section>

<section>
  <h2>Customer stories from [City]</h2>
  <!-- Local case studies -->
</section>

<section>
  <h2>Local FAQs</h2>
  <!-- City-specific questions -->
</section>

<section>
  <h2>Nearby areas</h2>
  <!-- Internal links to sister hubs -->
</section>
```

## F.4 Schema

```json
{
  "@type": "CollectionPage",
  "name": "Fibre Broadband in Whitefield",
  "about": {
    "@type": "Place",
    "name": "Whitefield, Bangalore"
  },
  "mainEntity": {
    "@type": "LocalBusiness",
    "@id": "https://example.com/#localbusiness"
  },
  "hasPart": [
    {
      "@type": "ItemList",
      "name": "Coverage areas",
      "itemListElement": [ /* sub-locations with ListItem */ ]
    }
  ]
}
```

## F.5 Audit checklist for location hubs

- **LH-1** `<h1>` includes the service + location.
- **LH-2** `CollectionPage` schema with `about: Place` present.
- **LH-3** Coverage detail specific to the location (maps, sub-areas, pincode list).
- **LH-4** Internal links to individual detail pages in this location.
- **LH-5** Links to sister location hubs ("Nearby areas") for topical clustering.
- **LH-6** Local proof (customer stories, testimonials) with location attribution.
- **LH-7** Location-specific FAQs marked up with `FAQPage`.
- **LH-8** Google Business Profile linked from the page footer (for local queries).

---

# Part G: Company / Provider Hubs

Reference for company or provider hub pages (e.g., `/careers/amazon`, `/providers/gsurf`).

## G.1 Purpose

A company hub is a page that:
- Ranks for "[company] jobs" / "[company] products" / "[company] reviews".
- Lists inventory related to that company (jobs, reviews, products, services).
- Signals Google that YOU are the authoritative aggregator for this brand.

## G.2 URL structure

```
/careers/[company-slug]
  /careers/amazon
  /careers/amazon/data-analyst  (refined)
  /careers/amazon/remote/data-analyst  (further refined)
  /careers/amazon/data-analyst/bangalore  (fully refined)
```

## G.3 Content rules

- Must have REAL data from the company (scraped + maintained, licensed, or contributed).
- Must differentiate from the company's own site (different UX, additional data, better search/filter).
- Company logo rendered via `<img alt="[Company name] logo">` — not via JS-hydrated sprite.

## G.4 Schema

```json
{
  "@type": "Organization",
  "@id": "https://example.com/careers/amazon/#organization",
  "name": "Amazon",
  "logo": "https://...",
  "sameAs": [
    "https://en.wikipedia.org/wiki/Amazon_(company)",
    "https://www.wikidata.org/wiki/Q3884",
    "https://www.crunchbase.com/organization/amazon"
  ]
}
```

Plus either `ItemList` (for jobs/products listed) or `CollectionPage` around the hub itself.

### Critical sameAs for third-party hubs
When YOU aggregate data about someone else's company, `sameAs` pointing to their Wikipedia / Wikidata / Crunchbase entry tells Google "this page is about the same Amazon that's on Wikipedia" — that's the entity disambiguation signal.

## G.5 Lifecycle for company hubs

- **Active company** — maintain, update, refresh.
- **Brand change / acquisition** — 301 old slug to new slug. Update sameAs.
- **Defunct company** — keep page as historical (archived status in schema); may still rank for "[company] careers" queries for months.
- **Trademark issue** — pre-empt by respecting DMCA / trademark policies. Don't use the logo if challenged.

## G.6 Audit checklist for company hubs

- **CH-1** Company `Organization` schema with `sameAs` to Wikipedia / Wikidata / Crunchbase.
- **CH-2** Company logo rendered as `<img>` in SSR HTML with proper alt text.
- **CH-3** Real data from/about the company (not a template).
- **CH-4** Differentiation from the company's own website (different UX or additional value).
- **CH-5** `ItemList` or `CollectionPage` schema wrapping any listed items (jobs, products).
- **CH-6** Trademark / brand usage compliant.
- **CH-7** Company's social profiles linked from the hub (helps entity graph).
- **CH-8** If aggregating jobs, `JobPosting` schema on each job detail linked from this hub.

---

## Cross-type severity guidance

Across every PSEO type, severity tends to cluster on:

- **Critical** — template-wide rendering broken (Hero in CSR); schema missing on rich-result-eligible pages; blanket `noindex`; URL pattern inconsistency across sitemap/routes/redirects
- **High** — missing required schema fields; lifecycle broken (stale records still indexed); dynamic sitemap not excluding inactive content
- **Medium** — unique per-variant content missing (doorway risk); FAQ absent; breadcrumbs missing
- **Low** — slug formatting issues; redundant pagination; unused `<priority>` in sitemap

See `issue-framework.md` for how to write up findings from this playbook.
