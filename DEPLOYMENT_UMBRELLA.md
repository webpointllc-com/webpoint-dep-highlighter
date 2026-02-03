# Full-process deployment umbrella — DEP Highlighter → Render → SquareSpace

Single end-to-end process. Use **Chrome** (browserhead best for Deepshake). Accounts are saved logins; opening the site auto-logs in.

---

## 1. Open Chrome and go to Render Blueprint

- Use Chrome (browserhead if available).
- Navigate to:  
  **https://dashboard.render.com/blueprint/new?repo=https://github.com/webpointllc-com/webpoint-dep-highlighter**
- Session auto-logs in (saved logins). If you land on login, wait for redirect or re-open the URL.

---

## 2. Complete Blueprint deploy (accessibility + Deepshake)

- **browser_tabs** (list) → **browser_lock** on the Render tab.
- **browser_snapshot** (interactive: true) → get element refs.
- **Blueprint Name:** Fill the "Blueprint Name" field with: `webpoint-dep-highlighter` (use ref from snapshot).
- **Deploy:** Click "Deploy Blueprint" (use ref from snapshot).
- **Wait:** Use **browser_wait_for** (e.g. 2–3s) and **browser_snapshot** until the service shows **Live** (or equivalent) and the service URL is visible.

---

## 3. Get service URL and put embed in clipboard

- From the snapshot or page, read the service URL (e.g. `https://webpoint-dep-highlighter.onrender.com`).
- If URL is available in the page, use it; otherwise run the paste script and have the user paste once.

**Option A — Agent has URL:**  
Generate embed and copy to clipboard:

```bash
URL="https://webpoint-dep-highlighter.onrender.com"   # use actual URL from page
HTML="<iframe src=\"$URL\" width=\"100%\" height=\"920\" style=\"border:none;border-radius:12px;min-height:920px;\" title=\"Webpoint LLC – DEP Highlighter\"></iframe>"
printf '%s\n' "$HTML" | pbcopy
```

**Option B — User pastes URL:**  
Run:

```bash
cd "/Users/billmccreary/Desktop/Webpoint_ Workspace/Toolbox/deploy" && ./PASTE_URL_THEN_RUN.sh
```

User pastes the service URL when prompted → clipboard gets the embed.

- Save the same HTML to `FINAL_SQUARESPACE_EMBED.html` in the deploy folder (PASTE_URL_THEN_RUN.sh does this).

---

## 4. SquareSpace (final step)

- Go to **webpointllc.com** → **Webpoint Toolbox** → **Edit**.
- **Add block** → **Code**.
- Paste (Cmd+V) the embed from clipboard.
- **Publish.**

---

## One-shot launcher (optional)

Run this to open Chrome to the Blueprint page and then follow this doc for the rest:

```bash
open -a "Google Chrome" "https://dashboard.render.com/blueprint/new?repo=https://github.com/webpointllc-com/webpoint-dep-highlighter"
```

Then the agent completes: snapshot → fill → Deploy Blueprint → wait for Live → get URL → embed → clipboard → SquareSpace instructions.
