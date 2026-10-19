# SEO Audit Plugin — Engineering Handoff Guide

**Version:** 1.9.1
**Maintainer:** [Girish Kumar G](https://in.linkedin.com/in/girisshgk) — Father of SEO
**For questions:** DM on LinkedIn, or ping in the team Slack / Linear channel for SEO work.

---

## Welcome to the team

If you're reading this, someone on the team has handed you this plugin and said "run an audit before you ship." This doc gets you from zero to a useful audit in under 30 minutes.

The plugin is a **Claude Code plugin** — a bundle of instructions that teaches Claude how to audit SEO, AEO (Answer Engine Optimization), and GEO (Generative Engine Optimization) on any web page or site. You don't run the audit yourself. You tell Claude what to audit, and it produces two reports: a Markdown one for your ticket system, and an interactive HTML one for your browser.

## TL;DR — 3-minute version

1. **Install** the plugin in Claude Code: `/plugin install <path-to-plugin-folder>`.
2. **Run** `/seo-audit` in Claude Code.
3. **Answer** Claude's clarifying questions (what URL, what stack, what environment).
4. **Get** two files: `seo-audit-<mode>-<date>.html` and `.md` in your project folder.
5. **Open** the HTML in your browser. Work through findings. Check off each one as you fix it. The "Ready to re-run" panel appears when you're done.

---

## What's in the plugin

### Eight slash commands
| Command | Use when you want to… |
|---|---|
| `/seo-audit` | Full technical SEO audit (~80 checks): crawl, index, render, meta, schema, performance. |
| `/aeo-audit` | Check if a page is ready to appear in Google AI Overviews + featured snippets. |
| `/geo-audit` | Check if a page is citable by ChatGPT, Perplexity, Claude, Gemini, Copilot. |
| `/ai-citation-audit` | Measure the three numbers that decide AI citation — chunk density, chunk relevance, extractable units — plus Bing indexation. |
| `/agentic-browsing-audit` | Check if autonomous AI browser agents can crawl, render, navigate, and act on the page (SXO / AXO). |
| `/vds-audit` | Map crawl presence to conversion, trust, and scalability targets (Visibility-to-Demand System). |
| `/full-audit` | All pillars in one pass. Use before shipping to production. |
| `/crawl-check` | Fast 14-check rendering-only audit. Use during active dev for quick sanity checks. |

### Thirty-Seven reference files
These are the "brain" of the plugin. Claude reads them as it runs the audit. They're in `skills/seo-audit/references/`:

- **Core checklists** — `issue-framework.md`, `seo-audit.md`, `aeo.md`, `geo.md`, `ai-citation-audit.md`, `vds-audit.md`
- **Stack profiles** — `react-nextjs-architecture-profile.md`, `wordpress-architecture-profile.md`, `shopify-architecture-profile.md`, `static-html-architecture-profile.md`, `angular-architecture-profile.md`, `php-architecture-profile.md`, `wix-webflow-architecture-profile.md`
- **Technical playbooks** — `crawlability-react.md`, `structured-data-advanced.md`, `robots-llms-txt-playbook.md`, `sitemap-playbook.md`
- **Content safety & Optimization** — `ai-content-safety.md`, `image-optimization.md`, `product-experience-audit.md`, `agentic-browsing.md`
- **Programmatic & Commercial** — `pseo-playbook.md`, `transaction-intent-playbook.md`, `aeo-transaction.md`, `geo-transaction.md`
- **AI Overview & RAG** — `ai-overview-playbook.md`, `llm-citation-playbook.md`, `ai-citation-audit.md`, `query-fanout.md`, `rag-optimization.md`, `rag-to-memory.md`
- **Tools, QA & Tracking** — `tools-to-use.md`, `quality-assurance.md`, `signature.md`, `tracking-validation.md`

You don't need to read them upfront. Claude loads the relevant ones when running your audit.

### One Python script
`skills/seo-audit/scripts/generate_report.py` — takes a findings JSON and produces the Markdown + HTML reports. Claude runs this automatically at the end of an audit.

---

## Installing the plugin

### Option A — install from local folder (fastest)

```
/plugin install <absolute-path-to-seo-audit-plugin-folder>
```

### Option B — install from marketplace (for team-wide distribution)

If your team has committed the plugin to a marketplace repo:

```
/plugin marketplace add seobiopse/advanced-seo-plugin-for-claude-code
/plugin install seo-audit@seo-audit-marketplace
```

### Verify it's installed

In a Claude Code session, type `/` and start typing `seo`. You should see the 8 slash commands autocomplete. If not, restart Claude Code and try again.

---

## Your first audit — step by step

### 1. Decide what to audit

The plugin can audit either:
- **A live URL** — production, staging, localhost, PR preview. Claude fetches the page and inspects it.
- **Pasted code** — a single component file, HTML blob, or template. Useful if the page isn't reachable.

Pick a representative page from your app. For a first audit, start with your homepage or a highest-traffic landing page.

### 1a. Know that the plugin tailors itself to your domain

Before doing any check, the plugin detects your site's **archetype** — is this a blog? A staffing site? A SaaS product? An e-commerce store? A bootcamp? A documentation site? — and loads ONLY the reference files that apply.

This matters because auditing a blog with job-board rules produces garbage. Auditing a staffing site without job-board rules misses the most important schema. The plugin uses URL patterns, existing schema types, homepage content, and nav structure to figure out what your site actually IS before checking anything.

**If the archetype detection is wrong, the plugin will tell you explicitly** — the audit's overview line includes "Detected archetype: [X]" and a list of "Explicitly NOT audited (wrong archetype)" items. If either is wrong, tell Claude to re-run with the correct archetype.

See `references/domain-discovery.md` for the full archetype list and the per-archetype audit scope.

### 2. Run the command

```
/full-audit https://your-domain.com/
```

(You can type `/full-audit` alone and Claude will ask for the URL.)

### 3. Answer clarifying questions

Claude will ask things like:
- What's your stack? (React + Next.js App Router / Pages Router / Remix / plain HTML / etc.)
- What environment? (localhost / staging / production)
- Which content type? (blog / product / landing / jobs / courses / events)

Answer honestly — these determine which deep-dive references Claude loads.

### 4. Wait for the audit

Full audits take 5–15 minutes depending on page complexity. Claude will:
- Fetch the page (as Googlebot UA, GPTBot UA, ClaudeBot UA)
- Compare raw HTML vs rendered DOM
- Parse JSON-LD schema
- Check robots.txt, sitemap.xml, llms.txt
- Cross-reference against the 230-item checklist
- Write findings into a JSON structure
- Run the generator to produce the two report files

### 5. Open the HTML report

The HTML report is designed to be self-contained. Just open it in Chrome / Firefox / Safari. You'll see:

**Top:** Audit metadata — target URL, date, stack, mode.

**Scorecard:** 3 headline numbers (total findings, critical issues, site score).

**Progress bar (sticky):** Shows "X of N addressed" as you check things off.

**TOC bar:** Jump to any section by name.

**Overview box:** A human-readable summary of what the audit found.

**Two banners:** "Traditional SEO" (Googlebot / Bingbot) and "LLM Visibility" (Google AI Overview, ChatGPT, Perplexity, Claude, Gemini, Copilot). Every finding sits under one of these.

**Findings:** Each one is a card with:
- **Severity badge** — Critical / High / Medium / Low / Info
- **Confidence score** — 0–100, with evidence source (how the audit knew)
- **Channels** — SEO / AEO / GEO chips
- **Category + page** — which page the finding applies to
- **"SEO Audit Finding"** (amber) — what's wrong + why it matters
- **"Revamp Implementation"** (navy) — the fix, with copy-pasteable code
- **How to verify** — the concrete test to confirm the fix worked
- **"Mark as addressed" checkbox** — check it when you ship the fix

**Re-run panel (appears when all checkboxes are ticked):** Suggests the commands to re-run the audit.

**Signature band:** A credit to the plugin author.

---

## Understanding the fields

### Severity

Five levels, picked pragmatically:

| Severity | Meaning |
|---|---|
| **Critical** | Page is effectively invisible or broken (noindex shipped, robots blocking, 5xx, missing `<title>`). Blocker. |
| **High** | Significant SEO/AEO/GEO value lost (missing canonical, missing H1, no schema on eligible page). Fix this sprint. |
| **Medium** | Measurable but recoverable (thin meta, missing OpenGraph, inconsistent heading hierarchy). Fix within 2–3 sprints. |
| **Low** | Polish (title slightly long, minor alt-text gaps). Batch together and fix when convenient. |
| **Info** | Not a defect but worth documenting. |

### Confidence score (0–100)

Every finding has a confidence score. It tells you how certain the audit is that the issue is real:

| Confidence | Meaning | Example |
|---|---|---|
| **95–100** | Directly observed in raw HTML / response headers. Deterministic. | "grep -c '&lt;h1&gt;' on the page returned 0." |
| **80–94** | Observed via rendered browser; depends on page state. | "DevTools Network panel shows 14 duplicate script loads." |
| **60–79** | Inferred from pattern; likely true but needs live verification. | "Page size 2.1 MB suggests CWV likely poor." |
| **40–59** | Theoretical risk; indicator seen but impact unconfirmed. | "Third-party script might block LCP." |
| **0–39** | Low-certainty. Worth mentioning but needs investigation. | "Inferred from file structure." |

Treat 95+ findings as settled facts. For lower-confidence findings, verify the underlying observation before investing fix time.

### Audit groups

- **Traditional SEO** — crawling, indexing, ranking in Google/Bing. What classic SEO has cared about for 20 years.
- **LLM Visibility** — being cited by AI answer engines. A newer discipline; overlaps with Traditional SEO but has its own specific signals.

### Categories within each group

- Traditional SEO → **On-Page** (HTML, schema, metadata) or **Technical** (robots, sitemap, server config).
- LLM Visibility → **Google AI Overview** (Gemini-powered SERP answers) or **Other LLM Models** (ChatGPT / Perplexity / Claude / Copilot).

### Pillars (SEO / AEO / GEO)

Each finding is tagged with the pillars it affects:
- **SEO** — traditional search
- **AEO** — answer engines (extracted answers in AIO, featured snippets, voice)
- **GEO** — generative engines (being cited in ChatGPT / Perplexity / Claude answers)

A finding can affect one, two, or all three. The report shows this as chips on each finding card.

---

## Using the interactive checklist

When you open the HTML report, every finding has a "Mark as addressed" checkbox in the top-right corner.

**As you ship fixes:**
1. Deploy the fix.
2. Open the HTML report.
3. Find the matching finding.
4. Read the "How to verify the fix" line at the bottom.
5. Run that verification.
6. If it passes, click the checkbox. The card dims. The progress bar at the top updates.

**State persistence:**
- Your check state is saved in your browser's localStorage, keyed by the report's URL.
- Share the report file → each teammate has their own state (in their browser).
- Clear browser data → state is reset.
- There's also a "Reset" button on the progress bar + the re-run panel.

**Re-run panel:**
When you check off the last box, a green "All findings addressed 🎉" panel appears at the bottom with suggested commands to re-run the audit. Copy the command, paste it in Claude Code, get a new report, compare.

---

## Re-running after fixes

Re-run the same command you used originally:

```
/full-audit https://your-domain.com/
```

Compare the new report to the old one. Findings you marked as addressed should now show as "pass" (they won't appear in the new report at all). Anything still in the new report either wasn't actually fixed, or the verification step didn't catch it.

**Pro tip:** Re-run after every major deploy. Three audits over a sprint gives you a time-series — you can see your SEO posture improving instead of stagnating.

---

## When things go wrong

### "Claude doesn't recognise /seo-audit"
The plugin isn't installed. Re-run `/plugin install`.

### "The report is empty"
Claude couldn't reach the URL. Common causes:
- Localhost firewall blocking outbound curl
- Staging behind HTTP basic auth
- CORS / WAF blocking crawlers
- The URL returned a 404 / 500

Try a different URL. Or paste code directly.

### "The audit flagged something I know is fine"
Confidence scores help here. If it's a 60-confidence finding, the audit is inferring. Check the evidence source on the finding card — if the observation is wrong, you can ignore the finding. If it's a 95+ confidence finding and you disagree, ping me on LinkedIn and I'll update the reference checklist so future audits get it right.

### "The 'Mark as addressed' state disappeared"
Likely cleared your browser's localStorage. There's no cloud sync — state is per-browser-per-report. Use the HTML + Markdown reports together: track ticket status in your project management tool, not in the HTML checklist.

### "I fixed a finding but the re-run still shows it"
Two common causes:
1. The fix didn't deploy to the URL you audited. Check your deploy.
2. The cache (your CDN, Cloudflare, Next.js ISR) is still serving the old version. Purge the cache before re-auditing.

### "My team wants to add a new check"
**Stop — do not edit the reference files directly.** Extensions go through a governance process, not a direct edit. See "Requesting a new check" in the Extensions section below. Unsanctioned changes to the reference files, severity definitions, or output format compromise the quality bar the whole team depends on.

---

## Common questions

### "This is a lot of findings. Where do I start?"
1. Read the report's "Overview" box first — it names the top blockers.
2. Fix all Critical findings. Every one of them is blocking indexation or citation.
3. Then fix High findings, prioritised by confidence score.
4. Medium findings — batch together for a cleanup sprint.
5. Low / Info — polish when convenient.

Don't try to fix everything at once. One week of focused work on Critical + High usually captures 80% of the value.

### "Can I run this on a staging URL?"
Yes. The plugin works on any reachable URL. Just make sure:
- Staging isn't behind HTTP basic auth (or provide the auth to Claude).
- Staging's `robots.txt` isn't blocking the audit UA.
- Staging's WAF / rate limiter isn't treating the audit as an attack.

### "Can I run this against a competitor's site?"
Yes, for intelligence purposes. The plugin just reads public HTML. Don't use this for anything manipulative — scraping public sites to understand the landscape is fine; trying to find vulnerabilities or sensitive data isn't what the plugin is for.

### "How do I know the plugin itself is up to date?"
Check the version in `plugin.json`. The maintainer (me) updates the references as new AI bots emerge, as Google changes guidance, etc. Pull the latest from the marketplace / repo every 2–3 months.

### "I don't use Claude Code. Can I still use this?"
Not directly — the plugin is built for Claude Code. But you can read the reference files in `skills/seo-audit/references/` manually and use them as a checklist. That loses the automation but preserves the methodology.

### "Who owns this? Where do bugs / feature requests go?"
Me: [Girish Kumar G](https://in.linkedin.com/in/girisshgk). DM me on LinkedIn, or ping the team Slack / Linear channel. I actively maintain the plugin; bug reports and suggestions are welcome and usually land in the next update.

---

## Extensions and changes — governance

**Read this before you try to change anything in the plugin.**

The plugin is a shared source of truth. Every audit the engineering team runs \u2014 for ourselves, for our clients, for internal stakeholders \u2014 relies on the reference files, the severity calibration, and the report format being consistent. Unreviewed changes compromise that consistency.

**Engineers must not edit the plugin directly.** No reference-file edits. No new slash commands. No generator changes. No severity adjustments. Not even \"small fixes\" \u2014 small fixes compound into incoherent standards within 3 months.

Every change goes through the process below.

### The approval chain

```
Engineer or team member \u2192 fills out Request Template \u2192
  \u2193
Marketing Team Director / AVP / Manager (review + decision) \u2192
  \u2193
Plugin maintainer (Girish Kumar G) (implementation + PR + version bump) \u2192
  \u2193
Team (pulls latest plugin, notified in changelog)
```

Three roles, three responsibilities:

1. **Engineer** \u2014 identifies the gap, documents it thoroughly, waits for approval. Does NOT commit changes.
2. **Marketing Director / AVP / Manager** \u2014 judges whether the proposal belongs in the plugin, whether severity / confidence calibration is right, whether it duplicates existing coverage, whether it's stack-relevant.
3. **Plugin maintainer (Girish Kumar G)** \u2014 implements approved changes, bumps version, updates changelog, notifies team. Sole commit access.

### Requesting a new check

1. Copy `NEW-CHECK-REQUEST-TEMPLATE.md` (in this plugin folder) into a new doc for your proposal.
2. Fill out every field \u2014 skipping fields is a signal you haven't thought through the gap.
3. Submit to the Marketing Director / AVP / Manager via the team's standard review channel (Linear ticket in the SEO queue, Confluence page, email \u2014 whichever the team uses).
4. Wait for one of four outcomes:
   - **Approved as-is** \u2192 routed to Girish for implementation.
   - **Approved with modifications** \u2192 you revise and resubmit.
   - **Deferred** \u2192 parked for quarterly review.
   - **Rejected** \u2192 you get a written reason. Read it. Future requests get stronger because you understand what bar wasn't met.
5. If approved, DO NOT merge changes yourself. Girish implements, bumps the version, and notifies the team.

### What gets fast-tracked vs reviewed

**Fast-tracked** (< 48-hour turnaround by Director + Girish):
- New AI bot appears and needs robots.txt handling
- Google publishes updated schema requirement that invalidates existing guidance
- Bug in an existing check (false positive / false negative with clear evidence)

**Standard review** (quarterly batch):
- New check on existing territory
- New category inside an existing audit group
- Severity recalibration of existing checks
- New reference file

**Director-level decision** (rarer):
- New slash command
- New audit group
- Major generator rewrite
- Change to the issue framework schema
- Change to the report visual design

### What about typos and small content edits?

If you notice a typo in a reference file, a broken link, or an obvious factual error \u2014 flag it the same way (via the Request Template, shorter form). Don't fix it yourself. The discipline of routing every change through the same process protects the bar.

### The reasoning

This governance exists for three reasons:

1. **Consistency.** Engineers fixing checks in different directions fragment the standard. A junior engineer's interpretation of \"High severity\" differs from a senior engineer's. Having one voice (the maintainer, with Marketing oversight) keeps calibration sharp.
2. **Quality control.** Not every good idea for a check actually belongs. Some are too narrow, some overlap with existing coverage, some use wrong severity. Marketing leadership catches these before they ship.
3. **Trust in the output.** When the marketing team hands an audit to a client or an exec, they need to be able to say \"the plugin produced this \u2014 it's reliable.\" If engineers can change the plugin on a whim, that trust erodes.

### If you disagree with the process

Fine. Raise it with the Marketing Director / AVP / Manager. If the team collectively decides to loosen governance, great \u2014 but until then, the process is the process. Don't try to route around it by editing files directly.

### Maintainer contact

[Girish Kumar G](https://in.linkedin.com/in/girisshgk) on LinkedIn. For anything urgent (broken audit, flag a regression), ping directly. For new-check requests, always go through the Director / AVP / Manager first.

---

## The philosophy

This plugin exists because SEO audits are mostly the same work done badly, over and over, by every engineering team. The plugin:

1. Codifies a high-quality checklist so no engineer has to reinvent it.
2. Produces a report that's client-ready without polish.
3. Uses confidence scores + evidence sources so findings can't be dismissed as "Claude hallucinated this."
4. Segments Traditional SEO from LLM Visibility so you can see both concerns independently.
5. Includes an interactive checklist so ownership of the fix is visible.

**Zero errors is the core value.** Every finding has evidence. Every severity rating is calibrated. Every fix has a verification step. If you find a place where the plugin is wrong or imprecise, that's a bug — ping me.

---

## Version history

- **v1.9.0 (2026-09-09)** — AI Citation Audit. New `ai-citation-audit.md` reference + `/ai-citation-audit` command (chunk density, chunk relevance via n-gram overlap + embedding similarity, extractable units per chunk, Bing indexation, content-refresh playbook). Folded into `/full-audit`. Marketplace manifest moved to `.claude-plugin/marketplace.json`.
- **v1.8.0 (2026-06-15)** — Quality Assurance & Data Integrity Guide. Added `quality-assurance.md` reference checklist for sub-agents to fact-check audit data and verify output layout formatting.
- **v1.7.0 (2026-06-15)** — Audit Integration Guide. Added `tools-to-use.md` reference mapping Playwright browser automation setup, MCP integration connectors (Ahrefs, Semrush, Screaming Frog), and public SEO site analytics scraping protocols.
- **v1.6.0 (2026-06-15)** — VDS Audit Integration. Added VDS (Visibility-to-Demand System) audit checklists, command hooks, examples, and updated audit templates with Telegram collaboration CTA.
- **v1.5.0 (2026-06-15)** — Agentic Browsing Readiness (SXO / AXO). Added dedicated reference profile `agentic-browsing.md` mapping WCAG standards to autonomous AI browser navigation.
- **v1.4.0 (2026-05-19)** — Universal stack coverage. Added WordPress, Shopify, Static HTML, Angular, PHP, and Wix/Webflow profiles.
- **v1.3.0 (2026-04-19)** — Universal pivot for public release. Sanitized profiles to use generic subdomains.
- **v1.2.0 (2026-04-19)** — Step 0 domain discovery added. Archetype detection and tailored scope scoping.
- **v1.1.0 (2026-04-19)** — SEO Quality Score + E-E-A-T Score models added.
- **v1.0.0 (2026-04-19)** — First production-ready release.

---

*Crafted with care by [Girish](https://www.linkedin.com/in/girisshgk/) · Father of SEO · [For Collaboration](http://t.me/spcgbot)*
