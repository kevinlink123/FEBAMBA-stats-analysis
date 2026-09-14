# database.py
from datetime import datetime
import glob
import re
import sqlite3
import os
from pathlib import Path

from constants import CATEGORIAS_MAP
from models.stats_jugadores import JugadorPromedios, JugadorResumenCategoria
from utils import extraer_jugadores_desde_csv

class Database:
    _instance = None
    _connection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Evitar reinicialización
        if not hasattr(self, 'initialized'):
            self.db_path = self._get_db_path()
            self.initialized = True
    
    def _get_db_path(self):
        """Obtiene la ruta de la base de datos"""
        # Puedes cambiar esto según tu estructura
        return 'stats.db'
    
    def get_connection(self):
        """Obtiene la conexión a la base de datos"""
        if self._connection is None:
            self._connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False  # Necesario para multi-threading
            )
            self._connection.row_factory = sqlite3.Row  # Para acceder por nombre de columna
        return self._connection
    
    def inicializar_db(self):
        """Crea todas las tablas si no existen."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabla de categorías
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL,
                nombre_amigable TEXT NOT NULL,
                orden INTEGER
            )
        ''')
        
        # Tabla de jugadores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jugadores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                categoria_id INTEGER NOT NULL,
                equipo TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (categoria_id) REFERENCES categorias(id),
                UNIQUE(nombre, categoria_id)
            )
        ''')
        
        # Tabla de partidos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS partidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                categoria_id INTEGER NOT NULL,
                archivo TEXT NOT NULL,
                fecha_partido DATE,
                fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (categoria_id) REFERENCES categorias(id)
            )
        ''')
        
        # Tabla de estadísticas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS estadisticas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                partido_id INTEGER NOT NULL,
                jugador_id INTEGER NOT NULL,
                minutos REAL,
                pts INTEGER,
                tc2_intentos INTEGER,
                tc2_acertados INTEGER,
                tc3_intentos INTEGER,
                tc3_acertados INTEGER,
                tl_intentos INTEGER,
                tl_acertados INTEGER,
                def_reb INTEGER,
                of_reb INTEGER,
                tot_reb INTEGER,
                ast INTEGER,
                rec INTEGER,
                per INTEGER,
                tapones_favor INTEGER,
                tapones_contra INTEGER,
                faltas_cometidas INTEGER,
                faltas_recibidas INTEGER,
                val INTEGER,
                plus_minus INTEGER,
                FOREIGN KEY (partido_id) REFERENCES partidos(id) ON DELETE CASCADE,
                FOREIGN KEY (jugador_id) REFERENCES jugadores(id) ON DELETE CASCADE,
                UNIQUE(partido_id, jugador_id)
            )
        ''')
        
        # Insertar categorías si no existen
        for nombre, data in CATEGORIAS_MAP.items():
            cursor.execute('''
                INSERT OR IGNORE INTO categorias (nombre, nombre_amigable, orden)
                VALUES (?, ?, ?)
            ''', (nombre, data["nombre"], data["orden"]))
        
        conn.commit()
        print("✅ Base de datos inicializada con el nuevo esquema.")
    
    def obtener_categoria_id(self, nombre_categoria):
        """Devuelve el ID de una categoría dado su nombre."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM categorias WHERE nombre = ?", (nombre_categoria,))
        resultado = cursor.fetchone()
        return resultado[0] if resultado else None

    def obtener_nombre_amigable_categoria(self, nombre_categoria):
        """Devuelve el nombre amigable y completo de la categoria"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT nombre_amigable FROM categorias WHERE nombre = ?", (nombre_categoria,))
        resultado = cursor.fetchone()
        return resultado[0] if resultado else None

    def crear_partido(self, categoria_id, archivo):
        """Crea un registro de partido y devuelve su ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Intentar extraer fecha del nombre del archivo (opcional)
        # Ejemplo: "partido_20260314.csv" -> "2026-03-14"
        fecha = None
        match = re.search(r'(\d{8})', archivo)
        if match:
            fecha_str = match.group(1)
            try:
                fecha = datetime.strptime(fecha_str, '%Y%m%d').strftime('%Y-%m-%d')
            except:
                pass
        
        cursor.execute('''
            INSERT INTO partidos (categoria_id, archivo, fecha_partido)
            VALUES (?, ?, ?)
        ''', (categoria_id, archivo, fecha))
        
        partido_id = cursor.lastrowid
        conn.commit()
        return partido_id
    
    def obtener_o_crear_jugador(self, nombre, categoria_id, equipo="ALL BOYS SAAVEDRA"):
        """Obtiene un jugador existente o lo crea si no existe."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Buscar jugador
        cursor.execute('''
            SELECT id FROM jugadores 
            WHERE nombre = ? AND categoria_id = ?
        ''', (nombre, categoria_id))
        
        resultado = cursor.fetchone()
        
        if resultado:
            jugador_id = resultado[0]
        else:
            # Crear nuevo jugador
            cursor.execute('''
                INSERT INTO jugadores (nombre, categoria_id, equipo)
                VALUES (?, ?, ?)
            ''', (nombre, categoria_id, equipo))
            jugador_id = cursor.lastrowid
            print(f"   🆕 Nuevo jugador: {nombre}")
        
        conn.commit()
        return jugador_id
    
    def guardar_estadisticas_en_db(self, categoria_id, archivo, jugadores):
        """Guarda partido y estadísticas en la nueva estructura."""
        if not jugadores:
            return
        
        # Crear el partido
        partido_id = self.crear_partido(categoria_id, archivo)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        for j in jugadores:
            # Obtener o crear jugador
            jugador_id = self.obtener_o_crear_jugador(j['jugador'], categoria_id)
            
            # Insertar estadísticas
            cursor.execute('''
                INSERT OR IGNORE INTO estadisticas (
                    partido_id, jugador_id, minutos, pts,
                    tc2_intentos, tc2_acertados,
                    tc3_intentos, tc3_acertados,
                    tl_intentos, tl_acertados,
                    def_reb, of_reb, tot_reb,
                    ast, rec, per,
                    tapones_favor, tapones_contra,
                    faltas_cometidas, faltas_recibidas,
                    val, plus_minus
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                partido_id, jugador_id, j['minutos'], j['pts'],
                j['tc2_intentos'], j['tc2_acertados'],
                j['tc3_intentos'], j['tc3_acertados'],
                j['tl_intentos'], j['tl_acertados'],
                j['def_reb'], j['of_reb'], j['tot_reb'],
                j['ast'], j['rec'], j['per'],
                j['tapones_favor'], j['tapones_contra'],
                j['faltas_cometidas'], j['faltas_recibidas'],
                j['val'], j['plus_minus']
            ))
        
        conn.commit()
        print(f"   ✅ Guardadas {len(jugadores)} estadísticas para el partido.")
    
    def procesar_todas_las_categorias(self):
        """Procesa todos los archivos CSV en todas las carpetas de categorías."""
        
        # Limpiar datos viejos (si quieres recargar todo)
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM estadisticas")
        cursor.execute("DELETE FROM partidos")
        conn.commit()
        print("🗑️ Datos antiguos eliminados.\n")
        
        # Procesar cada categoría
        for categoria, data in CATEGORIAS_MAP.items():
            carpeta = os.path.join("estadisticas", categoria)
            
            if not os.path.exists(carpeta):
                print(f"📁 Carpeta '{carpeta}' no encontrada. Saltando...")
                continue
            
            archivos = glob.glob(os.path.join(carpeta, "*.csv"))
            if not archivos:
                print(f"⚠️ No hay archivos .csv en '{carpeta}'")
                continue
            
            categoria_id = self.obtener_categoria_id(categoria)
            print(f"\n📂 Procesando categoría: {data['nombre']} ({len(archivos)} partidos)")
            
            for archivo in archivos:
                print(f"  ▶️ {os.path.basename(archivo)}")
                jugadores = extraer_jugadores_desde_csv(archivo)
                if jugadores:
                    self.guardar_estadisticas_en_db(categoria_id, archivo, jugadores)
                else:
                    print(f"     ⚠️ No se extrajeron jugadores de este archivo.")
        
        print("\n✅ PROCESAMIENTO COMPLETADO.")

    def obtener_resumen_categoria(self, categoria_nombre):
        categoria_id = self.obtener_categoria_id( categoria_nombre)
        if not categoria_id:
            print(f"❌ Categoría '{categoria_nombre}' no encontrada.")
            return []

        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT 
                j.nombre,
                COUNT(e.id) as partidos_jugados
            FROM jugadores j
            LEFT JOIN estadisticas e ON j.id = e.jugador_id
            WHERE j.categoria_id = ?
            GROUP BY j.id, j.nombre, j.equipo
            ORDER BY j.equipo, j.nombre
        ''', (categoria_id,))
        
        resultados = cursor.fetchall()

        # Verificar si hay jugadores para esa categoría
        if not resultados:
            print(f"⚠️ No hay datos para la categoría {categoria_nombre}")
            return []

        jugadores = []
        for row in resultados:
            (nombre, partidos_jugados) = row
            jugador = JugadorResumenCategoria(
                nombre=nombre,
                partidos_jugados=partidos_jugados
            )
            jugadores.append(jugador)

        return jugadores

    def obtener_data_basica_jugadores(self, categoria):
        categoria_id = self.obtener_categoria_id( categoria)
        if not categoria_id:
            print(f"❌ Categoría '{categoria}' no encontrada.")
            return []

        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT id, nombre
            FROM jugadores
            WHERE categoria_id = ?
            ORDER BY nombre
        """

        cursor.execute(query, (categoria_id,))
        jugadores = cursor.fetchall()
        return [
            {
                "id": j['id'],
                "nombre": j['nombre']
            }
            for j in jugadores
        ]

    def obtener_nombre_jugador(self, id_jugador: int):
        if not id_jugador:
            print(f"❌ Jugador con ID '{id_jugador}' no encontrado.")
            return []

        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT 
                j.nombre
            FROM jugadores j
            WHERE j.id = ?
        """
            
        cursor.execute(query, (id_jugador,))
        resultado = cursor.fetchone()
        return resultado['nombre']
    
    def obtener_datos_jugador(self, id_jugador: int):
        if not id_jugador:
            print(f"❌ Jugador con ID '{id_jugador}' no encontrado.")
            return []

        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT 
                p.fecha_partido,
                e.pts,
                e.tc2_intentos,
                e.tc2_acertados,
                e.tc3_intentos,
                e.tc3_acertados,
                e.tl_intentos,
                e.tl_acertados,
                e.minutos
            FROM estadisticas e
            JOIN partidos p ON e.partido_id = p.id
            WHERE e.jugador_id = ?
            AND p.fecha_partido IS NOT NULL
            ORDER BY p.fecha_partido ASC
        """
            
        cursor.execute(query, (id_jugador,))
        resultados = cursor.fetchall()
        
        evolucion_data = []
        for row in resultados:
            # Calcular porcentajes
            pct2 = (row['tc2_acertados'] / row['tc2_intentos'] * 100) if row['tc2_intentos'] > 0 else 0
            pct3 = (row['tc3_acertados'] / row['tc3_intentos'] * 100) if row['tc3_intentos'] > 0 else 0
            pct_tl = (row['tl_acertados'] / row['tl_intentos'] * 100) if row['tl_intentos'] > 0 else 0
            
            evolucion_data.append({
                'fecha': row['fecha_partido'] if row['fecha_partido'] else None,
                'pts': row['pts'] or 0,
                'pct2': round(pct2, 1),
                'pct3': round(pct3, 1),
                'pct_tl': round(pct_tl, 1),
                'minutos': row['minutos'] or 0
            })
        
        return evolucion_data

    def generar_promedios(self, categoria_nombre):
        """Generar lista de stats iterable"""
        categoria_id = self.obtener_categoria_id( categoria_nombre)
        if not categoria_id:
            print(f"❌ Categoría '{categoria_nombre}' no encontrada.")
            return []
        
        conn = self.get_connection()
        cursor = conn.cursor()

        team_totals_query = '''
            SELECT 
                SUM(e.tc2_intentos + e.tc3_intentos) AS team_total_fga,
                SUM(e.of_reb) AS team_total_of_reb,
                SUM(e.per) AS team_total_tov,
                SUM(e.tl_intentos) AS team_total_fta,
                COUNT(DISTINCT e.partido_id) AS team_total_partidos,
                SUM(e.tc2_intentos + e.tc3_intentos) - SUM(e.of_reb) + SUM(e.per) + (0.475 * SUM(e.tl_intentos)) AS team_total_possessions
            FROM estadisticas e
            JOIN partidos p ON e.partido_id = p.id
            WHERE p.categoria_id = ?;
        '''
        
        query = '''
            SELECT
                j.id,
                j.nombre,
                COUNT(DISTINCT e.partido_id) as partidos_jugados,
                ROUND(AVG(e.minutos), 1) as min_prom,
                ROUND(AVG(e.pts), 1) as pts_prom,
                ROUND(AVG(e.def_reb), 1) as def_reb_prom,
                ROUND(AVG(e.of_reb), 1) as of_reb_prom,
                ROUND(AVG(e.tot_reb), 1) as reb_prom,
                ROUND(AVG(e.ast), 1) as ast_prom,
                ROUND(AVG(e.rec), 1) as rec_prom,
                ROUND(AVG(e.tapones_favor), 1) as tap_prom,
                ROUND(AVG(e.per), 1) as per_prom,
                SUM(e.per) as per_total,
                SUM(e.tc2_intentos) as sum_tc2_att,
                SUM(e.tc2_acertados) as sum_tc2_made,
                SUM(e.tc3_intentos) as sum_tc3_att,
                SUM(e.tc3_acertados) as sum_tc3_made,
                SUM(e.tl_intentos) as sum_tl_att,
                SUM(e.tl_acertados) as sum_tl_made,
                ROUND(AVG(e.val), 1) as val_prom
            FROM estadisticas e
            JOIN jugadores j ON e.jugador_id = j.id
            WHERE j.categoria_id = ?
            GROUP BY j.id
            ORDER BY pts_prom DESC
        '''
        
        cursor.execute(query, (categoria_id,))
        resultados = cursor.fetchall()

        cursor.execute(team_totals_query, (categoria_id,))
        team_totals_results = cursor.fetchall()
        
        (team_total_fga, team_total_of_reb, team_total_tov, team_total_fta, team_total_partidos, team_total_possessions) = team_totals_results[0]
        print(team_total_fga, team_total_of_reb, team_total_tov, team_total_fta, team_total_partidos)
        print("Posesiones totales: ", team_total_possessions)
        
        if not resultados:
            print(f"⚠️ No hay datos para la categoría {categoria_nombre}")
            return []
        
        # Results is a tuple of lists containeing the following fields:
        # [nombre, pj, min_prom, pts_prom, def_reb_prom, of_reb_prom, reb_prom, ast_prom,
        # rec_prom, tap_prom, per_prom, per_total, total_att2, total_made2, total_att3, total_made3,
        # total_att_tl, total_made_tl, val_p]

        jugadores = []
        for row in resultados:
            # Remember to use the same order than the original query
            (id, nombre, pj, min_prom, pts_prom, def_reb_prom, of_reb_prom, reb_prom, ast_prom, rec_prom, tap_prom, per_prom, per_total,
            total_att2, total_made2, total_att3, total_made3, total_att_tl, total_made_tl, val_p) = row

            pct2 = (total_made2 / total_att2 * 100) if total_att2 > 0 else 0
            pct3 = (total_made3 / total_att3 * 100) if total_att3 > 0 else 0
            pct_tl = (total_made_tl / total_att_tl * 100) if total_att_tl > 0 else 0
            
            # ADVANCED STATS CALCULATION
            # Effective Field Goal %
            total_fga = total_att2 + total_att3
            efg = ( ((total_made2 + (1.5 * total_made3)) / total_fga) * 100 ) if (total_att2 + total_att3) > 0 else 0 
            
            # Turnover percentage
            # tov_percentage = (total_tov / (total_fga + 0.44 * total_fta + total_tov)) * 100
            divisor = total_fga + 0.44 * (total_att_tl / pj) + per_prom
            tov_percentage = (per_total / (total_fga + 0.44 * total_att_tl + per_total)) * 100 if (total_fga + 0.44 * total_att_tl + per_total) > 0 else 0

            # Usage Rate
            # Posesiones estimadas
            stimated_pos_prom = team_total_possessions/team_total_partidos
            # (FGA + 0.44*FTA + TO) / (Posesiones del equipo * minutos jugados / total minutos equipo
            # (100 * (0.33 asis + fga + 0.44 * fta + to)) / pos
            att_tl_prom = total_att_tl / pj
            fga_prom = total_fga / pj
            usage_rate = ((0.33 * (ast_prom + 2) + 0.44 * att_tl_prom + per_prom) / stimated_pos_prom) * 100
            jugador = JugadorPromedios(
                id,
                nombre, 
                partidos_jugados = pj, 
                min_prom = min_prom, 
                pts_prom = pts_prom, 
                reb_prom = reb_prom, 
                ast_prom = ast_prom, 
                rec_prom = rec_prom, 
                tap_prom = tap_prom, 
                per_prom = per_prom,
                pct2 = round(pct2, 2), 
                pct3 = round(pct3, 2), 
                pct_tl = round(pct_tl, 2), 
                efg = round(efg, 2),
                tov_percentage = round(tov_percentage, 2),
                usage_rate = round(usage_rate, 2)
            )
            jugadores.append(jugador)
        
        return jugadores

    def generar_reporte_categoria(self, categoria_nombre):
        """Genera reporte de promedios para una categoría específica."""
        categoria_id = self.obtener_categoria_id( categoria_nombre)
        if not categoria_id:
            print(f"❌ Categoría '{categoria_nombre}' no encontrada.")
            return
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT 
                j.nombre,
                COUNT(DISTINCT e.partido_id) as partidos_jugados,
                ROUND(AVG(e.minutos), 1) as min_prom,
                ROUND(AVG(e.pts), 1) as pts_prom,
                ROUND(AVG(e.tot_reb), 1) as reb_prom,
                ROUND(AVG(e.ast), 1) as ast_prom,
                ROUND(AVG(e.rec), 1) as rec_prom,
                ROUND(AVG(e.tapones_favor), 1) as tap_prom,
                ROUND(AVG(e.per), 1) as per_prom,
                SUM(e.tc2_intentos) as sum_tc2_att,
                SUM(e.tc2_acertados) as sum_tc2_made,
                SUM(e.tc3_intentos) as sum_tc3_att,
                SUM(e.tc3_acertados) as sum_tc3_made,
                SUM(e.tl_intentos) as sum_tl_att,
                SUM(e.tl_acertados) as sum_tl_made,
                ROUND(AVG(e.val), 1) as val_prom
            FROM estadisticas e
            JOIN jugadores j ON e.jugador_id = j.id
            WHERE j.categoria_id = ?
            GROUP BY j.id
            ORDER BY pts_prom DESC
        '''
        
        cursor.execute(query, (categoria_id,))
        resultados = cursor.fetchall()
        
        if not resultados:
            print(f"⚠️ No hay datos para la categoría {categoria_nombre}")
            return
        
        print(f"\n{'='*130}")
        print(f"📊 {categoria_nombre.upper()} - PROMEDIOS POR JUGADOR")
        print(f"{'='*130}")
        print(f"{'Jugador':<35} | {'PJ':<3} | {'MIN':<5} | {'PTS':<5} | {'REB':<5} | {'AST':<5} | {'REC':<5} | {'TAP':<5} | {'%2P':<6} | {'%3P':<6} | {'%TL':<6} | {'eFG%':<6} | {'TOV%':<6}")
        print("-"*130)

        # Calculate stats
        for row in resultados:
            # Remember to use the same order than the original query
            (nombre, pj, min_p, pts_p, reb_p, ast_p, rec_p, tap_p, per_p,
            att2, made2, att3, made3, att_tl, made_tl, val_p) = row
            
            pct2 = (made2 / att2 * 100) if att2 > 0 else 0
            pct3 = (made3 / att3 * 100) if att3 > 0 else 0
            pct_tl = (made_tl / att_tl * 100) if att_tl > 0 else 0
            
            # Advanced stats calculation
            # 
            fga = att2 + att3
            efg = ( ((made2 + (0.5 * made3)) / fga) * 100 ) if (att2 + att3) > 0 else 0 
            #TOV / (FGA + 0.44 * FTA + TOV
            divisor = fga + 0.44 * att_tl + per_p
            tov_percentage = (per_p / divisor) * 100 if divisor > 0 else 0

            nombre_display = nombre[:34] if len(nombre) > 34 else nombre
            print(f"{nombre_display:<35} | {pj:<3} | {min_p:<5} | {pts_p:<5} | {reb_p:<5} | {ast_p:<5} | {rec_p:<5} | {tap_p:<5} | {pct2:>5.1f}% | {pct3:>5.1f}% | {pct_tl:>5.1f}% | {efg:>5.1f}% | {tov_percentage:>5.1f}%")
        
        print(f"{'='*130}\n")
    
    def close(self):
        """Cierra la conexión"""
        if self._connection:
            self._connection.close()
            self._connection = None