import os
import uuid
import tempfile
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import xml.etree.ElementTree as ET

from xml_to_excel import parse_xml_to_rows, collect_all_columns, normalize_rows
import pandas as pd

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

app.config['MAX_CONTENT_LENGTH'] = 256 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

ALLOWED_EXTENSIONS = {'xml'}

converted_files = {}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload an XML file.'}), 400
    
    try:
        file_id = str(uuid.uuid4())
        
        temp_xml = os.path.join(app.config['UPLOAD_FOLDER'], f'{file_id}.xml')
        temp_xlsx = os.path.join(app.config['UPLOAD_FOLDER'], f'{file_id}.xlsx')
        
        file.save(temp_xml)
        
        try:
            rows = parse_xml_to_rows(temp_xml)
        except ET.ParseError as e:
            os.remove(temp_xml)
            return jsonify({'error': f'Invalid XML format: {str(e)}'}), 400
        
        if not rows:
            os.remove(temp_xml)
            return jsonify({'error': 'No data found in XML file'}), 400
        
        columns = collect_all_columns(rows)
        normalized_rows = normalize_rows(rows, columns)
        df = pd.DataFrame(normalized_rows)
        
        df.to_excel(temp_xlsx, index=False, engine='openpyxl')
        
        os.remove(temp_xml)
        
        original_filename = secure_filename(file.filename or 'converted')
        base_name = os.path.splitext(original_filename)[0] or 'converted'
        
        converted_files[file_id] = {
            'path': temp_xlsx,
            'filename': f'{base_name}.xlsx'
        }
        
        preview_rows = normalized_rows[:100]
        preview_cols = columns[:50]
        
        preview_data = []
        for row in preview_rows:
            preview_row = {}
            for col in preview_cols:
                value = row.get(col)
                preview_row[col] = '' if value is None else str(value)
            preview_data.append(preview_row)
        
        return jsonify({
            'success': True,
            'file_id': file_id,
            'filename': f'{base_name}.xlsx',
            'total_rows': len(normalized_rows),
            'total_columns': len(columns),
            'columns': preview_cols,
            'preview': preview_data,
            'preview_limited': len(normalized_rows) > 100 or len(columns) > 50
        })
        
    except Exception as e:
        return jsonify({'error': f'Conversion failed: {str(e)}'}), 500


@app.route('/download/<file_id>')
def download(file_id):
    if file_id not in converted_files:
        return jsonify({'error': 'File not found or expired'}), 404
    
    file_info = converted_files[file_id]
    
    if not os.path.exists(file_info['path']):
        del converted_files[file_id]
        return jsonify({'error': 'File not found or expired'}), 404
    
    return send_file(
        file_info['path'],
        as_attachment=True,
        download_name=file_info['filename'],
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
