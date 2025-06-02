from flask import Blueprint, jsonify, request
import pandas as pd
import io
import pdb

upload_bp = Blueprint('upload', __name__, url_prefix='/upload')

@upload_bp.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    uploaded_file = request.files['file'] 
    if uploaded_file.filename == '':
        return jsonify({'error': 'No file selected'}, 400)

    try:
        if uploaded_file and uploaded_file.filename.endswith('.csv'):
            csv_content = uploaded_file.stream.read().decode('utf-8')
            csv_file_buffer = io.StringIO(csv_content)
            df = pd.read_csv(csv_file_buffer)

            df_cols = [i for i in df.keys()]
            columns_needed = ['Data', 'Valor', 'Descrição']
            miss_cols = []

            miss_cols = [col for col in columns_needed if col not in df_cols]
            if miss_cols: return jsonify({'Columns missing': miss_cols}), 400
            
            df = df[columns_needed]
            return jsonify({'message': 'CSV file processed successfully', 'data': df.to_dict(orient='records')}), 200

        else:
            file_content = uploaded_file.stream.read()
            return jsonify({'message': 'File received', 'filename': uploaded_file.filename, 'content_length': len(file_content)}), 200

    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500