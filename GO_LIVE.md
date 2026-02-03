# Make DEP Highlighter Real Active and Live

## One command (Mac)

```bash
cd "/Users/billmccreary/Desktop/Webpoint_ Workspace/Toolbox/deploy"
chmod +x MAKE_LIVE.sh TRIGGER_DEPLOY.sh
./MAKE_LIVE.sh
```

This will:
1. **Wake** the Render service (so the first visitor isn’t waiting on cold start).
2. **Copy** the SquareSpace embed to your clipboard.
3. **Trigger deploy** on Render (if you’ve set the deploy hook once) so the latest commit (e.g. dark green) goes live.

### One-time: enable one-click deploy (deploy hook)

So `MAKE_LIVE.sh` can trigger the deploy without opening the dashboard:

1. Go to **[dashboard.render.com](https://dashboard.render.com)** and log in.
2. Open the **webpoint-dep-highlighter** service.
3. Go to **Settings** → scroll to **Deploy Hook**.
4. Copy the deploy hook URL (looks like `https://api.render.com/deploy/srv-...?key=...`).
5. In terminal:
   ```bash
   cd "/Users/billmccreary/Desktop/Webpoint_ Workspace/Toolbox/deploy"
   echo 'RENDER_DEPLOY_HOOK_URL=paste_your_url_here' >> .env
   ```
6. Next time you run `./MAKE_LIVE.sh` it will trigger the deploy automatically.

## Manual steps

### 1. Get latest code live on Render

- Go to **[dashboard.render.com](https://dashboard.render.com)**.
- Open the **webpoint-dep-highlighter** service.
- Click **Manual Deploy** → **Deploy latest commit**.
- Wait until the deploy shows **Live** (usually 1–2 minutes).

### 2. Embed on SquareSpace (if not already)

- Go to **webpointllc.com** → edit the **Webpoint Toolbox** page.
- Add a **Code** block.
- Paste (Cmd+V) the iframe (already in clipboard after running `MAKE_LIVE.sh`).
- Save and **Publish**.

### 3. Live URLs

| What | URL |
|------|-----|
| App (Render) | https://webpoint-dep-highlighter.onrender.com |
| Public page | https://webpointllc.com/webpoint-toolbox |

The app is **active** once Render has deployed and the service has been woken (e.g. by visiting the URL or running `MAKE_LIVE.sh`). It stays **live** as long as the Render service is running and the SquareSpace page has the embed.
