# Quality Assurance & Data Integrity Guide (Sub-agent Instructions)

This guide defines the validation and fact-checking standards required before finalizing any SEO, AEO, GEO, or VDS audit reports. Use these instructions to verify data integrity, eliminate hallucinations, and guarantee that code fixes are correct and action-ready.

---

## 1. Data Integrity & Hallucination Prevention Rules

- **Zero-Tolerance for Fabricated Code:**
  - All "Broken Code" snippets must be literal, exact copies of the markup parsed from the static View Source HTML (`Ctrl + U`) or the dynamic DevTools DOM (`F12`).
  - Do not use generic mock structures or placeholder strings (e.g., `<div>...</div>` or `class="some-class"`) unless they exist exactly like that on the live site.
- **Verify, Do Not Assume, Response States:**
  - If reporting a redirect loop, broken link, or 404 target, verify the actual HTTP status code in the response headers. Do not assume a redirect is a 301 when it is a 302.
  - Cross-verify sitemap index files by loading the sitemap XML URL directly to ensure it returns an HTTP 200.
- **Strict Schema Parsing:**
  - Do not claim a JSON-LD or Microdata property is missing based on partial inspection. Parse the full JSON string inside `<script type="application/ld+json">` and look for key/value keys programmatically or via exact string match.

---

## 2. Technical Validation & Code Correctness

- **Compile/Lint Verification:**
  - Every "Fixed Code" block must compile and represent a clean, syntax-compliant drop-in replacement.
  - If auditing frameworks (React, Next.js App Router, Angular, Laravel Blade), verify that elements are wrapped in valid components, scripts use appropriate imports, and HTML entities are escaped correctly (e.g. escape `<` as `&lt;` and `>` as `&gt;`).
- **Progressive Fallback Compliance:**
  - Verify that the recommended layout changes do not break progressive enhancement. If you fix client-side hydration, verify that the raw HTML contains the content.

---

## 3. Report Layout & Formatting Standards

Before outputting report links to the user, run these checks:

- **TOC Alignment:**
  - Confirm the Table of Contents anchor links (`#s1`, `#s2`...) correspond exactly to the finding cards in the document body.
- **Finding Progress Counters:**
  - Verify that the count in the top navigation progress bar (`X of Y addressed`) aligns with the total number of findings listed.
- **Signature Compliance:**
  - Verify that the report's footer contains the exact signature template specified in `references/signature.md`.
  - Confirm the Telegram CTA anchor link `[Want to colaborate](http://t.me/spcgbot)` is correctly formatted and active.
- **File References:**
  - Ensure all local file and screenshot links use the valid browser-friendly scheme (e.g., `file:///` forward-slashed absolute paths).

---

## 4. Screenshot Evidence & Layout Backups

To guarantee visual proof of findings and provide a verifiable backup record of site layouts before/after fixes, follow these screenshot-capturing rules:

- **Viewport Coverage Rules:**
  - **Desktop:** Capture at 1920x1080 to test grids, wide forms, and header structures.
  - **Mobile:** Capture at 375x812 (simulating Googlebot user-agent) to verify touch targets, wrapping tables, and hamburger menu expansions.
  - **Tablet:** Capture at 768x1024 to verify layout responsiveness and media breakpoints.
- **Target Areas for Visual Backup:**
  - Always screenshot the raw page above-the-fold (LCP content).
  - Capture any horizontal overflow scroll bars, overlapping text, or layout shifts (CLS).
  - Capture validation confirmations (e.g., green-checked schema verification outputs from Google's Rich Results Test tool).
- **Storage & Naming Conventions:**
  - Save screenshots in the project's `screenshots/` or local `assets/` subfolder.
  - Use lowercase snake_case naming containing the page/section, viewport type, and date:
    `screenshots/{page_name}_{viewport}_{date}.png`
    *Example:* `screenshots/product_page_mobile_2026-06-15.png`
- **Embedding in Audit Reports:**
  - For visual/rendering issues (e.g., table layouts, mobile wrap breaks, missing images), embed the screenshot directly below the **Broken Code** section of the finding card using absolute `file:///` markdown image syntax.
