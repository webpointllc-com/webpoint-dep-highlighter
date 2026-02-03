#!/bin/bash
# Full-process deployment umbrella: open Chrome to Render Blueprint (saved logins = auto-login),
# then agent completes deploy via accessibility/Deepshake; when live, paste URL here for embed → clipboard.
# Use Chrome (browserhead best for Deepshake). See DEPLOYMENT_UMBRELLA.md for full process.

DEPLOY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DEPLOY_DIR"

echo "=== DEP Highlighter — Full deployment umbrella ==="
echo ""
echo "1. Opening Chrome to Render Blueprint (saved logins = auto-login)..."
open -a "Google Chrome" "https://dashboard.render.com/blueprint/new?repo=https://github.com/webpointllc-com/webpoint-dep-highlighter"
echo ""
echo "2. Agent will: snapshot → fill Blueprint name → Deploy Blueprint → wait for Live → get URL."
echo "   When deploy is Live, copy the service URL from Render."
echo ""
echo "3. Paste the service URL below (or run ./PASTE_URL_THEN_RUN.sh in another terminal):"
read -r URL
URL="${URL//[[:space:]]/}"
URL="${URL%/}"

if [ -z "$URL" ]; then
  echo "No URL. Run ./PASTE_URL_THEN_RUN.sh when ready and paste the URL there."
  exit 0
fi

HTML="<iframe src=\"$URL\" width=\"100%\" height=\"920\" style=\"border:none;border-radius:12px;min-height:920px;\" title=\"Webpoint LLC – DEP Highlighter\"></iframe>"
printf '%s\n' "$HTML" | pbcopy
echo "$HTML" > "$DEPLOY_DIR/FINAL_SQUARESPACE_EMBED.html"
echo ""
echo "Done. Embed is in clipboard and in FINAL_SQUARESPACE_EMBED.html"
echo "→ SquareSpace: webpointllc.com → Webpoint Toolbox → Edit → Add block → Code → Cmd+V → Publish."
