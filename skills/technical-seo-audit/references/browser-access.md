# Live-site access and the Claude in Chrome fallback

Applies to every audit step that needs a live site: fetching pages, reading the rendered DOM, screenshots, the Network panel, tag checks. The same file ships in both audit skills; keep the two copies identical.

## The ladder

1. **Start with what the host gives you:** the built-in or in-app browser, a web-fetch tool, `curl`, or the probe script.
2. **Recognise a failure.** Treat any of these as "cannot access the site":
   - a tool error, timeout, "site not permitted" or "permission denied" for the domain
   - HTTP 401, 403, 429 or 5xx for the agent while the site works for the user
   - a bot challenge, CAPTCHA, "verify you are human" or Cloudflare-style interstitial
   - an empty page, or one that only shows "enable JavaScript", when the real page has content
   - a login wall, or a localhost / staging / VPN-only URL that the host cannot reach
3. **Say what happened and switch to Chrome.** Tell the user exactly what failed (which tool, which URL, which status or error), then say: "I'll use Claude in Chrome instead. It runs in your real Chrome with your own sign-ins." Do not carry on with guessed or partial data, and do not report the site as down or blocked to search engines on the strength of one failed request. Mark anything you could not check `not measured`.
4. **If the Claude in Chrome tools are available** (tools named `mcp__claude-in-chrome__*`, or a single `enable__mcp__claude-in-chrome` tool that you call first to turn them on):
   - Get the tab context, open a new tab for the audit, work there, and close the tabs you opened when you finish.
   - If Chrome asks for permission to act on the site, tell the user and wait for them to allow it.
   - Never solve a CAPTCHA or bot check for the user. Ask them to complete it in Chrome, then continue.
5. **If the extension is not available** (the tools are absent, or calls say the extension is not connected), stop and give the user these steps, then wait for "Chrome is ready":

   > To continue the audit I need Claude in Chrome. Please:
   > 1. Use Google Chrome on the same computer that runs this session (the extension only works in Chrome).
   > 2. Open https://claude.ai/chrome (or search "Claude in Chrome" in the Chrome Web Store) and choose **Add to Chrome**. Accept the permissions prompt.
   > 3. Pin the extension (puzzle-piece icon, then the pin) and sign in with the same Claude account you use here.
   > 4. Keep Chrome open. When asked, allow the site you want audited.
   > 5. Come back here and reply "Chrome is ready". If your host needs a restart or a setting to enable the Chrome connection, do that first. Menus change between releases, so check Anthropic's Claude in Chrome help page if a step does not match.

6. **If the user cannot or will not install it,** offer the alternatives and continue with what they give you:
   - paste the page source (`view-source:`), response headers (`curl -I <url>`), `robots.txt` and `sitemap.xml`
   - run `python3 scripts/tech_probe.py --url <url> --output probe.json` themselves (technical skill) and share the JSON
   - audit pasted code only (Method B)
   Browser-only checks stay `not measured`.

## Recording it

Put one line in the report overview: "Browser access: <built-in browser | fetch | probe> failed (<reason>); continued with Claude in Chrome" or "...; Claude in Chrome not available, browser-only checks not measured".

## Notes

- Claude in Chrome acts in the user's real browser with their sign-ins. Never sign out, change credentials or act on accounts beyond the audit.
- One request per page, small samples, same host only. Only audit sites the user is authorised to test.
- Other agent hosts (Codex, Antigravity) have their own browser tools. Use the host's equivalent, and apply the same ladder: say what failed, ask for the user's browser or pasted data.
