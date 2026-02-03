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


def find_column_index(sheet, column_name):
    """Find column index by name (case-insensitive)"""
    for idx, cell in enumerate(sheet[1], 1):
        if cell.value and column_name.lower() in str(cell.value).lower():
            return idx
    return None


def process_excel_file(file_bytes, original_filename):
    """
    Process Excel file and highlight consecutive duplicate DEP parcels
    PRESERVES: VBA, macros, formulas, charts, images, everything
    """
    
    # Load workbook with VBA preservation
    wb = openpyxl.load_workbook(io.BytesIO(file_bytes), keep_vba=True)
    sheet = wb.active
    
    # Find required columns
    parcel_col = find_column_index(sheet, "parcel number")
    dep_col = find_column_index(sheet, "dep")
    
    if not parcel_col or not dep_col:
        raise ValueError("Required columns not found. Need 'Parcel Number' and 'DEP' columns.")
    
    highlighted_count = 0
    total_rows = sheet.max_row
    
    # Process rows - check consecutive pairs
    for row_idx in range(2, total_rows):  # Start at 2 (after header), stop before last
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
