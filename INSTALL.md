# Install on every platform

One skill folder, `skills/seo-aeo-geo-audit/`, follows the open [Agent Skills](https://agentskills.io/specification) format. Every host below either loads that folder directly or needs a paste-in prompt.

| Platform | How | 
|---|---|
| **Claude Code** | `/plugin marketplace add seobiopse/seo-aeo-geo-audit` then `/plugin install seo-aeo-geo-audit@seobiopse-skills`. Slash commands included (`/full-audit`, `/geo-audit`, ...). |
| **Claude (web, desktop, mobile)** | Download `seo-aeo-geo-audit.zip` from the latest GitHub Release (or run `tools/package.sh`). In Claude: Settings, Capabilities, Skills, upload the zip. Needs skills and code execution enabled on your plan. |
| **Codex / ChatGPT agents** | Copy `skills/seo-aeo-geo-audit/` to `~/.agents/skills/` (all projects) or `<repo>/.agents/skills/` (one project). Restart Codex. `AGENTS.md` in this repo also works as project guidance. |
| **Google Antigravity** | Copy the folder to `<project>/.agents/skills/` (one project) or `~/.gemini/config/skills/` (global). |
| **Any agent via CLI** | `npx skills add seobiopse/seo-aeo-geo-audit` installs into `~/.agents/skills`, which Codex and Antigravity read. |
| **Vertex AI, Gemini Gems, ChatGPT Custom GPTs / Projects** (no skill folders) | Use `docs/CHAT-PROMPT.md` as the system instruction and upload the files in `skills/seo-aeo-geo-audit/references/` as knowledge. You lose the automatic report script; the model writes the report in Markdown directly. |

Manual copy works everywhere:

```bash
# macOS / Linux
mkdir -p ~/.agents/skills && cp -r skills/seo-aeo-geo-audit ~/.agents/skills/
```

```powershell
# Windows
New-Item -ItemType Directory -Force "$HOME\.agents\skills" | Out-Null
Copy-Item -Recurse skills\seo-aeo-geo-audit "$HOME\.agents\skills\"
```

Host menus and paths change between releases. If a step doesn't match your version, check the host's own skills documentation.

## What works where

| Capability | Claude Code | Claude app | Codex | Antigravity | Chat-only (Vertex, GPT, Gem) |
|---|---|---|---|---|---|
| Methodology + checklists | yes | yes | yes | yes | yes (as knowledge files) |
| Live site checks | yes | if web/code tools on | yes | yes (browser agent) | only with browsing tool |
| `generate_report.py` HTML report | yes | if code execution on | yes | yes | no |
| Slash commands | yes | no | no | no | no |
