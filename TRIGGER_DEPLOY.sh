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

if [ -n "$RENDER_DEPLOY_HOOK_URL" ]; then
  echo "Triggering deploy on Render (deploy hook)..."
  HTTP=$(curl -sS -o /tmp/render_deploy_resp.txt -w "%{http_code}" -X POST "$RENDER_DEPLOY_HOOK_URL")
elif [ -n "$RENDER_API_KEY" ]; then
  SVC_ID="${RENDER_SERVICE_ID:-srv-d616lm2li9vc73fqqps0}"
  echo "Triggering deploy on Render (API)..."
  HTTP=$(curl -sS -o /tmp/render_deploy_resp.txt -w "%{http_code}" \
    -X POST "https://api.render.com/v1/services/$SVC_ID/deploys" \
    -H "Authorization: Bearer $RENDER_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{}')
else
  echo "RENDER_DEPLOY_HOOK_URL or RENDER_API_KEY not set."
  echo ""
  echo "One-time setup: add to $SCRIPT_DIR/.env either:"
  echo "  (A) RENDER_DEPLOY_HOOK_URL=https://api.render.com/deploy/srv-...?key=..."
  echo "      from Render → webpoint-dep-highlighter → Settings → Deploy Hook"
  echo "  (B) RENDER_API_KEY=your_key and RENDER_SERVICE_ID=srv-d616lm2li9vc73fqqps0"
  echo ""
  exit 1
fi

if [ "$HTTP" = "200" ] || [ "$HTTP" = "201" ]; then
  echo "Deploy triggered (HTTP $HTTP). Wait 1–2 min then check https://webpoint-dep-highlighter.onrender.com"
else
  echo "Unexpected response HTTP $HTTP. Check /tmp/render_deploy_resp.txt"
  cat /tmp/render_deploy_resp.txt 2>/dev/null || true
  exit 1
fi
