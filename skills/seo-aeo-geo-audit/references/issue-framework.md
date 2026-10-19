# Issue Framework

Every finding MUST follow this structure. Engineers rely on consistency — skipping fields reduces the report to noise.

The framework has two equivalent input shapes:
- **Rich shape (preferred)** — matches the premium HTML report format: `finding_paragraphs` (HTML paragraphs for the "SEO Audit Finding" side) and `implementation_paragraphs` (HTML paragraphs for the "Revamp Implementation" side), each optionally followed by a code block.
- **Flat shape (legacy / quick)** — `summary`, `why_flagged`, `impact_seo/aeo/geo`, `benefits`, `broken_code`, `fixed_code`. The generator synthesises these into paragraphs automatically.

Prefer the rich shape for high-stakes audits and client-facing reports. Use the flat shape for quick internal audits where the writeup is terse.

## Why each field exists

- **Severity + Confidence + Pillars** — filtering and triage signals.
- **Confidence + evidence_source** — separates directly-observed findings from inferences. An engineer fixes a 95-confidence finding without debating it. A 50-confidence finding gets verified first.
- **Category (eyebrow)** — groups findings by audit section (e.g., "Rendering", "Structured Data", "Metadata").
- **Section title** — the headline of the finding, usually "Current state → Target state".
- **Section intro** — one-paragraph orientation below the title.
- **finding_paragraphs** — rich prose explaining what's wrong and why it matters. HTML with `<strong>`, `<em>`, `<code>` inline.
- **Broken code** — verbatim from the audit, displayed in an amber-framed dark block.
- **implementation_paragraphs** — rich prose explaining the fix and its benefits.
- **Fixed code** — copy-pasteable, displayed in a navy-framed dark block with a copy button.
- **Verify** — a concrete test the engineer runs to confirm the fix.

## The schema (JSON)

```json
{
  "id": "SEO-001",
  "severity": "critical | high | medium | low | info",
  "confidence": 95,
  "evidence_source": "curl -H 'User-Agent: GPTBot/1.0' <url> | grep -c '<h1>' → 0",
  "pillars": ["SEO", "AEO", "GEO"],

  "audit_group": "Traditional SEO | LLM Visibility",
  "category": "On-Page | Technical | Google AI Overview | Other LLM Models",

  "section_title": "206 KB of self.nextf.push1 pollution → 40 KB clean SSR",
  "section_intro": "One sentence orientation for the section.",
  "location": "app/jobs/[slug]/page.tsx",

  "page": "https://example.com/specific-page",
  "pages_affected": [
    "https://example.com/page-one",
    "https://example.com/page-two"
  ],

  "finding_paragraphs": [
    "<p>The live page has <strong>...</strong>.</p>",
    "<p>There was no way to rank separately for <em>...</em>.</p>"
  ],
  "broken_code": "// verbatim code...",
  "broken_language": "jsx",

  "implementation_paragraphs": [
    "<p>Rebuilt as <strong>...</strong>.</p>"
  ],
  "fixed_code": "// copy-pasteable code...",
  "fixed_language": "jsx",

  "verify": "curl -s <url> | wc -c → ≤ 40960"
}
```

## New fields (v0.4 schema)

Since v0.4 the finding schema supports three fields that change how the HTML report is organised:

### `audit_group`
Top-level report grouping. Two values:
- `"Traditional SEO"` — Googlebot / Bingbot / classic ranking signals.
- `"LLM Visibility"` — Google AI Overview + ChatGPT / Perplexity / Claude / Gemini / Copilot citations.

The generator renders a big gradient banner between groups. Findings are sorted by group → category → severity → id.

### `category` (new nuance)
Paired with `audit_group` to sub-group within:
- Under **Traditional SEO**: `"On-Page"`, `"Technical"`.
- Under **LLM Visibility**: `"Google AI Overview"`, `"Other LLM Models"`.

You can still use free-text categories (e.g., `"Rendering"`, `"Structured Data"`, `"Sitemap"`) — the generator falls back to alphabetical ordering when a category isn't in the known set. For the cleanest grouped output, use the canonical four.

### `page` vs `pages_affected`
Every finding should name the URL(s) it applies to. Use ONE of:
- **`page`** (string) — for a single-page finding.
- **`pages_affected`** (list of strings) — for site-wide or multi-page issues. Rendered as a chip grid under the finding's meta row.

Use `pages_affected` when the same root cause appears on multiple URLs (template-level issues). Use `page` when the issue is unique to one URL.

## Scores block (v0.5 addition)

On `/full-audit` mode or on explicit user request, findings JSON also carries a top-level `scores` object with two graders:

```json
{
  "scores": {
    "seo_quality": {
      "page_type": "Landing / Money Page" | "Blog / Article Page",
      "overall": 0..100,
      "grade": "Exceptional | Strong | Workable | Weak | Failing",
      "breakdown": [
        {"label": "LSI term coverage", "value": N, "max": N, "note": "..."},
        /* ... */
      ],
      "lsi_terms_present": [...], "lsi_terms_missing": [...],
      "entities_present": [...], "entities_missing": [...],
      "sentiment_distribution": {"confident": 0.xx, "neutral": 0.xx, ...},
      "top_improvements": [...]
    },
    "eeat": {
      "page_type": "Landing / Money Page" | "Blog / Article Page",
      "overall": 0..100,
      "grade": "...",
      "breakdown": [
        {
          "pillar": "Trust",
          "value": N, "max": N,
          "sub_signals": [
            {"label": "...", "value": N, "max": N, "status": "pass | partial | fail"}
          ]
        }
        /* Experience, Expertise, Authoritativeness */
      ],
      "top_improvements": [...]
    }
  }
}
```

The generator renders this as a dedicated scorecard section at the top of the HTML report — with visual progress bars per dimension, color-coded sub-signals (green/amber/red based on % of max), and a "Top improvements" list under each grader.

See `seo-quality-score-rubric.md` and `eeat-score-rubric.md` for the full scoring methodology.

## Interactive checklist in HTML reports

Each finding in the HTML report gets a "Mark as addressed" checkbox. State persists in `localStorage` keyed by report URL. A sticky progress bar at top tracks completion (`X of N addressed`). When all are addressed, a "Ready to re-run" panel appears at the bottom with suggested commands for the next audit pass.

Engineers can use this to:
- Track which findings they've already implemented.
- Hand the report to a colleague mid-way — state is saved in the recipient's browser.
- Visually confirm completeness before re-auditing.

Findings don't need any additional data for this to work — it's a pure UI layer on top of the existing schema.

## Confidence score — how to assign

Every finding carries a `confidence` (0–100) and `evidence_source` describing how it was verified.

| Confidence | When to use | Example evidence source |
|---|---|---|
| 95–100 | Directly observed in raw HTML / response headers / DOM. Deterministic. | `curl <url> \| grep -c '<h1>' → 0` |
| 80–94 | Observed via rendered browser; depends on page state. | `DevTools Network panel — 14 self.nextf.push1 scripts` |
| 60–79 | Inferred from pattern; likely true but needs live verification. | `Inferred from file structure in pasted code` |
| 40–59 | Theoretical risk; indicator seen but impact unconfirmed. | `Page weight 2.1 MB — CWV likely poor; no field data` |
| 0–39 | Low-certainty. Worth mentioning but needs investigation. | `Third-party script **might** block LCP` |

Always include `evidence_source` — "how I knew this was a problem" is what makes an audit credible. Even a flat-shape finding gets `evidence_source: "Inferred from pasted code — file not audited live"` rather than omitting.

## Field rules

### Severity
Use SKILL.md definitions. If torn between two levels, pick the lower one. Over-severity trains engineers to ignore reports.

### Pillars
Tag only the ones genuinely affected. Examples:
- Missing `<title>` → SEO, AEO, GEO
- Missing `FAQPage` schema → AEO mainly
- Missing `llms.txt` → GEO only
- Duplicate H1 → SEO; AEO secondary

### Category
A short label shown as the section eyebrow in the HTML. Examples: `Rendering`, `Structured Data`, `Metadata`, `Semantic HTML`, `Crawlers`, `URL Architecture`, `Performance`, `Internationalization`, `AI Readiness`.

### Section title
Phrased as "Current state → Target state" where possible. Drives the Playfair `<h2>` in the HTML.
- Good: "Zero JSON-LD → 53 schemas deployed"
- Good: "Generic title → page-specific keyword-rich titles"
- Weak: "Title tag issue"

### Section intro
One paragraph (< 2 sentences) below the title. Gives context before the before/after grid.

### finding_paragraphs / implementation_paragraphs
Array of HTML paragraph strings. Each element is a full `<p>...</p>` (or `<ul>...`, `<h4>...`, etc.).

Use:
- `<strong>` for ebeta-consulting on specific terms
- `<em>` for quoted user queries ("*near me*", "*fibre Whitefield*")
- `<code>` for file paths, tag names, property names
- `<ul><li>` for lists
- `<br><br>` to break paragraphs within a single string

Write these as client-facing copy. They show up verbatim in the HTML report.

### Location
Be specific. DOM path, file path with line number, or URL. "Site-wide" only for things like `robots.txt`.

### Evidence source
Specific. Helpful references: `curl` commands (with the output), `DevTools Network panel`, `GSC URL Inspection`, `Lighthouse report`, `Rich Results Test`, or `Inferred from <source>`.

### Broken code
Verbatim from what was observed or pasted. Don't clean it up. If the broken state is "nothing" (missing tag), show surrounding context with a comment:

```html
<head>
  <meta charset="utf-8">
  <!-- ❌ No canonical tag -->
  <title>...</title>
</head>
```

### Fixed code
Copy-pasteable with no edits. Use realistic placeholders with a comment indicating what to replace.

### Verify
Concrete action:
- `curl -I https://example.com/page` + expected output
- `Paste fixed JSON-LD into https://search.google.com/test/rich-results`
- `Reload; confirm document.title matches the new title in DevTools`
- `Re-run this audit; this check should now be pass`

### Language tags for code blocks
The generator supports these for syntax highlighting: `html`, `xml`, `svg`, `json`, `jsx`, `tsx`, `js`, `ts`, `css`, `bash`. Unknown languages render as escaped plain text.

## Writing style for the "before" side (finding_paragraphs)

1. Open with the specific observed problem, using hard numbers where possible.
2. Explain why it matters — with a standards reference (Google docs, schema.org, web.dev) or a production impact.
3. Optionally: root cause.

## Writing style for the "after" side (implementation_paragraphs)

1. Open with what was done (or should be done) — the concrete change.
2. Call out the knock-on benefits in one or two sentences.
3. Keep it shorter than the "before" side. The code block carries the weight.

## Severity quick-ref

- **Critical** — Page effectively invisible/broken (noindex shipped, robots blanket-blocking, 5xx, missing `<title>`, server content hidden from bots).
- **High** — Significant SEO/AEO/GEO value lost (missing canonical, missing H1, no schema on eligible page, CWV well below thresholds).
- **Medium** — Measurable but recoverable (thin meta, missing OG, inconsistent heading hierarchy, no author schema).
- **Low** — Polish (title slightly long, minor alt-text gaps, missing favicon variants).
- **Info** — Not a defect but worth documenting.

## Audit data the generator also accepts (optional)

On the audit object:
- `project_label` — appears in topbar, title, footer. Default "Audit — <MODE>".
- `stack_label` — e.g. "Next.js App Router + Pages Router + CSR". Shown in meta grid.
- `prepared_by` — e.g. "Kumar — AdsPilot". Shown in meta grid.

On the summary object:
- `scorecard` — array of `{label, value_from, value_to, hint}` objects. If omitted, the generator falls back to a counts-based scorecard.

At the top level:
- `overview` — free HTML for the overview callout box. Use `<strong>`, `<em>`, `<br>`.
- `additional_notes` — free HTML for a final callout (amber warning box).
