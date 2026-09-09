#!/usr/bin/env python3
"""
generate_report.py — Generate both a Markdown and a premium-styled HTML report
from a findings JSON for the SEO / AEO / GEO audit skill.

HTML output matches the reference "Audit Report" style:
- Navy palette, Playfair Display + DM Sans fonts
- Topbar / gradient header with 4-cell meta / sticky TOC / scorecard / footer
- Two-column "SEO Audit Finding" (amber) / "Revamp Implementation" (navy) grid
- Rich prose paragraphs + syntax-highlighted code blocks with icon copy button
- Severity + Channel pastel badges

Usage:
    python generate_report.py --input findings.json --output-dir /path/to/output
    cat findings.json | python generate_report.py --output-dir /path --stdin

Input JSON schema (v2):
{
  "audit": {
    "mode": "seo" | "aeo" | "geo" | "full" | "crawl-check",
    "target": "https://example.com",
    "date": "YYYY-MM-DD",
    "input_method": "live-url" | "code-snippet",
    "environment": "localhost" | "staging" | "production" | "code",
    "project_label": "optional — shows in topbar and header",
    "stack_label": "optional — e.g. 'Next.js App Router + Pages Router'",
    "prepared_by": "optional — e.g. 'Kumar — AdsPilot'"
  },
  "summary": {
    "total_checks_run": 87, "passed": 62, "failed": 15, "warned": 10,
    "scorecard": [
      {"label": "Indexable pages", "value_from": "1", "value_to": "16", "hint": "..."},
      {"label": "JSON-LD schemas", "value_from": "0", "value_to": "53", "hint": "..."},
      {"label": "FAQ pairs",      "value_from": "0", "value_to": "49", "hint": "..."}
    ]
  },
  "overview": "Free HTML for the overview box (use <strong>, <em>, <br><br> as needed).",
  "findings": [
    {
      "id": "SEO-001",
      "severity": "critical" | "high" | "medium" | "low" | "info",
      "confidence": 95,                              # 0-100
      "evidence_source": "curl -H 'User-Agent: GPTBot' <url> | grep -c '<h1>' → 0",
      "pillars": ["SEO", "AEO", "GEO"],
      "category": "Architecture",                    # shown as section eyebrow
      "section_title": "Single-page site → 16 independent pages",
      "section_intro": "Short paragraph below the title.",
      "location": "head > meta[name=robots]",

      # RICH "before" side
      "finding_paragraphs": [
        "<p>The live page has <strong>...</strong>.</p>",
        "<p>There was no way to rank separately for <em>...</em>.</p>"
      ],
      "broken_code": "<!-- ... -->",
      "broken_language": "html",

      # RICH "after" side
      "implementation_paragraphs": [
        "<p>Rebuilt as <strong>16 independent pages</strong> ...</p>"
      ],
      "fixed_code": "<!-- ... -->",
      "fixed_language": "html",

      # Legacy flat fields are still accepted and will be synthesised into paragraphs:
      "summary": "...", "why_flagged": "...",
      "impact_seo": "...", "impact_aeo": "...", "impact_geo": "...",
      "benefits": ["..."],
      "verify": "..."
    }
  ],
  "additional_notes": "Optional free HTML for a callout at the end."
}
"""

import argparse
import html as html_mod
import json
import re
import sys
from datetime import date
from pathlib import Path


SEVERITY_ORDER = ["critical", "high", "medium", "low", "info"]

AUDIT_GROUP_ORDER = ["Traditional SEO", "LLM Visibility"]
AUDIT_GROUP_SUBTITLES = {
    "Traditional SEO": "Crawling, indexing, ranking — Googlebot + Bingbot + classic SEO pillars",
    "LLM Visibility": "Google AI Overview + ChatGPT + Perplexity + Claude + Gemini + Copilot citation",
}
CATEGORY_ORDER_IN_GROUP = {
    "Traditional SEO": ["On-Page", "Technical"],
    "LLM Visibility": ["Google AI Overview", "Other LLM Models"],
}

SEV_BADGE_CLASS = {
    "critical": "sev-critical",
    "high":     "sev-high",
    "medium":   "sev-medium",
    "low":      "sev-low",
    "info":     "sev-info",
}
SEV_LABEL = {
    "critical": "Critical", "high": "High", "medium": "Medium", "low": "Low", "info": "Info",
}

CHANNEL_CLASS = { "SEO": "ch-seo", "AEO": "ch-aeo", "GEO": "ch-geo" }


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def esc(value):
    """HTML-escape a value for use inside an HTML element.

    Unescape any existing entities first so that callers who (by mistake)
    pre-encode text like 'Zero &lt;h1&gt;' get a single-escaped result
    rather than the double-escaped '&amp;lt;' which renders as literal '&lt;'.
    """
    if value is None:
        return ""
    return html_mod.escape(html_mod.unescape(str(value)))


def sort_findings(findings):
    def key(f):
        ag = f.get("audit_group", "Traditional SEO")
        ag_idx = AUDIT_GROUP_ORDER.index(ag) if ag in AUDIT_GROUP_ORDER else len(AUDIT_GROUP_ORDER)
        cat = f.get("category", "")
        # Strip group prefix if present (e.g. "Traditional SEO — On-Page" → "On-Page")
        cat_base = cat.split(" — ")[-1] if " — " in cat else cat
        cats = CATEGORY_ORDER_IN_GROUP.get(ag, [])
        cat_idx = cats.index(cat_base) if cat_base in cats else len(cats)
        sev = f.get("severity", "info").lower()
        sev_idx = SEVERITY_ORDER.index(sev) if sev in SEVERITY_ORDER else len(SEVERITY_ORDER)
        return (ag_idx, cat_idx, sev_idx, f.get("id", ""))
    return sorted(findings, key=key)


def group_findings_counts(findings):
    counts = {s: 0 for s in SEVERITY_ORDER}
    for f in findings:
        sev = f.get("severity", "info").lower()
        if sev in counts:
            counts[sev] += 1
    return counts


# ---------------------------------------------------------------------------
# Syntax highlighter (simple regex-based)
# ---------------------------------------------------------------------------

def highlight(code, language):
    """Return HTML with span-wrapped tokens for a dark code block.

    Supports: html, jsx, tsx, js, ts, json, css, bash. Unknown → escaped only.
    """
    if not code:
        return ""
    code_escaped = html_mod.escape(code)
    lang = (language or "").lower()

    if lang in ("html", "xml", "svg"):
        return _highlight_html(code_escaped)
    if lang in ("json", "jsonld", "json-ld"):
        return _highlight_json(code_escaped)
    if lang in ("jsx", "tsx", "js", "javascript", "ts", "typescript"):
        return _highlight_js(code_escaped)
    if lang == "css":
        return _highlight_css(code_escaped)
    if lang in ("bash", "sh", "shell"):
        return _highlight_bash(code_escaped)
    return code_escaped


def _highlight_html(code):
    # Comments first
    code = re.sub(r"(&lt;!--.*?--&gt;)", r'<span class="cm">\1</span>', code, flags=re.DOTALL)
    # Strings (attribute values inside quotes)
    code = re.sub(r'(=)(&quot;[^&]*?&quot;)', r'\1<span class="str">\2</span>', code)
    # Tag opens/closes: &lt;tag  or  &lt;/tag
    code = re.sub(r"(&lt;/?)([a-zA-Z][a-zA-Z0-9-]*)", r'<span class="kw">\1\2</span>', code)
    # Attribute names (word=)
    code = re.sub(r"(\s)([a-zA-Z-:]+)(=)", r'\1<span class="at">\2</span>\3', code)
    return code


def _highlight_json(code):
    # Comments (rare but supported)
    code = re.sub(r"(//[^\n]*)", r'<span class="cm">\1</span>', code)
    # Strings (need to handle before numbers/keywords)
    code = re.sub(r'(&quot;(?:[^&]|&(?!quot;))*?&quot;)(\s*:)', r'<span class="at">\1</span>\2', code)  # keys
    code = re.sub(r'(:\s*)(&quot;(?:[^&]|&(?!quot;))*?&quot;)', r'\1<span class="str">\2</span>', code)  # string values
    # Numbers
    code = re.sub(r"\b(-?\d+\.?\d*)\b", r'<span class="num">\1</span>', code)
    # Keywords
    code = re.sub(r"\b(true|false|null)\b", r'<span class="kw">\1</span>', code)
    return code


def _highlight_js(code):
    code = re.sub(r"(//[^\n]*)", r'<span class="cm">\1</span>', code)
    code = re.sub(r"(/\*.*?\*/)", r'<span class="cm">\1</span>', code, flags=re.DOTALL)
    code = re.sub(r"(&quot;[^&]*?&quot;|&#x27;[^&]*?&#x27;|`[^`]*?`)", r'<span class="str">\1</span>', code)
    keywords = r"\b(import|export|default|from|const|let|var|function|async|await|return|if|else|for|while|class|new|typeof|instanceof|true|false|null|undefined|try|catch|finally|throw)\b"
    code = re.sub(keywords, r'<span class="kw">\1</span>', code)
    code = re.sub(r"\b(-?\d+\.?\d*)\b", r'<span class="num">\1</span>', code)
    return code


def _highlight_css(code):
    code = re.sub(r"(/\*.*?\*/)", r'<span class="cm">\1</span>', code, flags=re.DOTALL)
    code = re.sub(r"(&quot;[^&]*?&quot;)", r'<span class="str">\1</span>', code)
    code = re.sub(r"([a-z-]+)(\s*:)", r'<span class="at">\1</span>\2', code)
    return code


def _highlight_bash(code):
    code = re.sub(r"(#[^\n]*)", r'<span class="cm">\1</span>', code)
    code = re.sub(r"(&quot;[^&]*?&quot;|&#x27;[^&]*?&#x27;)", r'<span class="str">\1</span>', code)
    code = re.sub(r"^(\$\s|[a-z]+\b)", r'<span class="kw">\1</span>', code, flags=re.MULTILINE)
    return code


# ---------------------------------------------------------------------------
# Markdown rendering (tickets-ready)
# ---------------------------------------------------------------------------

def render_markdown(data):
    audit = data.get("audit", {})
    summary = data.get("summary", {})
    findings = sort_findings(data.get("findings", []))
    counts = group_findings_counts(findings)

    out = []
    out.append(f"# SEO / AEO / GEO Audit — {audit.get('mode', 'unknown').upper()}")
    out.append("")
    out.append(f"**Target:** {audit.get('target', '—')}  ")
    out.append(f"**Date:** {audit.get('date', '—')}  ")
    out.append(f"**Environment:** {audit.get('environment', '—')}  ")
    out.append(f"**Input method:** {audit.get('input_method', '—')}")
    if audit.get("project_label"):
        out.append(f"  \n**Project:** {audit['project_label']}")
    if audit.get("stack_label"):
        out.append(f"  \n**Stack:** {audit['stack_label']}")
    if audit.get("prepared_by"):
        out.append(f"  \n**Prepared by:** {audit['prepared_by']}")
    out.append("")
    out.append("## Summary")
    out.append("")
    out.append(f"- Checks run: **{summary.get('total_checks_run', '—')}**")
    out.append(f"- Passed: **{summary.get('passed', '—')}**")
    out.append(f"- Warnings: **{summary.get('warned', '—')}**")
    out.append(f"- Failures: **{summary.get('failed', '—')}**")
    out.append("")
    out.append("### Findings by severity")
    out.append("")
    out.append("| Severity | Count |")
    out.append("|---|---|")
    for sev in SEVERITY_ORDER:
        out.append(f"| {SEV_LABEL[sev]} | {counts[sev]} |")
    out.append("")

    if summary.get("scorecard"):
        out.append("### Scorecard")
        out.append("")
        for card in summary["scorecard"]:
            vf = card.get("value_from", "—")
            vt = card.get("value_to", "—")
            out.append(f"- **{card.get('label', '')}:** {vf} → **{vt}** — {card.get('hint', '')}")
        out.append("")

    if data.get("overview"):
        out.append("### Overview")
        out.append("")
        # Strip HTML in MD for readability
        plain = re.sub(r"<[^>]+>", "", data["overview"])
        out.append(plain)
        out.append("")

    out.append("---")
    out.append("")
    out.append("## Findings")
    out.append("")

    if not findings:
        out.append("_No issues found. All applicable checks passed._")
    else:
        for idx, f in enumerate(findings, start=1):
            sev = f.get("severity", "info").lower()
            pillars = " | ".join(f.get("pillars", []))
            conf = f.get("confidence")
            conf_label = f"  (confidence {conf}/100)" if conf is not None else ""

            out.append(f"### {idx}. [{SEV_LABEL.get(sev, 'Info')}]{conf_label} {f.get('section_title', f.get('title', 'Untitled'))}")
            out.append("")
            out.append(f"**ID:** `{f.get('id', '—')}`  ")
            out.append(f"**Pillars:** {pillars or '—'}  ")
            out.append(f"**Category:** {f.get('category', '—')}  ")
            out.append(f"**Location:** `{f.get('location', '—')}`")
            if f.get("evidence_source"):
                out.append(f"  \n**Evidence:** `{f['evidence_source']}`")
            out.append("")

            if f.get("section_intro"):
                out.append(f.get("section_intro"))
                out.append("")

            # "Before" side
            out.append("**SEO Audit Finding**")
            out.append("")
            _render_paragraph_block(out, f, "finding_paragraphs", fallback=_synthesise_before(f))

            if f.get("broken_code"):
                out.append(f"```{f.get('broken_language', 'html')}")
                out.append(f["broken_code"].rstrip())
                out.append("```")
                out.append("")

            # "After" side
            out.append("**Revamp Implementation**")
            out.append("")
            _render_paragraph_block(out, f, "implementation_paragraphs", fallback=_synthesise_after(f))

            if f.get("fixed_code"):
                out.append(f"```{f.get('fixed_language', 'html')}")
                out.append(f["fixed_code"].rstrip())
                out.append("```")
                out.append("")

            if f.get("verify"):
                out.append(f"**How to verify:** {f['verify']}")
                out.append("")

            out.append("---")
            out.append("")

    return "\n".join(out)


def _render_paragraph_block(out, f, key, fallback):
    paragraphs = f.get(key) or fallback or []
    for p in paragraphs:
        plain = re.sub(r"<[^>]+>", "", p)
        out.append(plain)
        out.append("")


def _synthesise_before(f):
    paras = []
    parts = []
    if f.get("summary"):
        parts.append(f["summary"])
    if f.get("why_flagged"):
        parts.append(f["why_flagged"])
    if parts:
        paras.append("<p>" + " ".join(parts) + "</p>")
    impact_parts = []
    if f.get("impact_seo"):
        impact_parts.append(f"<strong>SEO:</strong> {f['impact_seo']}")
    if f.get("impact_aeo"):
        impact_parts.append(f"<strong>AEO:</strong> {f['impact_aeo']}")
    if f.get("impact_geo"):
        impact_parts.append(f"<strong>GEO:</strong> {f['impact_geo']}")
    if impact_parts:
        paras.append("<p><strong>Impact if ignored:</strong> " + " — ".join(impact_parts) + "</p>")
    return paras


def _synthesise_after(f):
    paras = []
    benefits = f.get("benefits") or []
    if benefits:
        benefits_html = "".join(f"<li>{b}</li>" for b in benefits)
        paras.append(f"<p><strong>Benefits if implemented:</strong></p><ul>{benefits_html}</ul>")
    return paras


# ---------------------------------------------------------------------------
# HTML rendering (styled to reference)
# ---------------------------------------------------------------------------

def render_severity_badge(severity):
    sev = severity.lower()
    cls = SEV_BADGE_CLASS.get(sev, "sev-info")
    return f'<span class="sev-badge {cls}">{esc(SEV_LABEL.get(sev, "Info"))}</span>'


def render_channel_badges(pillars):
    return "".join(
        f'<span class="ch-badge {CHANNEL_CLASS.get(p, "ch-seo")}">{esc(p)}</span>'
        for p in pillars
    )


def render_code_block(code, language):
    if not code:
        return ""
    highlighted = highlight(code, language)
    return f"""<div class="code-with-copy">
<button class="copy-btn" type="button" aria-label="Copy"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>Copy</button>
<pre>{highlighted}</pre>
</div>"""


def render_paragraphs(paragraphs):
    """paragraphs is a list of HTML paragraph strings. They're inserted verbatim (trusted)."""
    return "".join(paragraphs)


def render_confidence_chip(conf, evidence):
    if conf is None:
        return ""
    conf_class = "conf-high" if conf >= 80 else ("conf-med" if conf >= 60 else "conf-low")
    ev = f'<span class="conf-evidence">evidence: <code>{esc(evidence)}</code></span>' if evidence else ""
    return f'<span class="conf-chip {conf_class}">Confidence {conf}/100</span> {ev}'


def render_finding_section(idx, f):
    sev = f.get("severity", "info").lower()
    pillars = f.get("pillars", [])

    # Fall back to legacy flat fields if rich paragraphs aren't provided
    before_paragraphs = f.get("finding_paragraphs") or _synthesise_before(f)
    after_paragraphs = f.get("implementation_paragraphs") or _synthesise_after(f)

    section_title = esc(f.get("section_title") or f.get("title") or "Untitled")
    section_intro = esc(f.get("section_intro") or "")
    category = esc(f.get("category") or "")
    location = esc(f.get("location") or "")
    verify = esc(f.get("verify") or "")
    conf_row = render_confidence_chip(f.get("confidence"), f.get("evidence_source"))

    before_code = render_code_block(f.get("broken_code"), f.get("broken_language", "html"))
    after_code = render_code_block(f.get("fixed_code"), f.get("fixed_language", "html"))

    verify_block = ""
    if verify:
        verify_block = f'<p class="verify-line"><strong>How to verify:</strong> {verify}</p>'

    location_block = ""
    if location:
        location_block = f'<p class="location-line"><strong>Location:</strong> <code>{location}</code></p>'

    # Page / pages_affected rendering
    page = f.get("page")
    pages_affected = f.get("pages_affected") or []
    page_block = ""
    if page:
        page_block = f'<p class="page-line"><strong>Page:</strong> <code>{esc(page)}</code></p>'
    elif pages_affected:
        chips = "".join(f'<code class="page-chip">{esc(p)}</code>' for p in pages_affected)
        page_block = f'<p class="page-line"><strong>Pages affected ({len(pages_affected)}):</strong></p><div class="pages-grid">{chips}</div>'

    finding_id = f.get("id", f"#{idx}")

    return f"""
<div class="section finding-card" id="s{idx}" data-finding-id="{esc(finding_id)}">
  <label class="resolved-toggle" for="fix-{esc(finding_id)}">
    <input type="checkbox" class="finding-check" id="fix-{esc(finding_id)}" data-finding-id="{esc(finding_id)}">
    <span class="resolved-label"><span class="resolved-text-pending">Mark as addressed</span><span class="resolved-text-done">Addressed ✓</span></span>
  </label>
  <div class="section-head-row"><div class="section-num">{idx}</div><span class="section-eyebrow" style="margin-bottom:0;">{category}</span></div>
  <h2 class="section-h2">{section_title}</h2>
  <hr class="section-divider">
  {f'<p class="section-intro">{section_intro}</p>' if section_intro else ''}
  {page_block}
  {location_block}
  <div class="ba-grid">
    <div class="ba-col">
      <div class="ba-header before-h"><span class="ba-dot before-dot"></span>SEO Audit Finding</div>
      <div class="ba-body before-body">
        <p class="badge-row"><strong>Severity:</strong> {render_severity_badge(sev)} <strong>Channels:</strong> {render_channel_badges(pillars)}</p>
        {f'<p class="conf-row">{conf_row}</p>' if conf_row.strip() else ''}
        {render_paragraphs(before_paragraphs)}
        {before_code}
      </div>
    </div>
    <div class="ba-col">
      <div class="ba-header after-h"><span class="ba-dot after-dot"></span>Revamp Implementation</div>
      <div class="ba-body after-body">
        {render_paragraphs(after_paragraphs)}
        {after_code}
        {verify_block}
      </div>
    </div>
  </div>
</div>
"""


def render_toc(findings):
    items = []
    for i, f in enumerate(findings, start=1):
        short = esc(f.get("category") or (f.get("section_title") or f.get("title") or f"Finding {i}"))[:26]
        items.append(f'<a class="toc-link" href="#s{i}">{i}. {short}</a>')
    return "".join(items)


def render_scorecard(summary):
    cards = summary.get("scorecard") or []
    if not cards:
        return ""
    blocks = []
    for c in cards:
        vf = esc(c.get("value_from", "—"))
        vt = esc(c.get("value_to", "—"))
        blocks.append(f"""<div class="score-card">
  <div class="score-label">{esc(c.get('label', ''))}</div>
  <div class="score-value bad">{vf} &rarr; {vt}</div>
  <div class="score-hint">{esc(c.get('hint', ''))}</div>
</div>""")
    return f'<div class="scorecard" style="margin-top:24px;">{"".join(blocks)}</div>'


def _grade_color(value, max_value):
    """Return a color hint based on the % of max: green for >=75%, amber 60-74%, red <60%."""
    if max_value <= 0:
        return "#6b7280"
    pct = (value / max_value) * 100
    if pct >= 75:
        return "#047857"  # green
    if pct >= 60:
        return "#a16207"  # amber
    return "#b91c1c"      # red


def render_score_grader(label, score_obj, pillar_field="breakdown"):
    """Render a single grader block (SEO Quality OR E-E-A-T)."""
    if not score_obj:
        return ""
    overall = score_obj.get("overall", 0)
    grade = esc(score_obj.get("grade", ""))
    page_type = esc(score_obj.get("page_type", ""))
    overall_color = _grade_color(overall, 100)

    breakdown = score_obj.get(pillar_field) or score_obj.get("breakdown") or []

    bars_html = ""
    for b in breakdown:
        # Support both "label" and "pillar" naming
        blabel = esc(b.get("label") or b.get("pillar") or "")
        bval = b.get("value", 0)
        bmax = b.get("max", 0)
        bnote = esc(b.get("note", "") or "")
        bpct = (bval / bmax * 100) if bmax else 0
        bcolor = _grade_color(bval, bmax)
        # Sub-signals (E-E-A-T pillar can have sub_signals list)
        sub_signals = b.get("sub_signals") or []
        sub_html = ""
        if sub_signals:
            sub_rows = []
            for s in sub_signals:
                slabel = esc(s.get("label", ""))
                sval = s.get("value", 0)
                smax = s.get("max", 0)
                status = s.get("status", "")
                status_chip = ""
                if status:
                    status_cls = "status-pass" if status == "pass" else ("status-partial" if status == "partial" else "status-fail")
                    status_chip = f'<span class="sub-status {status_cls}">{esc(status)}</span>'
                sub_rows.append(
                    f'<li><span class="sub-label">{slabel}</span>'
                    f'<span class="sub-score">{sval}/{smax}</span>'
                    f'{status_chip}</li>'
                )
            sub_html = f'<ul class="sub-signals">{"".join(sub_rows)}</ul>'
        bars_html += f"""<div class="score-dim">
  <div class="score-dim-head">
    <span class="score-dim-label">{blabel}</span>
    <span class="score-dim-value" style="color:{bcolor}">{bval} / {bmax}</span>
  </div>
  <div class="score-dim-track"><div class="score-dim-fill" style="width:{bpct:.1f}%;background:{bcolor}"></div></div>
  {f'<div class="score-dim-note">{bnote}</div>' if bnote else ''}
  {sub_html}
</div>"""

    # Top improvements
    improvements = score_obj.get("top_improvements") or []
    improvements_html = ""
    if improvements:
        lis = "".join(f"<li>{esc(imp)}</li>" for imp in improvements)
        improvements_html = f'<div class="score-improvements"><h4>Top improvements</h4><ol>{lis}</ol></div>'

    return f"""
<div class="score-grader">
  <div class="score-grader-head">
    <div class="score-grader-title">
      <span class="score-grader-eyebrow">{esc(label)}</span>
      <h3 class="score-grader-name">{esc(score_obj.get('name', label))}</h3>
      <div class="score-grader-meta">Page type: <strong>{page_type}</strong></div>
    </div>
    <div class="score-grader-badge" style="border-color:{overall_color};color:{overall_color}">
      <div class="score-number">{overall}<span class="score-max">/100</span></div>
      <div class="score-grade">{grade}</div>
    </div>
  </div>
  <div class="score-bars">{bars_html}</div>
  {improvements_html}
</div>"""


def render_scores_block(data):
    scores = data.get("scores") or {}
    if not scores:
        return ""
    parts = []
    if "seo_quality" in scores:
        parts.append(render_score_grader("SEO Quality Score", {**scores["seo_quality"], "name": "SEO Quality Score"}, pillar_field="breakdown"))
    if "eeat" in scores:
        parts.append(render_score_grader("E-E-A-T Score", {**scores["eeat"], "name": "E-E-A-T Score"}, pillar_field="breakdown"))
    if "ai_citation" in scores:
        parts.append(render_score_grader("AI Citation Readiness", {**scores["ai_citation"], "name": "AI Citation Readiness"}, pillar_field="breakdown"))
    if not parts:
        return ""
    return f"""
<div class="scores-wrap" id="scores">
  <span class="section-eyebrow" style="padding:0 40px;">Scorecards</span>
  <h2 class="section-h2" style="padding:0 40px;">Quality, E-E-A-T &amp; AI Citation Grades</h2>
  <p class="section-intro" style="padding:0 40px;">Scoring models: <strong>SEO Quality</strong> (NLP-driven content grade), <strong>E-E-A-T</strong> (Google's Experience / Expertise / Authoritativeness / Trust), and <strong>AI Citation Readiness</strong> (chunk density, chunk relevance, extractable units, Bing indexation). Scores are summaries, not substitutes for the detailed findings below.</p>
  <div class="scores-grid">{"".join(parts)}</div>
</div>"""


def render_summary_stats(summary):
    """Fallback scorecard when none is provided — shows counts by severity."""
    counts = summary
    return f"""<div class="scorecard" style="margin-top:24px;">
  <div class="score-card"><div class="score-label">Checks run</div><div class="score-value">{esc(counts.get('total_checks_run', '—'))}</div><div class="score-hint">Total items evaluated</div></div>
  <div class="score-card"><div class="score-label">Passed</div><div class="score-value good">{esc(counts.get('passed', '—'))}</div><div class="score-hint">Items meeting the standard</div></div>
  <div class="score-card"><div class="score-label">Findings</div><div class="score-value bad">{int(counts.get('failed', 0) or 0) + int(counts.get('warned', 0) or 0)}</div><div class="score-hint">Warnings + failures combined</div></div>
</div>"""


def render_html(data):
    audit = data.get("audit", {})
    summary = data.get("summary", {})
    findings = sort_findings(data.get("findings", []))
    counts = group_findings_counts(findings)

    # Sections with audit-group dividers
    parts = []
    last_group = None
    for i, f in enumerate(findings, start=1):
        group = f.get("audit_group", "Traditional SEO")
        if group != last_group:
            subtitle = AUDIT_GROUP_SUBTITLES.get(group, "")
            parts.append(f"""<div class="group-divider" id="group-{group.replace(' ', '-').lower()}">
  <span class="group-eyebrow">Audit group</span>
  <h1 class="group-heading">{esc(group)}</h1>
  <p class="group-subtitle">{esc(subtitle)}</p>
</div>""")
            last_group = group
        parts.append(render_finding_section(i, f))
    finding_sections = "".join(parts)
    toc_links = render_toc(findings)
    scorecard_html = render_scorecard(summary) or render_summary_stats(summary)
    overview_html = data.get("overview") or (
        "This report documents SEO / AEO / GEO findings for the audited target. Each section pairs the observed code or configuration on the live site alongside the recommended implementation."
    )
    notes = data.get("additional_notes")
    notes_block = f'<div class="callout callout-warn" style="margin-top:24px;"><div class="callout-icon">&#9888;&#65039;</div><div>{notes}</div></div>' if notes else ""

    project_label = esc(audit.get("project_label") or f"Audit — {audit.get('mode', 'SEO').upper()}")
    stack_label = esc(audit.get("stack_label") or "—")
    prepared_by = esc(audit.get("prepared_by") or "—")
    target = esc(audit.get("target", "—"))
    audit_date = esc(audit.get("date", "—"))
    env = esc(audit.get("environment", "—"))
    input_method = esc(audit.get("input_method", "—"))
    mode_label = esc(audit.get("mode", "—").upper())

    scores_block = render_scores_block(data)

    return _HTML_TEMPLATE.format(
        project_label=project_label,
        stack_label=stack_label,
        prepared_by=prepared_by,
        target=target,
        audit_date=audit_date,
        env=env,
        input_method=input_method,
        mode_label=mode_label,
        critical_count=counts["critical"],
        high_count=counts["high"],
        medium_count=counts["medium"],
        low_count=counts["low"],
        info_count=counts["info"],
        scorecard_html=scorecard_html,
        scores_block=scores_block,
        overview_html=overview_html,
        notes_block=notes_block,
        toc_links=toc_links,
        finding_sections=finding_sections or '<p class="section-intro">No findings — all applicable checks passed.</p>',
        total_findings=len(findings),
    )


# Big template — uses {{ }} to escape literal braces in CSS.
_HTML_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SEO Audit Report — {project_label}</title>
<meta name="description" content="SEO / AEO / GEO audit with before/after code for every finding.">
<meta name="robots" content="noindex, follow">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
:root {{
  --navy-deep:#0a1f3d; --navy-dark:#123d7a; --navy-mid:#1e5cb8; --navy-light:#2e7ccc;
  --navy-pale:#eef4fc; --navy-border:#c5d9f2; --navy-muted:#4a6b9a; --navy-accent:#60a5fa;
  --text-dark:#0d1e38; --text-body:#1f2f4a; --text-muted:#4a6b9a;
  --white:#fff; --bg:#f5f8fc; --border:#d6e3f2;
  --amber-pale:#fef3c7; --amber-border:#fcd34d; --amber:#92400e;
  --blue-pale:#eff6ff; --blue-border:#bfdbfe; --blue:#1d4ed8;
  --red-pale:#fef2f2; --red-border:#fecaca; --red:#b91c1c;
  --purple-pale:#f5f3ff; --purple-border:#ddd6fe; --purple:#6d28d9;
  --green-pale:#ecfdf5; --green-border:#a7f3d0; --green:#047857;
  --code-bg:#0d1117; --code-text:#e6edf3;
  --mono: 'SF Mono','Fira Code','Cascadia Code','Consolas',monospace;
  --radius-sm:8px; --radius-md:12px; --radius-lg:18px;
}}
html {{ scroll-behavior:smooth; }}
body {{ font-family:'DM Sans', sans-serif; font-size:14px; line-height:1.7; color:var(--text-dark); background:var(--bg); }}

/* TOPBAR */
.topbar {{ background:var(--navy-deep); color:rgba(255,255,255,0.8); font-size:12px; padding:8px 40px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px; }}
.topbar-trust {{ display:flex; gap:18px; }}
.topbar-trust span::before {{ content:'✓ '; color:var(--navy-accent); }}

/* HEADER */
.doc-header {{ background:linear-gradient(135deg, var(--navy-deep) 0%, var(--navy-dark) 100%); padding:36px 40px 30px; color:white; }}
.header-row {{ display:flex; justify-content:space-between; align-items:flex-start; gap:20px; flex-wrap:wrap; margin-bottom:18px; }}
.doc-header h1 {{ font-family:'Playfair Display', serif; font-size:26px; font-weight:700; color:white; line-height:1.25; }}
.doc-header h1 span {{ color:var(--navy-accent); }}
.status-badge {{ display:inline-flex; align-items:center; gap:6px; background:rgba(255,255,255,0.12); border:1px solid rgba(255,255,255,0.22); color:white; font-size:11px; font-weight:700; padding:6px 14px; border-radius:20px; letter-spacing:0.5px; text-transform:uppercase; white-space:nowrap; flex-shrink:0; }}
.status-dot {{ width:7px; height:7px; background:var(--navy-accent); border-radius:50%; }}
.meta-grid {{ display:grid; grid-template-columns:repeat(4, 1fr); gap:6px 0; font-size:12.5px; color:rgba(255,255,255,0.65); border-top:1px solid rgba(255,255,255,0.12); padding-top:16px; }}
.meta-grid strong {{ display:block; color:white; font-weight:600; font-size:13px; }}

/* TOC */
.toc-bar {{ background:var(--white); border-bottom:1px solid var(--border); padding:11px 40px; display:flex; align-items:center; gap:6px; flex-wrap:wrap; position:sticky; top:0; z-index:50; box-shadow:0 1px 8px rgba(0,0,0,0.06); }}
.toc-label {{ font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:1px; margin-right:4px; }}
.toc-link {{ font-size:12px; color:var(--navy-dark); text-decoration:none; padding:4px 10px; border-radius:20px; border:1px solid var(--border); background:var(--white); transition:background 0.2s; white-space:nowrap; }}
.toc-link:hover {{ background:var(--navy-pale); border-color:var(--navy-border); }}

/* CONTENT */
.content {{ max-width:1100px; margin:0 auto; padding:36px 40px 80px; }}
.section {{ margin-bottom:48px; }}
.section-eyebrow {{ font-size:10px; font-weight:700; letter-spacing:2px; text-transform:uppercase; color:var(--navy-mid); margin-bottom:6px; display:block; }}
.section-h2 {{ font-family:'Playfair Display', serif; font-size:22px; font-weight:700; color:var(--text-dark); margin-bottom:10px; line-height:1.25; }}
.section-intro {{ font-size:14px; color:var(--text-muted); margin-bottom:22px; line-height:1.7; max-width:820px; }}
.section-head-row {{ display:flex; align-items:center; gap:12px; margin-bottom:8px; }}
.section-num {{ width:28px; height:28px; background:var(--navy-dark); color:white; border-radius:50%; font-size:13px; font-weight:700; display:flex; align-items:center; justify-content:center; flex-shrink:0; }}
.section-divider {{ border:none; border-top:2px solid var(--border); margin:0 0 22px; }}
.location-line {{ font-size:12.5px; color:var(--text-muted); margin-bottom:16px; }}
.location-line code {{ font-family:var(--mono); font-size:12px; background:var(--navy-pale); color:var(--navy-dark); padding:1px 6px; border-radius:4px; border:1px solid var(--navy-border); }}
.page-line {{ font-size:12.5px; color:var(--text-muted); margin:12px 0 6px; }}
.page-line code {{ font-family:var(--mono); font-size:12px; background:var(--navy-pale); color:var(--navy-dark); padding:1px 6px; border-radius:4px; border:1px solid var(--navy-border); }}
.pages-grid {{ display:flex; flex-wrap:wrap; gap:6px; margin:0 0 16px; }}
.page-chip {{ font-family:var(--mono); font-size:11px; background:var(--navy-pale); color:var(--navy-dark); padding:2px 8px; border-radius:4px; border:1px solid var(--navy-border); }}

/* SCORES BLOCK */
.scores-wrap {{ max-width:1100px; margin:0 auto; padding:36px 0 8px; }}
.scores-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; padding:0 40px; }}
@media (max-width: 900px) {{ .scores-grid {{ grid-template-columns:1fr; }} }}
.score-grader {{ background:var(--white); border:1.5px solid var(--border); border-radius:var(--radius-md); padding:22px 24px; box-shadow:0 2px 12px rgba(18,61,122,0.06); }}
.score-grader-head {{ display:flex; justify-content:space-between; align-items:flex-start; gap:16px; margin-bottom:18px; padding-bottom:14px; border-bottom:1px solid var(--border); }}
.score-grader-title {{ flex:1; }}
.score-grader-eyebrow {{ font-size:10px; font-weight:700; letter-spacing:1.5px; text-transform:uppercase; color:var(--navy-mid); display:block; margin-bottom:3px; }}
.score-grader-name {{ font-family:'Playfair Display', serif; font-size:19px; font-weight:700; color:var(--text-dark); margin:0 0 4px; }}
.score-grader-meta {{ font-size:12px; color:var(--text-muted); }}
.score-grader-meta strong {{ color:var(--navy-dark); }}
.score-grader-badge {{ flex-shrink:0; min-width:90px; border:2px solid; border-radius:var(--radius-md); padding:10px 14px; text-align:center; background:white; }}
.score-number {{ font-family:'Playfair Display', serif; font-size:32px; font-weight:700; line-height:1; }}
.score-max {{ font-size:13px; font-weight:400; opacity:0.6; }}
.score-grade {{ font-size:10px; font-weight:700; letter-spacing:0.8px; text-transform:uppercase; margin-top:4px; }}
.score-bars {{ display:flex; flex-direction:column; gap:10px; }}
.score-dim {{ font-size:12px; }}
.score-dim-head {{ display:flex; justify-content:space-between; align-items:baseline; margin-bottom:4px; }}
.score-dim-label {{ font-weight:600; color:var(--text-dark); }}
.score-dim-value {{ font-family:var(--mono); font-size:11px; font-weight:700; }}
.score-dim-track {{ height:6px; background:var(--bg-alt, #eef4fc); border-radius:3px; overflow:hidden; }}
.score-dim-fill {{ height:100%; border-radius:3px; transition:width 0.5s ease-out; }}
.score-dim-note {{ font-size:11px; color:var(--text-muted); margin-top:3px; font-style:italic; }}
.sub-signals {{ list-style:none; padding:6px 0 0 16px; margin:4px 0 0; font-size:11px; color:var(--text-muted); }}
.sub-signals li {{ display:flex; justify-content:space-between; align-items:center; padding:2px 0; gap:8px; }}
.sub-signals .sub-label {{ flex:1; }}
.sub-signals .sub-score {{ font-family:var(--mono); color:var(--text-body); }}
.sub-status {{ font-size:9px; font-weight:700; letter-spacing:0.5px; text-transform:uppercase; padding:1px 6px; border-radius:3px; border:1px solid; }}
.status-pass {{ background:var(--green-pale); color:var(--green); border-color:var(--green-border); }}
.status-partial {{ background:var(--amber-pale); color:var(--amber); border-color:var(--amber-border); }}
.status-fail {{ background:var(--red-pale); color:var(--red); border-color:var(--red-border); }}
.score-improvements {{ margin-top:16px; padding-top:14px; border-top:1px solid var(--border); }}
.score-improvements h4 {{ font-size:10px; font-weight:700; letter-spacing:1px; text-transform:uppercase; color:var(--text-muted); margin:0 0 8px; }}
.score-improvements ol {{ margin:0; padding-left:20px; font-size:12.5px; color:var(--text-body); line-height:1.55; }}
.score-improvements li {{ margin-bottom:5px; }}

/* AUDIT GROUP DIVIDER */
.group-divider {{ background:linear-gradient(135deg, var(--navy-deep) 0%, var(--navy-dark) 100%); color:white; padding:28px 32px; border-radius:var(--radius-md); margin:40px 0 32px; box-shadow:0 4px 16px rgba(10,31,61,0.18); }}
.group-eyebrow {{ font-size:10px; font-weight:700; letter-spacing:2px; text-transform:uppercase; color:var(--navy-accent); display:block; margin-bottom:8px; }}
.group-heading {{ font-family:'Playfair Display', serif; font-size:30px; font-weight:700; color:white; margin:0 0 6px; line-height:1.2; }}
.group-subtitle {{ font-size:14px; color:rgba(255,255,255,0.75); margin:0; max-width:720px; line-height:1.55; }}

/* PROGRESS BAR */
.audit-progress {{ position:sticky; top:42px; z-index:40; background:white; padding:10px 40px; border-bottom:1px solid var(--border); box-shadow:0 1px 6px rgba(0,0,0,0.04); }}
.progress-meta {{ display:flex; align-items:center; gap:12px; font-size:12px; color:var(--text-muted); margin-bottom:6px; }}
.progress-label {{ font-weight:700; text-transform:uppercase; letter-spacing:1px; color:var(--navy-dark); }}
.progress-count {{ font-family:var(--mono); }}
.progress-count #progress-done {{ color:var(--green); font-weight:700; }}
.progress-reset {{ margin-left:auto; background:transparent; border:1px solid var(--border); border-radius:6px; padding:3px 10px; font-size:11px; color:var(--text-muted); cursor:pointer; transition:all 0.15s; }}
.progress-reset:hover {{ background:var(--navy-pale); border-color:var(--navy-border); color:var(--navy-dark); }}
.progress-track {{ height:6px; background:var(--bg-alt, #eef4fc); border-radius:3px; overflow:hidden; }}
.progress-fill {{ height:100%; background:linear-gradient(90deg, var(--navy-mid) 0%, var(--green) 100%); transition:width 0.35s ease-out; border-radius:3px; }}
.progress-fill.complete {{ background:var(--green); }}

/* RESOLVED CHECKBOX ON FINDING */
.finding-card {{ position:relative; transition:opacity 0.3s, filter 0.3s; }}
.resolved-toggle {{ position:absolute; top:16px; right:20px; display:flex; align-items:center; gap:6px; cursor:pointer; user-select:none; padding:6px 10px; border:1px solid var(--border); border-radius:20px; background:white; font-size:11px; font-weight:600; color:var(--text-muted); transition:all 0.15s; z-index:5; }}
.resolved-toggle:hover {{ border-color:var(--navy-border); background:var(--navy-pale); color:var(--navy-dark); }}
.resolved-toggle input[type=checkbox] {{ margin:0; cursor:pointer; }}
.resolved-label {{ display:inline-block; }}
.resolved-label .resolved-text-done {{ display:none; color:var(--green); }}
.finding-card.resolved .resolved-label .resolved-text-pending {{ display:none; }}
.finding-card.resolved .resolved-label .resolved-text-done {{ display:inline; }}
.finding-card.resolved {{ opacity:0.55; }}
.finding-card.resolved:hover {{ opacity:0.85; }}
.finding-card.resolved .resolved-toggle {{ border-color:var(--green-border); background:var(--green-pale); color:var(--green); opacity:1; }}
.finding-card.resolved .section-h2 {{ text-decoration:line-through; text-decoration-color:rgba(0,0,0,0.2); }}

/* RERUN PANEL */
.rerun-panel {{ display:none; background:linear-gradient(135deg, #dcfce7 0%, #ecfdf5 100%); border:2px solid var(--green-border); border-radius:var(--radius-lg); padding:32px 36px; margin:40px 0 0; box-shadow:0 4px 20px rgba(4,120,87,0.12); }}
.rerun-panel.visible {{ display:block; animation:rerunFade 0.5s ease-out; }}
@keyframes rerunFade {{ from {{ opacity:0; transform:translateY(8px); }} to {{ opacity:1; transform:translateY(0); }} }}
.rerun-inner {{ text-align:center; max-width:720px; margin:0 auto; }}
.rerun-badge {{ font-size:48px; line-height:1; margin-bottom:8px; }}
.rerun-heading {{ font-family:'Playfair Display', serif; font-size:26px; font-weight:700; color:#065f46; margin:0 0 10px; }}
.rerun-sub {{ color:#065f46; font-size:15px; margin:0 0 20px; }}
.rerun-commands {{ text-align:left; background:white; border:1px solid var(--green-border); border-radius:var(--radius-md); padding:18px 22px; margin-bottom:16px; }}
.rerun-commands h3 {{ font-size:11px; text-transform:uppercase; letter-spacing:1px; color:var(--text-muted); margin:0 0 10px; font-weight:700; }}
.rerun-commands ol {{ margin:0; padding-left:22px; font-size:13.5px; color:var(--text-body); line-height:1.7; }}
.rerun-commands li {{ margin-bottom:8px; }}
.rerun-cmd {{ display:inline-block; background:#0f172a; color:#a8ff78; padding:4px 10px; border-radius:5px; font-family:var(--mono); font-size:12.5px; border:none; margin:3px 0; }}
.rerun-reset {{ background:transparent; border:1px solid rgba(6,95,70,0.25); color:#065f46; padding:6px 14px; border-radius:18px; cursor:pointer; font-size:12px; transition:all 0.15s; }}
.rerun-reset:hover {{ background:rgba(6,95,70,0.08); border-color:#065f46; }}

@media print {{
  .audit-progress, .resolved-toggle, .rerun-panel {{ display:none !important; }}
  .finding-card.resolved {{ opacity:1 !important; filter:none !important; }}
  .finding-card.resolved .section-h2 {{ text-decoration:none !important; }}
}}

/* OVERVIEW */
.overview-box {{ background:var(--navy-pale); border-left:4px solid var(--navy-dark); border-radius:0 var(--radius-sm) var(--radius-sm) 0; padding:18px 22px; font-size:14px; color:var(--text-body); line-height:1.75; }}
.overview-box strong {{ color:var(--navy-dark); }}

/* BEFORE/AFTER GRID */
.ba-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:0; border:1.5px solid var(--border); border-radius:var(--radius-md); overflow:hidden; background:var(--white); box-shadow:0 2px 12px rgba(18,61,122,0.06); margin-bottom:12px; }}
.ba-col {{ display:flex; flex-direction:column; min-width:0; }}
.ba-header {{ display:flex; align-items:center; gap:8px; padding:10px 18px; font-size:11px; font-weight:700; letter-spacing:0.8px; text-transform:uppercase; border-bottom:1px solid var(--border); }}
.ba-header.before-h {{ background:var(--amber-pale); color:#78350f; border-right:1px solid var(--border); }}
.ba-header.after-h {{ background:var(--navy-pale); color:var(--navy-dark); }}
.ba-dot {{ width:8px; height:8px; border-radius:50%; flex-shrink:0; }}
.ba-dot.before-dot {{ background:#d97706; }}
.ba-dot.after-dot {{ background:var(--navy-mid); }}
.ba-body {{ padding:20px; font-size:13.5px; color:var(--text-body); line-height:1.75; flex:1; min-width:0; }}
.ba-body.before-body {{ background:#fffdf7; border-right:1px solid var(--border); }}
.ba-body.after-body {{ background:#f5faff; }}
.ba-body strong {{ color:var(--text-dark); }}
.ba-body em {{ color:var(--text-muted); font-style:italic; }}
.ba-body p {{ margin-bottom:10px; }}
.ba-body p:last-child {{ margin-bottom:0; }}
.ba-body ul {{ margin:0 0 10px 20px; }}
.ba-body li {{ margin-bottom:4px; }}
.badge-row {{ margin-bottom:12px !important; }}
.conf-row {{ font-size:11.5px; color:var(--text-muted); margin-bottom:12px !important; }}
.verify-line {{ margin-top:14px !important; padding:10px 14px; border-radius:6px; background:var(--navy-pale); border-left:3px solid var(--navy-mid); font-size:13px; }}

/* CODE */
pre {{ background:var(--code-bg); color:var(--code-text); padding:14px 16px; border-radius:var(--radius-sm); font-family:var(--mono); font-size:11.5px; line-height:1.7; overflow-x:auto; margin:10px 0 0; white-space:pre; max-height:380px; overflow-y:auto; }}
pre::-webkit-scrollbar {{ height:6px; width:6px; }}
pre::-webkit-scrollbar-thumb {{ background:#444; border-radius:3px; }}
code {{ background:var(--navy-pale); color:var(--navy-dark); padding:1px 6px; border-radius:4px; font-family:var(--mono); font-size:12px; border:1px solid var(--navy-border); }}
pre code {{ background:none; border:none; color:inherit; padding:0; font-size:inherit; }}
.kw {{ color:#ff79c6; }}
.fn {{ color:#50fa7b; }}
.str {{ color:#a8ff78; }}
.cm {{ color:#6272a4; font-style:italic; }}
.at {{ color:#79c0ff; }}
.va {{ color:#ffb86c; }}
.num {{ color:#fcd34d; }}
.code-with-copy {{ position:relative; margin-top:10px; }}
.copy-btn {{ position:absolute; top:8px; right:8px; background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.18); color:rgba(255,255,255,0.85); font-family:var(--mono); font-size:10px; letter-spacing:0.5px; text-transform:uppercase; padding:4px 8px; border-radius:4px; cursor:pointer; display:inline-flex; align-items:center; gap:4px; transition:all 0.15s; }}
.copy-btn:hover {{ background:rgba(255,255,255,0.12); color:white; }}
.copy-btn.copied {{ background:var(--green); color:white; border-color:var(--green); }}
.copy-btn svg {{ width:12px; height:12px; }}

/* BADGES */
.sev-badge {{ display:inline-block; font-family:var(--mono); font-size:10px; font-weight:700; padding:2px 7px; border-radius:3px; text-transform:uppercase; letter-spacing:0.5px; border:1px solid; margin-right:5px; vertical-align:middle; }}
.sev-critical {{ background:var(--red-pale); color:var(--red); border-color:var(--red-border); }}
.sev-high {{ background:var(--red-pale); color:var(--red); border-color:var(--red-border); }}
.sev-medium {{ background:var(--amber-pale); color:var(--amber); border-color:var(--amber-border); }}
.sev-low {{ background:var(--navy-pale); color:var(--navy-dark); border-color:var(--navy-border); }}
.sev-info {{ background:#f3f4f6; color:#6b7280; border-color:#e5e7eb; }}

.ch-badge {{ display:inline-block; font-family:var(--mono); font-size:10px; font-weight:700; padding:2px 6px; border-radius:3px; letter-spacing:0.3px; border:1px solid; margin-right:4px; vertical-align:middle; }}
.ch-seo {{ background:var(--blue-pale); color:#1e40af; border-color:var(--blue-border); }}
.ch-aeo {{ background:var(--purple-pale); color:var(--purple); border-color:var(--purple-border); }}
.ch-geo {{ background:var(--green-pale); color:var(--green); border-color:var(--green-border); }}

.conf-chip {{ display:inline-block; font-family:var(--mono); font-size:10px; font-weight:700; padding:2px 6px; border-radius:3px; letter-spacing:0.3px; border:1px solid; margin-right:6px; vertical-align:middle; }}
.conf-high {{ background:var(--green-pale); color:var(--green); border-color:var(--green-border); }}
.conf-med  {{ background:var(--amber-pale); color:var(--amber); border-color:var(--amber-border); }}
.conf-low  {{ background:var(--red-pale); color:var(--red); border-color:var(--red-border); }}
.conf-evidence code {{ font-size:10.5px; }}

/* SCORECARD */
.scorecard {{ display:grid; grid-template-columns:repeat(3, 1fr); gap:12px; margin:16px 0; }}
.score-card {{ background:var(--white); border:1px solid var(--border); border-radius:var(--radius-sm); padding:14px 16px; }}
.score-label {{ font-size:10.5px; font-weight:700; text-transform:uppercase; letter-spacing:0.8px; color:var(--text-muted); margin-bottom:6px; }}
.score-value {{ font-family:'Playfair Display', serif; font-size:26px; font-weight:700; line-height:1; color:var(--navy-dark); }}
.score-value.bad {{ color:var(--red); }}
.score-value.good {{ color:var(--green); }}
.score-hint {{ font-size:11.5px; color:var(--text-muted); margin-top:4px; }}

/* CALLOUTS */
.callout {{ display:flex; gap:12px; padding:14px 18px; border-radius:var(--radius-sm); margin:14px 0; font-size:13.5px; line-height:1.65; border:1px solid; }}
.callout strong {{ display:block; margin-bottom:4px; }}
.callout-info {{ background:var(--navy-pale); border-color:var(--navy-border); color:var(--text-body); }}
.callout-warn {{ background:var(--amber-pale); border-color:var(--amber-border); color:#78350f; }}
.callout-good {{ background:var(--green-pale); border-color:var(--green-border); color:#065f46; }}
.callout-icon {{ font-size:18px; line-height:1; flex-shrink:0; }}

/* FOOTER */
.doc-footer {{ background:var(--navy-deep); color:rgba(255,255,255,0.6); padding:18px 40px; font-size:12px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; }}
.doc-footer strong {{ color:white; }}

/* SIGNATURE BAND */
.doc-signature {{ background:linear-gradient(90deg, #050e1f 0%, #0a1f3d 50%, #050e1f 100%); color:rgba(255,255,255,0.85); padding:16px 40px; display:flex; justify-content:center; align-items:center; gap:12px; font-family:'Playfair Display', serif; font-size:12px; letter-spacing:0.3px; border-top:1px solid rgba(96,165,250,0.18); }}
.doc-signature a {{ color:inherit; text-decoration:none; border-bottom:1px dotted rgba(96,165,250,0.4); transition:border-color 0.2s, color 0.2s; }}
.doc-signature a:hover {{ color:var(--navy-accent); border-bottom-color:var(--navy-accent); }}
.doc-signature strong {{ color:var(--navy-accent); font-weight:700; }}
.sig-heart {{ color:var(--navy-accent); font-size:10px; opacity:0.75; }}
.sig-text {{ font-style:italic; }}

/* RESPONSIVE */
@media (max-width: 780px) {{
  .topbar {{ padding:8px 16px; flex-direction:column; text-align:center; }}
  .doc-header {{ padding:24px 20px 20px; }}
  .doc-header h1 {{ font-size:20px; }}
  .meta-grid {{ grid-template-columns:1fr 1fr; }}
  .toc-bar {{ padding:10px 16px; overflow-x:auto; flex-wrap:nowrap; }}
  .toc-link {{ flex-shrink:0; }}
  .content {{ padding:24px 16px 60px; }}
  .ba-grid {{ grid-template-columns:1fr; }}
  .ba-header.before-h {{ border-right:none; border-bottom:1px solid var(--border); }}
  .ba-body.before-body {{ border-right:none; border-bottom:1px solid var(--border); }}
  .doc-footer {{ padding:14px 16px; flex-direction:column; text-align:center; }}
  .scorecard {{ grid-template-columns:1fr; }}
}}
@media print {{
  .topbar, .toc-bar, .doc-footer, .copy-btn {{ display:none !important; }}
  body {{ background:white; }}
  .section, .ba-grid {{ break-inside:avoid; page-break-inside:avoid; }}
}}
</style>
</head>
<body>

<div class="topbar">
  <div><strong>SEO / AEO / GEO Audit Plugin</strong></div>
  <div class="topbar-trust">
    <span>Mode: {mode_label}</span>
    <span>{critical_count} Critical · {high_count} High · {medium_count} Medium</span>
    <span>{total_findings} findings total</span>
  </div>
</div>

<div class="doc-header">
  <div class="header-row">
    <h1>SEO / AEO / GEO Audit<br><span>{project_label}</span></h1>
    <div class="status-badge"><span class="status-dot"></span>Ready for Engineering Review</div>
  </div>
  <div class="meta-grid">
    <div>Target<strong>{target}</strong></div>
    <div>Environment<strong>{env}</strong></div>
    <div>Input<strong>{input_method}</strong></div>
    <div>Date<strong>{audit_date}</strong></div>
    <div>Stack<strong>{stack_label}</strong></div>
    <div>Prepared by<strong>{prepared_by}</strong></div>
  </div>
</div>

<nav class="toc-bar" aria-label="Findings"><span class="toc-label">Jump to</span>{toc_links}</nav>

<div class="audit-progress" id="audit-progress" role="status" aria-label="Audit progress">
  <div class="progress-meta">
    <span class="progress-label">Progress</span>
    <span class="progress-count"><span id="progress-done">0</span> of <span id="progress-total">{total_findings}</span> addressed</span>
    <button type="button" class="progress-reset" id="progress-reset" title="Reset progress">↺ Reset</button>
  </div>
  <div class="progress-track"><div class="progress-fill" id="progress-fill" style="width:0%"></div></div>
</div>

<div class="content">

<div class="section" id="overview">
  <span class="section-eyebrow">What this report covers</span>
  <h2 class="section-h2">Overview</h2>
  <hr class="section-divider">
  <div class="overview-box">{overview_html}</div>
  {scorecard_html}
</div>

{scores_block}

{finding_sections}

{notes_block}

<aside class="rerun-panel" id="rerun-panel" aria-hidden="true">
  <div class="rerun-inner">
    <div class="rerun-badge">🎉</div>
    <h2 class="rerun-heading">All {total_findings} findings addressed</h2>
    <p class="rerun-sub">Great work. Verify with a fresh audit pass — either your team or Claude Code can re-run it.</p>
    <div class="rerun-commands">
      <h3>Re-run options</h3>
      <ol>
        <li>In Claude Code with this plugin installed, paste:<br><code class="rerun-cmd">/full-audit {target}</code></li>
        <li>Or run just the checks you changed:<br><code class="rerun-cmd">/seo-audit {target}</code> &nbsp;·&nbsp; <code class="rerun-cmd">/aeo-audit {target}</code> &nbsp;·&nbsp; <code class="rerun-cmd">/geo-audit {target}</code></li>
        <li>Compare the new report to this one. Findings with <em>Confidence 95+</em> should now show <em>pass</em>. Anything still failing means the fix didn't land or the verification step wasn't run.</li>
      </ol>
    </div>
    <button type="button" class="rerun-reset" id="rerun-reset">Reset my progress on this report</button>
  </div>
</aside>

</div>

<div class="doc-footer">
  <span>{project_label} · SEO / AEO / GEO Audit · {audit_date}</span>
  <span>Mode: <strong>{mode_label}</strong> · Target: <strong>{target}</strong></span>
</div>
<div class="doc-signature">
  <span class="sig-heart">✦</span>
  <span class="sig-text">Crafted with care by <a href="https://www.linkedin.com/in/girisshgk/" rel="author noopener" target="_blank"><strong>Giriish</strong></a> · Father of SEO · <a href="http://t.me/spcgbot" rel="author noopener" target="_blank">For Collaboration</a></span>
  <span class="sig-heart">✦</span>
</div>

<script>
(function () {{
  document.addEventListener('click', (e) => {{
    const btn = e.target.closest('.copy-btn');
    if (!btn) return;
    const wrap = btn.closest('.code-with-copy');
    const pre = wrap && wrap.querySelector('pre');
    if (!pre) return;
    const text = pre.innerText;
    const doCopy = (t) => (navigator.clipboard && navigator.clipboard.writeText(t)) || Promise.reject();
    Promise.resolve(doCopy(text)).then(() => {{
      btn.classList.add('copied');
      const oldHTML = btn.innerHTML;
      btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>Copied';
      setTimeout(() => {{ btn.classList.remove('copied'); btn.innerHTML = oldHTML; }}, 1600);
    }}).catch(() => {{
      const ta = document.createElement('textarea');
      ta.value = text; ta.style.position='fixed'; ta.style.opacity='0';
      document.body.appendChild(ta); ta.select();
      try {{ document.execCommand('copy'); }} catch(_) {{}}
      document.body.removeChild(ta);
    }});
  }});

  // ===== Interactive checklist + re-run panel =====
  var storageKey = 'seo-audit-progress:' + (location.pathname || 'report');
  var checkboxes = Array.prototype.slice.call(document.querySelectorAll('.finding-check'));
  var total = checkboxes.length;
  var progressDone = document.getElementById('progress-done');
  var progressTotal = document.getElementById('progress-total');
  var progressFill = document.getElementById('progress-fill');
  var progressReset = document.getElementById('progress-reset');
  var rerunPanel = document.getElementById('rerun-panel');
  var rerunReset = document.getElementById('rerun-reset');

  function loadState() {{
    try {{ return JSON.parse(localStorage.getItem(storageKey) || '{{}}'); }} catch (e) {{ return {{}}; }}
  }}
  function saveState(s) {{
    try {{ localStorage.setItem(storageKey, JSON.stringify(s)); }} catch (e) {{}}
  }}
  function refresh() {{
    var done = 0;
    checkboxes.forEach(function(cb) {{ if (cb.checked) done += 1; }});
    if (progressDone) progressDone.textContent = done;
    if (progressTotal) progressTotal.textContent = total;
    var pct = total === 0 ? 0 : Math.round((done / total) * 100);
    if (progressFill) {{
      progressFill.style.width = pct + '%';
      progressFill.classList.toggle('complete', done === total && total > 0);
    }}
    if (rerunPanel) {{
      var allDone = total > 0 && done === total;
      rerunPanel.classList.toggle('visible', allDone);
      rerunPanel.setAttribute('aria-hidden', allDone ? 'false' : 'true');
    }}
  }}
  function applyCard(cb) {{
    var card = cb.closest('.finding-card');
    if (card) card.classList.toggle('resolved', cb.checked);
  }}
  // Hydrate from localStorage
  var state = loadState();
  checkboxes.forEach(function(cb) {{
    var id = cb.getAttribute('data-finding-id');
    if (state[id]) {{ cb.checked = true; applyCard(cb); }}
    cb.addEventListener('change', function() {{
      var s = loadState();
      if (cb.checked) s[id] = true; else delete s[id];
      saveState(s);
      applyCard(cb);
      refresh();
    }});
  }});
  function resetAll() {{
    localStorage.removeItem(storageKey);
    checkboxes.forEach(function(cb) {{ cb.checked = false; applyCard(cb); }});
    refresh();
  }}
  if (progressReset) progressReset.addEventListener('click', resetAll);
  if (rerunReset) rerunReset.addEventListener('click', resetAll);
  refresh();
}})();
</script>

</body>
</html>
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def load_input(args):
    if args.stdin:
        return json.load(sys.stdin)
    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            return json.load(f)
    raise SystemExit("Provide --input <file> or --stdin.")


def main():
    parser = argparse.ArgumentParser(description="Generate SEO/AEO/GEO audit reports.")
    parser.add_argument("--input", help="Path to findings JSON file.")
    parser.add_argument("--stdin", action="store_true", help="Read JSON from stdin.")
    parser.add_argument("--output-dir", required=True, help="Directory to write reports.")
    parser.add_argument("--name", help="Base filename (default: seo-audit-<mode>-<date>).")
    args = parser.parse_args()

    data = load_input(args)
    audit = data.get("audit", {})
    mode = audit.get("mode", "seo")
    audit_date = audit.get("date") or date.today().isoformat()

    md = render_markdown(data)
    html = render_html(data)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    base = args.name or f"seo-audit-{mode}-{audit_date}"
    md_path = out_dir / f"{base}.md"
    html_path = out_dir / f"{base}.html"

    md_path.write_text(md, encoding="utf-8")
    html_path.write_text(html, encoding="utf-8")

    print(json.dumps({
        "markdown": str(md_path),
        "html": str(html_path),
        "findings_count": len(data.get("findings", [])),
    }, indent=2))


if __name__ == "__main__":
    main()
