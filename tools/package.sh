#!/usr/bin/env bash
# Builds dist/seo-aeo-geo-audit.zip for upload to Claude (Settings > Capabilities > Skills).
# The zip must contain the skill folder at its root.
set -euo pipefail
cd "$(dirname "$0")/.."
NAME=seo-aeo-geo-audit
mkdir -p dist
rm -f "dist/$NAME.zip"
find "skills/$NAME" -name '__pycache__' -prune -o -name '*.pyc' -prune -o -type f -print \
  | sed "s#^skills/##" | (cd skills && zip -q "../dist/$NAME.zip" -@)
unzip -l "dist/$NAME.zip" | tail -1
