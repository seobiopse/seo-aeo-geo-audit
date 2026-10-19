# LLM Citation Playbook (ChatGPT, Perplexity, Claude, Gemini, Copilot)

Optimization for non-Google generative AI citations. Distinct from Google AI Overview (see `ai-overview-playbook.md`) because the mechanics are different — these engines don't inherit Google's index.

Read whenever the audit target wants to appear in ChatGPT browse answers, Perplexity results, Claude web search citations, Gemini responses, or Microsoft Copilot's Bing-backed results.

## How each engine cites differently

### ChatGPT (with browse / search enabled)
- Retrieval via OpenAI's own index (built by `OAI-SearchBot` + licensed partnerships).
- On-demand web fetches via `ChatGPT-User` when answering a user.
- Training data cutoff — earlier crawl by `GPTBot`.
- Citations shown as inline links.

### Perplexity
- Always-retrieval model. No answer is generated without fresh search + citation.
- Heavy use of its own `PerplexityBot` + licensed indexes.
- Citations shown as numbered superscript links — extremely prominent.
- Ranks citations by perceived authority.

### Claude (Anthropic)
- Training via `anthropic-ai` / `ClaudeBot` crawlers.
- Web search (via `Claude-SearchBot` / `Claude-Web`) when user invokes it.
- Citations given when fetched; general knowledge from training doesn't cite.

### Gemini (Google)
- Different from Google AI Overview (which lives in Search).
- Trained on content `Google-Extended` was allowed to access.
- Live web access for grounded responses.
- Citations via link chips.

### Microsoft Copilot
- Powered by Bing's index.
- Uses Bingbot's crawl + Microsoft's retrieval layer.
- Citations inline with Bing source cards.

## Table of contents

1. [Training-citation vs retrieval-citation](#1-training-vs-retrieval)
2. [Per-engine crawler access](#2-per-engine-crawler-access)
3. [What gets cited — universal signals](#3-universal-signals)
4. [Engine-specific tuning](#4-engine-specific-tuning)
5. [Content patterns LLMs cite](#5-content-patterns-llms-cite)
6. [Entity presence — the multiplier](#6-entity-presence)
7. [Measurement: monitoring LLM citations](#7-measurement)
8. [Audit checklist](#8-audit-checklist)

---

## 1. Training-citation vs retrieval-citation

Two fundamentally different paths to being cited by an LLM:

### Training-based citation
The LLM learned about you during training. It cites you from memory (sometimes with hallucinated URLs). Slow feedback loop — your content written today affects citations 6–18 months from now.

- Controlled by `GPTBot`, `Google-Extended`, `anthropic-ai`, `CCBot`, `Bytespider`, `Meta-ExternalAgent`.
- Benefits from: broad content volume, brand mentions across the web, Wikipedia / Wikidata presence.

### Retrieval-based citation (RAG)
The LLM fetches content LIVE when answering a user's query. Fast feedback loop — content added today can be cited today.

- Controlled by `ChatGPT-User`, `OAI-SearchBot`, `Perplexity-User`, `PerplexityBot`, `Claude-SearchBot`, `Bingbot`.
- Benefits from: authoritative domain, strong E-E-A-T signals, content freshness, direct match to the query.

### Strategy
- **For fast visibility** → allow retrieval crawlers, write content that directly answers common LLM queries, maintain freshness.
- **For compounding visibility** → also allow training crawlers, publish volume + build brand mentions, claim Wikipedia / Wikidata entries.

## 2. Per-engine crawler access

Reference table — cross-check your `robots.txt` against it:

| Bot | Engine | Type | Allow for GEO? |
|---|---|---|---|
| `ChatGPT-User` | ChatGPT | Retrieval | YES |
| `OAI-SearchBot` | ChatGPT search | Retrieval | YES |
| `GPTBot` | ChatGPT | Training | Business call |
| `PerplexityBot` | Perplexity | Retrieval | YES |
| `Perplexity-User` | Perplexity | Retrieval | YES |
| `ClaudeBot` | Claude | Both | YES |
| `Claude-SearchBot` | Claude search | Retrieval | YES |
| `Claude-Web` | Claude (legacy) | Retrieval | YES |
| `anthropic-ai` | Claude (legacy) | Training | Business call |
| `Google-Extended` | Gemini training | Training | Business call |
| `Googlebot` | Search + AIO + Gemini live | Both | YES (non-negotiable) |
| `Bingbot` | Bing + Copilot | Retrieval | YES |
| `Applebot-Extended` | Apple Intelligence | Training | YES (usually) |
| `CCBot` | Common Crawl → most open LLMs | Training | Business call |
| `Bytespider` | Doubao / TikTok | Training | Business call |
| `Meta-ExternalAgent` | Meta AI | Training | Business call |
| `Meta-ExternalFetcher` | Meta AI | Retrieval | YES |

**Common mistake:** blocking `GPTBot` to "protect content" while allowing `ChatGPT-User` works as intended — the content isn't used for training but CAN still be fetched live when a user asks ChatGPT about it. This is often the right balance for content-heavy publishers.

## 3. Universal signals LLMs weight

Across all engines, these content signals increase citation odds:

### Authority
- Age of domain (older = more weight, within reason).
- Backlinks from `.edu`, `.gov`, established industry sites.
- Wikipedia / Wikidata entry (single biggest multiplier).
- Named expert author with verifiable external profile.

### Freshness
- `dateModified` within the last 3–6 months for non-evergreen topics.
- Explicit "Last reviewed [date]" on evergreen.
- Schema `dateModified` matches visible date.

### Factuality signals
- Specific numbers over vague claims ("47% of teams" > "many teams").
- Named attributions ("according to a 2025 NIH study") > "research shows".
- Citations to primary sources.
- Data methodology disclosed.

### Structural clarity
- Semantic HTML (`<article>`, `<section>`, `<h2>`).
- Question-based headings.
- Self-contained paragraphs (each chunk makes sense without adjacent ones).
- No pronouns referencing earlier paragraphs.

### Entity grounding
- `Organization` schema with rich `sameAs` links.
- `Person` schema on author pages with LinkedIn / X / ORCID / other profile links.
- Wikipedia page exists for the brand or key topic.

## 4. Engine-specific tuning

### ChatGPT
- OpenAI's index heavily weighs recent, well-cited web content.
- Direct Q/A pairs work well — ChatGPT often quotes or paraphrases a single authoritative paragraph.
- `ChatGPT-User` respects robots.txt — if you block it, you lose live citations.

### Perplexity
- Perplexity shows 3–6 citations per answer, extremely visible to users.
- Perplexity heavily weighs DOMAIN AUTHORITY — authoritative sites get cited disproportionately.
- For newer sites: focus on original data + clear methodology. Perplexity likes "here's our specific dataset" pages.
- Perplexity's "Pages" feature builds landing pages of AI-synthesised answers — if your content dominates a topic, you may become a go-to citation there.

### Claude
- Claude's training cutoff is declared and users often ask Claude to verify with web search.
- Claude cites cautiously and names uncertainties — content with clear factual backing gets cited more.
- `ClaudeBot` / `Claude-SearchBot` behavior is newer; monitor logs.

### Gemini
- Gemini's citations are lighter than Perplexity's but present for factual queries.
- Benefits from Google's Knowledge Graph integration — entities known to Google get more reliable Gemini citations.
- Google Business Profile + Knowledge Panel both help Gemini citations for local queries.

### Copilot (Bing)
- Bing UX surfaces citations prominently.
- Bing is undervalued in most SEO strategies — if your competitors ignore Bing, Copilot is an easier citation win.
- Submit sitemaps to Bing Webmaster Tools (separate from GSC).
- Bing weighs social signals more than Google does — LinkedIn / YouTube mentions help.

## 5. Content patterns LLMs cite

### The quotable paragraph
LLMs often cite a single paragraph verbatim or paraphrased. Write paragraphs that stand alone:

**Quotable:**
> Fibre broadband installation in Bangalore typically takes 5–10 business days from order. Reputable providers offer installation guarantees with refunds for delays beyond the committed window.

**Not quotable (requires context):**
> As we've seen in the previous section, the installation process depends on several factors. The key thing to understand is that it varies.

### Data-backed claims
LLMs prefer specific numbers. Studies show higher citation rates for:
- "47% of enterprise networks in India use fibre" (specific number + context)
- Methodology notes ("survey of 1,200 IT leaders, Q1 2025")

### Named-source quotes
LLMs cite you as the authority when you quote other authorities:
> "Symmetric gigabit fibre is now the baseline for video-first businesses," says Dr Priya Iyer, CTO at your brand.

This gives LLMs a clean attribution chain: Dr Iyer → your page → user's query.

### Definitional content
For any concept where users ask "what is X":
- Start with the direct definition
- Follow with 1-2 sentences of context
- Avoid long preambles

## 6. Entity presence — the multiplier

The single biggest multiplier for LLM citation: **being a recognised entity in the model's world-model.**

### How to become an entity
1. **Wikipedia article** — if notable enough; do NOT write it yourself (conflict of interest). Encourage independent editors.
2. **Wikidata entry** — lower bar than Wikipedia; describes the entity structurally.
3. **Crunchbase / Bloomberg / industry registries** — feed data to enterprise knowledge graphs.
4. **LinkedIn company page + rich profile** — cross-referenced by many LLMs.
5. **GitHub organization** (for tech brands) — developer-facing LLMs lean on this.
6. **Strong social profiles** — X / BlueSky / LinkedIn with cross-linking.

### sameAs in Organization schema — the consolidated signal
All of the above should be listed in your `Organization.sameAs` array:

```json
"sameAs": [
  "https://en.wikipedia.org/wiki/Example_Corp",
  "https://www.wikidata.org/wiki/Q12345",
  "https://www.crunchbase.com/organization/example",
  "https://www.linkedin.com/company/example",
  "https://twitter.com/example",
  "https://github.com/example"
]
```

This is how you tell schema-aware LLMs "the entity on my page is THE SAME ENTITY as the one on Wikipedia."

## 7. Measurement

### Direct monitoring
- **ChatGPT, Claude, Perplexity, Gemini** — manually query for your brand + key topics weekly. Record which domains are cited.
- **Perplexity Pages** — monitor if your content is being synthesised.
- **Bing Copilot** — same; Bing WMT shows some referral data.

### Referral traffic
In Google Analytics (GA4) → Acquisition → Referrals:
- `chatgpt.com`
- `perplexity.ai`
- `claude.ai`
- `gemini.google.com`
- `copilot.microsoft.com`

Growing referrals from these domains is a direct signal that LLMs are citing you + users are clicking through.

### Brand mention monitoring
Set Google Alerts + similar for brand name queries. Any new article mentioning you is potential training data.

### Gap analysis
For important queries where you'd expect to be cited but aren't:
- Who IS cited? What do they have that you don't?
- Usually: more authoritative domain + clearer passage structure + Wikipedia presence.

## 8. Audit checklist

- **LLM-1** `robots.txt` explicitly allows `ChatGPT-User`, `OAI-SearchBot`, `Perplexity-User`, `Claude-SearchBot`, `Applebot-Extended`, `Meta-ExternalFetcher` (retrieval crawlers).
- **LLM-2** Training-crawler policy (`GPTBot`, `Google-Extended`, `anthropic-ai`, `CCBot`, `Bytespider`, `Meta-ExternalAgent`) is deliberate — not accidental.
- **LLM-3** `llms.txt` present and follows the spec (see `robots-llms-txt-playbook.md`).
- **LLM-4** `Organization` schema `sameAs` array includes Wikipedia / Wikidata / Crunchbase / LinkedIn / primary socials.
- **LLM-5** Author pages have `Person` schema with `sameAs` → LinkedIn / X / published work.
- **LLM-6** Content is server-rendered (LLM crawlers mostly don't execute JS).
- **LLM-7** Content uses semantic HTML + self-contained paragraphs (no "as mentioned above" chains).
- **LLM-8** Specific numbers / named attributions over vague claims.
- **LLM-9** Named expert quotes included where appropriate (adds attribution clarity).
- **LLM-10** `dateModified` reflects real content changes (not rebuilds).
- **LLM-11** Sitemap submitted to Bing Webmaster Tools (for Copilot).
- **LLM-12** Brand is a named entity in at least one authoritative source (Wikipedia, Wikidata, Crunchbase, industry registry).
- **LLM-13** Analytics tracks referrals from `chatgpt.com`, `perplexity.ai`, `claude.ai`, `gemini.google.com`, `copilot.microsoft.com`.
- **LLM-14** Team members have verifiable external profiles (LinkedIn bios, published work, podcast appearances).
- **LLM-15** No cloaking across user-agents — all LLM bots get the same HTML as Googlebot.

---

## Severity guidance

- AI retrieval crawlers (`ChatGPT-User`, `Perplexity-User`, `Claude-SearchBot`) disallowed → **High** (silently removes brand from live AI answers)
- No Wikipedia / Wikidata presence for an established brand → **Medium** (missed multiplier)
- Author schema missing / generic bylines ("Content Team") → **Medium** (weakens attribution)
- Client-side-only content rendering → **High** (LLM crawlers don't execute JS)
- No `sameAs` links in Organization schema → **Medium**
- Never submitted sitemap to Bing WMT → **Low** (still affects Copilot visibility)
- Vague "studies show" / "experts agree" without attribution → **Low** (weakens quotability)
