#!/usr/bin/env python3
"""
DEP Highlighter Backend Server
Same logic as working Windows app: Parcel Notes + Parcel Number, consecutive DEP rows highlighted.
"""

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import pandas as pd
import openpyxl
from openpyxl.styles import PatternFill
import io
import os
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


def highlight_logic(df):
    """Same as Windows DEP Highlighter: consecutive rows with DEP in Parcel Notes and matching Parcel Number."""
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    parcel_notes_col = None
    parcel_col = None
    for col in df.columns:
        col_upper = str(col).upper().strip()
        if "PARCEL" in col_upper and "NOTES" in col_upper:
            parcel_notes_col = col
        elif "PARCEL" in col_upper and "NUMBER" in col_upper:
            parcel_col = col
    if parcel_notes_col is None and any("dep" in str(c).lower() for c in df.columns):
        for col in df.columns:
            if "dep" in str(col).lower():
                parcel_notes_col = col
                break
    if parcel_notes_col is None or parcel_col is None:
        raise ValueError(
            "Required columns not found. Need 'Parcel Number' and 'Parcel Notes' (or a column named DEP). "
            "Same as the Windows DEP Highlighter."
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
    """Read with pandas (same as Windows), get rows to highlight, apply with openpyxl, return buffer."""
    file_ext = Path(original_filename).suffix.lower()
    if file_ext == ".xls":
        raise ValueError("Old .xls is not supported. Save as .xlsx or .xlsm.")

    buf = io.BytesIO(file_bytes)
    try:
        df = pd.read_excel(buf, engine="openpyxl")
    except Exception as e:
        raise ValueError(f"Cannot read Excel file. Is it a valid .xlsx or .xlsm? Details: {e}")

    if df is None or len(df) == 0:
        raise ValueError("The file has no data rows.")

    df_processed = highlight_logic(df)
    rows_to_highlight = []
    for pandas_idx, row in df_processed.iterrows():
        if row["_highlight"]:
            excel_row = int(pandas_idx) + 2
            rows_to_highlight.append(excel_row)

    buf.seek(0)
    try:
        wb = openpyxl.load_workbook(buf, keep_vba=(file_ext == ".xlsm"))
    except Exception:
        buf.seek(0)
        wb = openpyxl.load_workbook(buf, keep_vba=False)

    sheet = wb.active
    for row_num in rows_to_highlight:
        if row_num <= sheet.max_row:
            for col in range(1, sheet.max_column + 1):
                sheet.cell(row_num, col).fill = YELLOW_FILL

    base_name = Path(original_filename).stem
    extension = Path(original_filename).suffix
    output_filename = f"{base_name}_WEBPT.processed{extension}"
    output_buffer = io.BytesIO()
    wb.save(output_buffer)
    output_buffer.seek(0)
    return output_buffer, output_filename, len(rows_to_highlight), len(df)


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
        output_buffer, output_filename, highlighted_count, total_rows = process_excel_file(
            file_bytes, file.filename
        )
        return send_file(
            output_buffer,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=output_filename,
        )
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        msg = str(e)
        if not msg:
            msg = traceback.format_exc()[:500]
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
