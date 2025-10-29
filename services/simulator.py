"""
services/simulator.py
Motor de Simulación de Escenarios - Soporte para HU-03
Calcula el cambio esperado en hemoglobina según intervenciones
"""

import numpy as np
from datetime import datetime, timedelta

class SimuladorIntervencion:
    """
    Simula el impacto de intervenciones nutricionales y suplementación
    en los niveles de hemoglobina a 4-6 semanas
    """

    def __init__(self):
        # Parámetros basados en evidencia clínica
        self.INCREMENTO_BASE_SUPLEMENTACION = 0.3  # g/dL en 4-6 semanas
        self.INCREMENTO_BASE_ALIMENTACION = 0.15   # g/dL en 4-6 semanas

        # Factores de ajuste por adherencia
        self.FACTOR_ADHERENCIA = {
            'alta': 1.0,      # >80% adherencia
            'media': 0.7,     # 50-80% adherencia
            'baja': 0.4       # <50% adherencia
        }

        # Factores de ajuste por edad
        self.FACTOR_EDAD = {
            '6-11_meses': 1.2,    # Mayor capacidad de recuperación
            '12-23_meses': 1.0,   # Baseline
            '24-59_meses': 0.9    # Menor incremento relativo
        }

    def simular_escenario(
        self,
        hb_actual,
        edad_meses,
        suplementacion=True,
        alimentacion_mejorada=True,
        adherencia='alta',
        semanas=6
    ):
        """
        Simula el cambio esperado en hemoglobina

        Args:
            hb_actual: Hemoglobina actual en g/dL
            edad_meses: Edad en meses
            suplementacion: Si recibe suplementación con hierro
            alimentacion_mejorada: Si sigue menú optimizado
            adherencia: 'alta', 'media' o 'baja'
            semanas: Tiempo de proyección (4-6 semanas)

        Returns:
            dict con proyección detallada
        """

        # Determinar grupo etario
        if 6 <= edad_meses <= 11:
            grupo_edad = '6-11_meses'
        elif 12 <= edad_meses <= 23:
            grupo_edad = '12-23_meses'
        else:
            grupo_edad = '24-59_meses'

        # Calcular incremento esperado
        incremento_total = 0.0

        # Contribución de suplementación
        if suplementacion:
            incremento_suplementacion = (
                self.INCREMENTO_BASE_SUPLEMENTACION *
                self.FACTOR_ADHERENCIA.get(adherencia, 1.0) *
                self.FACTOR_EDAD.get(grupo_edad, 1.0)
            )
            incremento_total += incremento_suplementacion
        else:
            incremento_suplementacion = 0.0

        # Contribución de alimentación mejorada
        if alimentacion_mejorada:
            incremento_alimentacion = (
                self.INCREMENTO_BASE_ALIMENTACION *
                self.FACTOR_ADHERENCIA.get(adherencia, 1.0) *
                self.FACTOR_EDAD.get(grupo_edad, 1.0)
            )
            incremento_total += incremento_alimentacion
        else:
            incremento_alimentacion = 0.0

        # Ajustar por tiempo (si es diferente de 6 semanas)
        factor_tiempo = semanas / 6.0
        incremento_total *= factor_tiempo

        # Proyección de hemoglobina
        hb_proyectada = hb_actual + incremento_total

        # Calcular nivel de mejora
        if incremento_total >= 0.5:
            nivel_mejora = "Excelente"
            emoji = "⭐⭐⭐"
        elif incremento_total >= 0.3:
            nivel_mejora = "Muy Bueno"
            emoji = "⭐⭐"
        elif incremento_total >= 0.15:
            nivel_mejora = "Moderado"
            emoji = "⭐"
        else:
            nivel_mejora = "Limitado"
            emoji = "⚠️"

        return {
            'hb_actual': hb_actual,
            'hb_proyectada': hb_proyectada,
            'incremento_total': incremento_total,
            'incremento_suplementacion': incremento_suplementacion,
            'incremento_alimentacion': incremento_alimentacion,
            'nivel_mejora': nivel_mejora,
            'emoji': emoji,
            'semanas': semanas,
            'fecha_proyeccion': (datetime.now() + timedelta(weeks=semanas)).strftime('%d/%m/%Y'),
            'grupo_edad': grupo_edad,
            'adherencia': adherencia
        }

    def comparar_escenarios(self, hb_actual, edad_meses):
        """
        Compara múltiples escenarios de intervención

        Returns:
            dict con comparación de escenarios
        """

        escenarios = {
            'sin_intervencion': self.simular_escenario(
                hb_actual, edad_meses,
                suplementacion=False,
                alimentacion_mejorada=False,
                adherencia='alta'
            ),
            'solo_suplementacion': self.simular_escenario(
                hb_actual, edad_meses,
                suplementacion=True,
                alimentacion_mejorada=False,
                adherencia='alta'
            ),
            'solo_alimentacion': self.simular_escenario(
                hb_actual, edad_meses,
                suplementacion=False,
                alimentacion_mejorada=True,
                adherencia='alta'
            ),
            'intervencion_completa': self.simular_escenario(
                hb_actual, edad_meses,
                suplementacion=True,
                alimentacion_mejorada=True,
                adherencia='alta'
            ),
            'intervencion_adherencia_media': self.simular_escenario(
                hb_actual, edad_meses,
                suplementacion=True,
                alimentacion_mejorada=True,
                adherencia='media'
            )
        }

        return escenarios

    def generar_timeline(self, hb_actual, edad_meses, suplementacion=True, alimentacion_mejorada=True, adherencia='alta'):
        """
        Genera una proyección semana a semana

        Returns:
            DataFrame con evolución proyectada
        """

        import pandas as pd

        semanas = list(range(0, 9))  # 0 a 8 semanas
        proyecciones = []

        for semana in semanas:
            if semana == 0:
                hb_proyectada = hb_actual
            else:
                resultado = self.simular_escenario(
                    hb_actual, edad_meses,
                    suplementacion, alimentacion_mejorada,
                    adherencia, semana
                )
                hb_proyectada = resultado['hb_proyectada']

            proyecciones.append({
                'semana': semana,
                'hemoglobina': hb_proyectada,
                'fecha': (datetime.now() + timedelta(weeks=semana)).strftime('%d/%m')
            })

        return pd.DataFrame(proyecciones)