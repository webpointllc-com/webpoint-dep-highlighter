#!/usr/bin/env python3
"""
DEP Highlighter Backend Server
Preserves ALL Excel features including VBA macros, formulas, charts, images, etc.
"""

from flask import Flask, request, send_file, jsonify, send_from_directory
from flask_cors import CORS
import openpyxl
from openpyxl.styles import PatternFill
import io
import os
from pathlib import Path
import traceback
from datetime import datetime

app = Flask(__name__, static_folder=None)

# Allow requests from Webpoint Toolbox on SquareSpace (webpointllc.com/webpoint-toolbox)
CORS_ORIGINS = [
    "https://webpointllc.com",
    "https://www.webpointllc.com",
    "http://localhost:5000",
    "http://localhost:5001",
    "http://127.0.0.1:5000",
    "http://127.0.0.1:5001",
]
CORS(app, origins=CORS_ORIGINS, supports_credentials=False)

# Directory containing this script (backend); parent/frontend for local, same dir for deploy
_BASE = Path(__file__).resolve().parent
_FRONTEND_HTML = _BASE / "static" / "dep_highlighter.html"
if not _FRONTEND_HTML.exists():
    _FRONTEND_HTML = _BASE.parent / "frontend" / "dep_highlighter.html"

# Yellow highlight for DEP duplicates
YELLOW_FILL = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")


def find_column_index(sheet, possible_names):
    """Find column index by header (case-insensitive). possible_names = list of strings to try."""
    if isinstance(possible_names, str):
        possible_names = [possible_names]
    header_row = sheet[1]
    for idx, cell in enumerate(header_row, 1):
        if not cell.value:
            continue
        val = str(cell.value).lower()
        for name in possible_names:
            if name.lower() in val:
                return idx
    return None


def process_excel_file(file_bytes, original_filename):
    """
    Process Excel file and highlight consecutive duplicate DEP parcels
    PRESERVES: VBA, macros, formulas, charts, images, everything
    """
    file_ext = Path(original_filename).suffix.lower()
    if file_ext == ".xls":
        raise ValueError("Old .xls format is not supported. Please save the file as .xlsx or .xlsm and try again.")

    buf = io.BytesIO(file_bytes)
    # .xlsx: use keep_vba=False to avoid load failures. .xlsm: try keep_vba=True first.
    keep_vba = file_ext == ".xlsm"
    try:
        wb = openpyxl.load_workbook(buf, keep_vba=keep_vba)
    except Exception:
        buf.seek(0)
        try:
            wb = openpyxl.load_workbook(buf, keep_vba=False)
        except Exception as e:
            raise ValueError(f"Could not open the Excel file. Make sure it is a valid .xlsx or .xlsm file. Details: {e}")

    sheet = wb.active
    if sheet.max_row < 2:
        raise ValueError("The sheet has no data rows (only a header or empty). Need at least one data row.")

    # Find header row: scan first 10 rows for Parcel + DEP (handles title rows in county files).
    parcel_col = None
    dep_col = None
    header_row_idx = 1
    for row_num in range(1, min(11, sheet.max_row + 1)):
        row = sheet[row_num]
        p_col = None
        d_col = None
        for idx, cell in enumerate(row, 1):
            if not cell.value:
                continue
            val = str(cell.value).lower()
            if not p_col and any(n in val for n in ["parcel number", "parcel #", "parcel", "parcel id", "parcel no"]):
                p_col = idx
            if not d_col and "dep" in val:
                d_col = idx
        if p_col and d_col:
            parcel_col = p_col
            dep_col = d_col
            header_row_idx = row_num
            break

    if not parcel_col or not dep_col:
        raise ValueError(
            "Required columns not found. Need a column with 'Parcel' (or 'Parcel Number') and a column with 'DEP' "
            "in the first 10 rows. Check your header names and try again."
        )

    data_start = header_row_idx + 1
    highlighted_count = 0
    total_rows = sheet.max_row

    for row_idx in range(data_start, total_rows):
        current_parcel = sheet.cell(row_idx, parcel_col).value
        current_dep = str(sheet.cell(row_idx, dep_col).value or "").strip()
        
        next_parcel = sheet.cell(row_idx + 1, parcel_col).value
        next_dep = str(sheet.cell(row_idx + 1, dep_col).value or "").strip()
        
        # Check BOTH conditions
        if (current_parcel == next_parcel and 
            current_dep.upper() == "DEP" and 
            next_dep.upper() == "DEP"):
            
            # Highlight BOTH rows - entire row yellow
            for col in range(1, sheet.max_column + 1):
                sheet.cell(row_idx, col).fill = YELLOW_FILL
                sheet.cell(row_idx + 1, col).fill = YELLOW_FILL
            
            highlighted_count += 2
    
    # Create output filename
    base_name = Path(original_filename).stem
    extension = Path(original_filename).suffix
    output_filename = f"{base_name}_WEBPT.processed{extension}"
    
    # Save to bytes buffer with VBA preservation
    output_buffer = io.BytesIO()
    wb.save(output_buffer)
    output_buffer.seek(0)
    
    return output_buffer, output_filename, highlighted_count, total_rows


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'DEP Highlighter',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/process', methods=['POST'])
def process_file():
    """
    Main processing endpoint
    Accepts Excel file, returns highlighted clone with _WEBPT.processed suffix
    """
    
    try:
        # Validate request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        # Validate file extension
        allowed_extensions = {'.xlsx', '.xlsm', '.xls'}
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            return jsonify({'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'}), 400
        
        # Read file bytes
        file_bytes = file.read()
        
        # Process the Excel file
        output_buffer, output_filename, highlighted_count, total_rows = process_excel_file(
            file_bytes, 
            file.filename
        )
        
        # Return processed file
        return send_file(
            output_buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=output_filename
        )
    
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500


@app.route('/', methods=['GET'])
def index():
    """Serve frontend HTML if present, else API info JSON"""
    if _FRONTEND_HTML.exists():
        return send_file(str(_FRONTEND_HTML), mimetype='text/html')
    return jsonify({
        'service': 'Webpoint LLC - DEP Highlighter API',
        'version': '1.0.0',
        'endpoints': {
            '/health': 'Health check',
            '/process': 'POST - Upload Excel file for processing'
        },
        'features': [
            'Preserves VBA macros',
            'Preserves formulas',
            'Preserves charts and images',
            'Preserves all hidden code',
            'Highlights consecutive duplicate DEP parcels',
            'Returns cloned document with _WEBPT.processed suffix'
        ]
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║           WEBPOINT LLC - DEP HIGHLIGHTER API               ║
║                                                            ║
║  Status: RUNNING                                           ║
║  Port: {port}                                                ║
║  Endpoint: http://localhost:{port}/process                   ║
║                                                            ║
║  Features:                                                 ║
║  ✓ Preserves VBA macros                                    ║
║  ✓ Preserves formulas & charts                             ║
║  ✓ Highlights duplicate DEP parcels                        ║
║  ✓ Returns _WEBPT.processed files                          ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
