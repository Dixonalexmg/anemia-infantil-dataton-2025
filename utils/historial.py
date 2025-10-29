"""
utils/historial.py
Sistema de historial y resumen de cambios entre consultas
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

def guardar_consulta(id_paciente: str, datos_consulta: Dict):
    """
    Guarda snapshot de consulta en JSON ligero
    
    Args:
        id_paciente: DNI o ID único del paciente
        datos_consulta: Diccionario con datos de la consulta
    """
    historial_dir = Path("data/historial")
    historial_dir.mkdir(parents=True, exist_ok=True)
    
    snapshot = {
        'fecha': datetime.now().isoformat(),
        'hemoglobina': datos_consulta.get('hemoglobina'),
        'hemoglobina_ajustada': datos_consulta.get('hemoglobina_ajustada'),
        'score_riesgo': datos_consulta.get('probabilidad_ml'),
        'tiene_anemia': datos_consulta.get('tiene_anemia'),
        'severidad': datos_consulta.get('severidad'),
        'edad_meses': datos_consulta.get('edad_meses'),
        'recibe_suplemento': datos_consulta.get('recibe_suplemento'),
        'asiste_cred': datos_consulta.get('asiste_cred')
    }
    
    archivo = historial_dir / f"{id_paciente}.json"
    
    # Cargar historial existente
    try:
        with open(archivo, 'r') as f:
            historial = json.load(f)
    except:
        historial = []
    
    historial.append(snapshot)
    
    # Mantener solo últimas 12 consultas (1 año aprox)
    historial = historial[-12:]
    
    with open(archivo, 'w') as f:
        json.dump(historial, f, indent=2)
    
    return snapshot

def obtener_historial(id_paciente: str) -> List[Dict]:
    """Obtiene historial completo del paciente"""
    archivo = Path(f"data/historial/{id_paciente}.json")
    
    if not archivo.exists():
        return []
    
    try:
        with open(archivo, 'r') as f:
            return json.load(f)
    except:
        return []

def generar_resumen_cambios(id_paciente: str) -> Optional[Dict]:
    """
    Compara última consulta vs anterior
    
    Returns:
        Dict con resumen de cambios o None si no hay historial
    """
    historial = obtener_historial(id_paciente)
    
    if len(historial) < 2:
        return None
    
    anterior = historial[-2]
    actual = historial[-1]
    
    # Calcular deltas
    delta_hb = actual['hemoglobina'] - anterior['hemoglobina']
    delta_riesgo = actual['score_riesgo'] - anterior['score_riesgo']
    
    # Calcular días transcurridos
    from datetime import datetime
    fecha_anterior = datetime.fromisoformat(anterior['fecha'])
    fecha_actual = datetime.fromisoformat(actual['fecha'])
    dias_transcurridos = (fecha_actual - fecha_anterior).days
    
    # Tendencia
    if delta_hb > 0.5:
        tendencia = "🟢 Mejorando significativamente"
        emoji = "✅"
    elif delta_hb > 0:
        tendencia = "🟢 Mejorando levemente"
        emoji = "✅"
    elif delta_hb > -0.5:
        tendencia = "🟡 Estable"
        emoji = "⚠️"
    else:
        tendencia = "🔴 Empeorando"
        emoji = "❌"
    
    # Cambio en tratamiento
    cambio_supl = actual['recibe_suplemento'] != anterior['recibe_suplemento']
    cambio_cred = actual['asiste_cred'] != anterior['asiste_cred']
    
    resumen = {
        'fecha_anterior': fecha_anterior.strftime('%d/%m/%Y'),
        'fecha_actual': fecha_actual.strftime('%d/%m/%Y'),
        'dias_transcurridos': dias_transcurridos,
        'delta_hb': round(delta_hb, 1),
        'delta_hb_pct': round((delta_hb / anterior['hemoglobina']) * 100, 1),
        'delta_riesgo': round(delta_riesgo * 100, 1),  # En puntos porcentuales
        'tendencia': tendencia,
        'emoji': emoji,
        'cambio_supl': cambio_supl,
        'cambio_cred': cambio_cred,
        'anterior': anterior,
        'actual': actual
    }
    
    return resumen
