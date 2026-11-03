#!/usr/bin/env bash
# Builds one zip per skill in dist/ for upload to Claude (Settings > Capabilities > Skills).
# Each zip contains its skill folder at the root.
# technical-seo-audit works alone, but borrows stack profiles, the report generator and the
# PageSpeed runner from seo-aeo-geo-audit when that skill is installed too.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p dist
for NAME in seo-aeo-geo-audit technical-seo-audit; do
  rm -f "dist/$NAME.zip"
  find "skills/$NAME" -name '__pycache__' -prune -o -name '*.pyc' -prune -o -type f -print \
    | sed "s#^skills/##" | (cd skills && zip -q "../dist/$NAME.zip" -@)
  echo "$NAME:"; unzip -l "dist/$NAME.zip" | tail -1
done
