---
name: technical-seo-audit
description: Dedicated technical SEO audit for any website or codebase. Checks crawl and indexation controls, status codes and redirects, sitemaps, canonicals, document head, structured-data validity, JavaScript rendering (raw vs rendered HTML, Next.js App and Pages Router), performance (optional PageSpeed Insights), security hygiene, stack detection (React, Next.js, Laravel, WordPress, Shopify and more) and tracking-tag coverage across pages (GTM, GA4, Meta, Ads, UET). Samples pages from the sitemap with a probe script, marks anything untested as not measured, and outputs a ticket-ready Markdown and HTML report. Use for technical SEO audits, pre-launch checks, JavaScript SEO, Next.js SEO, indexation problems and tracking-tag checks. Not for content, E-E-A-T, AEO or GEO.
license: MIT-Commons-Clause (see LICENSE; no resale without a commercial license)
compatibility: Works in any Agent Skills host (Claude, Claude Code, Codex/ChatGPT, Antigravity). Needs web or browser access for live checks and Python 3.8+ for the probe script. Bundles its own PageSpeed runner and browser-access fallback; the sibling seo-aeo-geo-audit skill adds stack profiles and the report generator when installed.
metadata:
  author: Girish Kumar G
  version: "2.6.0"
  homepage: https://seobiopse.com
---

# Technical SEO audit

Engineering-only scope: what can be fixed in code, config or infrastructure so that search engines can crawl, render, index and measure the site. For content quality, E-E-A-T, AEO, GEO, AI citation or VDS, use the `seo-aeo-geo-audit` skill instead.

## Rules that apply to every step

1. **Evidence or `not measured`.** Every checklist item ends as `pass`, `warn`, `fail` or `not measured`. Never guess a result, a score or a Core Web Vitals number.
2. **Say where each fact came from:** raw HTML (server response), rendered DOM (browser), headers, or inferred from pasted code. The probe reads raw HTML only.
3. **Sample, and say so.** Coverage statements (tags on all pages, canonicals on all pages) apply to the sampled pages. State the sample size and templates covered.
4. **Only audit what the user is authorised to test.** One request per page, small sample, no crawling beyond the target host.
5. **Credentials stay out of files.** See the PageSpeed step.
6. **Calibrate claims about Google.** Limits, retired features and thresholds were checked against Google Search Central on 2026-11-03. When the sibling skill is installed, read `../seo-aeo-geo-audit/references/google-guidance-alignment.md` before attributing anything to Google. Features Google no longer shows (FAQ and HowTo rich results, sitelinks search box) and optional files Google does not use (`llms.txt`) are `Info`, never defects. Google says heading order and count do not affect Search, so heading findings are `Low`.
7. **Ask before you skip.** The PageSpeed question in Step 1 is mandatory for any live public URL. Never decide to skip PageSpeed yourself and never tell the user it is "not available". This skill bundles the runner. The only valid reasons to skip are the user saying "skip" or a target that is not publicly reachable.
8. **Live-site access.** If the built-in browser or fetch tool cannot reach the site, follow `references/browser-access.md`: say what failed, use Claude in Chrome, and if the extension is missing give the user the install steps and wait.

## Inputs

- **A live URL** (production, staging, localhost): use the probe plus a browser for rendered checks.
- **A code snippet or repo:** analyse directly, apply the same checklist, mark live-only items `not measured`.

## Workflow

### Step 1: Scope and PageSpeed key (blocking)
In your FIRST message, get the target and ask for the PageSpeed key together, then wait for the answer before Step 2:

> Which URL (or pasted code) should I audit? Also, want a PageSpeed Insights test (Lighthouse scores + real-user Core Web Vitals)? Paste a PageSpeed API key, or say "skip".

Ask the single/whole-site question only if it is unclear. Note the environment (production, staging, localhost, preview). Skip the key question only if the user already gave a key or said "skip", or the target is not publicly reachable. Details and the key-safety rules are in `references/pagespeed.md`.

### Step 2: Probe (live sites)
Run:

```bash
python3 scripts/tech_probe.py --url <target> --sample 15 --output probe.json
```

Use `--urls-file` to add templates the sitemap omits (checkout, thank-you, 404). The probe returns framework signals, per-page raw-HTML facts, robots.txt and sitemap sanity, tracking coverage, and rule-based `hints` that cite checklist ids. Treat `hints` as leads: confirm each with `curl` or a browser before it becomes a finding. If the probe cannot run (no Python, blocked), do the same checks by hand with `curl` and the browser tools. If the target is blocked or unreachable (403, bot challenge, empty page, tool error), do not conclude anything yet: follow `references/browser-access.md` (use Claude in Chrome, or give the install steps if the extension is missing).

### Step 3: Stack and architecture (TECH-07)
Name the stack from the probe's `frameworks_seen` and headers, with evidence and confidence. Never infer a stack from URL shapes alone. If the sibling skill is installed, read the matching profile from `../seo-aeo-geo-audit/references/` (React/Next.js, WordPress, Shopify, static, Angular, PHP/Laravel, Wix/Webflow) and add its stack-specific checks.

### Step 4: JavaScript and rendering (TECH-08)
Read `references/javascript-rendering.md`. Compare raw HTML (probe/`curl`, also with a Googlebot user agent) against the rendered DOM (browser tool) and list every difference. For Next.js, identify the router type and apply the App/Pages Router checks. If the repo is available, grep for the listed anti-patterns.

### Step 5: Tracking tags (TECH-11)
Read `references/tracking-tags.md`. Use the probe's `tracking_coverage` for tags present in raw HTML, then verify in the browser (Network panel, console snippets, route changes, consent) because tag managers inject tags the probe cannot see.

### Step 6: Performance with PageSpeed (TECH-09)
Use the answer from Step 1. Do not ask again, and do not skip on your own.

- Key given: run `scripts/pagespeed.py` (bundled in this skill; commands and fallbacks in `references/pagespeed.md`). Handle the key as a session-only credential: never write it to a file, report, memory or git, pass it by stdin or an environment variable scoped to the command, and at the end ask the user whether to discard it. If Python cannot run, use the `curl` fallback in `references/pagespeed.md`.
- User said "skip" (or the target is not publicly reachable): mark TECH-09.1 `not measured` and say why in the report. Do not substitute remembered numbers.
- If the question was never asked, ask it now before Step 7.

### Step 7: Work the checklist
Read `references/technical-checklist.md`. Go through TECH-01 to TECH-13 in order, deciding pass / warn / fail / not measured for each item, citing the evidence. Skip TECH-12 if the site is single-language. Skip items that do not apply to the stack and say which.

### Step 8: Write findings
Each `warn` or `fail` becomes a finding with: severity, confidence (95+ for `curl`-verified, 80-94 for rendered-DOM, lower for inference), evidence source, location, current state, fix, broken code and fixed code where you saw the code (otherwise write "needs input"), and a concrete verification command. If the sibling skill is installed, follow its `../seo-aeo-geo-audit/references/issue-framework.md` exactly. Otherwise use the fallback structure below.

Severity:
- **Critical:** the site or key pages cannot be crawled or indexed (blanket `Disallow`, `noindex` shipped on money pages, 5xx, empty JS shell with no server content).
- **High:** large loss of crawl/index/measurement value (missing canonicals, soft 404s, primary analytics tag missing on a template, private URLs in the sitemap).
- **Medium:** measurable but recoverable (redirect chains, uniform `lastmod`, duplicate tag firing, TTFB).
- **Low:** polish (missing HSTS, `lang`, multiple H1).
- **Info:** worth recording (`changefreq`/`priority`, AI-crawler policy, disclosed headers).
When unsure between two levels pick the lower one.

### Step 9: Generate the report
Preferred, when the sibling skill is installed:

```bash
python3 ../seo-aeo-geo-audit/scripts/generate_report.py --input findings.json --output-dir <dir>
```

Set `"audit": {"mode": "technical", ...}` in `findings.json`. Put `scores.pagespeed` in it if PageSpeed was run (from `pagespeed.py`'s `scores_block`). Put the tracking coverage table and the raw-versus-rendered table in the finding text. Put the stack, environment, sample size and the list of `not measured` items in `overview`.

Fallback without the generator: write `technical-seo-audit-<date>.md` with these sections: Summary (target, date, environment, stack with evidence, sample size), Findings by severity (table), Findings (each with the fields above), Tracking coverage table, Checklist results (all TECH items with pass/warn/fail/not measured), Not measured and why, Next steps.

### Step 10: Summarise for the user
3 to 6 sentences: what was audited and how many pages were sampled, findings by severity, the top three issues by name, what was `not measured`, and where the reports are.

## Things not to do

- Do not invent findings outside the checklist. Real extra issues go in as "additional finding".
- Do not report a probe `hint` as fact without confirming it.
- Do not claim a tag is missing when a tag manager is present and you have only seen raw HTML.
- Do not give traffic or ranking predictions as numbers.
- Do not run the probe against hosts the user did not name.

## Files

- `references/technical-checklist.md`: the TECH-01 to TECH-13 checklist (read every time)
- `references/javascript-rendering.md`: raw versus rendered method, framework anti-patterns, Next.js App/Pages Router checks
- `references/tracking-tags.md`: tag coverage method, browser verification, how to judge results
- `scripts/tech_probe.py`: sampled raw-HTML probe (stdlib only)
- `scripts/pagespeed.py` and `references/pagespeed.md`: PageSpeed Insights runner and key handling (identical copies ship in `seo-aeo-geo-audit`)
- `references/browser-access.md`: what to do when the site cannot be reached (Claude in Chrome fallback and install steps)
- Sibling skill `seo-aeo-geo-audit` (optional): `references/google-guidance-alignment.md`, stack profiles, `references/issue-framework.md`, `scripts/generate_report.py`, `tracking-validation.md`
