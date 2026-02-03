#!/bin/bash
# Make DEP Highlighter real active and live:
# 1. Wake Render service (ping)
# 2. Copy SquareSpace embed to clipboard
# 3. Open Render dashboard for Manual Deploy (latest commit = dark green)

set -e
DEPLOY_URL="https://webpoint-dep-highlighter.onrender.com"
RENDER_DASH="https://dashboard.render.com"

echo "Making DEP Highlighter active and live..."
echo ""

# Wake the service (Render free tier spins down when idle)
echo "[1/3] Waking Render service..."
curl -sS -o /dev/null -w "    → %{http_code} %{url_effective}\n" "$DEPLOY_URL" || true
echo ""

# Copy embed to clipboard for SquareSpace
echo "[2/3] Copying SquareSpace embed to clipboard..."
IFRAME="<iframe src=\"$DEPLOY_URL\" width=\"100%\" height=\"920\" style=\"border:none;border-radius:12px;min-height:920px;\" title=\"Webpoint LLC – DEP Highlighter\"></iframe>"
printf '%s\n' "$IFRAME" | pbcopy
echo "$IFRAME" > "$(dirname "$0")/FINAL_SQUARESPACE_EMBED.html"
echo "    → Embed in clipboard and in FINAL_SQUARESPACE_EMBED.html"
echo ""

# Trigger deploy if deploy hook is set (real one-click live)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$SCRIPT_DIR/.env" ]; then
  set -a
  source "$SCRIPT_DIR/.env" 2>/dev/null || true
  set +a
fi
if [ -n "$RENDER_DEPLOY_HOOK_URL" ]; then
  echo "[3/3] Triggering deploy on Render..."
  "$SCRIPT_DIR/TRIGGER_DEPLOY.sh" 2>/dev/null && echo "    → Deploy triggered. Wait 1–2 min for live." || true
else
  echo "[3/3] Opening Render dashboard (set RENDER_DEPLOY_HOOK_URL in .env for one-click deploy)..."
  open "$RENDER_DASH" 2>/dev/null || true
  echo "    → Log in → webpoint-dep-highlighter → Manual Deploy, or add deploy hook to .env (see .env.example)"
fi
echo ""

echo "Done. Next:"
echo "  • SquareSpace: webpointllc.com/webpoint-toolbox → Edit → Code block → Cmd+V → Publish."
echo "  • Live app: $DEPLOY_URL"
echo "  • Public page: https://webpointllc.com/webpoint-toolbox"
