# Image Optimization Reference

How images should be formatted, named, and described so they work for SEO, AEO, and GEO simultaneously — without breaking logo and icon rendering.

Read whenever an audit targets any page with images beyond decorative UI (hero banners, product shots, illustrations, screenshots, infographics).

## The three jobs an image does for search

1. **SEO** — contributes to ranking via Google Images, feeds LCP, gives Googlebot additional context via `alt` text.
2. **AEO** — extracted into Google AI Overviews and Rich Results alongside the text. The alt text often becomes the image's caption in the AI-generated answer.
3. **GEO** — LLMs cite both text and images when training or retrieving. A well-described image with a meaningful filename is more likely to be attached to a citation.

## Table of contents

1. [Format rules (WebP / AVIF / PNG / JPG / SVG)](#1-format-rules)
2. [Alt text — the programmatic-SEO/AEO/GEO formula](#2-alt-text)
3. [Title attribute — when to use, when not to](#3-title-attribute)
4. [Filename conventions](#4-filename-conventions)
5. [Dimensions, srcset, sizes](#5-dimensions-srcset-sizes)
6. [Lazy loading and priority](#6-lazy-loading-and-priority)
7. [LCP image handling](#7-lcp-image-handling)
8. [Structured-data image requirements](#8-structured-data-image-requirements)
9. [Accessibility + SEO overlap](#9-accessibility--seo-overlap)
10. [Audit checklist](#10-audit-checklist)

---

## 1. Format rules

Different image types should use different formats. Treating all images the same way breaks either rendering quality or SEO.

| Image type | Format | Why |
|---|---|---|
| Banner / hero / LCP | **WebP** (primary) with JPG fallback | 30–40% smaller than JPG at equivalent quality → faster LCP. AVIF is better but Safari < 16 and older Android don't support it well yet. |
| Product shots, thumbnails, editorial | **WebP** (primary) with JPG fallback | Same — use WebP widely. |
| Infographics, diagrams with text | **WebP** or PNG | WebP lossless is fine; PNG if you need crisp line art. |
| Logo | **SVG** (primary) → PNG fallback | Vector scales perfectly on high-DPI screens. No conversion to WebP — SVG is already smaller and renders better at any size. |
| Favicon set | `.ico` + PNG (16, 32, 180, 192, 512) + SVG (`favicon.svg`) | Browser compatibility spans 20+ years of standards; keep the full set. |
| UI icons | **SVG** inline or as sprites | Inline SVG is zero-request, hand-tintable with CSS. No WebP. |
| Profile / avatar images | **WebP** with JPG fallback | Lots of them, so compression matters. |
| Animated images | **WebP** animated OR a short muted autoplay **MP4/WebM** | Never use animated GIF — it's 5–10x the size. MP4/WebM is better for anything longer than 3s. |

### WebP ≠ universal

- Never convert `favicon.ico` to WebP (browsers require the ICO format for the root favicon).
- Never convert SVG logos to WebP (you lose scalability; WebP rasterises).
- Never convert small icons (< 48×48) to WebP — the byte savings are negligible and SVG or PNG is universally supported.
- **Always keep an original-format fallback** using `<picture>`:

```html
<picture>
  <source srcset="/img/hero.webp" type="image/webp">
  <source srcset="/img/hero.avif" type="image/avif">
  <img src="/img/hero.jpg" alt="..." width="1200" height="630" loading="eager">
</picture>
```

Without the fallback, browsers without WebP support (rare but real) see a broken image — and Googlebot's WRS sometimes gives up before processing unknown MIME types.

## 2. Alt text — the programmatic-SEO/AEO/GEO formula

Alt text is not keyword stuffing and not a caption. It's a **one-sentence description for a user who can't see the image**, written in a way that happens to help search indexing.

### The formula

```
[Primary subject] [action or state] [context — location, time, or purpose]
```

Optionally append one brand or keyword if the page's topic absolutely requires it, but only when it reads naturally.

### Examples, by page intent

**Informative blog post** (topic = "Best frameworks for server-rendered React in 2026")
- ✅ Good: `alt="Screenshot of the Next.js 15 App Router documentation showing the revalidate export"`
- ❌ Bad: `alt="Next.js React framework screenshot 2026 server rendering App Router documentation"` (keyword stuffing)
- ❌ Bad: `alt="next-js-screenshot.png"` (filename; useless)

**Transaction / money page** (topic = "Enterprise fibre broadband Whitefield")
- ✅ Good: `alt="Fibre optic cable being installed at a Whitefield office building"`
- ❌ Bad: `alt="fibre internet"` (too vague)
- ❌ Bad: `alt="Best fibre broadband provider Whitefield enterprise internet"` (keyword stuffing)

**Programmatic page — job detail**
- ✅ Good: `alt="Beta Consulting company logo"`
- ✅ Good: `alt="Senior React Developer role at Beta Consulting — office photo from Pune campus"` (if the image is a campus photo, not the logo)
- ❌ Bad: `alt="Senior React Developer React TypeScript Next.js jobs Pune Beta Consulting apply now"` (keyword stuff)

**Programmatic page — course detail**
- ✅ Good: `alt="JEE Advanced Physics course — instructor Dr Priya Iyer during a live class"`
- ✅ Good: `alt="JEE Advanced Physics syllabus coverage diagram"`

**Programmatic page — event detail**
- ✅ Good: `alt="Past attendees at the 2025 your-event-name, Mumbai"`

### Decorative images

If the image is purely decorative (background pattern, geometric divider, stock "generic office" shot), use:

```html
<img src="..." alt="" role="presentation">
```

An empty `alt` tells screen readers and Googlebot "skip this". **Missing `alt` entirely is different** — that's a hard accessibility failure and a soft SEO signal.

### Icon images

If the icon conveys meaning (e.g., "✓ Verified"):
```html
<svg aria-label="Verified" role="img">...</svg>
```

If the icon is purely decorative (e.g., a star burst next to a heading):
```html
<svg aria-hidden="true" focusable="false">...</svg>
```

## 3. Title attribute — when to use, when not to

The `title` attribute on an image shows a tooltip on hover. In 99% of cases, **don't use it**:

- Most users don't hover (mobile + touch).
- Screen readers sometimes read `title` instead of `alt`, producing confusing audio.
- It's not a ranking signal — Google explicitly ignores `title` for image search.
- If you use it, browsers show it as a native tooltip, which breaks custom tooltip UI.

**Use `title` only when:**
- The image is inside a link and you want a descriptive tooltip on hover (desktop UX); even here, use it sparingly.
- Keep it a short phrase (< 50 chars), not a sentence.

## 4. Filename conventions

- Lowercase, hyphen-separated, descriptive.
- No spaces, no underscores (search engines treat underscores as word-joiners inconsistently).
- No dates or version numbers embedded in public URLs (they look dated and clutter the URL).
- Match the image to the topic where possible.

| Bad | Good |
|---|---|
| `IMG_20261215_1042.jpg` | `whitefield-fibre-installation.jpg` |
| `banner_final_v2.jpg` | `enterprise-fibre-banner.jpg` |
| `hero.webp` | `jee-advanced-physics-live-class.webp` |

Filename is a minor signal compared to alt text + surrounding context, but it's cheap to get right.

## 5. Dimensions, srcset, sizes

Every `<img>` should have explicit `width` and `height` attributes matching the intrinsic dimensions. Otherwise the browser can't reserve layout space → CLS.

```html
<img src="/img/hero.webp" alt="..." width="1200" height="630">
```

For responsive images, use `srcset` and `sizes`:

```html
<img
  src="/img/hero-1200.webp"
  srcset="/img/hero-600.webp 600w, /img/hero-900.webp 900w, /img/hero-1200.webp 1200w, /img/hero-1800.webp 1800w"
  sizes="(max-width: 600px) 100vw, (max-width: 1200px) 80vw, 1100px"
  alt="..."
  width="1200"
  height="630">
```

Key rules:
- Generate at least 3 widths (small, medium, large). 4 is better for retina.
- The largest `src` should match the page's max container width, not the full viewport.
- `sizes` must match your actual CSS layout — wrong `sizes` makes browsers download too-large images.

## 6. Lazy loading and priority

```html
<!-- Above the fold (LCP image) — load eagerly, mark high priority -->
<img src="..." alt="..." width="..." height="..." loading="eager" fetchpriority="high">

<!-- Below the fold — lazy load -->
<img src="..." alt="..." width="..." height="..." loading="lazy" decoding="async">
```

**Never lazy-load the LCP image.** Lazy loading the hero delays LCP by 200–500ms. The LCP candidate should be preloaded:

```html
<link rel="preload" as="image" href="/img/hero.webp"
      imagesrcset="/img/hero-600.webp 600w, /img/hero-1200.webp 1200w"
      imagesizes="(max-width: 600px) 100vw, 1100px">
```

## 7. LCP image handling

LCP (Largest Contentful Paint) is almost always an image. Three rules:

1. **Identify it.** In Chrome DevTools → Performance → LCP — the element is highlighted. Usually the hero banner.
2. **Preload it.** `<link rel="preload" as="image" ...>` in `<head>`, before any fonts or CSS that aren't render-blocking.
3. **Don't lazy-load it.** `loading="eager"` explicitly, or simply omit the attribute (default is eager).

For Next.js sites:
```jsx
<Image
  src="/hero.webp"
  alt="..."
  width={1200}
  height={630}
  priority  // ← this is the "preload + eager" equivalent
  sizes="(max-width: 600px) 100vw, 1100px"
/>
```

`priority` on the LCP image is non-negotiable. Pages where `priority` isn't set on the hero consistently lose 300–800ms of LCP.

## 8. Structured-data image requirements

Different schema types have different image requirements. Google enforces these for rich-result eligibility.

| Schema type | Image property | Min dimensions | Format |
|---|---|---|---|
| `Article` / `NewsArticle` | `image` (array of URLs preferred) | 1200 × 675 (landscape) OR 1200 × 1200 (square) | Absolute URL, one per aspect ratio |
| `Product` | `image` | 696 × 696 minimum | JPG/PNG (WebP accepted by Google since 2022) |
| `Recipe` | `image` | 1200 × 675 or square | Same |
| `JobPosting` | `hiringOrganization.logo` | 112 × 112 minimum | Absolute URL to the company logo |
| `LocalBusiness` | `logo` + `image` | 112 × 112 (logo) and 696 × 696 (image) | Absolute URLs |
| `Event` | `image` | 696 × 696 | Absolute URL |
| `Organization` | `logo` | 112 × 112, square preferred | Absolute URL |
| `Person` | `image` | No hard minimum but 400×400+ | Absolute URL |

### Always absolute URLs in schema

```json
"image": "/img/hero.webp"         // ❌ relative — Google rejects
"image": "https://example.com/img/hero.webp"  // ✅
"image": ["https://example.com/img/hero-1200x675.webp", "https://example.com/img/hero-1200x1200.webp"]  // ✅ multiple aspect ratios
```

### OpenGraph / Twitter Card image

```html
<meta property="og:image" content="https://example.com/og-hero-1200x630.webp">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Descriptive alt text — same rules as the formula above">

<meta name="twitter:image" content="https://example.com/og-hero-1200x630.webp">
<meta name="twitter:image:alt" content="...">
```

## 9. Accessibility + SEO overlap

Good alt text helps both screen-reader users and search crawlers. These overlap almost completely:

- WCAG 2.1 requires alt on every meaningful image (SC 1.1.1).
- Google's Image SEO guide explicitly recommends descriptive alt.
- Lighthouse and axe both flag missing alt as a hard fail.

Fix for accessibility → benefit for SEO. There's no tradeoff.

## 10. Audit checklist

- **IMG-1** Every non-decorative `<img>` has a descriptive `alt` attribute (not missing, not empty).
- **IMG-2** Decorative images have `alt=""` (explicit, not missing).
- **IMG-3** Alt text follows the formula `[subject] [action/state] [context]` — not keyword-stuffed, not just the filename.
- **IMG-4** Hero / banner images use WebP (primary) with JPG fallback via `<picture>` element.
- **IMG-5** Logo is SVG (primary) with PNG fallback. NOT converted to WebP.
- **IMG-6** Icons are inline SVG or SVG sprites. NOT WebP.
- **IMG-7** Favicons: full set (`.ico`, 16/32/180/192/512 PNG, `favicon.svg`).
- **IMG-8** Every `<img>` has explicit `width` + `height` attributes (CLS prevention).
- **IMG-9** Responsive images use `srcset` + `sizes` with 3+ widths.
- **IMG-10** LCP image has `fetchpriority="high"` (or Next.js `priority`) and is preloaded.
- **IMG-11** Below-the-fold images have `loading="lazy"` + `decoding="async"`.
- **IMG-12** Filenames are lowercase, hyphen-separated, descriptive (not `IMG_20261215.jpg`).
- **IMG-13** OpenGraph/Twitter image ≥ 1200×630 absolute URL.
- **IMG-14** Structured-data `image` properties are absolute URLs meeting type-specific min dimensions.
- **IMG-15** Structured-data `image` arrays include multiple aspect ratios (landscape + square) for Article/Recipe/Product.
- **IMG-16** No `title` attribute on images (unless specific UX justification).
- **IMG-17** Animated content uses WebP animated or MP4/WebM — NOT GIF.

---

## Severity guidance

- Missing alt on critical hero / product image → **High** (hurts accessibility + image SEO + AI Overview caption)
- Wrong format (WebP on a logo, breaking the rendering) → **High**
- Missing `width`/`height` on LCP image → **High** (CLS + LCP penalty)
- Alt text keyword-stuffed → **Medium** (passes basic crawl but signals low quality)
- Filename ugly (`IMG_20261215.jpg`) → **Low**
- No `srcset` on responsive images → **Medium**
- Missing favicon set → **Low**
