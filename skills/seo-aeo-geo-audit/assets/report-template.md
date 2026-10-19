# SEO / AEO / GEO Audit — {{MODE_LABEL}}

**Target:** {{TARGET}}
**Date:** {{DATE}}
**Environment:** {{ENVIRONMENT}}
**Input method:** {{INPUT_METHOD}}

## Summary

- Checks run: **{{TOTAL_CHECKS}}**
- Passed: **{{PASSED}}**
- Warnings: **{{WARNED}}**
- Failures: **{{FAILED}}**

### Findings by severity

| Severity | Count |
|---|---|
| Critical | {{COUNT_CRITICAL}} |
| High | {{COUNT_HIGH}} |
| Medium | {{COUNT_MEDIUM}} |
| Low | {{COUNT_LOW}} |
| Info | {{COUNT_INFO}} |

{{NOTES_SECTION}}

---

## Findings

{{FINDINGS}}

<!--
Per-finding template:

### N. [SEVERITY] Title

**ID:** `SEO-001`
**Pillars:** SEO | AEO | GEO
**Category:** Technical
**Location:** `head > meta[name=robots]`

**Summary**
One or two sentences.

**Why it's flagged**
Standards reference.

**Impact if ignored**
- **SEO:** ...
- **AEO:** ...
- **GEO:** ...

**Benefits if fixed**
- Bullet 1
- Bullet 2

**Broken code**
```html
<!-- broken -->
```

**Fixed code**
```html
<!-- fixed -->
```

**How to verify the fix**
Concrete step.

---
-->
