#!/bin/bash
cd "/Users/billmccreary/Desktop/Webpoint_ Workspace/Toolbox/deploy"
echo "Step 1: Approve in browser (use code shown below), then press ENTER here."
gh auth login -h github.com -p https -w
echo "Step 2: Pushing..."
git push -u origin main
echo "Done. If push succeeded, reply 'posted'."
