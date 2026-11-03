# PageSpeed Insights audit (optional)

Adds Lighthouse lab data and Chrome UX Report (CrUX) field data from Google's PageSpeed Insights API v5 (https://developers.google.com/speed/docs/insights/v5/get-started). It requires a user-provided API key. **No key means no PageSpeed test: skip it, say so in the report overview, and continue the audit.**

## 1. Ask for the key

Ask once, near Step 1 (scope), in one short message:

> Want a PageSpeed Insights test (Lighthouse scores + real-user Core Web Vitals)? If so, paste a PageSpeed API key. If you'd rather skip it, say "skip" and I'll continue without it.

- "skip", no answer, or no key: do not run the script. Do not guess values, and do not substitute Core Web Vitals numbers from memory. Add an `Info` note to `overview`: "PageSpeed test skipped (no API key provided)."
- Free key: create one in Google Cloud Console (enable "PageSpeed Insights API", then Credentials → Create API key).

## 2. Handle the key safely

The key is a credential. Rules for the agent:

1. **Session-only.** Use it for this audit run and nothing else. Do not reuse it for another site or later session unless the user pastes it again.
2. **Never persist it.** Do not write it to any file: not `findings.json`, reports, scratch files, `.env`, shell profiles, git-tracked files, or agent memory. Do not echo it back in chat or put it in a URL you display.
3. **Pass it without leaving traces.** Prefer stdin or an env var scoped to the single command, over `--key` (which shows in process lists and shell history):

   ```bash
   # stdin (preferred)
   printf '%s' "$KEY" | python3 scripts/pagespeed.py --url https://example.com/ --key-stdin --output pagespeed.json
   ```

   ```powershell
   # PowerShell: env var scoped to this command, removed straight after
   $env:PAGESPEED_API_KEY = '<key>'; python scripts/pagespeed.py --url https://example.com/ --output pagespeed.json; Remove-Item Env:PAGESPEED_API_KEY
   ```

4. **Forget it after the run.** Once the test finishes, stop using the key, clear any env var you set, and delete nothing but your own temp files. Then ask:

   > PageSpeed test done. I've discarded the key and nothing was saved to disk. For extra safety, you can delete or restrict that key in Google Cloud Console (APIs & Services → Credentials → restrict it to the PageSpeed Insights API). Want to keep it for another page in this session, or discard it now?

   Keep it only if the user says to, and only in the conversation, not on disk.
5. **If the user pastes the key in chat**, it remains in the conversation transcript, which the agent cannot erase. Mention this once and recommend rotating the key if the transcript is shared or the key is unrestricted.
6. `scripts/pagespeed.py` never writes the key to its output and strips it from error messages. Still check `pagespeed.json` before sharing it.

## 3. Run it

```bash
python3 scripts/pagespeed.py --url <page-url> --key-stdin --strategy both --output pagespeed.json
```

- One representative page per template (the API runs a real Lighthouse test and takes 10–60 s per strategy). Run mobile and desktop (`both`, default). Mobile is the headline number.
- Exit codes: 0 = ok or skipped, 1 = every strategy failed. If one strategy fails, `errors` lists it and the other is still returned. On `429` or quota errors, report it and carry on without PageSpeed data; don't retry in a loop.
- Test the public URL. PSI can't reach localhost or staging behind auth; for those, skip it and say why.

## 4. Read the output

`results.<strategy>` contains:
- `scores`: 0–100 for performance, accessibility, best-practices, seo. 90+ Good, 50–89 Needs improvement, below 50 Poor.
- `lab`: FCP, LCP, TBT, CLS, Speed Index, TTI (Lighthouse, simulated device and network).
- `field.page` / `field.origin`: CrUX real-user data with `percentile` and `category` (FAST/AVERAGE/SLOW) per metric. Field data is absent for low-traffic URLs; if `field.page` is null, say so, and use `field.origin` if present. Field data beats lab data when they disagree.
- `opportunities`: up to 10 failing performance audits, sorted by estimated savings.

Core Web Vitals thresholds (75th percentile): LCP ≤ 2.5 s good, > 4 s poor; INP ≤ 200 ms good, > 500 ms poor; CLS ≤ 0.1 good, > 0.25 poor.

## 5. Turn it into findings

- Copy `scores_block` into `findings.json` as `scores.pagespeed`. The HTML report renders it as a "PageSpeed Insights" grader; the Markdown report renders a table.
- Create a finding per failed Core Web Vital (field data first, lab data if no field data) and per significant opportunity. Follow `issue-framework.md` exactly, with pillar `SEO` (add `AEO`/`GEO` only if you can justify it), `audit_group: "Traditional SEO"`.

  | Condition | Severity |
  |---|---|
  | Field LCP/INP/CLS in the "poor" band | High |
  | Field metric in "needs improvement", or lab-only performance score < 50 | Medium |
  | Lab performance 50–89, or accessibility/best-practices < 90 | Low |
  | Everything passing | Info (record as passed) |

- Broken/fixed code: base it on what you actually saw (the audit's own title and details, plus the page source). Mark "needs input" if you haven't seen the offending resource.
- Lab and field numbers vary run to run. Never present them as exact or as a ranking prediction.
