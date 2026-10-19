# Advanced SEO & VDS Audit Toolkit (Tools-to-Use Guide)

This guide documents the core toolset and inspection techniques required to execute high-fidelity Visibility-to-Demand System (VDS), SEO, AEO, and GEO audits. These tools allow the auditing agent to interact with live web elements, retrieve competitive market intelligence, and output standardized technical reports.

---

## 1. Browser-Specific Audits via Playwright

To capture dynamic client-side renders, analyze hydration loops, and simulate crawl behavior across different browser viewports (mobile, tablet, desktop) and user-agents, the agent uses **Playwright**.

### 📦 Setup & Installation
Run the following commands in the workspace to set up the browser automation layer:

```bash
# Initialize Playwright in the project
npm init playwright@latest -- --yes --quiet --browser=chromium

# Or install playwright directly as a dependency
npm install -D playwright

# Install browser binaries
npx playwright install chromium
```

### 🤖 Sample Automation Script
Use this script template to capture raw vs. rendered HTML and take screenshots under simulated bots:

```javascript
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    viewport: { width: 375, height: 812 }, // Mobile viewport
    isMobile: true
  });
  
  const page = await context.newPage();
  
  // Navigate to target domain
  await page.goto('http://localhost:8000', { waitUntil: 'networkidle' });
  
  // Extract rendered DOM and screenshot
  const renderedHTML = await page.content();
  await page.screenshot({ path: './screenshots/mobile-viewport.png', fullPage: true });
  
  console.log("Rendered HTML length:", renderedHTML.length);
  await browser.close();
})();
```

---

## 2. Manual Crawl & Code Extraction Techniques

When executing live site reviews, the agent uses both raw source and dynamic elements inspector views to compare what search engine crawlers see vs. what human users experience.

### 🔍 Raw HTML Extraction (Static Source Code)
- **Action:** Open target page in a browser and load the source view.
- **Shortcuts:** `Ctrl + U` (Windows/Linux) or `Cmd + Option + U` (Mac).
- **Purpose:** Identifies the exact markup delivered on the first HTTP response wave. This is what static search indexers and non-JS AI retrieval bots (e.g., Gemini, ChatGPT, Claude search crawls) read. If content is missing here, it is invisible to most crawl budgets.

### ⚡ Rendered HTML Extraction (Live DOM Tree)
- **Action:** Open Developer Tools and select the Elements / Inspector panel.
- **Shortcuts:** `F12` or `Ctrl + Shift + I` (Windows/Linux) or `Cmd + Option + I` (Mac).
- **Purpose:** Displays the fully hydrated DOM after React, Next.js, or generic client-side scripts execute. Used to discover hydration template anomalies, client-side overrides (like broken `"undefined"` titles), and dynamic grids.

### 🛡️ Manual Fallback Extraction Actions
If automated scraping tools or scripts crash due to security walls (Cloudflare, Akamai), CORS exceptions, or host barriers, use these fallbacks:
1. **cURL Simulation:** Run a cURL request spoofing Googlebot:
   ```bash
   curl -A "Googlebot" -L "https://example.com" -o raw-source.html
   ```
2. **Browser Copy-Paste:** Manually open the page using `Ctrl + U`, select all (`Ctrl + A`), copy, and save locally to `raw-source.html`.
3. **DevTools DOM Export:** Open DevTools (`F12`), right-click the root `<html>` tag, select **Copy -> Copy outerHTML**, and save locally to `rendered-dom.html`.

---

## 3. Specific Selector and Code Target Checklists

When inspecting HTML files, search and parse these elements:

- **Meta Tags & Head Content:**
  - `<title>`: Verify presence, character length (30–60), and relevance.
  - `<meta name="description">`: Verify presence and character length (110–160).
  - `<link rel="canonical" href="...">`: Check for absolute URLs matching the indexable location.
  - `<meta name="robots" content="...">`: Check for `noindex`, `nofollow`, or AI blocks.
- **Heading Structures (`<h1>` to `<h6>`):**
  - Check for exactly **one** `<h1>` representing the page entity.
  - Scan for broken strings (e.g., `<h1>undefined</h1>`, `<h1>null</h1>`).
  - Verify semantic heading levels (don't use styling classes on empty tags).
- **Anchor Elements (`<a>`):**
  - Extract `href` targets: check for lowercase paths, trailing-slash mismatches, and relative vs. absolute patterns.
  - Review anchor text for descriptive entity matching (avoid "click here," "read more").
- **Structured Data & Schema:**
  - Locate JSON-LD blocks: `<script type="application/ld+json">`.
  - Extract Microdata attributes: `itemscope`, `itemtype`, `itemprop`, `itemid`.
  - Verify complete entity matching (e.g. nested product stars, return policy graphs).
- **Images & Media Elements:**
  - `<img alt="...">`: Verify descriptive attributes on content images, and empty `alt=""` on decorative graphics.
  - Scan for `width`, `height`, and `loading="lazy"` attributes.
- **Agentic & Accessibility Labels:**
  - Form attributes: `<form action="..." method="...">`.
  - Form fields: `<input name="..." id="..." required aria-label="...">`.
  - Target labels: `aria-label`, `aria-labelledby`, `aria-describedby` used to guide autonomous browsers (SXO/AXO).

---

## 4. Model Context Protocol (MCP) Integrations

Model Context Protocol (MCP) allows the LLM agent to connect directly to professional SEO platforms and desktop crawlers to audit technical parameters, search visibility, backlink networks, and AI search presence.

### 🔗 Core MCP Servers to Install
Add these servers to your `.claude-plugin/manifest.json` or local Claude Code config:

- **Ahrefs MCP Server**
  - **Purpose:** Connects backlink authority profiling, page-level crawl status, search index errors, and keyword rankings directly to the chat context.
  - **Reference:** [Ahrefs Developer Portal / MCP Server](https://github.com/ahrefs/mcp-server-ahrefs)
- **Semrush MCP Server**
  - **Purpose:** Query search volumes, domain analytics, keyword difficulty, intent categorization, and organic visibility scores.
  - **Reference:** [Semrush API / MCP Connector](https://github.com/semrush/mcp-server-semrush)
- **Screaming Frog Crawler MCP Server**
  - **Purpose:** Automate site crawls to isolate XML sitemap gaps, redirection loops (301 chains), 404 targets, missing metadata, and invalid header sizes.
  - **Reference:** [Screaming Frog CLI Integration Guide](https://github.com/mcp-community/mcp-screamingfrog)

---

## 5. Public Search Analytics & Scraping Opportunities

When API keys are unavailable, the agent can leverage public analytics URLs. By dynamically replacing target domain query parameters, the browser automation layer can scrape ranking summaries, search traffic volumes, and page-level statistics.

### 📊 Semrush Public Analytics
Semrush exposes public domain overview analytics that can be fetched by substituting the target domain in the URL query string:

- **URL Pattern:**
  `https://www.semrush.com/analytics/overview/?searchType=domain&q=https%3A%2F%2F{target_domain}`
- **Example for Girish Kumar G:**
  `https://www.semrush.com/analytics/overview/?searchType=domain&q=https%3A%2F%2Fgirishkumarg.com`

**Automation Rule:** To retrieve organic traffic curves, ranking keywords, and referring domains without an API key, instruct Playwright to navigate to this public URL, wait for the metrics charts to render, and extract screenshot elements or read JSON responses via network requests.

---

## 6. Sitemaps, Bots & Statistical Sampling Protocols

To evaluate crawl path efficiency and index coverage, the agent must check config endpoints and calculate statistical audit sample sizes to ensure data accuracy.

### 🤖 Config File & XML Sitemap Extraction
1. **Robots.txt Analysis:** Fetch `/robots.txt` from the host. Check for correct user-agent rules (allow/disallow) and links to XML sitemaps.
2. **LLMs.txt Analysis:** Fetch `/llms.txt` or `/llm.txt`. Analyze if the site exposes context summaries and structural markdown pages optimized for LLM/agentic crawler ingestion.
3. **Single XML Sitemap:** Fetch `/sitemap.xml` directly to check for canonical URLs.
4. **Multiple Sitemaps Index:** If `/sitemap.xml` returns a `<sitemapindex>` root (containing links to sub-sitemaps like `/sitemaps/products-sitemap.xml` or `/sitemap_index.xml`), the agent must:
   - Identify the categories (e.g. products, categories, posts, users).
   - Fetch each child sitemap in a separate request to check for indexable, canonical URLs and correct `<lastmod>` headers.

### 🌐 Google Indexed Count Verification
- **Verification Query:** Search Google verbatim using the `site:` operator:
  `site:{domain}`
- **Metrics Check:** Extract the estimated number of indexed pages (e.g., "About 4,200 results"). Note the indexation rate by comparing this to the total count in the XML sitemaps index.

### 🏷️ Brand Mentions & Off-Page Authority Monitoring
To audit a brand's authority, footprint, and unlinked mentions across external indexable sites, execute these advanced Google search operators:
1. **Unlinked Brand Mentions:** Search for the brand name in quotes while excluding the brand's own domain:
   `"brand name" -site:{domain}`
   *Example:* `"BuildingWorld" -site:buildingworld.ai`
2. **Brand Mentions in Titles (High Authority Relevance):** Find pages where the brand name is featured directly in the page title across the web:
   `allintitle:"brand name" -site:{domain}`
   *Example:* `allintitle:"BuildingWorld" -site:buildingworld.ai`
3. **Co-Mentions & PR Profiling:** Identify instances where the brand name is mentioned alongside industry keywords, partners, or competitors:
   `"brand name" ("competitor name" OR "industry term") -site:{domain}`
   *Example:* `"BuildingWorld" ("Infra.Market" OR "building products") -site:buildingworld.ai`
4. **Excluding Partner/Sister Domains:** If the brand owns multiple domains (e.g., blogs or international sites) and they pollute the results, chain exclusions:
   `"brand name" -site:{domain} -site:{sister_domain_1} -site:{sister_domain_2}`
   *Example:* `"BuildingWorld" -site:buildingworld.ai -site:buildingworld.in`

### 📊 Statistical Audit Sample Size Math
To make audits highly accurate without crawling redundant pages, calculate the sample size ($n$) based on the indexed page count ($N$):

- **Very Small Catalog ($N < 100$):**
  - **Rule:** Audit 100% of pages ($n = N$).
- **Small Catalog ($N$ between 100 and 1,000):**
  - **Formula:** $n = 50 + 0.1 \times N$ pages.
  - *Example:* For $N = 500$, audit 100 pages.
- **Medium Catalog ($N$ between 1,000 and 50,000):**
  - **Formula:** $n = 100 + 0.01 \times N$ pages (capped at 200).
  - *Example:* For $N = 10,000$, audit 200 pages.
- **Enterprise / pSEO Catalog ($N > 50,000$):**
  - **Formula:** $n = 200 + 0.001 \times N$ pages (capped at 500).
  - *Example:* For $N = 100,000$, audit 300 pages.

### 🧬 Sample Page Distribution Rules
Once the total sample size ($n$) is calculated, distribute the checks across unique page templates:
- **Homepage:** Always check.
- **Listing & Detail Pages:** Sample at least **5 distinct URLs** for every structural template route (e.g., 5 L1 listing URLs, 5 product detail URLs).
- **Template Verification:** Confirm that findings (such as missing structured schema or hydration bugs) repeat consistently across the sampled URLs to rule out outlier configuration errors.

---

## 7. Report Formatting & Template Standardization

Every completed VDS/SEO audit must be compiled into both **Markdown** and **HTML** formats. To maintain a premium look and consistent ticketing structure, follow the templates configured in the plugin assets.

### 📝 Markdown Audit File (.md)
Standardized for developer tickets and task backlogs.
- **Header:** Include target URL, date, stack, and auditor metadata.
- **Body:** Document issues grouped by severity (Critical, High, Medium, Low, Info) pairing **broken code** side-by-side with **fixed code** examples.
- **Footer:** Append the mandatory VDS/SEO signature blocks as defined in the `references/signature.md` guide.

### 🎨 Interactive HTML Report (.html)
Standardized for client-facing dashboards.
- **TOC Sidebar & Progress Bar:** Include a sticky progress counter showing completed tasks (`X of Y addressed`).
- **Interactive Checklists:** Every finding card must have a tick-box that persists the resolved state to browser `localStorage`.
- **Developer Snippets:** Embed code blocks with copy-to-clipboard buttons and clear `How to verify` guidelines.
- **Brand Signature Band:** Ensure the footer renders the signature:
  `Crafted with care by [Girish](https://www.linkedin.com/in/girisshgk/) · Father of SEO · [For Collaboration](http://t.me/spcgbot)`

