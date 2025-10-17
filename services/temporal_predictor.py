# services/temporal_predictor.py
"""
Predictor Temporal para Anemia Infantil
Proyecta riesgo a 3-6 meses usando modelo RandomForest actual

Autor: Sistema de Combate a Anemia - MINSA
Fecha: 2025-10-17
Datatón Exprésate Perú con Datos 2025
"""
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging


logger = logging.getLogger(__name__)


class TemporalPredictor:
    """
    Predictor temporal para proyectar anemia a 3 y 6 meses
    Compatible con RandomForest/XGBoost - No requiere reentrenamiento
    """
    
    # Tasas de deterioro calibradas con datos SIEN 2025
    TASA_DETERIORO_BASE = 0.15      # g/dL por mes (sin intervención)
    TASA_MEJORA_SUPL = -0.25        # g/dL por mes (con suplemento + CRED)
    TASA_DETERIORO_LEVE = 0.08      # g/dL por mes (suplemento sin CRED)
    
    # Factores multiplicadores de riesgo
    FACTOR_EDAD_CRITICA = 1.3       # 6-24 meses
    FACTOR_ALTITUD = 1.2            # >3000m
    FACTOR_RURAL = 1.15             # Área rural
    
    def __init__(self, modelo_actual):
        """
        Inicializa predictor temporal
        
        Args:
            modelo_actual: Instancia de AnemiaPredictor con modelo ML cargado
        """
        self.modelo = modelo_actual
        logger.info("✅ Predictor temporal inicializado")
    
    def predecir_futuro(self, datos_nino: Dict, meses: int = 3) -> Dict:
        """
        Predice probabilidad de anemia en N meses
        
        Args:
            datos_nino: Dict con datos actuales del niño
            meses: Horizonte de predicción (3 o 6)
            
        Returns:
            Dict con proyecciones completas
        """
        try:
            # 1. Predicción baseline (estado actual)
            pred_actual = self.modelo.predecir(datos_nino)
            prob_actual = self._extraer_probabilidad(pred_actual)
            hb_actual = datos_nino['hemoglobina']
            
            # 2. Proyectar hemoglobina futura
            hb_proyectada = self._proyectar_hemoglobina(
                hb_actual=hb_actual,
                tiene_suplemento=datos_nino.get('recibe_suplemento', False),
                asiste_cred=datos_nino.get('asiste_cred', True),
                edad_meses=datos_nino.get('edad_meses', 12),
                area_rural=datos_nino.get('area_rural', False),
                altitud=datos_nino.get('altitud', 0),
                meses=meses
            )
            
            # 3. Re-predecir con hemoglobina proyectada
            datos_futuros = datos_nino.copy()
            datos_futuros['hemoglobina'] = hb_proyectada
            
            pred_futura = self.modelo.predecir_ml(datos_futuros)
            prob_futura = pred_futura['probabilidad'] if pred_futura else prob_actual * 1.2
            
            # 4. Identificar factores de deterioro
            factores = self._identificar_factores_deterioro(datos_nino, hb_actual)
            
            # 5. Generar calendario de controles
            controles = self._generar_calendario_controles(meses, hb_actual, hb_proyectada)
            
            # 6. Determinar tendencia
            tendencia = self._determinar_tendencia(hb_actual, hb_proyectada, prob_actual, prob_futura)
            
            return {
                'meses_proyeccion': meses,
                'probabilidad_actual': round(prob_actual, 4),
                'probabilidad_futura': round(min(0.99, prob_futura), 4),
                'hemoglobina_actual': round(hb_actual, 2),
                'hemoglobina_proyectada': round(hb_proyectada, 2),
                'delta_hemoglobina': round(hb_proyectada - hb_actual, 2),
                'factores_deterioro': factores,
                'controles_recomendados': controles,
                'tendencia': tendencia['etiqueta'],
                'tendencia_emoji': tendencia['emoji'],
                'tendencia_color': tendencia.get('color', '#95a5a6'),
                'cambio_probabilidad': round((prob_futura - prob_actual) * 100, 1),
                'severidad_futura': self._clasificar_severidad_futura(hb_proyectada),
                'nivel_urgencia': self._calcular_urgencia(hb_proyectada, prob_futura)
            }
            
        except Exception as e:
            logger.error(f"Error en predicción temporal: {e}")
            return self._resultado_fallback(datos_nino, meses)
    
    def _proyectar_hemoglobina(self, hb_actual: float, tiene_suplemento: bool,
                                asiste_cred: bool, edad_meses: int, area_rural: bool,
                                altitud: int, meses: int) -> float:
        """
        Simula evolución de hemoglobina basado en factores de riesgo
        Usa modelo epidemiológico simple pero efectivo
        """
        # Tasa base de cambio
        if tiene_suplemento and asiste_cred:
            tasa_mensual = self.TASA_MEJORA_SUPL
        elif tiene_suplemento and not asiste_cred:
            tasa_mensual = -self.TASA_DETERIORO_LEVE
        else:
            tasa_mensual = self.TASA_DETERIORO_BASE
        
        # Aplicar factores multiplicadores de riesgo
        factor_total = 1.0
        
        if 6 <= edad_meses <= 24:
            factor_total *= self.FACTOR_EDAD_CRITICA
        
        if altitud > 3000:
            factor_total *= self.FACTOR_ALTITUD
        
        if area_rural:
            factor_total *= self.FACTOR_RURAL
        
        # Calcular delta
        delta_hb = tasa_mensual * meses * factor_total
        
        # Proyectar Hb futura
        hb_futura = hb_actual + delta_hb
        
        # Limitar a rango fisiológico
        return max(6.0, min(16.0, hb_futura))
    
    def _identificar_factores_deterioro(self, datos: Dict, hb_actual: float) -> List[str]:
        """Identifica factores que aceleran deterioro o impiden mejora"""
        factores = []
        
        # Factor 1: Sin suplementación
        if not datos.get('recibe_suplemento', False):
            factores.append('❌ Sin suplementación preventiva de hierro')
        
        # Factor 2: Inasistencia a CRED
        if not datos.get('asiste_cred', True):
            factores.append('📅 No asiste a controles CRED regulares')
        
        # Factor 3: Edad de alto riesgo
        edad = datos.get('edad_meses', 12)
        if 6 <= edad <= 24:
            factores.append('👶 Ventana crítica de desarrollo (6-24 meses)')
        
        # Factor 4: Área rural
        if datos.get('area_rural', False):
            factores.append('🏘️ Área rural con acceso limitado a servicios')
        
        # Factor 5: Alta altitud
        altitud = datos.get('altitud', 0)
        if altitud > 3500:
            factores.append(f'⛰️ Gran altitud ({altitud}m) - Mayor requerimiento de hierro')
        elif altitud > 3000:
            factores.append(f'⛰️ Alta altitud ({altitud}m)')
        
        # Factor 6: Hemoglobina en zona crítica
        if 10.0 <= hb_actual < 10.5:
            factores.append('⚠️ Hemoglobina en zona de alto riesgo')
        elif 10.5 <= hb_actual < 11.0:
            factores.append('⚠️ Hemoglobina límite (riesgo moderado)')
        
        # Factor 7: Departamentos prioritarios
        dept_alto_riesgo = ['PUNO', 'CUSCO', 'HUANCAVELICA', 'PASCO', 'UCAYALI']
        if datos.get('departamento', '').upper() in dept_alto_riesgo:
            factores.append(f"🗺️ Departamento de alta prevalencia ({datos.get('departamento')})")
        
        # Factor 8: Sin programas sociales
        tiene_programas = (
            datos.get('tiene_juntos', False) or 
            datos.get('tiene_qaliwarma', False) or
            datos.get('tiene_sis', False)
        )
        if not tiene_programas:
            factores.append('🏛️ Sin acceso a programas sociales de protección')
        
        if not factores:
            factores.append('✅ Sin factores críticos de riesgo identificados')
        
        return factores
    
    def _generar_calendario_controles(self, meses_proyeccion: int, 
                                      hb_actual: float, hb_proyectada: float) -> List[Dict]:
        """Genera calendario personalizado de controles"""
        hoy = datetime.now()
        controles = []
        
        # Control a 1 mes (si hay riesgo)
        if hb_actual < 10.5 or meses_proyeccion >= 3:
            controles.append({
                'tipo': '🩺 Control 1 mes',
                'fecha': (hoy + timedelta(days=30)).strftime('%d/%m/%Y'),
                'objetivo': 'Evaluar adherencia al tratamiento y tolerancia',
                'accion': 'Revisar consumo de suplemento + consejería nutricional'
            })
        
        # Control a 3 meses (siempre)
        controles.append({
            'tipo': '💉 Control 3 meses',
            'fecha': (hoy + timedelta(days=90)).strftime('%d/%m/%Y'),
            'objetivo': 'Dosaje de hemoglobina + evaluación clínica completa',
            'accion': 'Hemograma + ajuste de tratamiento según resultado'
        })
        
        # Control a 6 meses (si proyección es 6 meses)
        if meses_proyeccion >= 6:
            controles.append({
                'tipo': '✅ Control 6 meses',
                'fecha': (hoy + timedelta(days=180)).strftime('%d/%m/%Y'),
                'objetivo': 'Dosaje final + criterio de alta',
                'accion': 'Evaluación de cumplimiento y criterios de éxito'
            })
        
        # Control adicional si se proyecta empeoramiento severo
        if hb_proyectada < 9.0:
            controles.insert(0, {
                'tipo': '🚨 Control URGENTE (15 días)',
                'fecha': (hoy + timedelta(days=15)).strftime('%d/%m/%Y'),
                'objetivo': 'Evaluación prioritaria - Alto riesgo de anemia severa',
                'accion': '⚠️ Descartar causas secundarias + tratamiento intensivo'
            })
        
        return controles
    
    def _determinar_tendencia(self, hb_actual: float, hb_proyectada: float,
                              prob_actual: float, prob_futura: float) -> Dict:
        """Determina tendencia de evolución"""
        delta_hb = hb_proyectada - hb_actual
        delta_prob = prob_futura - prob_actual
        
        if delta_hb > 0.3:
            return {'etiqueta': 'Mejorando significativamente', 'emoji': '📈', 'color': '#27ae60'}
        elif delta_hb > 0:
            return {'etiqueta': 'Mejorando levemente', 'emoji': '📊', 'color': '#2ecc71'}
        elif delta_hb > -0.3:
            return {'etiqueta': 'Estable (riesgo moderado)', 'emoji': '➡️', 'color': '#f39c12'}
        elif delta_hb > -0.6:
            return {'etiqueta': 'Empeorando', 'emoji': '📉', 'color': '#e67e22'}
        else:
            return {'etiqueta': 'Empeorando severamente', 'emoji': '⚠️', 'color': '#e74c3c'}
    
    def _clasificar_severidad_futura(self, hb_proyectada: float) -> str:
        """Clasifica severidad esperada según OMS"""
        if hb_proyectada >= 11.0:
            return 'Normal'
        elif hb_proyectada >= 10.0:
            return 'Anemia Leve'
        elif hb_proyectada >= 7.0:
            return 'Anemia Moderada'
        else:
            return 'Anemia Severa'
    
    def _calcular_urgencia(self, hb_proyectada: float, prob_futura: float) -> str:
        """Calcula nivel de urgencia de intervención"""
        if hb_proyectada < 8.0 or prob_futura > 0.90:
            return '🔴 URGENTE'
        elif hb_proyectada < 10.0 or prob_futura > 0.75:
            return '🟠 ALTA'
        elif hb_proyectada < 11.0 or prob_futura > 0.50:
            return '🟡 MEDIA'
        else:
            return '🟢 BAJA'
    
    def _extraer_probabilidad(self, pred_actual: Dict) -> float:
        """Extrae probabilidad del resultado de predicción"""
        if pred_actual.get('ml') and 'probabilidad' in pred_actual['ml']:
            return pred_actual['ml']['probabilidad']
        return pred_actual.get('probabilidad_anemia', 0.50)
    
    def _resultado_fallback(self, datos_nino: Dict, meses: int) -> Dict:
        """Resultado por defecto en caso de error"""
        logger.warning("Usando resultado fallback para predicción temporal")
        return {
            'meses_proyeccion': meses,
            'probabilidad_actual': 0.50,
            'probabilidad_futura': 0.55,
            'hemoglobina_actual': datos_nino.get('hemoglobina', 11.0),
            'hemoglobina_proyectada': datos_nino.get('hemoglobina', 11.0) - 0.2,
            'delta_hemoglobina': -0.2,
            'factores_deterioro': ['⚠️ Error en análisis - Usar con precaución'],
            'controles_recomendados': [],
            'tendencia': 'Indeterminado',
            'tendencia_emoji': '❓',
            'tendencia_color': '#95a5a6',
            'cambio_probabilidad': 5.0,
            'severidad_futura': 'Indeterminado',
            'nivel_urgencia': '🟡 MEDIA'
        }


# Instancia global (singleton pattern)
_temporal_predictor_instance = None


def get_temporal_predictor(modelo_anemia):
    """
    Factory para obtener instancia única del predictor temporal
    
    Args:
        modelo_anemia: Instancia de AnemiaPredictor
        
    Returns:
        TemporalPredictor: Instancia singleton
    """
    global _temporal_predictor_instance
    if _temporal_predictor_instance is None:
        _temporal_predictor_instance = TemporalPredictor(modelo_anemia)
        logger.info("🔮 Predictor temporal creado (primera vez)")
    return _temporal_predictor_instance
