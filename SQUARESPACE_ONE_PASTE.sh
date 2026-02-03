#!/bin/bash
# ONE script: paste your deploy URL → clipboard gets the iframe → paste into SquareSpace Code block. Done.

set -e
cd "$(dirname "${BASH_SOURCE[0]}")"

echo ""
echo "DEP Highlighter → SquareSpace one-paste"
echo "────────────────────────────────────────"
echo "Paste your deploy URL (from Render or Railway), then press Enter:"
echo "  Example: https://webpoint-dep-highlighter.onrender.com"
echo ""
read -r URL
URL="${URL//[[:space:]]/}"
URL="${URL%/}"

if [ -z "$URL" ]; then
  echo "No URL. Exiting."
  exit 1
fi

IFRAME="<iframe src=\"$URL\" width=\"100%\" height=\"920\" style=\"border:none;border-radius:12px;min-height:920px;\" title=\"Webpoint LLC – DEP Highlighter\"></iframe>"
printf '%s\n' "$IFRAME" | pbcopy
echo "$IFRAME" > "FINAL_SQUARESPACE_EMBED.html"

echo ""
echo "Done. Clipboard has the embed."
echo "→ Go to webpointllc.com/webpoint-toolbox → Edit → Add block → Code → Cmd+V → Publish."
echo ""
