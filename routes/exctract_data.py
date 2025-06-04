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
        df_data = get_data(uploaded_file)
        return jsonify({'Message': 'File readed successfully', 'Data': df_data})

    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

def get_data(up_file):
    try:
        if up_file.filename == '':
            return FileNotFoundError({'Error': 'No file sended'})

        if up_file and up_file.filename.endswith('.csv'):
            df = extract_data(up_file)
            
            if 'Descrição' in df.columns:
                df['Descrição'] = df['Descrição'].apply(summarize_desc)

            return df.to_dict(orient='records')

        else:
            file_content = up_file.stream.read()
            return jsonify({'message': 'File received', 'filename': up_file.filename, 'content_length': len(file_content)}), 200
        
    except Exception as e:
        return jsonify({'Error': f'Server error: {str(e)}'})


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
    prompt = f'remova dados não necessários para um relatório financeiro como dados bancários ou outras informações irrelevantes, mantenha apenas o nome de quem recebeu/enviou a transferencia ou o que foi a transferência, não há necessidade de manter o nome do banco ou coisas parecidas.\n O texto à ser resumido é: {desc}'

    api_key = os.getenv("LLM_TOKEN")
    model = os.getenv("LLM_MODEL")
    api_url = f'http://195.179.229.119/gpt/api.php?prompt={requests.utils.quote(prompt)}&api_key={requests.utils.quote(api_key)}&model={requests.utils.quote(model)}'

    try:
        response = requests.get(api_url)
        response.raise_for_status()  
        data = response.json()
        return data['content']
    except Exception as e:
        return jsonify({'Server Error': f'{str(e)}'})
