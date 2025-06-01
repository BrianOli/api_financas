from flask import Blueprint, jsonify, request
import pandas as pd 
import csv
import io

upload_bp = Blueprint('upload', __name__, url_prefix='/upload')

@upload_bp.route('/', methods=['POST'])
def upload_file():
    if not request.method == 'POST' and request.content_type != 'text/csv':
        return jsonify({'Non supported method', 400})
    
    csv_content = request.get_data(as_text=True)

    if not csv_file:
        return jsonify({'Nenhum arquivo recebido, por favor envie novamente', 400})
    
    if csv_file:
        try:
            csv_file = io.StringIO(csv_content)
            csv_reader = csv.reader(csv_file)
            data_df = pd.DataFrame(list(csv_reader)[1:], columns=list(csv_reader)[0])

            columns_needed = ['Valor', 'Descrição', 'Data']
            if not all(col in data_df.columns for col in columns_needed):
                missing_col = [col for col in columns_needed if col not in data_df.columns]
                return jsonify({f'Colunas faltantes: {missing_col}', 400})
            
            data_df = data_df(columns_needed)

            return jsonify({f'DataFrame Obtida do arquivo {file.filename}: \n {data_df}', 200})

        except Exception:
            raise jsonify({'Server Error', 500})