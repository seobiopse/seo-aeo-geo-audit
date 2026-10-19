# robots.txt and llms.txt Playbook

Deep-dive on the two text files at the root of your domain that decide which bots see your content. Most sites get both wrong.

Read whenever the audit involves crawler access decisions — or any time bot traffic matters (always, if you care about GEO).

## Two files, two jobs

- **`robots.txt`** — the standards-based crawl-control file. Tells bots what they may and may not fetch. Does NOT control indexing (use `noindex` for that).
- **`llms.txt`** — an emerging standard. Tells LLMs where your most important content lives and how to summarise it. Does NOT control access (use `robots.txt` for that).

They work together, not interchangeably.

## Table of contents

1. [robots.txt — file structure + precedence](#1-robotstxt-structure)
2. [User-agent list for 2026](#2-user-agent-list)
3. [Per-bot policy decisions](#3-per-bot-policy-decisions)
4. [Common robots.txt mistakes](#4-common-robotstxt-mistakes)
5. [llms.txt — the spec](#5-llmstxt-spec)
6. [llms-full.txt — when and how](#6-llms-full-txt)
7. [What to NEVER put in either file](#7-what-to-never-put)
8. [Testing and verification](#8-testing-and-verification)
9. [Audit checklist](#9-audit-checklist)

---

## 1. robots.txt — file structure + precedence

Must be at `https://<domain>/robots.txt`, HTTP 200, `Content-Type: text/plain`.

### Record structure

```
User-agent: <bot-name or *>
Disallow: <path-prefix>
Allow: <path-prefix>
Crawl-delay: <seconds>   # not supported by Googlebot; Bing honors it

Sitemap: <absolute URL>  # anywhere in file, applies globally
```

### Precedence rules (important — often misunderstood)

1. **Most specific User-agent wins for that bot.** If you have both `User-agent: *` and `User-agent: Googlebot`, Googlebot obeys ONLY the `Googlebot` block, not the `*` block.

2. **Longest matching rule wins within a block.** `Allow: /blog/public/` beats `Disallow: /blog/` for `/blog/public/post`.

3. **Empty `Disallow:` = allow everything.** Used to override an earlier `Disallow` for a specific bot.

4. **Case sensitivity** — path matching is case-sensitive. `/Blog/` and `/blog/` are different to robots.txt.

5. **The `$` anchor** — `Disallow: /*.pdf$` blocks files ending in `.pdf`. Supported by Googlebot and Bingbot.

### Example with precedence

```
User-agent: *
Disallow: /admin/
Disallow: /draft/

User-agent: Googlebot
Disallow: /draft/
# Googlebot can now access /admin/ — its block doesn't include that Disallow

User-agent: Bingbot
Disallow: /admin/
Disallow: /draft/
Crawl-delay: 2

Sitemap: https://example.com/sitemap.xml
```

## 2. User-agent list for 2026

Keep this list updated as new bots emerge.

### Search engines (allow unless deliberate)
- `Googlebot` (+ `Googlebot-News`, `Googlebot-Image`, `Googlebot-Video`)
- `Bingbot`
- `DuckDuckBot`
- `Applebot` (Apple search)
- `YandexBot`
- `Baiduspider`

### AI retrieval crawlers (allow for live citation in AI products)
- `ChatGPT-User` — ChatGPT browse-on-behalf-of-user
- `OAI-SearchBot` — OpenAI's search index
- `PerplexityBot` — Perplexity's search crawler
- `Perplexity-User` — Perplexity retrieval for user queries
- `ClaudeBot` — Anthropic's general crawler
- `Claude-SearchBot` — Anthropic's search crawler
- `Claude-Web` — legacy Anthropic crawler
- `anthropic-ai` — legacy Anthropic
- `Applebot-Extended` — Apple Intelligence
- `Meta-ExternalFetcher` — Meta AI retrieval

### AI training crawlers (business decision whether to allow)
- `GPTBot` — OpenAI training
- `Google-Extended` — Google Gemini training (does NOT control AI Overviews; those use Googlebot)
- `Bytespider` — ByteDance/TikTok/Doubao training
- `CCBot` — Common Crawl (feeds most open training datasets)
- `Meta-ExternalAgent` — Meta AI training
- `FacebookBot` — Meta training
- `ImagesiftBot` — CC training derivative
- `omgilibot` — SEMRush / training

### SEO tools (allow if you use them, block if you don't)
- `AhrefsBot`, `SemrushBot`, `MJ12bot`, `DotBot`, `BLEXBot`

### Bad actors (block)
- Any bot you don't recognise that's hitting your server hard.

## 3. Per-bot policy decisions

### Decision 1 — AI retrieval (live citation)
**Recommendation: ALLOW** these bots. Blocking them silently removes your brand from ChatGPT / Perplexity / Claude answers.

- `ChatGPT-User`, `OAI-SearchBot`, `PerplexityBot`, `Perplexity-User`, `ClaudeBot`, `Claude-SearchBot`, `Applebot-Extended`

### Decision 2 — AI training crawlers
**Mixed.** This is a business / legal / IP decision:
- ALLOW → your content enters training sets → eventually contributes to model knowledge → more likely to be cited in general queries even without retrieval.
- DISALLOW → your content stays out of training → but you LOSE long-term presence in model world-knowledge.

Industry defaults in 2026:
- Publishers with strong IP: DISALLOW `GPTBot`, `CCBot`, `Google-Extended`.
- Marketing sites / open content / docs: ALLOW all.
- B2B SaaS: Mixed — allow retrieval, variably allow training.

### Decision 3 — SEO tools
Allow `AhrefsBot` / `SemrushBot` if you use those tools to audit your own site. Otherwise block to save bandwidth.

## 4. Common robots.txt mistakes

### 4.1 Blocking CSS / JS
```
# ❌ BAD — blocks Googlebot from seeing the page as a user sees it
User-agent: *
Disallow: /assets/
Disallow: /_next/
```

Googlebot needs CSS + JS to render the page. Blocking these breaks Mobile-Friendly test and ranking.

### 4.2 Blocking the sitemap path
```
# ❌ BAD
User-agent: *
Disallow: /sitemap.xml
```

### 4.3 Typos in user agent
```
# ❌ BAD — "Google-bot" isn't a real user agent; rule has no effect
User-agent: Google-bot
```

Correct: `Googlebot` (one word, capital G).

### 4.4 Confusing `Disallow:` with `noindex`
`Disallow:` blocks fetch. If another site links to a blocked URL, Google CAN still index the URL (just without content). To actually prevent indexing, the URL must be FETCHABLE and return `<meta name="robots" content="noindex">` or `X-Robots-Tag: noindex`.

### 4.5 Using `Disallow:` for staging
```
# ❌ INSUFFICIENT
User-agent: *
Disallow: /
```

For staging environments, use HTTP basic auth, IP allowlist, OR server-side `X-Robots-Tag: noindex`. `robots.txt` alone doesn't prevent accidental indexation when your URL is discovered via backlinks.

### 4.6 Trailing slash confusion
```
Disallow: /api/  # blocks /api/ and everything under it
Disallow: /api   # blocks /api, /api/, /apikey, /api-docs — probably not what you want
```

Always include the trailing slash when you mean "directory".

### 4.7 Missing `Sitemap:` directive
The `Sitemap:` directive isn't required, but including it lets bots discover your sitemap without needing to guess `/sitemap.xml`.

## 5. llms.txt — the spec

Official spec: https://llmstxt.org/

### File structure

Must be at `https://<domain>/llms.txt`, HTTP 200, `Content-Type: text/markdown`.

Format is Markdown with specific conventions:

```markdown
# Brand or Site Name

> One-sentence description of what this site is.

A few paragraphs explaining what the site covers and who it's for. Keep under ~500 words.

## Docs

- [Getting started](https://example.com/docs/start): Short description
- [API reference](https://example.com/api): Short description
- [Authentication](https://example.com/docs/auth): Short description

## Guides

- [Building your first integration](https://example.com/guides/first): Description
- [Best practices](https://example.com/guides/best-practices): Description

## Optional

- [Changelog](https://example.com/changelog): Version history
- [Blog](https://blog.example.com): Long-form content
```

### Rules

- Only one `#` H1 — the brand/site name.
- Blockquote (`>`) is the short description. Used by LLMs as the canonical one-liner.
- `##` H2 sections group links by category. Common categories: `Docs`, `Guides`, `API`, `Optional`.
- Every link is `[Title](absolute URL): short description`.
- Under "Optional" — links LLMs can skip for a concise summary but read for deeper context.

### Purpose

`llms.txt` is to LLMs what `sitemap.xml` is to search engines — but curated and summarised. When an LLM needs to understand your site, it can read 50 lines of Markdown instead of crawling 10,000 pages.

## 6. llms-full.txt — when and how

`llms-full.txt` is an optional extension: the full Markdown of your most important content, flattened into one file. Useful for:

- Documentation sites (entire docs in one file).
- Small marketing sites (entire site in one file).

```markdown
# Docs for your brand

## Getting Started

[Full Markdown of the Getting Started page goes here.]

---

## API Reference

[Full Markdown of the API reference page goes here.]

---

[etc.]
```

### Who should produce it
- Technical docs sites: yes.
- Marketing/ecommerce sites: no (too much noise, too many ephemeral pages).
- Job boards / programmatic sites: no (jobs change too fast).

### Size limit
Keep under 500 KB. Most LLMs cap the retrievable-file size around 1 MB but chunking quality degrades above ~500 KB.

## 7. What to NEVER put in either file

- Internal / staging URLs.
- Unpublished features, prices, or product names.
- Customer data or PII.
- Credentials, API keys, auth tokens.
- Draft / private documentation.

`robots.txt` and `llms.txt` are both public. Treat them like you'd treat a newspaper ad.

## 8. Testing and verification

### robots.txt tester
- Google Search Console → Settings → `robots.txt` → open the tester.
- Paste a test URL + user-agent → the tester shows whether it's blocked or allowed.

### llms.txt validation
- Open https://llmstxt.org/ for the reference spec.
- Fetch your file: `curl https://example.com/llms.txt` — should return HTTP 200 and Markdown.
- Try asking Claude / ChatGPT / Perplexity a question about your product; if it cites your llms.txt URLs, it's working.

### Cross-bot consistency check

```bash
for ua in "Googlebot" "Bingbot" "GPTBot" "ChatGPT-User" "ClaudeBot" "PerplexityBot" "CCBot"; do
  echo "=== $ua ==="
  curl -s -H "User-Agent: $ua" https://example.com/robots.txt | head -20
done
```

All bots should see the same file. If your CDN or WAF serves a different version per user-agent, you have a cloaking risk.

## 9. Audit checklist

- **RL-1** `robots.txt` reachable at `/robots.txt` with HTTP 200 + `text/plain`.
- **RL-2** `robots.txt` does NOT have blanket `Disallow: /` (unless intentionally private).
- **RL-3** `robots.txt` does NOT block CSS (`/css/`, `/assets/`, `/_next/static/`) or JS critical for rendering.
- **RL-4** Staging/dev directives (blanket `Disallow: /` or explicit `Disallow: /staging/`) REMOVED from prod robots.txt.
- **RL-5** User-agent typos none (verify: Googlebot, Bingbot, GPTBot, ClaudeBot, PerplexityBot — exact casing).
- **RL-6** `Sitemap:` directive(s) present and use absolute URLs.
- **RL-7** AI retrieval crawlers (ChatGPT-User, OAI-SearchBot, Perplexity-User, Claude-SearchBot, Applebot-Extended) explicitly allowed (or covered by `User-agent: *` with no disallow).
- **RL-8** AI training crawler policy (GPTBot, Google-Extended, CCBot, Bytespider, anthropic-ai) deliberate — not accidental.
- **RL-9** No cloaking: same `robots.txt` served to all user agents (cross-bot check above).
- **RL-10** `llms.txt` present at `/llms.txt`, HTTP 200, `text/markdown`.
- **RL-11** `llms.txt` follows the spec: one `#` H1, `>` blockquote description, `##` sections, markdown links with descriptions.
- **RL-12** `llms.txt` contains no internal URLs, no unpublished content, no PII.
- **RL-13** `llms-full.txt` (if used): < 500 KB, well-structured Markdown.
- **RL-14** For important paths, `noindex` is used where the goal is "don't index" — not `Disallow:` alone.

---

## Severity guidance

- Blanket `Disallow: /` in prod `robots.txt` → **Critical** (page does not exist for search)
- CSS/JS blocked in `robots.txt` → **High** (breaks Googlebot rendering)
- Missing `Sitemap:` directive → **Low**
- No `llms.txt` → **Medium** (missed GEO opportunity)
- AI retrieval bots disallowed → **High** (silent drop in AI citations)
- User-agent typo → **Medium** (rule has no effect)
