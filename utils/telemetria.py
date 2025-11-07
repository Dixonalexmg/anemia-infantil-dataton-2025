"""
utils/telemetria.py
Sistema de telemetría para NutriSenseIA - Tracking de uso y efectividad
Registra: diagnósticos, menús preparados, feedback, métricas de rendimiento
"""

import os
import json
import csv
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)

# ════════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE RUTAS
# ════════════════════════════════════════════════════════════════════════════════

TELEMETRIA_DIR = Path("data/telemetria")
FEEDBACK_DIR = TELEMETRIA_DIR / "feedback"
LOGS_DIR = TELEMETRIA_DIR / "logs"
METRICS_DIR = TELEMETRIA_DIR / "metrics"

# Crear directorios si no existen
for directorio in [TELEMETRIA_DIR, FEEDBACK_DIR, LOGS_DIR, METRICS_DIR]:
    directorio.mkdir(parents=True, exist_ok=True)

# ════════════════════════════════════════════════════════════════════════════════
# CLASE TELEMETRIA
# ════════════════════════════════════════════════════════════════════════════════

class TelemetriaManager:
    """Gestor centralizado de telemetría del sistema"""

    def __init__(self):
        """Inicializa el gestor de telemetría"""
        self.session_id = self._generar_session_id()
        self.timestamp_inicio = datetime.now()

        # Crear archivos de log si no existen
        self._crear_archivos_base()

    def _generar_session_id(self) -> str:
        """Genera ID de sesión único"""
        import uuid
        return f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

    def _crear_archivos_base(self):
        """Crea archivos CSV base con headers"""
        # diagnósticos.csv
        diagnosticos_csv = LOGS_DIR / "diagnosticos.csv"
        if not diagnosticos_csv.exists():
            with open(diagnosticos_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'session_id', 'usuario', 'edad_meses', 'hemoglobina',
                    'nivel_riesgo', 'probabilidad_anemia', 'tiempo_procesamiento_ms'
                ])

        # feedback.csv
        feedback_csv = FEEDBACK_DIR / "feedback.csv"
        if not feedback_csv.exists():
            with open(feedback_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'session_id', 'usuario', 'pagina', 'comprension',
                    'utilidad', 'comentario', 'rating'
                ])

        # adherencia_menus.csv
        adherencia_csv = LOGS_DIR / "adherencia_menus.csv"
        if not adherencia_csv.exists():
            with open(adherencia_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'session_id', 'usuario', 'nombre_plato', 'hierro_mg',
                    'costo_s', 'preparado', 'fue_util'
                ])

        # metricas_rendimiento.csv
        metricas_csv = METRICS_DIR / "rendimiento.csv"
        if not metricas_csv.exists():
            with open(metricas_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'session_id', 'pagina', 'tiempo_carga_ms',
                    'tiempo_proceso_ms', 'memoria_mb', 'error'
                ])

    def registrar_diagnostico(self, datos: Dict[str, Any]) -> bool:
        """
        Registra un diagnóstico realizado

        Args:
            datos: {
                'usuario': str,
                'edad_meses': int,
                'hemoglobina': float,
                'nivel_riesgo': str,
                'probabilidad_anemia': float,
                'tiempo_procesamiento_ms': int
            }
        """
        try:
            diagnosticos_csv = LOGS_DIR / "diagnosticos.csv"

            with open(diagnosticos_csv, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().isoformat(),
                    self.session_id,
                    datos.get('usuario', 'anonimo'),
                    datos.get('edad_meses', 0),
                    datos.get('hemoglobina', 0),
                    datos.get('nivel_riesgo', 'no_evaluado'),
                    round(datos.get('probabilidad_anemia', 0), 3),
                    datos.get('tiempo_procesamiento_ms', 0)
                ])

            logger.info(f"✅ Diagnóstico registrado: {datos.get('usuario')}")
            return True

        except Exception as e:
            logger.error(f"❌ Error registrando diagnóstico: {e}")
            return False

    def registrar_feedback(self, datos: Dict[str, Any]) -> bool:
        """
        Registra feedback del usuario

        Args:
            datos: {
                'usuario': str,
                'pagina': str,
                'comprension': int (1-5),
                'utilidad': int (1-5),
                'comentario': str,
                'rating': int (1-5)
            }
        """
        try:
            feedback_csv = FEEDBACK_DIR / "feedback.csv"

            with open(feedback_csv, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().isoformat(),
                    self.session_id,
                    datos.get('usuario', 'anonimo'),
                    datos.get('pagina', 'desconocida'),
                    datos.get('comprension', 3),
                    datos.get('utilidad', 3),
                    datos.get('comentario', ''),
                    datos.get('rating', 3)
                ])

            logger.info(f"✅ Feedback registrado: {datos.get('usuario')} - {datos.get('pagina')}")
            return True

        except Exception as e:
            logger.error(f"❌ Error registrando feedback: {e}")
            return False

    def registrar_menu_preparado(self, datos: Dict[str, Any]) -> bool:
        """
        Registra cuando un usuario prepara un menú

        Args:
            datos: {
                'usuario': str,
                'nombre_plato': str,
                'hierro_mg': float,
                'costo_s': float,
                'fue_util': bool
            }
        """
        try:
            adherencia_csv = LOGS_DIR / "adherencia_menus.csv"

            with open(adherencia_csv, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().isoformat(),
                    self.session_id,
                    datos.get('usuario', 'anonimo'),
                    datos.get('nombre_plato', 'desconocido'),
                    round(datos.get('hierro_mg', 0), 1),
                    round(datos.get('costo_s', 0), 2),
                    True,  # preparado
                    datos.get('fue_util', None)
                ])

            logger.info(f"✅ Menú registrado: {datos.get('nombre_plato')}")
            return True

        except Exception as e:
            logger.error(f"❌ Error registrando menú: {e}")
            return False

    def registrar_metrica_rendimiento(self, datos: Dict[str, Any]) -> bool:
        """
        Registra métricas de rendimiento de la aplicación

        Args:
            datos: {
                'pagina': str,
                'tiempo_carga_ms': int,
                'tiempo_proceso_ms': int,
                'memoria_mb': float,
                'error': str (opcional)
            }
        """
        try:
            metricas_csv = METRICS_DIR / "rendimiento.csv"

            with open(metricas_csv, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().isoformat(),
                    self.session_id,
                    datos.get('pagina', 'desconocida'),
                    datos.get('tiempo_carga_ms', 0),
                    datos.get('tiempo_proceso_ms', 0),
                    round(datos.get('memoria_mb', 0), 2),
                    datos.get('error', '')
                ])

            return True

        except Exception as e:
            logger.error(f"❌ Error registrando métrica: {e}")
            return False

    @staticmethod
    def obtener_diagnosticos_recientes(dias: int = 30) -> pd.DataFrame:
        """Obtiene diagnósticos de los últimos N días"""
        diagnosticos_csv = LOGS_DIR / "diagnosticos.csv"

        if not diagnosticos_csv.exists():
            return pd.DataFrame()

        try:
            df = pd.read_csv(diagnosticos_csv)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            fecha_cutoff = datetime.now() - timedelta(days=dias)
            return df[df['timestamp'] > fecha_cutoff]
        except Exception as e:
            logger.error(f"Error leyendo diagnósticos: {e}")
            return pd.DataFrame()

    @staticmethod
    def obtener_feedback_reciente(dias: int = 30) -> pd.DataFrame:
        """Obtiene feedback de los últimos N días"""
        feedback_csv = FEEDBACK_DIR / "feedback.csv"

        if not feedback_csv.exists():
            return pd.DataFrame()

        try:
            df = pd.read_csv(feedback_csv)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            fecha_cutoff = datetime.now() - timedelta(days=dias)
            return df[df['timestamp'] > fecha_cutoff]
        except Exception as e:
            logger.error(f"Error leyendo feedback: {e}")
            return pd.DataFrame()

    @staticmethod
    def obtener_adherencia_menus(dias: int = 30) -> pd.DataFrame:
        """Obtiene datos de adherencia de menús"""
        adherencia_csv = LOGS_DIR / "adherencia_menus.csv"

        if not adherencia_csv.exists():
            return pd.DataFrame()

        try:
            df = pd.read_csv(adherencia_csv)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            fecha_cutoff = datetime.now() - timedelta(days=dias)
            return df[df['timestamp'] > fecha_cutoff]
        except Exception as e:
            logger.error(f"Error leyendo adherencia: {e}")
            return pd.DataFrame()

    @staticmethod
    def obtener_metricas_rendimiento(dias: int = 7) -> pd.DataFrame:
        """Obtiene métricas de rendimiento"""
        metricas_csv = METRICS_DIR / "rendimiento.csv"

        if not metricas_csv.exists():
            return pd.DataFrame()

        try:
            df = pd.read_csv(metricas_csv)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            fecha_cutoff = datetime.now() - timedelta(days=dias)
            return df[df['timestamp'] > fecha_cutoff]
        except Exception as e:
            logger.error(f"Error leyendo métricas: {e}")
            return pd.DataFrame()

    @staticmethod
    def calcular_estadisticas() -> Dict[str, Any]:
        """Calcula estadísticas agregadas del sistema"""

        stats = {
            'total_diagnosticos': 0,
            'comprension_promedio': 0,
            'utilidad_promedio': 0,
            'adherencia_menus_pct': 0,
            'tiempo_respuesta_promedio_ms': 0,
            'riesgo_distribution': {}
        }

        # Diagnósticos
        df_diag = TelemetriaManager.obtener_diagnosticos_recientes(30)
        if not df_diag.empty:
            stats['total_diagnosticos'] = len(df_diag)
            stats['tiempo_respuesta_promedio_ms'] = int(df_diag['tiempo_procesamiento_ms'].mean())
            stats['riesgo_distribution'] = df_diag['nivel_riesgo'].value_counts().to_dict()

        # Feedback
        df_feed = TelemetriaManager.obtener_feedback_reciente(30)
        if not df_feed.empty:
            stats['comprension_promedio'] = round(df_feed['comprension'].mean(), 2)
            stats['utilidad_promedio'] = round(df_feed['utilidad'].mean(), 2)

        # Adherencia
        df_ader = TelemetriaManager.obtener_adherencia_menus(30)
        if not df_ader.empty:
            total_menus = len(df_ader)
            menus_utiles = len(df_ader[df_ader['fue_util'] == True])
            stats['adherencia_menus_pct'] = round((menus_utiles / total_menus * 100) if total_menus > 0 else 0, 1)

        return stats


# ════════════════════════════════════════════════════════════════════════════════
# INSTANCIA GLOBAL
# ════════════════════════════════════════════════════════════════════════════════

_telemetria_instance = None

def get_telemetria() -> TelemetriaManager:
    """Devuelve la instancia global del gestor de telemetría (singleton)"""
    global _telemetria_instance
    if _telemetria_instance is None:
        _telemetria_instance = TelemetriaManager()
    return _telemetria_instance