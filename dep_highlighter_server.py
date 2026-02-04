#!/usr/bin/env python3
"""
DEP Highlighter Backend Server
Same logic as working Windows app: Parcel Notes + Parcel Number, consecutive DEP rows highlighted.
All processing runs on the server; the browser only uploads the file and downloads the result.
User device (Mac, Windows, etc.) does not affect processing — only the server does the work.
Deploy: push -> GitHub Action -> Render deploy hook -> live.
"""

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import pandas as pd
import openpyxl
from openpyxl.styles import PatternFill
import io
import os
import tempfile
from pathlib import Path
import traceback
from datetime import datetime

app = Flask(__name__, static_folder=None)

CORS_ORIGINS = [
    "https://webpointllc.com",
    "https://www.webpointllc.com",
    "http://localhost:5000",
    "http://localhost:5001",
    "http://127.0.0.1:5000",
    "http://127.0.0.1:5001",
]
CORS(app, origins=CORS_ORIGINS, supports_credentials=False)

_BASE = Path(__file__).resolve().parent
_FRONTEND_HTML = _BASE / "static" / "dep_highlighter.html"
if not _FRONTEND_HTML.exists():
    _FRONTEND_HTML = _BASE.parent / "frontend" / "dep_highlighter.html"

YELLOW_FILL = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")


def _find_dep_and_parcel_columns(df):
    """Find column that can contain 'DEP' (notes/dep col) and parcel identifier column. Works with NY RDM (Tax ID, Bill ID)."""
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    parcel_notes_col = None
    parcel_col = None
    # DEP column: Parcel Notes, DEP, Bill ID, Bill Type, Activity, Action (any col where value can be "DEP")
    for col in df.columns:
        col_upper = str(col).upper().strip()
        if "PARCEL" in col_upper and "NOTES" in col_upper:
            parcel_notes_col = col
            break
    if parcel_notes_col is None:
        for col in df.columns:
            c = str(col).lower()
            if c == "dep" or "bill id" in c or "bill type" in c:
                parcel_notes_col = col
                break
        if parcel_notes_col is None:
            for col in df.columns:
                if "dep" in str(col).lower():
                    parcel_notes_col = col
                    break
    # Parcel column: Tax ID, Client Request ID, Parcel Number, Parcel #, etc.
    for col in df.columns:
        col_upper = str(col).upper().strip()
        c = str(col).lower()
        if "TAX ID" in col_upper and "BILL" not in col_upper:
            parcel_col = col
            break
        if "CLIENT REQUEST ID" in col_upper:
            parcel_col = col
            break
        if "PARCEL" in col_upper and ("NUMBER" in col_upper or "NO" in col_upper or "#" in col_upper):
            parcel_col = col
            break
    if parcel_col is None:
        for col in df.columns:
            c = str(col).lower()
            if "parcel" in c and ("number" in c or "#" in c or "no" in c or "id" in c):
                parcel_col = col
                break
        if parcel_col is None:
            for col in df.columns:
                if "parcel" in str(col).lower():
                    parcel_col = col
                    break
    return parcel_notes_col, parcel_col


def highlight_logic(df):
    """Consecutive rows with DEP in notes column and matching parcel get highlighted. Supports NY RDM (Tax ID, Bill ID)."""
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    parcel_notes_col, parcel_col = _find_dep_and_parcel_columns(df)
    if parcel_notes_col is None or parcel_col is None:
        cols_preview = ", ".join(str(c) for c in list(df.columns)[:20])
        if len(df.columns) > 20:
            cols_preview += ", ..."
        raise ValueError(
            "Required columns not found. Need a parcel column (e.g. Tax ID, Client Request ID, Parcel Number) and a DEP column (e.g. Bill ID, Parcel Notes, DEP). Your columns: " + cols_preview
        )

    parcel_notes = df[parcel_notes_col].fillna("").astype(str).str.strip().str.upper()
    parcel = df[parcel_col].fillna("").astype(str).str.strip()

    flags = [False] * len(df)
    for i in range(1, len(df)):
        row_i_dep = parcel_notes.iloc[i] == "DEP"
        row_i_minus_1_dep = parcel_notes.iloc[i - 1] == "DEP"
        parcel_i = parcel.iloc[i]
        parcel_i_minus_1 = parcel.iloc[i - 1]
        parcels_match = (parcel_i == parcel_i_minus_1) and parcel_i != "" and parcel_i != "NAN"
        if row_i_dep and row_i_minus_1_dep and parcels_match:
            flags[i] = True
            flags[i - 1] = True
    df["_highlight"] = flags
    return df


def process_excel_file(file_bytes, original_filename):
    """Read with pandas, run highlight logic, build a NEW workbook from scratch with yellow fill.
    Output is minimal valid xlsx so Excel on Mac and Windows opens it.
    Supports NY RDM-style docs: header on row 6, Tax ID / Bill ID columns."""
    file_ext = Path(original_filename).suffix.lower()
    if file_ext == ".xls":
        raise ValueError("Old .xls is not supported. Save as .xlsx or .xlsm.")

    buf = io.BytesIO(file_bytes)
    df = None
    for header_row in (0, 5, 4, 6, 3, 7):
        try:
            buf.seek(0)
            df_try = pd.read_excel(buf, engine="openpyxl", sheet_name=0, header=header_row)
            if df_try is None or len(df_try) == 0:
                continue
            n, p = _find_dep_and_parcel_columns(df_try)
            if n is not None and p is not None:
                df = df_try
                break
        except Exception:
            continue
    if df is None:
        try:
            buf.seek(0)
            df = pd.read_excel(buf, engine="openpyxl", sheet_name=0)
        except Exception as e:
            raise ValueError(f"Cannot read Excel file. Is it a valid .xlsx or .xlsm? Details: {e}")
        if df is None or len(df) == 0:
            raise ValueError("The file has no data rows.")
        n, p = _find_dep_and_parcel_columns(df)
        if n is None or p is None:
            raise ValueError(
                "Could not find parcel column (e.g. Tax ID, Parcel Number) and DEP column (e.g. Bill ID, Parcel Notes). Try a file with headers like Tax ID and Bill ID."
            )

    df_processed = highlight_logic(df)
    rows_to_highlight = set()
    for pandas_idx, row in df_processed.iterrows():
        if row["_highlight"]:
            rows_to_highlight.add(int(pandas_idx))

    # Build from scratch: new workbook, one sheet, data + yellow fill. Opens in Excel Mac/Windows.
    data_cols = [c for c in df_processed.columns if c != "_highlight"]
    col_count = len(data_cols)
    wb = openpyxl.Workbook()
    ws = wb.active
    if ws is None:
        ws = wb.create_sheet("Sheet1", 0)
    for c, col_name in enumerate(data_cols, 1):
        ws.cell(row=1, column=c, value=col_name)
    for pandas_idx, row in df_processed.iterrows():
        excel_row = int(pandas_idx) + 2
        for c, col in enumerate(data_cols, 1):
            ws.cell(row=excel_row, column=c, value=row[col])
            if pandas_idx in rows_to_highlight:
                ws.cell(row=excel_row, column=c).fill = YELLOW_FILL

    base_name = Path(original_filename).stem
    output_filename = f"{base_name}_WEBPT.processed.xlsx"
    tmp = None
    try:
        fd, tmp = tempfile.mkstemp(suffix=".xlsx")
        os.close(fd)
        wb.save(tmp)
        with open(tmp, "rb") as f:
            output_bytes = f.read()
    except Exception:
        output_bytes = None
    finally:
        if tmp and os.path.exists(tmp):
            try:
                os.unlink(tmp)
            except OSError:
                pass
    if not output_bytes:
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        output_bytes = buf.getvalue()
    return io.BytesIO(output_bytes), output_filename, len(rows_to_highlight), len(df), len(output_bytes)


@app.errorhandler(500)
def handle_500(e):
    return jsonify({"error": str(e) if str(e) else "Internal server error"}), 500


@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "DEP Highlighter",
        "timestamp": datetime.now().isoformat(),
    })


@app.route("/process", methods=["POST"])
def process_file():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in (".xlsx", ".xlsm", ".xls"):
            return jsonify({"error": "Invalid file type. Use .xlsx or .xlsm"}), 400
        if file_ext == ".xls":
            return jsonify({"error": "Old .xls not supported. Save as .xlsx or .xlsm"}), 400

        file_bytes = file.read()
        if not file_bytes or len(file_bytes) < 100:
            return jsonify({"error": "File is empty or too small. Use a valid .xlsx or .xlsm file."}), 400

        output_buffer, output_filename, highlighted_count, total_rows, content_length = process_excel_file(
            file_bytes, file.filename
        )
        return send_file(
            output_buffer,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=output_filename,
            content_length=content_length,
        )
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        msg = str(e).strip() or "Processing failed"
        if len(msg) > 400:
            msg = msg[:397] + "..."
        print("Process error:", msg)
        print(traceback.format_exc())
        return jsonify({"error": msg}), 500


@app.route("/", methods=["GET"])
def index():
    if _FRONTEND_HTML.exists():
        return send_file(str(_FRONTEND_HTML), mimetype="text/html")
    return jsonify({
        "service": "Webpoint LLC - DEP Highlighter API",
        "version": "1.0.0",
        "endpoints": {"/health": "GET", "/process": "POST"},
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
