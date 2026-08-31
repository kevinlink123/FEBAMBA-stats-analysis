from flask import Blueprint, render_template

from db.db import Database


html_bp = Blueprint('html', __name__, url_prefix='/')
db = Database()

@html_bp.route('/<categoria>/stats', methods=['GET'])
def get_stats_html(categoria):
    """Endpoint HTML - Pagina de estadisticas de cada categoria"""
    jugadores = db.generar_promedios(categoria)
    
    return render_template('stats.html', jugadores=jugadores, categoria=categoria)

@html_bp.route('/', methods=['GET'])
def home_page():
    """Endpoint HTML - Home Page"""

    return render_template('home.html')