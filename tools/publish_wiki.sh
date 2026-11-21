#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WIKI_URL="https://github.com/MuXue1230-owo/CPN.wiki.git"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
git clone "$WIKI_URL" "$TMP/wiki"
python3 "$ROOT/tools/build_wiki.py" "$TMP/wiki"
git -C "$TMP/wiki" add -A -- '*.md'
if git -C "$TMP/wiki" diff --cached --quiet; then
    echo "Wiki already up to date."
    exit 0
fi
git -C "$TMP/wiki" commit -m "docs: publish CPN26 wiki with 32 normative chapters"
git -C "$TMP/wiki" push origin HEAD
echo "Published to https://github.com/MuXue1230-owo/CPN/wiki"
