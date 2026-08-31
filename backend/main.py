from datetime import datetime

from flask import Flask
from flask_cors import CORS

from api.routes import api_bp
from api.html_routes import html_bp
from db.db import Database
from constants import CATEGORIAS_MAP, MAX_CONTENT_LENGTH

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'estadisticas'
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
CORS(app)

app.register_blueprint(api_bp)
app.register_blueprint(html_bp)
db = Database()
db.inicializar_db()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)