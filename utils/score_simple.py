"""
utils/score_simple.py
Sistema de score único y explicable (reemplaza clasificar_nivel_riesgo)
"""

def calcular_score_simple(probabilidad_ml, top_factores):
    """
    Score único basado SOLO en ML + explicación simple
    
    Args:
        probabilidad_ml: float (0-1)
        top_factores: list de tuples (factor, impacto, descripcion)
    
    Returns:
        dict con score, nivel, color, explicacion
    """
    
    # Convertir probabilidad a nivel
    if probabilidad_ml < 0.20:
        nivel = "RIESGO BAJO"
        emoji = "🟢"
        color = "#28a745"
        mensaje = "Tu bebé está bien. Mantén los controles preventivos."
    elif probabilidad_ml < 0.50:
        nivel = "RIESGO MODERADO"
        emoji = "🟡"
        color = "#ffc107"
        mensaje = "Necesita atención. Programa control CRED en 15 días."
    elif probabilidad_ml < 0.75:
        nivel = "RIESGO ALTO"
        emoji = "🟠"
        color = "#ff9800"
        mensaje = "Atención urgente. Inicia tratamiento HOY y control en 7 días."
    else:
        nivel = "RIESGO CRÍTICO"
        emoji = "🔴"
        color = "#dc3545"
        mensaje = "CRÍTICO. Evaluación médica inmediata + hospitalización si es necesario."
    
    # Explicación en lenguaje simple
    prob_pct = int(probabilidad_ml * 100)
    
    if prob_pct < 30:
        explicacion = f"De cada 10 niños como el tuyo, solo {prob_pct//10} tiene anemia."
    elif prob_pct < 70:
        explicacion = f"De cada 10 niños como el tuyo, {prob_pct//10} tiene anemia."
    else:
        explicacion = f"De cada 10 niños como el tuyo, {prob_pct//10} o más tiene anemia."
    
    # Top 3 factores explicables
    top_3_explicaciones = []
    if top_factores:
        for i, (factor, impacto, desc) in enumerate(top_factores[:3], 1):
            # Convertir impacto a lenguaje simple
            if impacto > 0.1:
                influencia = "MUCHA"
            elif impacto > 0.05:
                influencia = "BASTANTE"
            else:
                influencia = "ALGO de"
            
            top_3_explicaciones.append(f"{i}. **{desc}** tiene {influencia} influencia")
    
    return {
        'nivel': nivel,
        'emoji': emoji,
        'color': color,
        'probabilidad_pct': prob_pct,
        'mensaje': mensaje,
        'explicacion': explicacion,
        'top_3_factores': top_3_explicaciones
    }
