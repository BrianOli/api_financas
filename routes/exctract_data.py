from flask import Blueprint, jsonify, request
from dotenv import load_dotenv
import pandas as pd
import requests
import io
import os

load_dotenv()

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
            df = extract_data(uploaded_file)
            
            for data in df.Descrição:
                data = summarize_desc(data)

            return jsonify({'message': 'CSV file processed successfully', 'data': df.to_dict(orient='records')}), 200

        else:
            file_content = uploaded_file.stream.read()
            return jsonify({'message': 'File received', 'filename': uploaded_file.filename, 'content_length': len(file_content)}), 200

    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

def extract_data(uploaded_file):
    csv_content = uploaded_file.stream.read().decode('utf-8')
    csv_file_buffer = io.StringIO(csv_content)
    df = pd.read_csv(csv_file_buffer)

    df_cols = [i for i in df.keys()]
    columns_needed = ['Data', 'Valor', 'Descrição']
    miss_cols = []

    miss_cols = [col for col in columns_needed if col not in df_cols]
    if miss_cols: return jsonify({'Columns missing': miss_cols}), 400
    
    return df[columns_needed]


def summarize_desc(desc):
    prompt = f'Resuma: {desc}, Por exemplo: `Transferência Recebida - Adriano de Jesus Pereira Carvalho - •••.584.408-•• - NU PAGAMENTOS - IP (0260) Agência: 1 Conta: 32993603-6` transforme em `Transferência Recebida - Adriano de Jesus Pereira Carvalho`'

    headers = {"Authorization": os.getenv('LLM_TOKEN')}
    url = os.getenv('LLM_URL')
    payload = {
        "providers": "microsoft,connexun",
        "language": "pt-br",
        "text": f"{prompt}",
    }

    try:
        response = requests.post(url, json=payload, headers=headers)    
        result = response.json()
        return result

    except Exception as e:
        return jsonify({'Server Error': f'{str(e)}'})
