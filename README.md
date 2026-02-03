# Webpoint LLC – DEP Highlighter

Backend + frontend in one deploy. Serves the DEP Highlighter UI at `/` and the process API at `/process`.

**Deploy to Railway or Render** – see parent `GO_ONLINE.md` for steps.

- **Health:** `GET /health`
- **UI:** `GET /`
- **Process:** `POST /process` (form field: `file`, Excel .xlsx/.xlsm/.xls)
