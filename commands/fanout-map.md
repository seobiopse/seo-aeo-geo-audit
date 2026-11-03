---
description: Map how well a page covers the related sub-queries behind a topic (fan-out), find content gaps, and optionally compare against a competitor page. Offers real Google data via a Serper key or your connected SEO tools. Produces JSON, Markdown and an HTML heat map.
---

Run a **fan-out coverage map** (mode = `fanout`).

## What to do

1. Load the `seo-aeo-geo-audit` skill and read `references/fanout-mapper.md`. Follow it end to end. This is a lightweight mode: skip the archetype, stack and scoring steps of a full audit.
2. In your FIRST message ask for the inputs together and wait: the seed query or topic, the page (URL or pasted content), an optional competitor page, optional brand terms to exclude, the market/language, and a **Serper API key for real Google data (or "skip")**. Use `$ARGUMENTS` for anything already given. Never skip the key question on your own. No PageSpeed question is needed for this mode.
3. Build the agent-generated sub-query set (60 to 150 queries in 8 to 15 aspects) as the reference describes, and save it as `fanout.json`. Do not call these queries "real".
4. Add real-search data (Step 2a of the reference): if a key was given, use it (dry run first, session-only, never written to a file); if not, check for connected Ahrefs, Semrush, SerpApi or OpenRush tools and ASK PERMISSION before using any; otherwise continue and offer the paste-in option. Label every real-data source.
5. Run `scripts/fanout_coverage.py`. If it exits with code 2 (page needs a browser), follow `references/browser-access.md`: use Claude in Chrome, copy the rendered text, and re-run with `--text`.
6. Read the results honestly: review borderline and "missing" items against the best passages listed, and say what the word-overlap score cannot see.
7. Turn the gaps into the smallest set of recommended additions (heading, where it goes, answer-first opener, supporting detail). Flag sub-queries that deserve their own page. Offer the competitor candidates for battle mode and never copy a competitor's wording.
8. Share the `.html` and `.md` files. Summarise: score and grade, weakest aspects, top three additions, data sources used, limits of the score. Ask whether to discard the key. Label the score as a plugin heuristic, not a search-engine metric.

If the in-app browser or fetch tool cannot reach the site, follow `references/browser-access.md` in the skill you loaded: tell the user what failed, switch to Claude in Chrome, and if the extension is not installed give the install steps and wait.

$ARGUMENTS