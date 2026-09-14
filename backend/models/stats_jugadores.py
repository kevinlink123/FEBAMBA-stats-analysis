# models/stats.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class JugadorPromedios:
    """Modelo de datos para estadísticas de jugador"""
    id: int
    nombre: str
    partidos_jugados: int
    min_prom: float
    pts_prom: float
    reb_prom: float
    ast_prom: float
    rec_prom: float
    tap_prom: float
    per_prom: float
    pct2: float
    pct3: float 
    pct_tl: float
    efg: float
    tov_percentage: float
    usage_rate: float
    
    def to_dict(self):
        """Convertir a diccionario para JSON"""
        return {k: v for k, v in self.__dict__.items() if v is not None}

@dataclass
class JugadorResumenCategoria:
    """Modelo para los datos obtenidos de un jugador para mostrar en una pagina de categoria"""
    nombre: str
    partidos_jugados: int
    