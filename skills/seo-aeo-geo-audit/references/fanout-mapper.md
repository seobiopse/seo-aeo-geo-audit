# Fan-Out Mapper

Maps how well a page covers the set of related sub-queries behind a topic, finds the gaps, and (optionally) compares the page with a competitor's. Command: `/fanout-map`. Script: `scripts/fanout_coverage.py`. Mode name: `fanout`.

> **Calibration:** the sub-query set is the agent's estimate of what readers and answer systems ask around a topic. Search engines do not publish theirs. The coverage score is a word-overlap content-gap heuristic computed by this plugin. It is not a search-engine metric and does not predict rankings or citations. Google says its AI features need no special optimization; use this to find missing content that would help people, not to chase a number. See `google-guidance-alignment.md`.

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
- If a real-data source is available (autocomplete, related searches, People Also Ask, or a keyword tool connected through MCP such as Ahrefs or Semrush), add its queries as an extra aspect named "From real searches". Say which source you used.
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

Share the `.html` and `.md` files and summarise: overall score and grade, the weakest aspects, the top three additions, what the score cannot see, and how many sub-queries were removed as branded or duplicate. If the user wants the result inside a full audit report, copy the JSON's `scores_block` into `findings.json` as `scores.fanout`; `generate_report.py` renders it as a "Fan-Out Coverage" grader.

## Notes

- The scorer reads only the pages you give it. Pasted content stays on the machine.
- Stemming and stop words are English. Other languages still work through word overlap but with weaker matching; say so in the report.
- Re-run after changes to see the score move, and keep the same `fanout.json` so runs are comparable.
