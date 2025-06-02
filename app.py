from flask import Flask
from routes.exctract_data import upload_bp

app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello_world():
    return "Olá mundo"

app.register_blueprint(upload_bp)

if __name__ == '__main__':
    app.run(debug=True)