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
import sys
import platform
import tempfile
from pathlib import Path
import traceback
from datetime import datetime

# Max upload size (50MB) - helps avoid Render memory/timeout issues
MAX_FILE_SIZE = 50 * 1024 * 1024

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
    """Highlight every row that has DEP and whose parcel number appears on at least one other row that also has DEP (connected via same parcel, anywhere in file)."""
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

    # Rows marked DEP
    dep_mask = parcel_notes == "DEP"
    # Parcel numbers that appear on at least 2 DEP rows (same parcel, DEP on another row somewhere)
    parcel_dep_count = {}
    for i in range(len(df)):
        if dep_mask.iloc[i]:
            p = parcel.iloc[i]
            if p and p != "NAN":
                parcel_dep_count[p] = parcel_dep_count.get(p, 0) + 1
    parcels_with_parallel_dep = {p for p, c in parcel_dep_count.items() if c >= 2}

    # Highlight every row that has DEP and its parcel is in that set
    flags = [False] * len(df)
    for i in range(len(df)):
        if dep_mask.iloc[i]:
            p = parcel.iloc[i]
            if p and p != "NAN" and p in parcels_with_parallel_dep:
                flags[i] = True
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
    header_row_used = 0
    for header_row in (0, 5, 4, 6, 3, 7):
        try:
            buf.seek(0)
            df_try = pd.read_excel(buf, engine="openpyxl", sheet_name=0, header=header_row)
            if df_try is None or len(df_try) == 0:
                continue
            n, p = _find_dep_and_parcel_columns(df_try)
            if n is not None and p is not None:
                df = df_try
                header_row_used = header_row
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

    base_name = Path(original_filename).stem
    extension = Path(original_filename).suffix
    output_filename = f"{base_name}_Highlighted{extension}"

    # Clone: load original workbook, apply yellow only to highlighted rows, preserve VBA/sheets/metadata
    output_bytes = None
    try:
        buf.seek(0)
        wb = openpyxl.load_workbook(buf, keep_vba=(file_ext == ".xlsm"))
        sheet = wb.worksheets[0]
        # pandas index i -> Excel row (1-based): header at row header_row_used+1, data starts header_row_used+2
        for pandas_idx in rows_to_highlight:
            excel_row = header_row_used + 2 + int(pandas_idx)
            if 1 <= excel_row <= sheet.max_row:
                for col in range(1, sheet.max_column + 1):
                    sheet.cell(excel_row, col).fill = YELLOW_FILL
        tmp = None
        try:
            fd, tmp = tempfile.mkstemp(suffix=extension)
            os.close(fd)
            wb.save(tmp)
            with open(tmp, "rb") as f:
                output_bytes = f.read()
        finally:
            if tmp and os.path.exists(tmp):
                try:
                    os.unlink(tmp)
                except OSError:
                    pass
    except Exception:
        output_bytes = None

    # Fallback: build from scratch if clone failed (preserves open-on-Mac behavior)
    if not output_bytes:
        data_cols = [c for c in df_processed.columns if c != "_highlight"]
        wb = openpyxl.Workbook()
        ws = wb.active or wb.create_sheet("Sheet1", 0)
        for c, col_name in enumerate(data_cols, 1):
            ws.cell(row=1, column=c, value=col_name)
        for pandas_idx, row in df_processed.iterrows():
            excel_row = int(pandas_idx) + 2
            for c, col in enumerate(data_cols, 1):
                ws.cell(row=excel_row, column=c, value=row[col])
                if pandas_idx in rows_to_highlight:
                    ws.cell(row=excel_row, column=c).fill = YELLOW_FILL
        tmp = None
        try:
            fd, tmp = tempfile.mkstemp(suffix=extension)
            os.close(fd)
            wb.save(tmp)
            with open(tmp, "rb") as f:
                output_bytes = f.read()
        finally:
            if tmp and os.path.exists(tmp):
                try:
                    os.unlink(tmp)
                except OSError:
                    pass
        if not output_bytes:
            buf_out = io.BytesIO()
            wb.save(buf_out)
            buf_out.seek(0)
            output_bytes = buf_out.getvalue()

    return io.BytesIO(output_bytes), output_filename, len(rows_to_highlight), len(df), len(output_bytes)


@app.errorhandler(500)
def handle_500(e):
    msg = str(e) if str(e) else "Internal server error"
    return jsonify({"error": msg, "details": msg}), 500


@app.errorhandler(Exception)
def handle_exception(e):
    msg = str(e) or "Unexpected server error"
    return jsonify({"error": msg, "details": msg}), 500


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "service": "DEP Highlighter",
        "timestamp": datetime.now().isoformat(),
        "python_version": platform.python_version(),
        "openpyxl_installed": "openpyxl" in sys.modules,
        "temp_writable": os.access("/tmp", os.W_OK),
        "cwd": os.getcwd(),
    })


@app.route("/process", methods=["POST"])
def process_file():
    temp_path = None
    try:
        print(f"[{datetime.now().isoformat()}] === Processing started ===", flush=True)

        if "file" not in request.files:
            print("400: No file in request.files", flush=True)
            return jsonify({"error": "No file provided", "details": "No file provided. The upload form did not include a file. Try selecting a file again and click Process."}), 400
        file = request.files["file"]
        if file.filename == "" or not (file.filename or "").strip():
            print("400: Empty filename", flush=True)
            return jsonify({"error": "No file selected", "details": "No file selected. Please choose an Excel file (.xlsx or .xlsm) and try again."}), 400

        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in (".xlsx", ".xlsm", ".xls"):
            print(f"400: Invalid file type: {file_ext}", flush=True)
            return jsonify({"error": "Invalid file type. Use .xlsx or .xlsm", "details": "Invalid file type. Use .xlsx or .xlsm"}), 400
        if file_ext == ".xls":
            print("400: .xls not supported", flush=True)
            return jsonify({"error": "Old .xls not supported. Save as .xlsx or .xlsm", "details": "Old .xls not supported. Save as .xlsx or .xlsm"}), 400

        file_bytes = file.read()
        file_size = len(file_bytes)
        print(f"File received: {file.filename}, size: {file_size} bytes ({file_size / 1024 / 1024:.2f} MB)", flush=True)

        if not file_bytes or file_size < 100:
            print(f"400: File too small: {file_size} bytes", flush=True)
            return jsonify({"error": "File is empty or too small. Use a valid .xlsx or .xlsm file.", "details": "File is empty or too small (under 100 bytes). Use a valid .xlsx or .xlsm file."}), 400

        if file_size > MAX_FILE_SIZE:
            msg = f"File too large: {file_size / 1024 / 1024:.1f} MB. Max {MAX_FILE_SIZE // (1024*1024)} MB."
            print(msg, file=sys.stderr, flush=True)
            return jsonify({"error": msg, "details": msg}), 413

        # Optional temp save for Render diagnostics (per doc: "File system issues - temp file writes failing")
        try:
            safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in file.filename)
            temp_path = os.path.join(tempfile.gettempdir(), safe_name)
            print(f"Saving to temp file: {temp_path}", flush=True)
            with open(temp_path, "wb") as f:
                f.write(file_bytes)
            print(f"Saved to: {temp_path}", flush=True)
        except Exception as te:
            print(f"Temp save failed (continuing in-memory): {te}", file=sys.stderr, flush=True)

        print("Loading workbook with openpyxl...", flush=True)
        output_buffer, output_filename, highlighted_count, total_rows, content_length = process_excel_file(
            file_bytes, file.filename
        )
        print(f"Processing complete. Rows: {total_rows}, highlighted: {highlighted_count}. Sending file: {output_filename}", flush=True)

        return send_file(
            output_buffer,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=output_filename,
            content_length=content_length,
        )
    except ValueError as ve:
        print(f"ValueError: {ve}", file=sys.stderr, flush=True)
        return jsonify({"error": str(ve), "details": str(ve)}), 400
    except MemoryError as e:
        error_msg = f"MEMORY ERROR: {e}"
        print(error_msg, file=sys.stderr, flush=True)
        return jsonify({"error": "File too large for processing", "details": error_msg}), 413
    except Exception as e:
        msg = str(e).strip() or "Processing failed"
        if len(msg) > 400:
            msg = msg[:397] + "..."
        error_msg = f"ERROR: {e}\n{traceback.format_exc()}"
        print(error_msg, file=sys.stderr, flush=True)
        return jsonify({"error": msg, "details": msg}), 500
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
                print(f"Cleaned up {temp_path}", flush=True)
            except Exception:
                pass


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
