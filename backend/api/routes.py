# api/routes.py
from datetime import datetime
import os
from flask import Blueprint, jsonify, request, render_template, current_app
from werkzeug.utils import secure_filename

from constants import ALLOWED_EXTENSIONS
from db.db import Database

def allowed_file(filename):
    """Verifica si el archivo tiene extensión permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

api_bp = Blueprint('api', __name__, url_prefix='/api')
db = Database()

@api_bp.route('/health', methods=['GET'])
def health():
    return 'OK'

# Process all files and data
@api_bp.route('/stats/process', methods=['GET'])
def process_data():
    try:
        db.procesar_todas_las_categorias()
        data = {
            'status': 'Data process succesfully!'
        }
        return jsonify(data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/<categoria>', methods=['GET'])
def get_category(categoria):
    try:
        if categoria is None:
            return jsonify({
                'success': False,
                'error': 'El parámetro "categoria" es requerido'
            }), 400

        nombre_amigable_categoria = db.obtener_nombre_amigable_categoria(categoria)
        jugadores = db.obtener_resumen_categoria(categoria)
        data = {
            'categoria': nombre_amigable_categoria,
            'total_jugadores': len(jugadores),
            'jugadores': jugadores
        }
        return jsonify(data)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al obtener los datos: {str(e)}'
        }), 500

# 🔥 ENDPOINT JSON (para consumir desde cualquier frontend)
@api_bp.route('/<categoria>/stats', methods=['GET'])
def get_stats_json(categoria):
    """Endpoint para API - Devuelve JSON puro"""
    try:
        jugadores = db.generar_promedios(categoria)
        
        # Convertir a JSON
        data = {
            'categoria': categoria,
            'total_jugadores': len(jugadores),
            'jugadores': jugadores
        }
        return jsonify(data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 📊 Endpoint para HTML (opcional - puedes eliminar después)
@api_bp.route('/stats/<categoria>/html', methods=['GET'])
def get_stats_html(categoria):
    """Endpoint HTML - Para usar con Flask + Jinja"""
    jugadores = db.generar_promedios(categoria)
    
    return render_template('stats.html', jugadores=jugadores, categoria=categoria)

@api_bp.route('/stats/add', methods=['GET'])
def add_stats():
    """Endpoint HTML - Presenta un form para agregar un archivo de estadistica de partido"""

    return render_template('add-stats.html')

@api_bp.route('/stats/add', methods=['POST'])
def add_stats_to_server():
    """Endpoint HTML - Presenta un form para agregar un archivo de estadistica de partido"""

    try:
        if 'fecha' not in request.form:
            return jsonify({'error': 'Campo "fecha" es requerido'}), 400
        
        if 'opcion' not in request.form:
            return jsonify({'error': 'Campo "opcion" es requerido'}), 400
        
        if 'csv' not in request.files:
            return jsonify({'error': 'Archivo CSV es requerido'}), 400
        
        fecha = request.form['fecha']
        option = request.form['opcion']
        file = request.files['csv']

        if file.filename == '':
            return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
        
        # 4. Validar extensión del archivo
        if not allowed_file(file.filename):
            return jsonify({'error': 'Solo se permiten archivos CSV'}), 400

        folder_name = secure_filename(option.lower().replace(' ', '_'))
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'estadisticas')
        target_folder = os.path.join(upload_folder, folder_name)
        os.makedirs(target_folder, exist_ok=True)

        new_filename = f"{option.upper()}_estadistica_{fecha}.csv"
        file_path = os.path.join(target_folder, new_filename)

        # Si ya existe, agregar un sufijo para no sobrescribir
        if os.path.exists(file_path):
            timestamp = datetime.now().strftime('%H%M%S')
            name, ext = os.path.splitext(new_filename)
            new_filename = f"{name}_{timestamp}{ext}"
            file_path = os.path.join(target_folder, new_filename)

        file.save(file_path)

        db.procesar_todas_las_categorias()

        return jsonify({
            'mensaje': 'Archivo subido exitosamente',
            'archivo': new_filename,
            'ruta': file_path,
            'opcion': option,
            'fecha': fecha
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error al procesar la solicitud: {str(e)}'}), 500

# 📈 Endpoint con filtros (ejemplo)
@api_bp.route('/stats/<categoria>/filter', methods=['POST'])
def filter_stats(categoria):
    """Filtro de estadísticas (ejemplo)"""
    data = request.json
    min_pts = data.get('min_pts', 0)
    max_pts = data.get('max_pts', 100)
    
    jugadores = db.generar_promedios(categoria)
    
    # Filtrar
    filtrados = [j for j in jugadores if min_pts <= j.pts_prom <= max_pts]
    
    return jsonify({
        'total': len(filtrados),
        'jugadores': filtrados
    })