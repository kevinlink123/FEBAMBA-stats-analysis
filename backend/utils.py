import os
import shlex


def extraer_jugadores_desde_csv(ruta_archivo):
    """
    Lee el CSV y devuelve una lista de diccionarios con las stats de los jugadores
    de ALL BOYS SAAVEDRA.
    """
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        lineas = f.readlines()

    equipo_buscado = "ALL BOYS SAAVEDRA"
    idx_inicio = None

    # Buscar la línea del equipo
    for i, linea in enumerate(lineas):
        texto_limpio = linea.strip(',')
        if equipo_buscado in texto_limpio and not "vs" in texto_limpio:
            # El encabezado de columnas ("Num.,Nombre,MIN...") está 2 líneas después.
            # Los datos empiezan 1 línea después de ese encabezado.
            idx_inicio = i + 3
            break

    if idx_inicio is None:
        print(f"⚠️ Equipo {equipo_buscado} no encontrado en {ruta_archivo}")
        return []

    jugadores = []
    for linea in lineas[idx_inicio:]:
        linea_limpia = linea.strip()

        if(linea_limpia.strip(',').strip() == ''):
            continue

        # Condiciones de parada
        if ( "TOTALES" in linea_limpia or 
            "ALL BOYS" in linea_limpia):
            break
        
        # Dividir por comas y limpiar espacios
        lexer = shlex.shlex(linea, posix=True)
        lexer.whitespace = ','  # El separador es la coma
        lexer.whitespace_split = True
        lexer.quotes = '"'  # Respetar comillas dobles

        columnas = list(lexer)
        # Validar que tenga al menos 22 columnas (mínimo esperado)
        if len(columnas) < 22:
            continue

        # El primer campo debe ser el número de camiseta (numérico) para filtrar filas basura
        if not columnas[0].isdigit():
            continue

        # Extraer datos manualmente por índice (ver mapeo definido)
        try:
            # Funcion auxiliar para parsear "2/3" -> (acertados, intentos)
            def parse_fraction(val):
                if '/' in val:
                    partes = val.split('/')
                    return int(partes[0]), int(partes[1])
                return 0, 0

            tc2_made, tc2_att = parse_fraction(columnas[4])
            tc3_made, tc3_att = parse_fraction(columnas[6])
            tl_made, tl_att = parse_fraction(columnas[8])

            # Convertir minutos (MM:SS) a decimal
            tiempo_str = columnas[2]
            minutos_decimal = 0.0
            if ':' in tiempo_str:
                partes = tiempo_str.split(':')
                minutos_decimal = int(partes[0]) + int(partes[1]) / 60.0
            else:
                minutos_decimal = float(tiempo_str) if tiempo_str else 0.0

            jugador = {
                'archivo': os.path.basename(ruta_archivo),
                'jugador': columnas[1],
                'minutos': round(minutos_decimal, 2),
                'pts': int(columnas[3]) if columnas[3].isdigit() else 0,
                'tc2_intentos': tc2_att,
                'tc2_acertados': tc2_made,
                'tc3_intentos': tc3_att,
                'tc3_acertados': tc3_made,
                'tl_intentos': tl_att,
                'tl_acertados': tl_made,
                'def_reb': int(columnas[10]) if columnas[10].isdigit() else 0,
                'of_reb': int(columnas[11]) if columnas[11].isdigit() else 0,
                'tot_reb': int(columnas[12]) if columnas[12].isdigit() else 0,
                'ast': int(columnas[13]) if columnas[13].isdigit() else 0,
                'rec': int(columnas[14]) if columnas[14].isdigit() else 0,
                'per': int(columnas[15]) if columnas[15].isdigit() else 0,
                'tapones_favor': int(columnas[16]) if columnas[16].isdigit() else 0,
                'tapones_contra': int(columnas[17]) if columnas[17].isdigit() else 0,
                'faltas_cometidas': int(columnas[18]) if columnas[18].isdigit() else 0,
                'faltas_recibidas': int(columnas[19]) if columnas[19].isdigit() else 0,
                'val': int(columnas[20]) if columnas[20].isdigit() else 0,
                'plus_minus': int(columnas[21]) if len(columnas) > 21 and columnas[21].isdigit() else 0
            }
            jugadores.append(jugador)
        except (ValueError, IndexError) as e:
            print(f"⚠️ Error parseando fila en {ruta_archivo}: {linea_limpia[:50]}... Error: {e}")
            continue

    return jugadores