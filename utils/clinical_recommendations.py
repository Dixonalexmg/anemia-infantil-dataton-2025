# utils/clinical_recommendations.py
"""
Recomendaciones clínicas basadas en NTS 213-MINSA/DGIESP-2024
Genera protocolos específicos por grupo etario según normativa vigente
"""
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class ClinicalProtocols:
    """Protocolos clínicos oficiales MINSA para prevención y tratamiento de anemia"""
    
    # Dosificación según NTS 213-2024
    DOSIS_PREVENTIVA = {
        'RN_bajo_peso': {'dosis': '2 mg/kg/día', 'inicio': 30, 'duracion_meses': 6, 'presentacion': 'Gotas'},
        '0-5_meses': {'dosis': '2 mg/kg/día', 'inicio': 120, 'duracion_meses': 2, 'presentacion': 'Gotas'},
        '6-11_meses': {'dosis': '2 mg/kg/día', 'duracion_meses': 6, 'presentacion': 'Gotas/MMN'},
        '12-23_meses': {'dosis': '2 mg/kg/día', 'duracion_meses': 6, 'presentacion': 'Gotas/Jarabe/MMN', 'descanso': 3},
        '24-35_meses': {'dosis': '30 mg Fe elemental', 'duracion_meses': 6, 'presentacion': 'Jarabe/MMN'},
        '36-59_meses': {'dosis': '30 mg Fe elemental', 'duracion_meses': 3, 'presentacion': 'Jarabe/MMN'},
        '5-11_años': {'dosis': '60 mg Fe elemental', 'duracion_meses': 3, 'presentacion': 'Tabletas'},
        'adolescente': {'dosis': '60 mg Fe + 400µg Ácido Fólico', 'frecuencia': '2 veces/semana', 'duracion_meses': 3},
        'gestante': {'dosis': '60 mg Fe + 400µg Ácido Fólico', 'frecuencia': 'Diaria', 'duracion': 'Hasta 30 días posparto'}
    }
    
    DOSIS_TRATAMIENTO = {
        '<36_meses': {'dosis': '3 mg/kg/día', 'duracion_meses': 6, 'presentacion': 'Gotas/Jarabe'},
        '36m-11años': {'dosis': '3 mg/kg/día', 'duracion_meses': 6, 'presentacion': 'Jarabe/Tabletas'},
        'adolescente': {'dosis': '60 mg Fe + 400µg Ácido Fólico', 'frecuencia': 'Diaria', 'duracion_meses': 6},
        'gestante': {'dosis': '120 mg Fe + 800µg Ácido Fólico', 'frecuencia': 'Diaria', 'duracion': 'Hasta 30 días posparto'}
    }
    
    @staticmethod
    def get_grupo_etario(edad_meses: int, es_bajo_peso: bool = False, es_prematuro: bool = False) -> str:
        """Determina grupo etario según NTS 213-2024"""
        if es_bajo_peso or es_prematuro:
            return 'RN_bajo_peso'
        elif edad_meses < 6:
            return '0-5_meses'
        elif 6 <= edad_meses < 12:
            return '6-11_meses'
        elif 12 <= edad_meses < 24:
            return '12-23_meses'
        elif 24 <= edad_meses < 36:
            return '24-35_meses'
        elif 36 <= edad_meses < 60:
            return '36-59_meses'
        elif 60 <= edad_meses < 144:
            return '5-11_años'
        else:
            return 'adolescente'
    
    @staticmethod
    def calcular_dosis_individual(peso_kg: float, dosis_mg_kg: float, concentracion_mg_ml: float = 25) -> Dict[str, float]:
        """
        Calcula dosis específica para el niño
        Args:
            peso_kg: Peso del niño en kg
            dosis_mg_kg: Dosis en mg/kg (2 o 3 según sea preventiva o tratamiento)
            concentracion_mg_ml: Concentración del sulfato ferroso (25mg/ml por defecto)
        Returns:
            Dict con dosis en mg y gotas/ml
        """
        dosis_mg = peso_kg * dosis_mg_kg
        dosis_ml = dosis_mg / concentracion_mg_ml
        dosis_gotas = dosis_ml * 20  # 1 ml = 20 gotas aproximadamente
        
        return {
            'dosis_mg': round(dosis_mg, 1),
            'dosis_ml': round(dosis_ml, 2),
            'dosis_gotas': round(dosis_gotas, 0)
        }


def generar_recomendaciones_personalizadas(
    edad_meses: int,
    peso_kg: float,
    tiene_anemia: bool,
    factores_riesgo: List[str],
    hb_actual: float,
    altitud_m: int = 0,
    es_bajo_peso: bool = False,
    es_prematuro: bool = False
) -> Dict[str, any]:
    """
    Genera recomendaciones clínicas personalizadas según NTS 213-2024
    
    Args:
        edad_meses: Edad en meses
        peso_kg: Peso en kilogramos
        tiene_anemia: Diagnóstico de anemia
        factores_riesgo: Lista de factores identificados
        hb_actual: Hemoglobina actual (g/dL)
        altitud_m: Altitud en metros
        es_bajo_peso: Nació con bajo peso (<2500g)
        es_prematuro: Nació prematuro (<37 semanas)
    
    Returns:
        Dict con protocolo completo personalizado
    """
    
    protocols = ClinicalProtocols()
    grupo = protocols.get_grupo_etario(edad_meses, es_bajo_peso, es_prematuro)
    
    # Seleccionar dosis según tenga o no anemia
    if tiene_anemia:
        if edad_meses < 36:
            dosis_config = protocols.DOSIS_TRATAMIENTO['<36_meses']
            dosis_mg_kg = 3
        elif edad_meses < 144:
            dosis_config = protocols.DOSIS_TRATAMIENTO['36m-11años']
            dosis_mg_kg = 3
        else:
            dosis_config = protocols.DOSIS_TRATAMIENTO['adolescente']
            dosis_mg_kg = None
        tipo_intervencion = 'TRATAMIENTO'
    else:
        dosis_config = protocols.DOSIS_PREVENTIVA.get(grupo, protocols.DOSIS_PREVENTIVA['6-11_meses'])
        dosis_mg_kg = 2 if 'mg/kg' in dosis_config['dosis'] else None
        tipo_intervencion = 'PREVENCIÓN'
    
    # Calcular dosis individual si aplica
    dosis_calculada = None
    if dosis_mg_kg and peso_kg:
        dosis_calculada = protocols.calcular_dosis_individual(peso_kg, dosis_mg_kg)
    
    # Alimentación según edad (basado en guías MINSA)
    alimentacion = generar_recomendaciones_alimentarias(edad_meses, tiene_anemia, altitud_m)
    
    # Controles según protocolo
    frecuencia_controles = generar_calendario_controles(edad_meses, tiene_anemia)
    
    # Alertas prioritarias
    alertas = []
    if 'sin_suplemento' in factores_riesgo:
        alertas.append('🚨 INICIAR SUPLEMENTACIÓN HOY MISMO - Factor de riesgo crítico detectado')
    if altitud_m > 3000:
        alertas.append(f'⛰️ Zona de gran altitud ({altitud_m}m) - Ajuste de Hb ya aplicado')
    if 6 <= edad_meses <= 24:
        alertas.append('⚠️ Ventana crítica de desarrollo cerebral - Prevención prioritaria')
    if es_bajo_peso or es_prematuro:
        alertas.append('👶 Condición especial al nacer - Protocolo diferenciado aplicado')
    
    return {
        'grupo_etario': grupo,
        'tipo_intervencion': tipo_intervencion,
        'edad_meses': edad_meses,
        'peso_kg': peso_kg,
        'tiene_anemia': tiene_anemia,
        'dosis_config': dosis_config,
        'dosis_calculada': dosis_calculada,
        'alimentacion': alimentacion,
        'frecuencia_controles': frecuencia_controles,
        'alertas_prioritarias': alertas,
        'normativa': 'NTS 213-MINSA/DGIESP-2024'
    }


def generar_recomendaciones_alimentarias(edad_meses: int, tiene_anemia: bool, altitud_m: int) -> Dict[str, List[str]]:
    """Genera recomendaciones alimentarias específicas por edad"""
    
    if edad_meses < 6:
        return {
            'principal': ['🤱 Lactancia materna exclusiva a libre demanda'],
            'evitar': ['❌ NO dar ningún otro alimento o líquido'],
            'nota': 'La leche materna cubre todas las necesidades nutricionales hasta los 6 meses'
        }
    
    elif 6 <= edad_meses < 12:
        alimentos_base = [
            '🥩 Hígado de pollo/res molido o licuado: 10-20g, 2-3 veces/semana',
            '🍖 Sangrecita licuada o bazo: 10-15g, 2 veces/semana',
            '🥚 Yema de huevo cocida (iniciar gradualmente): diario',
            '🫘 Lentejas/frijoles pasados por tamiz: 3 veces/semana',
            '🥬 Espinaca/acelga bien cocida y licuada con jugo de limón'
        ]
        
        evitar = [
            '❌ Té, café o infusiones cerca de comidas (bloquean absorción de hierro)',
            '❌ Leche de vaca antes del año',
            '✅ Dar vitamina C (frutas cítricas) después de comidas con hierro'
        ]
        
        if tiene_anemia:
            alimentos_base.insert(0, '⚠️ AUMENTAR frecuencia de alimentos ricos en hierro a diario')
        
        return {
            'principal': alimentos_base,
            'evitar': evitar,
            'nota': '🤱 Continuar lactancia materna + alimentación complementaria'
        }
    
    elif 12 <= edad_meses < 24:
        return {
            'principal': [
                '🥩 Sangrecita/hígado/carne roja: 30-50g, 3-4 veces/semana',
                '🍗 Pollo/pescado: 30-40g, 4 veces/semana',
                '🫘 Menestras (lentejas, frijoles, garbanzos): 3 veces/semana',
                '🥚 Huevo entero: diario',
                '🥬 Verduras de hoja verde con limón/naranja'
            ],
            'evitar': [
                '🚫 NO dar lácteos en comida principal (bloquean hierro)',
                '🚫 Evitar té/café/bebidas azucaradas',
                '✅ Dar cítricos post-comida para aumentar absorción'
            ],
            'nota': '🤱 Continuar lactancia materna a demanda + 3 comidas principales + 2 refrigerios'
        }
    
    elif 24 <= edad_meses < 60:
        return {
            'principal': [
                '🥩 Carnes rojas magras: 50-70g, 4-5 veces/semana',
                '🍖 Hígado/sangrecita/bazo: 40-60g, 2 veces/semana',
                '🫘 Menestras variadas: 4 veces/semana',
                '🥚 Huevo: diario',
                '🥗 Ensaladas con verduras verdes y cítricos',
                '🍊 Frutas: naranja, papaya, plátano (post-comida)'
            ],
            'evitar': [
                '🚫 Separar lácteos de comidas principales (2 horas antes/después)',
                '🚫 Limitar comida chatarra y azúcares',
                '✅ Combinar alimentos ricos en hierro con vitamina C'
            ],
            'nota': 'Dieta familiar variada con énfasis en proteína animal y hierro'
        }
    
    else:  # 5 años en adelante
        return {
            'principal': [
                '🥩 Proteína animal magra en almuerzo y cena',
                '🫘 Menestras 3-4 veces/semana',
                '🥗 Ensalada verde en almuerzo y cena',
                '🍊 Frutas cítricas post-comida',
                '🥜 Frutos secos (si no hay alergia)'
            ],
            'evitar': [
                '🚫 Comida rápida/procesada',
                '🚫 Bebidas azucaradas con comidas',
                '✅ Hidratación con agua natural'
            ],
            'nota': 'Promover hábitos saludables permanentes'
        }


def generar_calendario_controles(edad_meses: int, tiene_anemia: bool) -> Dict[str, str]:
    """Genera calendario de controles según NTS 213-2024"""
    
    if tiene_anemia:
        return {
            'primer_control': '1 mes después de iniciar tratamiento',
            'controles_seguimiento': 'Mensual hasta el 3er mes',
            'control_final': '6 meses (finalización de tratamiento)',
            'criterio_alta': 'Hb normalizada + 6 meses de tratamiento completado',
            'accion_si_no_mejora': 'Referencia a especialista (pediatra/hematólogo)'
        }
    else:
        if edad_meses < 12:
            return {
                'frecuencia': 'Mensual (CRED)',
                'dosaje_hb': 'A los 6 meses, al 3er mes de suplementación, al finalizar (6 meses)',
                'visita_domiciliaria': 'A los 7 días de iniciar + seguimiento mensual'
            }
        elif 12 <= edad_meses < 24:
            return {
                'frecuencia': 'Cada 2 meses (CRED)',
                'dosaje_hb': 'Antes de iniciar, al 3er mes, al finalizar',
                'periodo_descanso': '3 meses si Hb ≥10.5 g/dL a los 12 meses'
            }
        elif 24 <= edad_meses < 60:
            return {
                'frecuencia': 'Cada 3 meses (CRED)',
                'dosaje_hb': '2 veces al año (inicio y fin de suplementación)'
            }
        else:
            return {
                'frecuencia': 'Cada 6 meses',
                'dosaje_hb': '1 vez al año'
            }
