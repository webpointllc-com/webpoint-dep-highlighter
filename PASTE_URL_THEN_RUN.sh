#!/bin/bash
# After Render/Railway deploy: paste your service URL when prompted. Script puts final SquareSpace embed in clipboard.
# Example URL: https://webpoint-dep-highlighter.onrender.com  or  https://webpoint-dep-highlighter-production-xxxx.up.railway.app

DEPLOY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DEPLOY_DIR"

echo "Paste your deploy URL (e.g. https://webpoint-dep-highlighter.onrender.com) then press Enter:"
read -r URL
URL="${URL//[[:space:]]/}"
URL="${URL%/}"

if [ -z "$URL" ]; then
  echo "No URL. Exiting."
  exit 1
fi

HTML="<iframe src=\"$URL\" width=\"100%\" height=\"920\" style=\"border:none;border-radius:12px;min-height:920px;\" title=\"Webpoint LLC – DEP Highlighter\"></iframe>"
printf '%s\n' "$HTML" | pbcopy
echo "$HTML" > "$DEPLOY_DIR/FINAL_SQUARESPACE_EMBED.html"

echo ""
echo "Done. Final embed is in your clipboard and in FINAL_SQUARESPACE_EMBED.html"
echo "Paste (Cmd+V) into SquareSpace Code block on webpointllc.com/webpoint-toolbox → Publish."
