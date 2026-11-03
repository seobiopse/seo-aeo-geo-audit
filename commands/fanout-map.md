---
description: Map how well a page covers the related sub-queries behind a topic (fan-out), find content gaps, and optionally compare against a competitor page. Produces JSON, Markdown and an HTML heat map.
---

Run a **fan-out coverage map** (mode = `fanout`).

## What to do

1. Load the `seo-aeo-geo-audit` skill and read `references/fanout-mapper.md`. Follow it end to end. This is a lightweight mode: skip the archetype, stack and scoring steps of a full audit.
2. In your FIRST message ask for the inputs together and wait: the seed query or topic, the page (URL or pasted content), an optional competitor page, optional brand terms to exclude, and the market/language. Use `$ARGUMENTS` for anything already given. No PageSpeed question is needed for this mode.
3. Build the sub-query set (60 to 150 queries in 8 to 15 aspects) as the reference describes, and save it as `fanout.json`. Do not invent search volumes or call the queries "real" unless they came from a data source.
4. Run `scripts/fanout_coverage.py`. If it exits with code 2 (page needs a browser), follow `references/browser-access.md`: use Claude in Chrome, copy the rendered text, and re-run with `--text`.
5. Read the results honestly: review borderline and "missing" items against the best passages listed, and say what the word-overlap score cannot see.
6. Turn the gaps into the smallest set of recommended additions (heading, where it goes, answer-first opener, supporting detail). Flag sub-queries that deserve their own page. Never recommend copying a competitor's wording.
7. Share the `.html` and `.md` files. Summarise: score and grade, weakest aspects, top three additions, limits of the score. Label the score as a plugin heuristic, not a search-engine metric.

If the in-app browser or fetch tool cannot reach the site, follow `references/browser-access.md` in the skill you loaded: tell the user what failed, switch to Claude in Chrome, and if the extension is not installed give the install steps and wait.

$ARGUMENTS
