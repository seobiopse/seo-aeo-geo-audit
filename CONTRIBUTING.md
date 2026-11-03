# Contributing to the SEO Audit Plugin

Thanks for your interest in improving the plugin. **Please read this document before opening a PR or editing any file.**

---

## The short version

1. **Do not edit reference files directly.** Engineers don't commit changes — the maintainer does.
2. **All extensions go through [NEW-CHECK-REQUEST-TEMPLATE.md](NEW-CHECK-REQUEST-TEMPLATE.md)** → Marketing Director / AVP / Manager review → maintainer implementation.
3. **Bug reports and typo fixes also route through the same form** (marked as "bug" or "typo").
4. **For anything urgent** (broken audit, flagged regression, new AI bot needs robots.txt coverage) — fast-track: ping the maintainer on LinkedIn + file the form concurrently.

---

## The three roles

### 1. Engineer / team member (you, if you're reading this)
- Identifies gaps in the plugin's coverage.
- Documents the gap using the Request Template (NEW-CHECK-REQUEST-TEMPLATE.md).
- Submits to the reviewer.
- **Does NOT commit changes to the plugin.**

### 2. Marketing Director / AVP / Manager
- Reviews submitted requests.
- Judges whether the proposal belongs in the plugin.
- Checks severity / confidence calibration.
- Checks for overlap with existing checks.
- Decides: Approve / Approve with modifications / Defer / Reject (with written reason).
- Routes approved changes to the maintainer.

### 3. Plugin maintainer (Girish Kumar G)
- Sole commit access to reference files, SKILL.md, HANDOFF.md, and the generator script.
- Implements approved changes.
- Bumps the version number.
- Updates CHANGELOG.md.
- Notifies the team.

---

## Why governance exists

**Consistency.** Engineers fixing checks in different directions fragment the standard. A junior engineer's interpretation of "High severity" differs from a senior engineer's. Having one voice (the maintainer, with Marketing oversight) keeps calibration sharp.

**Quality control.** Not every good idea for a check actually belongs. Some are too narrow, some overlap with existing coverage, some use wrong severity. Marketing leadership catches these before they ship.

**Trust in the output.** When the marketing team hands an audit to a client or an exec, they need to be able to say "the plugin produced this — it's reliable." If engineers can change the plugin on a whim, that trust erodes.

---

## Fast-track vs standard review

### Fast-track (< 48-hour turnaround)
- A new AI bot appears and needs robots.txt handling.
- Google publishes updated schema requirement that invalidates existing guidance.
- Bug in an existing check (false positive / false negative with clear evidence).

### Standard review (quarterly batch)
- New check on existing territory.
- New category inside an existing audit group.
- Severity recalibration of existing checks.
- New reference file.

### Director-level decision
- New slash command.
- New audit group.
- Major generator rewrite.
- Change to the issue framework schema.
- Change to the report visual design.

---

## How to submit a request

1. Copy [`NEW-CHECK-REQUEST-TEMPLATE.md`](NEW-CHECK-REQUEST-TEMPLATE.md) into a new doc.
2. Fill out EVERY field (skipped fields signal the gap isn't well understood yet).
3. Submit via your team's standard review channel (Linear ticket / Confluence page / email to Marketing lead).
4. Wait for the decision.
5. If approved, the maintainer will implement. DO NOT merge changes yourself.

---

## What about typos and small content edits?

Same process. Submit a short form. Don't fix it yourself. The discipline of routing every change through the same review protects the bar.

---

## What about forking the plugin?

The plugin is MIT-licensed — you're free to fork, modify, and use it for commercial or non-commercial projects without asking permission.

**If you fork for a different brand:**
- Replace `react-nextjs-architecture-profile.md` with your own `<brand>-profile.md` (see the instructions inside that file).
- Update the signature band in `scripts/generate_report.py` if you want to attribute to your team instead of the original author.
- Fork-specific changes don't need to route through upstream governance — that's your fork, your rules.

**Upstream contributions are welcome** but not required. If you fix a bug or add a generally-useful feature, open a PR with a clear description — the maintainer will review.

---

## What about pull requests?

Upstream PRs need:

- A linked request doc (filed via the template) showing it was reviewed.
- Clear description of what changed and why.
- Updated CHANGELOG.md entry.
- Tests (if the change touches `generate_report.py`).
- No more than one concern per PR.

PRs without a linked approved request doc will be closed without review. This isn't hostile — it's the process working.

---

## Questions

[Girish Kumar G](https://in.linkedin.com/in/girish-theseoguy) — Father of SEO. DM on LinkedIn for anything urgent. For general discussion, use the team channel.
