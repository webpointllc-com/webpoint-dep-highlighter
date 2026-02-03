# DEP Highlighter – Requirements and Paths

## Required columns (same as Windows DEP Highlighter)

- **Parcel Number** – column whose header contains "Parcel" and "Number" (e.g. "Parcel Number", "Parcel #").
- **Parcel Notes** or **DEP** – column whose header contains "Parcel" and "Notes", or a column named "DEP". The cell value must be exactly `DEP` (case-insensitive) for duplicate detection.

The first row of the sheet is treated as the header. Consecutive rows with the same Parcel Number and both cells `DEP` in Parcel Notes are highlighted in yellow.

## Supported file types

- `.xlsx`
- `.xlsm`

`.xls` is not supported; save as .xlsx or .xlsm.

## Environment

- **PORT** – set by Render (e.g. 10000). Default 5000 locally.
- **DEBUG** – optional; set to `true` for debug mode.

## Paths (deploy)

- Server script: `dep_highlighter_server.py` (repo root).
- Frontend: `static/dep_highlighter.html`.
- No env file required; Render provides PORT.

## SquareSpace embed

Use this iframe (no change unless the service URL changes):

```html
<iframe src="https://webpoint-dep-highlighter.onrender.com" width="100%" height="920" style="border:none;border-radius:12px;min-height:920px;" title="Webpoint LLC – DEP Highlighter"></iframe>
```

You do **not** need to change the embed on SquareSpace when we update the server; the same URL serves the updated app after Render redeploys.
