"""
utils/feedback.py
Sistema de feedback y métrica de comprensión
"""
import json
from datetime import datetime
from pathlib import Path
import pandas as pd

def guardar_feedback(caso_id: str, comprension: int, util: bool,
                     preparó_menu: bool = None, comentario: str = ""):
    """
    Guarda feedback del usuario
    
    Args:
        caso_id: ID único del caso
        comprension: 0 (no entendí), 50 (dudas), 100 (muy claro)
        util: Boolean si fue útil
        preparó_menu: Boolean si preparó el menú (para HU-02)
        comentario: Texto libre opcional
    
    Returns:
        Dict con el feedback guardado
    """
    feedback_dir = Path("data/feedback")
    feedback_dir.mkdir(parents=True, exist_ok=True)

    feedback = {
        'caso_id': caso_id,
        'timestamp': datetime.now().isoformat(),
        'comprension_score': comprension,
        'fue_util': util,
        'preparó_menu': preparó_menu,
        'comentario': comentario
    }

    # Guardar archivo individual
    archivo = feedback_dir / f"{caso_id}.json"
    with open(archivo, 'w') as f:
        json.dump(feedback, f, indent=2)
    
    # ✨ AGREGAR: También guardar en log consolidado
    log_file = feedback_dir / "feedback_log.csv"
    
    # Crear archivo si no existe
    if not log_file.exists():
        import csv
        with open(log_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'caso_id', 'comprension', 'util', 'comentario'])
    
    # Agregar registro
    import csv
    with open(log_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            feedback['timestamp'],
            caso_id,
            comprension,
            util,
            comentario
        ])

    return feedback

# ... (resto del código igual)


def calcular_metrica_comprension():
    """Calcula % de comprensión global (objetivo: 80-90%)"""
    feedback_dir = Path("data/feedback")
    
    if not feedback_dir.exists():
        return {
            'comprension_pct': 0,
            'n_total': 0,
            'n_muy_claro': 0,
            'n_dudas': 0,
            'n_no_entendí': 0,
            'objetivo_cumplido': False
        }
    
    feedbacks = []
    for archivo in feedback_dir.glob("*.json"):
        try:
            with open(archivo, 'r') as f:
                feedbacks.append(json.load(f))
        except:
            continue
    
    if not feedbacks:
        return {
            'comprension_pct': 0,
            'n_total': 0,
            'n_muy_claro': 0,
            'n_dudas': 0,
            'n_no_entendí': 0,
            'objetivo_cumplido': False
        }
    
    n_muy_claro = len([f for f in feedbacks if f['comprension_score'] == 100])
    n_dudas = len([f for f in feedbacks if f['comprension_score'] == 50])
    n_no_entendí = len([f for f in feedbacks if f['comprension_score'] == 0])
    
    comprension_pct = (n_muy_claro / len(feedbacks)) * 100
    
    return {
        'comprension_pct': round(comprension_pct, 1),
        'n_total': len(feedbacks),
        'n_muy_claro': n_muy_claro,
        'n_dudas': n_dudas,
        'n_no_entendí': n_no_entendí,
        'objetivo_cumplido': comprension_pct >= 80
    }

def exportar_feedbacks_csv():
    """Exporta todos los feedbacks a CSV para análisis"""
    feedback_dir = Path("data/feedback")
    
    if not feedback_dir.exists():
        return None
    
    feedbacks = []
    for archivo in feedback_dir.glob("*.json"):
        try:
            with open(archivo, 'r') as f:
                feedbacks.append(json.load(f))
        except:
            continue
    
    if not feedbacks:
        return None
    
    df = pd.DataFrame(feedbacks)
    output_path = feedback_dir / "feedbacks_export.csv"
    df.to_csv(output_path, index=False)
    
    return output_path
