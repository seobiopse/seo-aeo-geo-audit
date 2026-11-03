# Fan-Out Mapper

Maps how well a page covers the set of related sub-queries behind a topic, finds the gaps, and (optionally) compares the page with a competitor's. Command: `/fanout-map`. Script: `scripts/fanout_coverage.py`. Mode name: `fanout`.

> **Calibration:** the sub-query set is the agent's estimate of what readers and answer systems ask around a topic, unless real-search data was added (the report lists its sources). Search engines do not publish their own sub-queries. The coverage score is a word-overlap content-gap heuristic computed by this plugin. It is not a search-engine metric and does not predict rankings or citations. Google says its AI features need no special optimization; use this to find missing content that would help people, not to chase a number. See `google-guidance-alignment.md`.

## When to use it

- "What content is my page missing for <topic>?"
- Before writing or refreshing a page, to plan sections.
- To compare a page with a competitor's page on the same topic (battle mode).
- To check a draft the user pastes in, before it is published.

This is a lightweight mode. Skip the archetype, stack and scoring steps of a full audit and follow the steps below.

## Step 1. Ask for the inputs (one message, wait for the answers)

1. **Seed query:** the topic or question to cover (for example "what to pack on a cruise").
2. **Page:** a URL, or the page content pasted in.
3. **Competitor page (optional):** a URL or pasted content, for battle mode.
4. **Brand terms to exclude (optional):** brand and product names whose sub-queries should be dropped (the user's and the competitor's).
5. **Market and language (optional):** defaults to the user's market, English.
6. **Real-search data (blocking question, same pattern as the PageSpeed key):** ask for a Serper API key, or "skip" (see Step 2a). Ask it in this same first message and wait for the answer. Never decide to skip on your own.

If the page cannot be fetched (403, bot challenge, JavaScript-only, login wall), follow `browser-access.md` before going on.

## Step 2. Build the sub-query set

Create 60 to 150 sub-queries in 8 to 15 aspects. Write each the way a person would type or say it (3 to 10 words), one distinct need per query, no near-duplicates. Mix question and statement forms. Use these aspect families, adding topic-specific ones as needed:

| Aspect | What it holds |
|---|---|
| Same question, other words | paraphrases, synonyms, plain-language and expert wording |
| Follow-up questions | what a reader asks right after the first answer |
| Broader context | the larger decision or process this topic sits inside |
| Narrower specifics | audience, season, place, size, budget, device, constraint |
| Definitions and prerequisites | terms to understand, things needed first (documents, tools, requirements) |
| Clarifications | ambiguous words, "X vs Y" meanings, common confusions |
| Comparisons and alternatives | options, versus questions, "best for" |
| How-to and steps | procedures, checklists, order of operations |
| Costs, timing and numbers | price, duration, limits, quantities, deadlines |
| Risks, mistakes and myths | what goes wrong, what to avoid, what is not true |
| Evidence, examples and proof | statistics, case examples, sources, reviews |
| Local, seasonal and situational | where, when and under what circumstances the answer changes |
| Other languages | only if the page serves more than one language |

Rules:
- Do not invent search volumes or claim the queries are "real" unless they came from a data source.
- Drop branded sub-queries (the script also removes any containing the brand terms the user gave).
- Real-search data is added afterwards in Step 2a. Build the agent-generated set first and save it as `fanout.json`.
- Keep time-sensitive qualifiers current; use the year only when a searcher would.

Save it as `fanout.json`:

```json
{
  "query": "what to pack on a cruise",
  "aspects": [
    {"name": "Follow-up questions", "queries": ["do you need formal wear on a cruise", "..."]},
    {"name": "Narrower specifics", "queries": ["what to pack for an alaska cruise in july", "..."]}
  ]
}
```

## Step 2a. Add real-search data (key first, then connectors, ask before using either)

The question in Step 1 offered a Serper key. Follow this order.

**1. Key given: use it.** [Serper](https://serper.dev) is a third-party Google results API with a free allowance (2,500 queries, no card at the time of writing). The script adds Google's "People also ask" and "Related searches" for the seed, plus a few second-level expansions, as extra aspects. Handle the key as a session-only credential, exactly like the PageSpeed key:
- Never write it to a file, report, memory or git, and never echo it back. Pass it by stdin or an environment variable scoped to the command.
- Show the plan first with `--dry-run`: it uses about 6 requests (roughly 6 credits; the user can confirm in their Serper dashboard).
- Tell the user what is sent: only the seed query and a few related queries, to Serper. Confidential text must not be used as the seed. Serper is a separate service with its own terms and privacy policy.
- Run it after `fanout.json` exists:

```bash
printf '%s' "$KEY" | python3 scripts/fanout_enrich.py --provider serper --key-stdin \
  --query "<seed>" --gl us --hl en --max-requests 6 \
  --exclude-domain <user-domain> --brand "<brands>" --merge fanout.json
```
```powershell
$env:SERPER_API_KEY = '<key>'; python scripts/fanout_enrich.py --provider serper --query "<seed>" --max-requests 6 --exclude-domain <user-domain> --merge fanout.json; Remove-Item Env:SERPER_API_KEY
```
- The result lists `competitor_candidates` (top-ranking domains, the user's own excluded). Offer them for battle mode and ask which to compare; never pick one silently.
- At the end ask whether to discard the key, and recommend deleting or rotating it in the Serper dashboard if the transcript will be shared.
- Exit status `error` with a hint means the key was rejected or the credits ran out. Say so, do not retry in a loop, and continue with the agent-generated set.

**2. No key (user said "skip" or gave none): check for connected data tools, and ask first.** Look through the tools you have for connectors named Ahrefs, Semrush, SerpApi/SERP API or OpenRush. If at least one is connected:
- Ask permission before any call, naming the connector and what you will pull (related and question keywords for the seed, People Also Ask and related searches, top-ranking URLs). Mention it may use the user's credits or quota. Wait for a clear yes. Never use a connector the user declined or did not answer.
- After a yes, pull a limited amount (about 100 rows at most). Typical sources: Ahrefs keyword explorer (matching terms, related terms, search suggestions) and SERP overview; Semrush keyword research reports (related keywords, questions); OpenRush keyword research and SERP inspection; SerpApi Google results (`related_questions`, `related_searches`). Call a connector's own schema or doc tool first when it has one.
- Add the queries to `fanout.json` as an aspect named "From real searches (<connector>)" and append a source entry such as `{"type": "connector", "label": "Ahrefs related terms", "date": "<today>"}` to its `sources` list, so the report states where they came from. Do not show volumes unless the tool returned them.
- If a connector is listed but needs authorization, tell the user to authorize it (in Claude Code with `/mcp`, or in the host's connector settings) and either wait or continue without it.

**3. Nothing available.** Continue with the agent-generated set and say so. Offer two upgrades: a free Serper key, or pasting queries observed elsewhere (for example the "searched for" queries an assistant shows, or related searches copied from a results page):

```bash
python3 scripts/fanout_enrich.py --provider import --import queries.txt --label "ChatGPT (pasted)" --merge fanout.json
```

Rules for all three: label every real-data aspect with its source, never call agent-generated queries "real", and never describe SERP features as the queries an AI system used. They show what people ask and what Google lists around the topic.

## Step 3. Run the scorer

```bash
python3 scripts/fanout_coverage.py --fanout fanout.json --url <page-url> \
  [--competitor-url <url>] [--brand "acme,acme corp"] --output-dir <dir>
```

Other page sources: `--html FILE` (saved HTML) or `--text FILE` (pasted text; a line starting with `#` is a heading). The same exist for the competitor (`--competitor-html`, `--competitor-text`). It needs only Python 3.8+, no packages and no API key. It makes one request per URL you give it and nothing else.

Exit code 2 means the page needs a real browser (little or no text was found, or the fetch failed). Open the page in Claude in Chrome (`browser-access.md`), copy the rendered text with `get_page_text`, save it to a file and re-run with `--text`.

Outputs in `<dir>`: `fanout-map-<query>-<date>.json`, `.md` and `.html` (score ring, aspect bars, heat map, gap list, missing words, every sub-query with its best passage, and battle mode when a competitor was given).

## Step 4. Read the result honestly

- **How it scores:** the page is split into passages under their headings. Each sub-query is scored against windows of 1 to 3 consecutive passages plus the section heading, using weighted word overlap (rare words count more than the topic word that every query shares) and adjacent-word overlap, with light English stemming. At or above 0.72 is covered; 0.45 to 0.72 is partial; below is missing. The score is covered plus half of partial, as a percentage.
- **What it cannot see:** synonyms and paraphrases beyond stemming, content inside images or video, content added by JavaScript after load, and meaning. Review borderline and surprising results by reading the best passage the report lists. If a "missing" sub-query is clearly answered in different words, say so in your write-up and do not count it as a gap.
- **Check the set, not just the page:** a low score can mean a weak sub-query list. Remove sub-queries that are off-topic for this page's intent.

## Step 5. Turn gaps into recommendations

- Group gaps by aspect and propose the smallest set of additions that closes them: usually a handful of sections, not one section per sub-query.
- For each addition give: the heading (phrased as the question), where it goes (extend the named section, or add a new one), the answer-first sentence to open with, and the supporting detail needed (data, example, table, steps).
- Flag sub-queries that need their own page because they serve a different intent, instead of stuffing them into this one.
- Write for people. Do not recommend repeating sub-queries as keywords, padding, or headings that add nothing.
- Missing words: list the terms that appear nowhere on the page and say whether each deserves a mention.

## Step 6. Battle mode

When a competitor page is given, report both scores, the per-aspect comparison, "they cover, you don't" (the opportunities) and "you cover, they don't" (your advantages). Use it to find topics to cover better. Never recommend copying their wording.

## Step 7. Report

Share the `.html` and `.md` files and summarise: overall score and grade, the weakest aspects, the top three additions, what the score cannot see, how many sub-queries were removed as branded or duplicate, and which data sources fed the sub-query set (agent estimate, Serper, a connector, or pasted queries). If the user wants the result inside a full audit report, copy the JSON's `scores_block` into `findings.json` as `scores.fanout`; `generate_report.py` renders it as a "Fan-Out Coverage" grader.

## Notes

- The scorer reads only the pages you give it. Pasted content stays on the machine.
- Stemming and stop words are English. Other languages still work through word overlap but with weaker matching; say so in the report.
- Re-run after changes to see the score move, and keep the same `fanout.json` so runs are comparable.
