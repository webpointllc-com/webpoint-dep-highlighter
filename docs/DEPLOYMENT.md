# DEP Highlighter – Deployment

## Repo description (for GitHub)

Use this as the **Description** when creating or editing the repo on GitHub:

**Short:**  
`DEP Highlighter – Webpoint Toolbox. Clone Excel, highlight duplicate DEP parcels, preserve VBA/macros. Deploy to Railway/Render.`

**Long (optional):**  
`Backend + frontend for Webpoint LLC DEP Highlighter. Processes Excel files: highlights consecutive duplicate DEP parcels in yellow while preserving VBA, macros, formulas, and structure. Serves UI at / and API at /process. CORS set for webpointllc.com.`

---

## What’s in this repo

| Path | Purpose |
|------|--------|
| `dep_highlighter_server.py` | Flask app: serves `/`, `/health`, `/process`; CORS for webpointllc.com. |
| `static/dep_highlighter.html` | Webpoint-styled UI (drop zone, process, download). |
| `requirements.txt` | flask, flask-cors, openpyxl, gunicorn. |
| `Procfile` | For Railway/Heroku: gunicorn. |
| `runtime.txt` | Python 3.11. |
| `README.md` | Description, usage, API, deploy steps. |
| `docs/DEPLOYMENT.md` | This file; repo description and deploy notes. |

---

## Railway (recommended)

1. railway.app → New Project → Deploy from GitHub repo.
2. Select this repository.
3. Railway detects Python and uses Procfile.
4. Settings → Networking → Generate Domain.
5. Copy the public URL for the SquareSpace iframe.

---

## Render

1. render.com → New → Web Service.
2. Connect this GitHub repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn -w 1 -b 0.0.0.0:$PORT --timeout 120 dep_highlighter_server:app`
5. Deploy; use the generated URL in the iframe.

---

## SquareSpace (webpointllc.com/webpoint-toolbox)

1. Edit the Webpoint Toolbox page.
2. Add block → Code.
3. Paste (replace with your deploy URL):

```html
<iframe src="https://YOUR-RAILWAY-OR-RENDER-URL" width="100%" height="920" style="border:none;border-radius:12px;min-height:920px;" title="Webpoint LLC – DEP Highlighter"></iframe>
```

4. Save and publish. Visitors to webpointllc.com/webpoint-toolbox can use the tool; the server allows requests from webpointllc.com (CORS).
