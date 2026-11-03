#!/usr/bin/env bash
# Builds one zip per skill in dist/ for upload to Claude (Settings > Capabilities > Skills).
# Each zip contains its skill folder at the root.
# technical-seo-audit works alone (it bundles the PageSpeed runner and the browser-access
# fallback), but borrows stack profiles and the report generator from seo-aeo-geo-audit
# when that skill is installed too.
set -euo pipefail
cd "$(dirname "$0")/.."

# These files ship in BOTH skills and must stay identical.
for f in scripts/pagespeed.py references/pagespeed.md references/browser-access.md; do
  if ! cmp -s "skills/seo-aeo-geo-audit/$f" "skills/technical-seo-audit/$f"; then
    echo "ERROR: $f differs between skills/seo-aeo-geo-audit and skills/technical-seo-audit. Sync them first." >&2
    exit 1
  fi
done

mkdir -p dist
for NAME in seo-aeo-geo-audit technical-seo-audit; do
  rm -f "dist/$NAME.zip"
  find "skills/$NAME" -name '__pycache__' -prune -o -name '*.pyc' -prune -o -type f -print \
    | sed "s#^skills/##" | (cd skills && zip -q "../dist/$NAME.zip" -@)
  echo "$NAME:"; unzip -l "dist/$NAME.zip" | tail -1
done
