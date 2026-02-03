#!/bin/bash
# Push deploy package to GitHub. Run this once after you create the repo.
# Usage: ./DEPLOY_PUSH.sh https://github.com/YOUR_USERNAME/webpoint-dep-highlighter

set -e
REPO_URL="${1:-}"

if [ -z "$REPO_URL" ]; then
  echo "Usage: ./DEPLOY_PUSH.sh <repo-url>"
  echo "Example: ./DEPLOY_PUSH.sh https://github.com/yourusername/webpoint-dep-highlighter"
  echo ""
  echo "Create the repo first: https://github.com/new?name=webpoint-dep-highlighter"
  exit 1
fi

cd "$(dirname "$0")"
if git remote get-url origin 2>/dev/null; then
  git remote set-url origin "$REPO_URL"
else
  git remote add origin "$REPO_URL"
fi
git branch -M main
git push -u origin main
echo ""
echo "Done. Next: Railway.app → New Project → Deploy from GitHub repo → select webpoint-dep-highlighter → Generate Domain → copy URL → paste in SquareSpace Code block iframe."
