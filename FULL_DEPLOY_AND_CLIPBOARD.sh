#!/bin/bash
# Full deploy: GitHub (auth + create repo + push) → Railway → final HTML in clipboard.
# Run from: Toolbox/deploy. Approve when prompted.

set -e
DEPLOY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DEPLOY_DIR"

REPO_NAME="webpoint-dep-highlighter"
REPO_DESC="DEP Highlighter – Webpoint Toolbox. Clone Excel, highlight duplicate DEP parcels, preserve VBA/macros. Deploy to Railway/Render."
RAILWAY_URL_FILE="$DEPLOY_DIR/.railway_url"

echo "═══════════════════════════════════════════════════════════════"
echo "  FULL DEPLOY: GitHub → Railway → SquareSpace HTML → Clipboard"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# ─── 1. GitHub auth ─────────────────────────────────────────────────
echo "[1/5] GitHub auth..."
if ! gh auth status &>/dev/null; then
  echo "      Opening GitHub device login. Approve in browser, then press Enter here."
  gh auth login -h github.com -p https -w
fi
echo "      OK – GitHub authenticated."
echo ""

# ─── 2. Create repo and push (if not already) ───────────────────────
echo "[2/5] GitHub repo: $REPO_NAME..."
if git remote get-url origin &>/dev/null; then
  echo "      Remote origin already set. Pushing..."
  git push -u origin main
else
  echo "      Creating repo and pushing..."
  gh repo create "$REPO_NAME" --public --source=. --remote=origin --push --description "$REPO_DESC"
fi
echo "      OK – Code is on GitHub."
echo ""

# ─── 3. Railway ─────────────────────────────────────────────────────
echo "[3/5] Railway deploy..."
echo "      Opening Railway. You: New Project → Deploy from GitHub repo → select $REPO_NAME"
echo "      After deploy: Settings → Networking → Generate Domain → copy the URL."
open "https://railway.app/new"
echo ""
echo "      Paste your Railway URL here (e.g. https://webpoint-dep-highlighter-production-xxxx.up.railway.app) then press Enter:"
read -r RAILWAY_URL
RAILWAY_URL="${RAILWAY_URL// }"
if [ -z "$RAILWAY_URL" ]; then
  echo "      No URL entered. Using placeholder – replace YOUR_RAILWAY_URL in the generated HTML."
  RAILWAY_URL="YOUR_RAILWAY_URL"
fi
echo "$RAILWAY_URL" > "$RAILWAY_URL_FILE"
echo "      OK – URL saved."
echo ""

# ─── 4. Generate final HTML (server call ready) ──────────────────────
echo "[4/5] Generating final SquareSpace embed HTML (server call ready)..."
FINAL_HTML="<iframe src=\"$RAILWAY_URL\" width=\"100%\" height=\"920\" style=\"border:none;border-radius:12px;min-height:920px;\" title=\"Webpoint LLC – DEP Highlighter\"></iframe>"
EMBED_FILE="$DEPLOY_DIR/FINAL_SQUARESPACE_EMBED.html"
printf '%s\n' "$FINAL_HTML" > "$EMBED_FILE"
echo "      Written to: $EMBED_FILE"
echo ""

# ─── 5. Clipboard ───────────────────────────────────────────────────
echo "[5/5] Copying HTML to clipboard..."
printf '%s\n' "$FINAL_HTML" | pbcopy
echo "      OK – HTML is in your clipboard."
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  DONE. Paste (Cmd+V) into SquareSpace Code block on"
echo "  webpointllc.com/webpoint-toolbox and publish."
echo "═══════════════════════════════════════════════════════════════"
