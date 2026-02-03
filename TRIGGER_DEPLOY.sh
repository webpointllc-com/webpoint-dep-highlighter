#!/bin/bash
# Trigger a deploy on Render (latest commit = dark green). Uses deploy hook so no login.
# One-time: get deploy hook URL from Render → webpoint-dep-highlighter → Settings → Deploy Hook.

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

if [ -z "$RENDER_DEPLOY_HOOK_URL" ]; then
  echo "RENDER_DEPLOY_HOOK_URL not set."
  echo ""
  echo "One-time setup:"
  echo "  1. Go to https://dashboard.render.com and log in."
  echo "  2. Open service 'webpoint-dep-highlighter' → Settings."
  echo "  3. Find 'Deploy Hook' → copy the URL (looks like https://api.render.com/deploy/srv-...)."
  echo "  4. Run: echo 'RENDER_DEPLOY_HOOK_URL=paste_url_here' >> $SCRIPT_DIR/.env"
  echo "  5. Run this script again: $SCRIPT_DIR/TRIGGER_DEPLOY.sh"
  echo ""
  exit 1
fi

echo "Triggering deploy on Render (latest commit)..."
HTTP=$(curl -sS -o /tmp/render_deploy_resp.txt -w "%{http_code}" -X POST "$RENDER_DEPLOY_HOOK_URL")
if [ "$HTTP" = "200" ] || [ "$HTTP" = "201" ]; then
  echo "Deploy triggered (HTTP $HTTP). Wait 1–2 min then check https://webpoint-dep-highlighter.onrender.com"
else
  echo "Unexpected response HTTP $HTTP. Check /tmp/render_deploy_resp.txt"
  cat /tmp/render_deploy_resp.txt 2>/dev/null || true
  exit 1
fi
