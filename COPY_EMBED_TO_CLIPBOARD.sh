#!/bin/bash
# Usage: ./COPY_EMBED_TO_CLIPBOARD.sh "https://your-app.up.railway.app"
# Puts SquareSpace iframe HTML in clipboard. No trailing slash on URL.

URL="${1:-}"
if [ -z "$URL" ]; then
  echo "Usage: ./COPY_EMBED_TO_CLIPBOARD.sh \"https://your-app.up.railway.app\""
  exit 1
fi
URL="${URL%/}"
HTML="<iframe src=\"$URL\" width=\"100%\" height=\"920\" style=\"border:none;border-radius:12px;min-height:920px;\" title=\"Webpoint LLC – DEP Highlighter\"></iframe>"
echo "$HTML" | pbcopy
echo "Copied to clipboard. Paste (Cmd+V) into SquareSpace Code block on webpointllc.com/webpoint-toolbox"
