# utils/risk_classifier.py
"""
Clasificador de riesgo con sistema de semáforo (verde/ámbar/rojo)
Cumple con requisitos del concurso: alertas tempranas visuales
"""
from typing import Dict
import logging

logger = logging.getLogger(__name__)


def clasificar_nivel_riesgo(
    probabilidad_ml: float,
    tiene_anemia: bool,
    edad_meses: int,
    factores_riesgo: list,
    hb_actual: float
) -> Dict[str, any]:
    """
    Clasifica riesgo en semáforo verde/ámbar/rojo
    
    Priorización según:
    1. Anemia confirmada (siempre crítico)
    2. Ventana de desarrollo crítico (< 24 meses)
    3. Probabilidad ML
    4. Múltiples factores de riesgo
    
    Returns:
        Dict con nivel, color, emoji, urgencia, background
    """
    
    # 🔴 ROJO - CRÍTICO: Anemia confirmada
    if tiene_anemia:
        if hb_actual < 7.0:
            return {
                'nivel': 'CRÍTICO - ANEMIA SEVERA',
                'color': 'rojo',
                'emoji': '🆘',
                'urgencia': 'DERIVACIÓN HOSPITALARIA URGENTE',
                'background': '#d32f2f',
                'accion_inmediata': 'Referir a hospital de inmediato para evaluación de transfusión',
                'prioridad': 1
            }
        elif hb_actual < 10.0:
            return {
                'nivel': 'CRÍTICO - ANEMIA MODERADA',
                'color': 'rojo',
                'emoji': '🔴',
                'urgencia': 'INICIAR TRATAMIENTO HOY',
                'background': '#e53935',
                'accion_inmediata': 'Iniciar sulfato ferroso 3mg/kg/día + control en 1 mes',
                'prioridad': 2
            }
        else:
            return {
                'nivel': 'ALERTA - ANEMIA LEVE',
                'color': 'rojo',
                'emoji': '⚠️',
                'urgencia': 'TRATAMIENTO INMEDIATO',
                'background': '#ef5350',
                'accion_inmediata': 'Iniciar tratamiento + seguimiento estricto',
                'prioridad': 3
            }
    
    # 🔴 ROJO - ALTO RIESGO: Ventana crítica + alta probabilidad
    if edad_meses < 24 and probabilidad_ml >= 0.70:
        return {
            'nivel': 'ALTO RIESGO - PREVENCIÓN URGENTE',
            'color': 'rojo',
            'emoji': '🚨',
            'urgencia': 'INICIAR PREVENCIÓN AHORA',
            'background': '#ff6b6b',
            'accion_inmediata': 'Ventana crítica de desarrollo. Iniciar suplementación preventiva hoy.',
            'prioridad': 4
        }
    
    # 🟠 ÁMBAR - RIESGO MODERADO
    if probabilidad_ml >= 0.60:
        return {
            'nivel': 'RIESGO MODERADO',
            'color': 'ambar',
            'emoji': '⚠️',
            'urgencia': 'INICIAR PREVENCIÓN',
            'background': '#ff9800',
            'accion_inmediata': 'Evaluar factores de riesgo e iniciar suplementación preventiva',
            'prioridad': 5
        }
    
    # 🟡 ÁMBAR BAJO - VIGILANCIA
    if probabilidad_ml >= 0.40 or len(factores_riesgo) >= 2:
        return {
            'nivel': 'RIESGO BAJO-MODERADO',
            'color': 'ambar_claro',
            'emoji': '⚡',
            'urgencia': 'VIGILANCIA Y PREVENCIÓN',
            'background': '#ffa726',
            'accion_inmediata': 'Seguimiento en controles CRED. Considerar suplementación si hay factores.',
            'prioridad': 6
        }
    
    # 🟢 VERDE - BAJO RIESGO
    return {
        'nivel': 'BAJO RIESGO',
        'color': 'verde',
        'emoji': '✅',
        'urgencia': 'SEGUIMIENTO DE RUTINA',
        'background': '#4caf50',
        'accion_inmediata': 'Continuar controles CRED regulares y alimentación adecuada',
        'prioridad': 7
    }


def extraer_factores_criticos(factores_riesgo_list: list, top_n: int = 3) -> list:
    """
    Extrae los factores más críticos para mostrar en alerta
    
    Args:
        factores_riesgo_list: Lista de factores identificados por SHAP
        top_n: Número de factores a mostrar
    
    Returns:
        Lista de factores priorizados con descripción clínica
    """
    
    # Mapeo de features técnicos a lenguaje clínico
    mapeo_clinico = {
        'sin_suplemento': {
            'nombre': 'Sin suplementación de hierro',
            'criticidad': 1,
            'emoji': '💊',
            'descripcion': 'No recibe sulfato ferroso preventivo'
        },
        'edad_6_24m': {
            'nombre': 'Edad de máxima vulnerabilidad',
            'criticidad': 2,
            'emoji': '👶',
            'descripcion': 'Ventana crítica de desarrollo cerebral (6-24 meses)'
        },
        'alta_altitud': {
            'nombre': 'Zona de gran altitud',
            'criticidad': 3,
            'emoji': '⛰️',
            'descripcion': 'Residencia en altura (>3000 msnm)'
        },
        'sin_cred': {
            'nombre': 'No asiste a controles CRED',
            'criticidad': 1,
            'emoji': '📋',
            'descripcion': 'Falta de seguimiento regular'
        },
        'area_rural': {
            'nombre': 'Área rural',
            'criticidad': 4,
            'emoji': '🏘️',
            'descripcion': 'Menor acceso a servicios de salud'
        },
        'bajo_peso': {
            'nombre': 'Bajo peso al nacer',
            'criticidad': 2,
            'emoji': '⚖️',
            'descripcion': 'Nació con menos de 2500g'
        },
        'prematuro': {
            'nombre': 'Prematuro',
            'criticidad': 2,
            'emoji': '🍼',
            'descripcion': 'Nacimiento antes de 37 semanas'
        },
        'sin_sis': {
            'nombre': 'Sin seguro de salud',
            'criticidad': 3,
            'emoji': '🏥',
            'descripcion': 'No afiliado al SIS'
        }
    }
    
    # Ordenar por criticidad
    factores_mapeados = []
    for factor in factores_riesgo_list:
        if factor in mapeo_clinico:
            info = mapeo_clinico[factor].copy()
            factores_mapeados.append(info)
    
    factores_mapeados.sort(key=lambda x: x['criticidad'])
    
    return factores_mapeados[:top_n]
