#!/bin/bash
# Trigger production deploy and verify live server returns _Highlighted filename.
# One-time: add deploy hook to .env (see below).

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
LIVE_URL="https://webpoint-dep-highlighter.onrender.com"

if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

if [ -z "$RENDER_DEPLOY_HOOK_URL" ]; then
  echo "=== RENDER_DEPLOY_HOOK_URL not set. One-time setup ==="
  echo "1. Open https://dashboard.render.com → webpoint-dep-highlighter → Settings"
  echo "2. Copy the 'Deploy Hook' URL"
  echo "3. Run: echo 'RENDER_DEPLOY_HOOK_URL=paste_url_here' >> $SCRIPT_DIR/.env"
  echo "4. Run this script again: $SCRIPT_DIR/GO_LIVE_NOW.sh"
  echo ""
  echo "Or trigger manually: Render Dashboard → webpoint-dep-highlighter → Manual Deploy"
  exit 1
fi

echo "Triggering Render deploy..."
HTTP=$(curl -sS -o /tmp/render_deploy.txt -w "%{http_code}" -X POST "$RENDER_DEPLOY_HOOK_URL")
if [ "$HTTP" != "200" ] && [ "$HTTP" != "201" ]; then
  echo "Deploy trigger failed: HTTP $HTTP"
  cat /tmp/render_deploy.txt 2>/dev/null
  exit 1
fi
echo "Deploy triggered. Waiting for live server to update (up to 3 min)..."

for i in $(seq 1 18); do
  sleep 10
  DISP=$(curl -sS -D - -o /tmp/live_check.xlsx -F "file=@test_NY_NewYorkCity.xlsx" "$LIVE_URL/process" --max-time 30 2>/dev/null | grep -i content-disposition || true)
  if echo "$DISP" | grep -q "_Highlighted"; then
    echo "LIVE: Server is serving current build (filename contains _Highlighted)."
    exit 0
  fi
done

echo "Server not updated yet. Check Render dashboard for deploy status, or try again in 2 min."
exit 0
