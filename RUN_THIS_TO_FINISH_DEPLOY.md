# Run this to finish full deploy → HTML in clipboard

Do this **in Terminal** (one time). Approve when prompted.

## 1. Open Terminal and run

```bash
cd "/Users/billmccreary/Desktop/Webpoint_ Workspace/Toolbox/deploy"
./FULL_DEPLOY_AND_CLIPBOARD.sh
```

## 2. When you see the GitHub device code

- Copy the one-time code (e.g. `14FC-4136`).
- Open the URL shown (https://github.com/login/device).
- Paste the code and approve.
- Back in Terminal, press **Enter**.

## 3. Repo is created and pushed

Script will create `webpoint-dep-highlighter` on GitHub (if needed) and push. Railway will open in your browser.

## 4. Deploy on Railway

- **New Project** → **Deploy from GitHub repo**.
- Select **webpoint-dep-highlighter**.
- After deploy: **Settings** → **Networking** → **Generate Domain**.
- Copy the URL (e.g. `https://webpoint-dep-highlighter-production-xxxx.up.railway.app`).

## 5. Paste URL when the script asks

Back in Terminal, when it says “Paste your Railway URL here”, paste the URL and press **Enter**.

## 6. Done

The script will write **FINAL_SQUARESPACE_EMBED.html** (with your real server URL) and **copy that HTML to your clipboard**.  

Paste (**Cmd+V**) into the SquareSpace **Code** block on **webpointllc.com/webpoint-toolbox** and publish.

---

## If you already have the Railway URL

Just put the embed HTML in the clipboard:

```bash
cd "/Users/billmccreary/Desktop/Webpoint_ Workspace/Toolbox/deploy"
./COPY_EMBED_TO_CLIPBOARD.sh "https://your-app.up.railway.app"
```

Then paste (Cmd+V) into SquareSpace.
