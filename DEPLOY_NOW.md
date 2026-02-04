# Make the live server use the latest code (one-time or when you need a deploy)

The app at **https://webpoint-dep-highlighter.onrender.com** only updates when Render runs a new deploy. Code is already pushed to `main`; you just need to trigger a deploy.

## Option A – Deploy hook (recommended; then every push = auto deploy)

1. **Get the deploy hook URL**
   - Go to https://dashboard.render.com → open service **webpoint-dep-highlighter** → **Settings**.
   - Find **Deploy Hook** → copy the URL (e.g. `https://api.render.com/deploy/srv-xxx?key=xxx`).

2. **Add it in GitHub**
   - Repo **webpoint-dep-highlighter** → **Settings** → **Secrets and variables** → **Actions**.
   - **New repository secret** → Name: `RENDER_DEPLOY_HOOK_URL`, Value: paste the URL → Save.

3. **Trigger a deploy now**
   - Same repo → **Actions** → workflow **"Deploy to production (live)"** → **Run workflow** → **Run workflow**.
   - Wait 1–2 minutes. The live server will then run the latest code from `main`.

After this, every **push to main** will trigger a deploy automatically.

## Option B – Manual deploy on Render

1. Go to https://dashboard.render.com → **webpoint-dep-highlighter**.
2. Click **Manual Deploy** → **Deploy latest commit** (or **Clear build cache & deploy** if needed).
3. Wait until the deploy shows **Live**.

---

**Check it’s live:** Upload your NY RDM file at https://webpoint-dep-highlighter.onrender.com. If it processes (no “Parcel Number and DEP” error), the new code is live.
