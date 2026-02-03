# Webpoint LLC – DEP Highlighter

Push to `main` → GitHub Action triggers Render deploy → live worldwide.

**Clone Excel workbooks, highlight consecutive duplicate DEP parcels in yellow. VBA, macros, formulas, and structure preserved. Output: `filename_WEBPT.processed.xlsx`.**

Backend + frontend in one deploy. Serves the DEP Highlighter UI at `/` and the process API at `/process`. CORS allows **webpointllc.com** and **www.webpointllc.com** so the tool can be embedded on **webpointllc.com/webpoint-toolbox**.

---

## What it does

- **Input:** Excel file (.xlsx, .xlsm, .xls) with **Parcel Number** and **DEP** columns.
- **Logic:** For each pair of consecutive rows: if they share the same Parcel Number and both have "DEP" in the DEP column, both rows are highlighted yellow.
- **Output:** Cloned file with only yellow highlighting added; all VBA, macros, formulas, charts, images, and hidden code preserved.
- **Filename:** `originalname_WEBPT.processed.xlsx` (or same extension as upload).

---

## Deploy (push = live worldwide)

**We deploy to production on every push to `main`.** No local-only by default; full permission to push and make changes live.

1. **Push this repo** to GitHub. If **RENDER_DEPLOY_HOOK_URL** is set in this repo’s **Settings → Secrets and variables → Actions**, the GitHub Action (`.github/workflows/deploy-live.yml`) triggers a Render deploy automatically. Otherwise trigger manually: run `./TRIGGER_DEPLOY.sh` (with deploy hook in `.env`) or use Render Dashboard → Manual Deploy.
2. **One-time secret (optional but recommended):** Render Dashboard → webpoint-dep-highlighter → Settings → Deploy Hook → copy URL. In GitHub: repo **Settings → Secrets and variables → Actions → New repository secret** → name `RENDER_DEPLOY_HOOK_URL`, value = paste URL. After that, every push to `main` deploys to production.
3. **Railway (alternative):** [railway.app](https://railway.app) → New Project → Deploy from GitHub repo → select this repo → Settings → Networking → **Generate Domain** → copy URL.
4. **Render (manual):** [render.com](https://render.com) → New Web Service → connect this repo → Build: `pip install -r requirements.txt` → Start: `gunicorn -w 1 -b 0.0.0.0:$PORT --timeout 120 dep_highlighter_server:app` → Deploy.
5. **Embed on SquareSpace (webpoint-toolbox):** Add a Code block, paste:
   ```html
   <iframe src="YOUR-DEPLOY-URL" width="100%" height="920" style="border:none;border-radius:12px;min-height:920px;" title="Webpoint LLC – DEP Highlighter"></iframe>
   ```
   Replace `YOUR-DEPLOY-URL` with your Railway or Render URL.

---

## API

| Endpoint    | Method | Description |
|------------|--------|-------------|
| `/`        | GET    | Serves the DEP Highlighter UI (HTML). |
| `/health`  | GET    | Health check. Returns `{"status":"healthy",...}`. |
| `/process` | POST   | Upload Excel file (form field `file`). Returns processed file as download. |

**Allowed origins (CORS):** `https://webpointllc.com`, `https://www.webpointllc.com`, and localhost for development.

---

## Local run

```bash
pip install -r requirements.txt
python dep_highlighter_server.py
```

Default port 5000 (or set `PORT`). Open `http://localhost:5000/` for the UI.

---

## License

Proprietary – Webpoint LLC.
