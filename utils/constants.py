"""
utils/constants.py
Constantes globales del sistema - OMS 2024
"""

# ============================================================================
# CONSTANTES OMS 2024
# ============================================================================

# Umbrales de anemia por edad (g/dL)
UMBRAL_ANEMIA = {
    '6-59_meses': 11.0,
    '5-11_anos': 11.5,
    '12-14_anos': 12.0,
    'mujeres_no_embarazadas': 12.0,
    'mujeres_embarazadas': 11.0,
    'hombres': 13.0
}

# Clasificación de severidad
SEVERIDAD_ANEMIA = {
    'leve': (10.0, 10.9),
    'moderada': (7.0, 9.9),
    'severa': (0.0, 6.9)
}

# Ajuste de hemoglobina por altitud (OMS 2024)
AJUSTE_ALTITUD = {
    (0, 1000): 0.0,
    (1000, 1500): 0.2,
    (1500, 2000): 0.5,
    (2000, 2500): 0.8,
    (2500, 3000): 1.3,
    (3000, 3500): 1.9,
    (3500, 4000): 2.7,
    (4000, 4500): 3.5,
    (4500, 5000): 4.5
}

# Altitudes por departamento (capital departamental en msnm)
ALTITUDES_DEPARTAMENTO = {
    'AMAZONAS': 2300, 'ANCASH': 3100, 'APURIMAC': 2900, 'AREQUIPA': 2350,
    'AYACUCHO': 2750, 'CAJAMARCA': 2750, 'CALLAO': 10, 'CUSCO': 3400,
    'HUANCAVELICA': 3680, 'HUANUCO': 1900, 'ICA': 400, 'JUNIN': 3250,
    'LA LIBERTAD': 2800, 'LAMBAYEQUE': 30, 'LIMA': 150, 'LORETO': 120,
    'MADRE DE DIOS': 260, 'MOQUEGUA': 1400, 'PASCO': 4350, 'PIURA': 30,
    'PUNO': 3850, 'SAN MARTIN': 280, 'TACNA': 560, 'TUMBES': 10, 'UCAYALI': 150
}

# ============================================================================
# SEMÁFORO DE RIESGO
# ============================================================================

SEMAFORO_CONFIG = {
    'verde': {
        'umbral_max': 0.30,
        'color': '#28a745',
        'background': '#d4edda',
        'emoji': '🟢',
        'nivel': 'RIESGO BAJO',
        'accion': 'Continuar con controles preventivos CRED'
    },
    'amarillo': {
        'umbral_min': 0.30,
        'umbral_max': 0.60,
        'color': '#ffc107',
        'background': '#fff3cd',
        'emoji': '🟡',
        'nivel': 'RIESGO MODERADO',
        'accion': 'Reforzar suplementación y seguimiento mensual'
    },
    'rojo': {
        'umbral_min': 0.60,
        'color': '#dc3545',
        'background': '#f8d7da',
        'emoji': '🔴',
        'nivel': 'RIESGO ALTO',
        'accion': 'Intervención inmediata - Protocolo de tratamiento'
    }
}

# ============================================================================
# GRUPOS ETARIOS
# ============================================================================

GRUPOS_ETARIOS = {
    '6-11_meses': (6, 11),
    '12-23_meses': (12, 23),
    '24-35_meses': (24, 35),
    '36-47_meses': (36, 47),
    '48-59_meses': (48, 59)
}

# ============================================================================
# DOSIS DE SUPLEMENTACIÓN (NTS 213-MINSA/DGIESP-2024)
# ============================================================================

DOSIS_HIERRO = {
    'preventivo': {
        'dosis_mg_kg_dia': 2.0,
        'duracion_meses': 6
    },
    'tratamiento': {
        'dosis_mg_kg_dia': 3.0,
        'duracion_meses': 6
    },
    'gotas_por_ml': 20,  # Sulfato ferroso
    'mg_hierro_por_ml': 25  # 125mg sulfato ferroso = 25mg hierro elemental
}

# ============================================================================
# REQUERIMIENTOS NUTRICIONALES
# ============================================================================

REQUERIMIENTO_HIERRO_MG_DIA = {
    '6-11_meses': 11.0,
    '12-23_meses': 7.0,
    '24-59_meses': 10.0
}

# ============================================================================
# COLORES Y ESTILOS
# ============================================================================

COLORES = {
    'primario': '#667eea',
    'secundario': '#764ba2',
    'exito': '#28a745',
    'advertencia': '#ffc107',
    'peligro': '#dc3545',
    'info': '#17a2b8',
    'gris': '#6c757d'
}

# ============================================================================
# TEXTOS ESTÁNDAR
# ============================================================================

TEXTO_ACCION_INMEDIATA = {
    'bajo': 'Continuar con controles preventivos CRED según calendario',
    'moderado': 'Reforzar suplementación de hierro y programar seguimiento mensual',
    'alto': 'Iniciar protocolo de tratamiento INMEDIATO. Control en 7 días',
    'critico': '🚨 URGENTE: Evaluación médica inmediata. Posible hospitalización'
}

TEXTO_NORMATIVA = "NTS 213-MINSA/DGIESP-2024 - Manejo Terapéutico y Preventivo de Anemia en Niños"
