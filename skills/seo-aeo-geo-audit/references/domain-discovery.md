# Domain Discovery — Step 0 of every audit

**Read this first, before any other reference file, on every single audit.**

Not every domain has the same shape. A staffing subdomain has JobPostings. A bootcamp has Courses. A marketing site has Products or Services. A blog has Articles. A documentation site has TechArticles. Applying checks that don't fit the domain produces noise findings — Google-for-Jobs schema warnings on a marketing site, course-schema gaps on a blog, product-review audits on a legal policy page. That erodes trust in the plugin.

**Rule:** audit only what the domain actually needs to be good at. Skip what doesn't apply. Say so explicitly in the report.

## Table of contents

1. [Why this step exists](#1-why-this-step-exists)
2. [How to detect the archetype](#2-how-to-detect-the-archetype)
3. [Domain archetypes + per-archetype audit scope](#3-domain-archetypes)
4. [What ALWAYS applies regardless of archetype](#4-what-always-applies)
5. [What to explicitly skip](#5-what-to-explicitly-skip)
6. [Reporting the archetype](#6-reporting-the-archetype)

---

## 1. Why this step exists

Three failure modes this step prevents:

1. **False-positive findings.** Flagging "No JobPosting schema on the pricing page" for a SaaS product site is noise — the site should never have JobPosting schema. A finding that doesn't apply is worse than no finding.

2. **Missed checks that do apply.** A blog-specific audit checks Article schema, Person authors, citation density, freshness. Running a generic audit misses these entirely.

3. **Wrong severity calibration.** "No Organization schema on homepage" is Critical for a business site, Low for a personal portfolio. Archetype decides calibration.

The archetype also changes which scoring rubric applies (Landing/Money vs Blog/Article from `seo-quality-score-rubric.md` and `eeat-score-rubric.md`).

## 2. How to detect the archetype

Detect the domain's primary purpose BEFORE loading any deep-dive reference. Use these signals in order:

### 2a. User intent (ask if unclear)
If the user says "audit my blog" or "check our recruitment site," use their framing. Confirm only if the URL contradicts the framing (e.g., user says "blog" but the URL is a pricing page).

### 2b. URL patterns
Strong signals from URL structure:

| URL contains | Likely archetype |
|---|---|
| `/jobs/`, `/careers/`, `/job-detail` | Job board OR staffing / recruitment services |
| `/courses/`, `/programs/`, `/curriculum`, `/bootcamp`, `/learn/` | Course platform / bootcamp |
| `/events/`, `/webinars/`, `/masterclass` | Event platform OR event section of a larger site |
| `/blog/`, `/articles/`, `/posts/`, `/news/`, `/guides/` | Blog / editorial |
| `/products/`, `/shop/`, `/cart`, `/checkout` | E-commerce |
| `/pricing`, `/plans`, `/features`, `/use-cases`, `/integrations` | SaaS / marketing |
| `/docs/`, `/api/`, `/reference/` | Documentation |
| `/portfolio`, `/case-studies`, `/work` | Agency / personal portfolio |
| `/mentors/`, `/experts/`, `/coaches` | Marketplace for services |
| `/policy`, `/terms`, `/privacy`, `/cookies` | Legal utility (not a standalone archetype; always exists alongside a main archetype) |

### 2c. Schema types present
Run the Rich Results Test OR parse existing JSON-LD from the homepage + 1 representative deep page:

| Schema types found | Likely archetype |
|---|---|
| `JobPosting` | Job board / staffing |
| `Course` + `CourseInstance` | Course platform / bootcamp |
| `Product` + `Offer` + `AggregateRating` | E-commerce |
| `SoftwareApplication` | SaaS / software product site |
| `Article` / `NewsArticle` / `BlogPosting` (primary on many pages) | Blog / news site |
| `LocalBusiness` + `address` + `geo` | Local-services business |
| `Organization` + `Service` + `EmploymentAgency` | Staffing / recruitment services (like services.example.com) |
| `Event` | Events platform |
| `Person` (primary on page) | Personal site / portfolio |
| Only `Organization` + `WebSite` | Marketing site / brand landing |

### 2d. Homepage content signals
Look at the homepage's H1 + first visible paragraph:

- "Hire top talent" / "Find your next role" → jobs
- "Learn to code" / "Master [skill]" / "Bootcamp" / "5-month program" → bootcamp / course
- "Book a demo" / "Start your free trial" / "API" → SaaS
- "Shop our collection" / "Add to cart" → e-commerce
- "Latest articles" / "Our thoughts" / "News" → blog
- "Our services" / "What we do" + contact-focused CTA → agency / professional services
- "Book a session" / "Browse mentors" / "Find an expert" → marketplace

### 2e. Top-nav structure
Primary navigation tells you what the site thinks it's about:

- Nav: `Home | About | Services | Industries | Case Studies | Contact` → professional services
- Nav: `Home | Jobs | Companies | Blog | For Employers` → job board
- Nav: `Home | Programs | Curriculum | Mentors | Events | Blog` → bootcamp
- Nav: `Home | Features | Pricing | Docs | Log in` → SaaS
- Nav: `Shop | Categories | Deals | Account | Cart` → e-commerce

### 2f. When in doubt — ask the user
If you can't confidently classify within 30 seconds of observation, ask the user:

> "I'm seeing [URL pattern] + [schema type] + [nav structure]. That looks like [archetype guess]. Is that right, or is this something different?"

Better to ask than to produce wrong findings.

## 3. Domain archetypes + per-archetype audit scope

### A. Marketing / corporate brand site
Homepage + About + Services + Contact + maybe Blog + Legal. No programmatic content, no product catalog.

**Examples:** agency homepages, B2B services brand, early-stage SaaS before the product launches.

**Apply:**
- `seo-audit.md` (core SEO checklist) ✓
- `aeo.md` + `aeo-transaction.md` on commercial pages ✓
- `geo.md` + `geo-transaction.md` on commercial pages ✓
- `crawlability-react.md` if React stack ✓
- `structured-data-advanced.md` — Organization, WebSite, FAQPage, LocalBusiness ✓
- `robots-llms-txt-playbook.md` ✓
- `sitemap-playbook.md` ✓
- `image-optimization.md` ✓
- `transaction-intent-playbook.md` on money pages ✓
- `product-experience-audit.md` if multi-product ✓
- `tracking-validation.md` ✓
- `ai-overview-playbook.md` ✓
- `llm-citation-playbook.md` ✓

**Skip:**
- `pseo-playbook.md` — no programmatic pages
- JobPosting / Course / Event schema checks

**Scoring rubric:** Landing/Money for commercial pages; Blog/Article if there's an editorial section.

### B. Blog / editorial site
Primary content is articles. May have commercial CTAs but not the focus.

**Apply:**
- `seo-audit.md` ✓
- `aeo.md` (informative content AEO) ✓
- `geo.md` (informative content GEO) ✓
- `crawlability-react.md` if React ✓
- `structured-data-advanced.md` — Article, NewsArticle, Person (authors), BreadcrumbList ✓
- `robots-llms-txt-playbook.md` ✓
- `sitemap-playbook.md` ✓
- `image-optimization.md` ✓
- `ai-content-safety.md` if AI-assisted ✓
- `ai-overview-playbook.md` ✓
- `llm-citation-playbook.md` ✓

**Skip:**
- `transaction-intent-playbook.md`
- `aeo-transaction.md` / `geo-transaction.md`
- `pseo-playbook.md` (unless per-category page programmatic)
- `product-experience-audit.md` sections on per-item detail pages (unless mentor-directory-style)
- JobPosting / Course / Event schema checks

**Scoring rubric:** Blog/Article.

### C. E-commerce store
Product catalog, cart, checkout, reviews.

**Apply:**
- `seo-audit.md` ✓
- `aeo-transaction.md` (with Shopping schema) ✓
- `geo-transaction.md` ✓
- `crawlability-react.md` if React ✓
- `structured-data-advanced.md` — Product, Offer, AggregateRating, Review, BreadcrumbList ✓
- `robots-llms-txt-playbook.md` ✓
- `sitemap-playbook.md` (with Product sub-sitemap) ✓
- `image-optimization.md` ✓
- `transaction-intent-playbook.md` ✓
- `pseo-playbook.md` Part A (for category / filter pages if programmatic) ✓
- `tracking-validation.md` (especially GA4 e-commerce + Google Ads + Meta Pixel) ✓
- `ai-overview-playbook.md` — shopping integration ✓
- `llm-citation-playbook.md` ✓

**Skip:**
- JobPosting / Course / Event schema checks
- `pseo-playbook.md` Parts B-G (unless specifically applicable)

**Scoring rubric:** Landing/Money (product detail pages).

### D. SaaS / software product site
Marketing site for a software product. Pricing, features, docs.

**Apply:**
- `seo-audit.md` ✓
- `aeo-transaction.md` + `geo-transaction.md` on pricing/feature pages ✓
- `aeo.md` + `geo.md` on docs/blog ✓
- `crawlability-react.md` if React ✓
- `structured-data-advanced.md` — SoftwareApplication, Product, Organization, WebSite, FAQPage ✓
- `robots-llms-txt-playbook.md` ✓
- `sitemap-playbook.md` ✓
- `image-optimization.md` ✓
- `transaction-intent-playbook.md` ✓
- `tracking-validation.md` ✓
- `ai-overview-playbook.md` ✓
- `llm-citation-playbook.md` ✓

**Skip:**
- JobPosting (unless /careers exists separately — audit that as a separate scope)
- Course / Event schema
- `pseo-playbook.md` parts that don't apply

**Scoring rubric:** Landing/Money on commercial pages; Blog/Article on docs.

### E. Job board (native, not staffing)
Aggregated job listings from many employers.

**Apply:**
- `seo-audit.md` ✓
- `pseo-playbook.md` Part A (Jobs) ✓
- `structured-data-advanced.md` — JobPosting, Organization, hiringOrganization ✓
- `crawlability-react.md` ✓
- `sitemap-playbook.md` (with jobs sub-sitemap, lifecycle rules) ✓
- `robots-llms-txt-playbook.md` ✓
- `image-optimization.md` ✓
- `aeo-transaction.md` on /jobs/[slug] pages ✓
- `geo-transaction.md` ✓
- `tracking-validation.md` ✓
- `ai-overview-playbook.md` — Google for Jobs ✓
- `llm-citation-playbook.md` ✓

**Skip:**
- Course / Event schema

**Scoring rubric:** Landing/Money on individual job pages; different scoring needed for the /jobs listing page.

### F. Staffing / recruitment services
B2B services brand that happens to also list open positions. Mix of marketing + jobs.

**Examples:** services.example.com — services-first, jobs are a secondary surface.

**Apply:**
- `seo-audit.md` ✓
- `structured-data-advanced.md` — Organization + EmploymentAgency + Service + JobPosting (if jobs exist) ✓
- `transaction-intent-playbook.md` on services/pricing pages ✓
- `pseo-playbook.md` Part A ONLY if there are many job detail pages ✓
- `aeo-transaction.md` + `geo-transaction.md` ✓
- All generic refs (sitemap, robots, image, tracking, AIO, LLM citation) ✓

**Skip:**
- Course / Event schema (unless they also run training)
- `pseo-playbook.md` parts unrelated to jobs

**Scoring rubric:** Landing/Money (B2B services content).

### G. Course platform / bootcamp
Paid learning programs. Curriculum, mentors, events, testimonials.

**Apply:**
- `seo-audit.md` ✓
- `structured-data-advanced.md` — Course, CourseInstance, Person (instructors/mentors), Organization ✓
- `pseo-playbook.md` Part B (Courses) ✓
- `pseo-playbook.md` Part C (Events) if events ✓
- `pseo-playbook.md` Part D (Skill Assessments) if assessments ✓
- `transaction-intent-playbook.md` ✓
- `product-experience-audit.md` — mentor profiles, UGC, testimonials ✓
- `aeo-transaction.md` + `geo-transaction.md` ✓
- All generic refs ✓

**Skip:**
- JobPosting schema (unless they also hire)
- E-commerce `Product` schema unless selling physical goods
- Pure `Service` schema (use `Course` instead)

**Scoring rubric:** Landing/Money (program pages).

### H. Documentation site
Developer / product docs. Version-controlled, reference-heavy.

**Apply:**
- `seo-audit.md` ✓ (but with doc-specific interpretation — heading hierarchy matters more, breadcrumbs essential)
- `structured-data-advanced.md` — TechArticle, HowTo, BreadcrumbList, `inLanguage` ✓
- `aeo.md` + `geo.md` ✓ (docs are AIO gold)
- `ai-overview-playbook.md` ✓
- `llm-citation-playbook.md` ✓ (docs are heavily cited by LLMs)
- `crawlability-react.md` if React ✓
- `robots-llms-txt-playbook.md` ✓ (often has `llms.txt` + `llms-full.txt`)
- `sitemap-playbook.md` ✓

**Skip:**
- All commercial / transaction playbooks
- JobPosting / Course / Event / Product schema
- `tracking-validation.md` typically unless marketing team specifically requests

**Scoring rubric:** Blog/Article (docs behave like articles).

### I. Multi-product conglomerate / parent brand
Parent site that has multiple product subdomains (e.g., `www.example.com` with `jobs.example.com`, `learn.example.com`, `services.example.com`, `blog.example.com`).

**Apply:**
- `seo-audit.md` ✓
- `structured-data-advanced.md` — Organization with `subOrganization` array + consistent `@id` across subdomains ✓
- `product-experience-audit.md` — cross-subdomain IA ✓
- `aeo-transaction.md` + `geo-transaction.md` on the brand homepage ✓
- React / Next.js-specific: `react-nextjs-architecture-profile.md` ✓
- All generic refs ✓
- Cross-subdomain consistency check (sameAs, contact info, logo, policies) ✓

**Focus areas specific to this archetype:**
- Each subdomain should reference the parent `@id`
- Consistent NAP (name + address + phone) across subdomains
- Consistent `Organization.sameAs` across subdomains
- Parent brand's homepage should introduce each subdomain clearly

**Scoring rubric:** Landing/Money on parent homepage; recommend scoring each subdomain separately using its own archetype.

### J. Personal site / portfolio
Individual's site. Bio, portfolio, blog, contact.

**Apply:**
- `seo-audit.md` ✓
- `structured-data-advanced.md` — Person as primary, `sameAs` to social + published work ✓
- `aeo.md` + `geo.md` ✓
- `llm-citation-playbook.md` ✓
- Generic refs ✓

**Skip:**
- All transaction/commercial playbooks (unless the person is selling services)
- PSEO / Job / Course schema

**Scoring rubric:** Blog/Article (usually).

## 4. What ALWAYS applies regardless of archetype

Some checks apply to every web property on the internet:

- `seo-audit.md` core checks — always
- `image-optimization.md` — every page has images
- `robots-llms-txt-playbook.md` — every site needs a robots.txt
- `sitemap-playbook.md` — every site should have a sitemap
- `crawlability-react.md` — if the stack is React / Next.js / any SPA
- `issue-framework.md` — always (required for reporting)
- Basic Organization schema + `<title>` + meta description + canonical — always

## 5. What to explicitly skip

If a check doesn't apply to the detected archetype, **don't silently ignore it** — say so in the report. This prevents confusion and makes the archetype-detection itself reviewable.

Pattern:

```
## Audit Scope (auto-detected)

**Detected archetype:** Staffing / recruitment services (B)
**Loaded reference files:** seo-audit.md, structured-data-advanced.md, transaction-intent-playbook.md, aeo-transaction.md, geo-transaction.md, sitemap-playbook.md, robots-llms-txt-playbook.md, image-optimization.md, tracking-validation.md, ai-overview-playbook.md, llm-citation-playbook.md, react-nextjs-architecture-profile.md

**Explicitly NOT audited (wrong archetype):**
- Course / CourseInstance schema (no courses on this domain)
- Event schema (no events on this domain)
- Product catalog + e-commerce rules (no shop)
- Programmatic SEO Parts B-G (not applicable)

If any of the above IS relevant (e.g., the staffing brand is starting to offer training programs), let me know and I'll re-run with the additional scope.
```

This transparency serves three purposes:
- The user can see what was checked and what wasn't
- The user can correct a mis-classification
- Future re-runs have a clear scope history

## 6. Reporting the archetype

Include the detected archetype in the audit's `overview` in the findings JSON — prominent, at the top of the report.

Also include it in the "audit.stack_label" or a new "audit.archetype" field, which the generator can render in the header meta grid.

### In the overview field
```
Detected domain archetype: Staffing / recruitment services. Audit scope tailored accordingly — no Course / Event / Product / PSEO-Jobs-board checks applied.
```

### In the summary card
A dedicated scorecard entry:
```json
{"label": "Detected archetype", "value_from": "auto", "value_to": "Staffing services", "hint": "Audit scope tailored to this site type — no course/event/product checks"}
```

---

## Edge cases

### A domain spans multiple archetypes
Example: Example Group has a marketing homepage + jobs + courses + mentors all mixed in. The answer is **subdomain-scoped auditing** — audit each subdomain with its own archetype. The parent brand homepage gets its own archetype (Marketing / Multi-product conglomerate). `react-nextjs-architecture-profile.md` has the site-specific pattern for this.

### A single URL mixes archetypes
Example: a long-form blog post with a product CTA embedded. Score the page with the PRIMARY archetype (blog), then flag the embedded CTA separately as a transaction-intent check.

### The archetype is genuinely unclear
Don't guess — ask. A wrong archetype produces worse findings than a 30-second clarifying question.

### The archetype changes over time
Revisit domain discovery on every audit. A site that was a blog last year may have launched a course platform this year. Classification isn't permanent.

---

## For junior engineers reading this

If you're running an audit and wondering "should I check Course schema on this page?" — come back to Section 3. Find the archetype. Look at the "Apply" and "Skip" lists. Done.

If you're not sure which archetype applies, come back to Section 2 (detection signals) or just ask the user. Asking is always better than guessing.
