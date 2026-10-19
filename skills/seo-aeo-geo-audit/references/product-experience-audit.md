# Product Experience Audit Reference

Technical audits catch what's broken in the code. This reference catches what's wrong in the **product architecture** — the decisions that determine whether a site is actually usable for search and discoverable by LLMs, independent of whether the HTML is well-formed.

Read whenever the audit target has any of these patterns:
- A subdomain or section that represents more than one product / offering
- A listing page (mentors, authors, products, cities, events) where individual items are interactive content
- A paid product (course, subscription, service) above ~₹1 L / $1 K in price
- A lead-gen funnel (webinars, downloadable content, demo bookings)
- Any page where trust signals (reviews, testimonials, case studies) would influence a buying decision

Product-experience issues don't show up in Lighthouse. They show up in conversion rates, in Perplexity source cards, in how Google classifies your site's purpose.

## Table of contents

1. [Dedicated homepage vs product-first landing](#1-dedicated-homepage-vs-product-first-landing)
2. [Per-item detail pages for listings](#2-per-item-detail-pages-for-listings)
3. [Marketing-funnel design on lead-gen pages](#3-marketing-funnel-design-on-lead-gen-pages)
4. [UGC and review infrastructure](#4-ugc-and-review-infrastructure)
5. [Named testimonials with verifiable attribution](#5-named-testimonials-with-verifiable-attribution)
6. [Information architecture for multi-product sites](#6-information-architecture-for-multi-product-sites)
7. [Audit checklist](#7-audit-checklist)

---

## 1. Dedicated homepage vs product-first landing

### The problem

Subdomains and sites that host multiple products / services often evolve from a single product. The root URL becomes the sales page for that product — because when there was only one product, that was the correct call. Then more products get added as sibling paths (<code>/fullstack</code>, <code>/events</code>, <code>/mentors</code>), but the root stays as the original product's sales page.

### Why it hurts SEO, AEO, and GEO

- **Branded search** — a user searching your subdomain's name lands on a sales page for one product. They see pricing, don't understand the broader offering, and bounce.
- **AEO** — Google AI Overview answers "what is [subdomain]" by extracting the H1 + first paragraph of the root URL. If those describe one product, AIO describes the subdomain as that one product only.
- **GEO** — ChatGPT / Perplexity / Claude citations for "what does [brand] do" pull from the homepage. A product-specific homepage tells LLMs the brand is narrower than it actually is.

### The fix pattern

```
Before:                               After:
/                → DSA program         /                → Brand overview (new)
/fullstack       → Fullstack program   /programs/dsa    → DSA program (301 from /)
/events          → Events listing      /programs/fullstack  → Fullstack (301 from /fullstack)
/mentors         → Mentors listing     /events          → Events (unchanged)
                                        /mentors         → Mentors (unchanged)
```

The new root URL is a genuine overview:
- H1 describes the full brand / subdomain scope
- A grid of all products with individual CTAs
- Cross-sell paths to mentors, events, blog, testimonials
- Aggregate social proof (total students, total placements, etc.)

### Signal to watch for in an audit

If the subdomain's root URL has a Course / Product / Service schema (not Organization + WebSite), it's a product page pretending to be a homepage.

### Severity
**High** if the subdomain represents more than one product / offering. The miss compounds across every marketing channel that points at the root URL.

## 2. Per-item detail pages for listings

### The problem

Listing pages (mentors, authors, products, cities, job categories, event speakers) often display a grid of cards — but the cards don't link to dedicated detail pages. Each item is a dead end.

This is a huge miss because each item deserves a URL. Each item has:
- A name a user might search for directly
- Expertise / attributes that rank for long-tail queries
- Social proof / reviews that LLMs want to cite
- Social profile URLs that feed sameAs / entity graph

### Common examples

- Mentor directory without `/mentors/[slug]`
- Author listing without `/authors/[slug]`
- City landing pages without a top-of-category hub linking to them
- Event listings where past events vanish instead of becoming recordings
- Customer logos displayed as images without case-study URLs

### Why it hurts SEO, AEO, and GEO

- **SEO:** Long-tail searches for "[individual name] at [brand]" have no landing page.
- **AEO:** Google AI Overview can't cite a specific entity without a dedicated page for it.
- **GEO:** LLMs answering "who should I book for [specialty]" need named entity pages. A listing can't be cited for a specific person.
- **Internal link equity:** each detail page backlinks into the listing and cross-links to related items (mentors ↔ courses ↔ events). Without detail pages, there's no internal link graph.

### The fix pattern

For every listing page with N items:

1. Build `/[listing]/[slug]` for each item.
2. Each detail page has:
   - H1 = item name
   - Full schema for the entity type (Person for mentors/authors, Product for products, Event for events)
   - Rich `sameAs` links for entity disambiguation
   - Reviews / testimonials specific to this item
   - Cross-links to related items (other mentors who cover the same topic, other events from the same speaker)
3. Add a per-type sub-sitemap (`sitemap-mentors.xml`, `sitemap-authors.xml`) with per-URL real lastmod.
4. Update the listing page's item cards to link to each detail page.

### Severity
**High** on mentor-driven / author-driven / person-heavy products. **Medium** on product catalogs where product pages exist but drill-down may be thin.

## 3. Marketing-funnel design on lead-gen pages

### The problem

Free events, webinars, downloadable content, and demos are top-of-funnel lead-gen vehicles for paid products. But the pages for these often read as informational listings — no registration form, no email capture, no per-event pages, no recording archive, no cross-sell to the paid offer.

### What a marketing-funnel page actually needs

For each event / webinar / masterclass / resource:

- **Dedicated URL** (`/events/[slug]`, `/resources/[slug]`).
- **Full schema for the event/resource type** (Event schema with eventStatus, eventAttendanceMode, offers, performer).
- **Conversion apparatus** on the page:
  - Registration / download form (with email capture)
  - Add-to-calendar links (ICS, Google Calendar, Outlook)
  - Confirmation email flow after registration
  - Reminder emails pre-event
- **Speaker / author cross-links** → link to their mentor/author profile page.
- **Recording / replay URL** after the event. Past events become evergreen content assets.
- **Cross-sell to paid product** — every event page ends with "ready for the full program?" + CTA.
- **Related content** — blog posts on the same topic, related events, next event in the series.

### Why missing this hurts SEO, AEO, and GEO

- **SEO:** Individual event pages rank for "free [topic] webinar India April 2026" style queries. Listings don't.
- **AEO:** Google's Event rich result surfaces date + registration + speaker in SERPs — only works with per-event pages + Event schema.
- **GEO:** LLMs answering "best free DSA webinars" need specific event entities to cite.
- **Conversion:** Without email capture, attendees never enter your CRM. Without speaker cross-links, they don't discover your paid mentors. Without cross-sell, the funnel is a cul-de-sac.

### Severity
**Medium** on a site with an events section. **High** if paid product pricing is significant (> ₹1 L / $1 K) — the event funnel is often the primary qualification channel.

## 4. UGC and review infrastructure

### The problem

Sites selling paid products above a certain price point need verifiable social proof. This includes:

- **Google Business Profile reviews** (first-class signal for Gemini, AI Overview, local queries).
- **Third-party review platforms** — Trustpilot, G2, Capterra, Glassdoor, AmbitionBox (India), Clutch (B2B services), TripAdvisor (hospitality), App Store / Play Store (apps).
- **On-site reviews and testimonials** with Review + Person schema.
- **Outcome stories / case studies** with named clients + verifiable metrics.

### Why missing this hurts GEO specifically

LLMs weigh reviews heavily for commercial queries. When a user asks ChatGPT "is [brand] legit" or Perplexity "best bootcamps with student reviews," the model's answer pulls from platforms that HAVE reviews. If your brand has no review corpus anywhere, you don't appear in the citation carousel even if the product is great.

The flywheel:
1. Paid product.
2. Real customer outcomes.
3. Outreach to customers to leave reviews on GBP / Trustpilot / AmbitionBox.
4. Each new review is indexable content + LLM-citable data + trust signal for new buyers.
5. Rising review count → better rankings + better LLM citation + higher conversion on landing pages.

Starting this flywheel from 0 takes 60–90 days with consistent outreach. Starting at 0 with no plan takes forever.

### The audit questions

- Is Google Business Profile claimed and linked from the site footer?
- Are there ≥ 20 real reviews on at least one authoritative platform?
- Are those platform URLs in `Organization.sameAs`?
- Are any on-site testimonials real (named, with a verifiable LinkedIn / company)?
- Does any page have `aggregateRating` schema? If yes, does the rating + count match a visible source on the page?

### Severity
**Critical** — on a paid product above ~₹1 L / $1 K with zero review infrastructure. This is a structural trust deficit.
**High** — if reviews exist but aren't linked / integrated.

## 5. Named testimonials with verifiable attribution

### The problem

Testimonials on landing pages are often anonymous ("Sarah K., software engineer"), un-photographed, or completely fabricated. They carry almost no weight because a visitor can't verify them.

### The fix pattern

Every testimonial should include:

- **Full name** (first + last) OR first name + last initial with clear justification (e.g. "Sarah K. asked us not to publish her full name because she's still at her previous employer").
- **Photo** of the real person.
- **Current role + company** (post-outcome if outcome-based).
- **LinkedIn profile URL** (`rel="nofollow noopener"`) — the verification mechanism.
- **Specific outcome quantified** (salary jump, interview round cleared, cert earned, timeframe).
- **Date** of the testimonial.
- **Review schema** with typed `author` Person + `reviewRating` + `datePublished`.

### Why this matters for every pillar

- **SEO:** Verifiable reviews are positive ranking signals for YMYL and commercial pages. Google's quality systems detect fake reviews and penalize.
- **AEO:** Google AI Overview surfaces named reviews when answering "is [brand] any good" queries.
- **GEO:** LLMs heavily weight first-person named attributions. "Priya K., now an SDE-2 at Flipkart, says..." is citable; "A student said..." is not.
- **Conversion:** Named + verifiable testimonials typically lift landing-page conversion 10–30% over anonymous ones.

### Anti-patterns

- "Trusted by teams at Google, Meta, Amazon..." with just logo images — no way to verify.
- Stock photos with fake names — screens obvious to users and flagged by Google.
- `aggregateRating` schema without a visible source on the page — manual-action trigger.
- Reviews only visible after a carousel rotates — non-JS crawlers see nothing.

### Severity
**Medium** on most sites. **High** for paid products where a real review library exists but isn't being used on landing pages.

## 6. Information architecture for multi-product sites

### The problem

Sites that host multiple products often have implicit IA (information architecture) that only the builders understand. Users arriving fresh can't figure out:
- Is this a job board or a bootcamp?
- Which products are live vs coming soon?
- How do the products relate to each other?
- What's the upgrade path between free and paid tiers?

### IA principles that affect SEO / AEO / GEO

1. **Consistent navigation across pages.** Users + crawlers should see the same top-nav and footer structure regardless of which page they land on.
2. **Breadcrumbs on every non-homepage page** — both visible and in `BreadcrumbList` schema.
3. **Cross-linking between related content** — blog post → relevant product, product → relevant mentor, mentor → next event with that mentor, etc.
4. **A site-wide search or navigation hub** — helps users who arrived via a deep link understand where they are.
5. **Canonical domain strategy** — when the brand has multiple subdomains, each subdomain should have its own Organization `@id` with a clear `parentOrganization` reference.
6. **Consistent branding across subdomains** — same logo, same color palette, same voice. Cross-subdomain flow should feel like one brand.

### Signal to watch for in an audit

- Breadcrumbs missing from a deep page
- Footer varies between pages
- Sub-product pages don't reference the parent brand
- No path from a blog post to the relevant product

### Severity
**Medium** — these issues compound silently but aren't crises individually.

## 7. Audit checklist

- **PX-1** Subdomain or site root is a genuine overview (not a product-specific sales page) when the site hosts more than one product.
- **PX-2** Every listing page (mentors, authors, cities, events) has individual detail pages at `/[listing]/[slug]`.
- **PX-3** Each detail page has entity schema (Person, Event, Product, Place).
- **PX-4** Detail pages have rich `sameAs` links (LinkedIn, X, GitHub, Wikipedia where applicable).
- **PX-5** Per-type sub-sitemap exists for listings with more than a handful of items.
- **PX-6** Event / webinar / masterclass pages have registration forms with email capture.
- **PX-7** Event pages have add-to-calendar links (ICS + Google Calendar).
- **PX-8** Past events stay live with recordings; they don't 404 after the date.
- **PX-9** Event pages cross-link to speaker profiles AND to the paid program CTA.
- **PX-10** Google Business Profile claimed + linked from site footer.
- **PX-11** Brand has at least 20 reviews on a relevant review platform; profile URL in Organization.sameAs.
- **PX-12** On-site testimonials include real names, photos, current role + company, LinkedIn URLs.
- **PX-13** Named outcome stories with quantified results (salary jump, interview cleared, metric achieved).
- **PX-14** `aggregateRating` schema only if verifiable review corpus exists + matches visible page content.
- **PX-15** Breadcrumbs on every non-homepage page — visible AND `BreadcrumbList` schema.
- **PX-16** Consistent top-nav and footer across every page on the subdomain.
- **PX-17** Blog posts cross-link to relevant paid products; products cross-link to related blog content.
- **PX-18** For multi-subdomain brands, each subdomain declares `parentOrganization` in Organization schema.

---

## Severity guidance

- Product-first "homepage" on a multi-product subdomain → **High**
- Listing without individual detail pages on a person-driven / mentor-driven product → **High**
- Paid product above ₹1 L / $1 K with zero UGC / review infrastructure → **Critical**
- Event/webinar page with no registration form → **Medium**
- Testimonials without names / photos / LinkedIn verification → **Medium**
- Cross-linking weak across the site → **Medium**
- Breadcrumbs missing → **Low**
