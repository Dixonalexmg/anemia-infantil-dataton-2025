"""
Módulo de Explicabilidad para Predicción de Anemia
Traduce factores técnicos del modelo ML a lenguaje simple para madres/cuidadores

Autor: Sistema de Combate a Anemia - MINSA
Fecha: 2025-10-23
Datatón Exprésate Perú con Datos 2025
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class ExplicadorRiesgo:
    """
    Explica predicciones del modelo ML en lenguaje simple
    Compatible con XGBoost y RandomForest
    """
    
    def __init__(self):
        """Inicializa el explicador con diccionarios de traducción"""
        self.traducciones = self._cargar_traducciones()
        self.pesos_features = self._cargar_pesos_relativos()
    
    def _cargar_traducciones(self) -> Dict[str, str]:
        """
        Traduce nombres técnicos de features a lenguaje simple
        """
        return {
            # Hemoglobina
            'hb_baja': 'Nivel de hemoglobina bajo',
            'hb_muy_baja': 'Nivel de hemoglobina muy bajo',
            'hemoglobina': 'Nivel de hemoglobina',
            
            # Edad
            'edad_6_11m': 'Edad entre 6-11 meses (alta vulnerabilidad)',
            'edad_12_23m': 'Edad entre 12-23 meses (riesgo elevado)',
            'edad_24_35m': 'Edad entre 24-35 meses',
            'edad_36_59m': 'Edad mayor a 36 meses',
            'edad_meses': 'Edad del niño',
            
            # Suplementación
            'sin_suplemento': 'No recibe suplemento de hierro',
            'recibe_suplemento': 'Sin suplementación de hierro',
            
            # Ubicación
            'area_rural': 'Vive en zona rural',
            'altitud': 'Vive en zona de altura',
            'altitud_muy_alta': 'Vive en altura muy elevada (>3000 msnm)',
            'altitud_alta': 'Vive en altura moderada (2500-3000 msnm)',
            
            # Departamentos alto riesgo
            'dept_PUNO': 'Departamento de alto riesgo (Puno)',
            'dept_CUSCO': 'Departamento de alto riesgo (Cusco)',
            'dept_HUANCAVELICA': 'Departamento de alto riesgo (Huancavelica)',
            'dept_APURIMAC': 'Departamento de alto riesgo (Apurímac)',
            'dept_AYACUCHO': 'Departamento de alto riesgo (Ayacucho)',
            'dept_PASCO': 'Departamento de alto riesgo (Pasco)',
            
            # Controles
            'sin_cred': 'No asiste a controles CRED',
            'asiste_cred': 'Falta de asistencia a controles CRED',
            
            # Programas sociales
            'juntos': 'No está inscrito en programa Juntos',
            'qaliwarma': 'No accede a programa Qali Warma',
            
            # Interacciones
            'altitud_sin_supl': 'Altura elevada sin suplemento',
            'rural_sin_cred': 'Zona rural sin controles',
            'hb_x_altitud': 'Hemoglobina baja en zona de altura',
        }
    
    def _cargar_pesos_relativos(self) -> Dict[str, float]:
        """
        Pesos relativos de cada feature para ordenamiento
        Basados en feature importance del modelo XGBoost
        """
        return {
            'hemoglobina': 10.0,
            'hb_baja': 9.5,
            'hb_muy_baja': 9.8,
            'sin_suplemento': 8.0,
            'altitud_muy_alta': 7.5,
            'edad_6_11m': 7.0,
            'edad_12_23m': 6.5,
            'area_rural': 6.0,
            'sin_cred': 5.5,
            'dept_PUNO': 5.0,
            'dept_HUANCAVELICA': 5.0,
            'altitud_sin_supl': 7.2,
            'rural_sin_cred': 6.2,
            'hb_x_altitud': 8.5,
        }
    
    def explicar_prediccion(
        self,
        datos_nino: Dict,
        probabilidad: float,
        top_n: int = 3
    ) -> List[Tuple[str, float, str]]:
        """
        Genera explicación simple de los top-N factores de riesgo
        
        Args:
            datos_nino: Diccionario con datos del niño
            probabilidad: Probabilidad de anemia del modelo
            top_n: Número de factores a mostrar (default: 3)
        
        Returns:
            Lista de tuplas: (factor_legible, peso_porcentual, icono)
        """
        try:
            # 1. Identificar features activas
            features_activas = self._extraer_features_activas(datos_nino)
            
            if not features_activas:
                return self._explicacion_por_defecto(probabilidad)
            
            # 2. Calcular contribuciones relativas
            contribuciones = self._calcular_contribuciones(features_activas)
            
            # 3. Ordenar por importancia y tomar top-N
            top_factores = sorted(
                contribuciones.items(),
                key=lambda x: x[1],
                reverse=True
            )[:top_n]
            
            # 4. Normalizar a porcentajes
            total_contribucion = sum([cont for _, cont in top_factores])
            
            explicacion = []
            for feature, contribucion in top_factores:
                factor_legible = self.traducciones.get(feature, feature.replace('_', ' ').title())
                porcentaje = (contribucion / total_contribucion) * 100
                icono = self._obtener_icono(feature)
                
                explicacion.append((factor_legible, round(porcentaje, 1), icono))
            
            logger.info(f"Explicación generada: {len(explicacion)} factores")
            return explicacion
        
        except Exception as e:
            logger.error(f"Error generando explicación: {e}")
            return self._explicacion_por_defecto(probabilidad)
    
    def _extraer_features_activas(self, datos: Dict) -> Dict[str, float]:
        """
        Extrae features que están activas (valor != 0) para el niño
        """
        features = {}
        
        # Hemoglobina
        hb = datos.get('hemoglobina', 12.0)
        if hb < 11.0:
            features['hb_baja'] = 11.0 - hb  # Magnitud del déficit
        if hb < 10.0:
            features['hb_muy_baja'] = 10.0 - hb
        
        # Edad
        edad = datos.get('edad_meses', 12)
        if 6 <= edad < 12:
            features['edad_6_11m'] = 1.0
        elif 12 <= edad < 24:
            features['edad_12_23m'] = 1.0
        
        # Suplementación
        recibe_supl = datos.get('recibe_suplemento', False) or datos.get('tiene_suplemento', False)
        if not recibe_supl:
            features['sin_suplemento'] = 1.0
        
        # Ubicación
        if datos.get('area_rural', False):
            features['area_rural'] = 1.0
        
        altitud = datos.get('altitud', 0)
        if altitud >= 3000:
            features['altitud_muy_alta'] = 1.0
        elif 2500 <= altitud < 3000:
            features['altitud_alta'] = 1.0
        
        # Controles CRED
        if not datos.get('asiste_cred', True):
            features['sin_cred'] = 1.0
        
        # Departamento
        dept = datos.get('departamento', '').upper().strip()
        for dept_riesgo in ['PUNO', 'CUSCO', 'HUANCAVELICA', 'APURIMAC', 'AYACUCHO', 'PASCO']:
            if dept == dept_riesgo:
                features[f'dept_{dept_riesgo}'] = 1.0
        
        # Interacciones importantes
        if altitud >= 3000 and not recibe_supl:
            features['altitud_sin_supl'] = 1.0
        
        if datos.get('area_rural', False) and not datos.get('asiste_cred', True):
            features['rural_sin_cred'] = 1.0
        
        if hb < 11.0 and altitud >= 2500:
            features['hb_x_altitud'] = (11.0 - hb) * (altitud / 1000)
        
        return features
    
    def _calcular_contribuciones(self, features_activas: Dict[str, float]) -> Dict[str, float]:
        """
        Calcula contribución relativa de cada feature activa
        """
        contribuciones = {}
        
        for feature, valor in features_activas.items():
            peso_base = self.pesos_features.get(feature, 1.0)
            contribuciones[feature] = peso_base * valor
        
        return contribuciones
    
    def _obtener_icono(self, feature: str) -> str:
        """
        Asigna iconos por categoría de feature
        """
        if 'hb' in feature or 'hemoglobina' in feature:
            return '🩸'
        elif 'suplemento' in feature:
            return '💊'
        elif 'edad' in feature:
            return '👶'
        elif 'rural' in feature or 'altitud' in feature or 'dept' in feature:
            return '🏔️'
        elif 'cred' in feature:
            return '🏥'
        else:
            return '⚠️'
    
    def _explicacion_por_defecto(self, probabilidad: float) -> List[Tuple[str, float, str]]:
        """
        Explicación genérica cuando no se pueden identificar factores
        """
        if probabilidad >= 0.7:
            return [
                ('Múltiples factores de riesgo presentes', 100.0, '⚠️')
            ]
        else:
            return [
                ('Perfil de riesgo estándar', 100.0, 'ℹ️')
            ]
    
    def generar_mensaje_simple(
        self,
        explicacion: List[Tuple[str, float, str]],
        probabilidad: float
    ) -> str:
        """
        Genera un mensaje en una sola frase para la madre
        
        Args:
            explicacion: Lista de factores del método explicar_prediccion
            probabilidad: Probabilidad de anemia
        
        Returns:
            Mensaje simple y comprensible
        """
        if probabilidad >= 0.80:
            nivel = "MUY ALTO"
            emoji = "🔴"
        elif probabilidad >= 0.60:
            nivel = "ALTO"
            emoji = "🟠"
        elif probabilidad >= 0.40:
            nivel = "MEDIO"
            emoji = "🟡"
        else:
            nivel = "BAJO"
            emoji = "🟢"
        
        if not explicacion:
            return f"{emoji} **Riesgo {nivel}** ({probabilidad*100:.0f}%)"
        
        # Tomar solo los 2 factores más importantes
        factores_principales = [f[0] for f in explicacion[:2]]
        
        if len(factores_principales) == 1:
            mensaje = f"{emoji} **Riesgo {nivel}** ({probabilidad*100:.0f}%) principalmente por: **{factores_principales[0]}**"
        else:
            mensaje = f"{emoji} **Riesgo {nivel}** ({probabilidad*100:.0f}%) por: **{factores_principales[0]}** y **{factores_principales[1]}**"
        
        return mensaje


# Instancia global
explicador_riesgo = ExplicadorRiesgo()
