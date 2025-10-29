"""
utils/nudges.py
Sistema de nudges (recordatorios) con A/B testing
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import random
import csv
from pathlib import Path

class SistemaNudges:
    """Sistema de recordatorios con pruebas A/B"""

    def __init__(self):
        self.variantes = {
            'A': {
                'nombre': 'Formal institucional',
                'asunto': '🩺 Recordatorio: Control CRED de {nombre}',
                'mensaje': 'Hola, es momento del control CRED de {nombre}. Agenda tu cita llamando al centro de salud.',
                'canal': 'SMS'
            },
            'B': {
                'nombre': 'Impacto emocional',
                'asunto': '👶 {nombre} necesita su control médico',
                'mensaje': 'Tu bebé necesita su control. Los niños con controles regulares tienen 3 veces menos anemia.',
                'canal': 'WhatsApp'
            },
            'C': {
                'nombre': 'Recordatorio con fecha',
                'asunto': '⏰ Cita programada para {nombre}',
                'mensaje': 'Tienes una cita de control CRED el {fecha}. No olvides llevar el carnet de vacunación.',
                'canal': 'SMS'
            }
        }

    def enviar_recordatorio(self, telefono: str, nombre_paciente: str, tipo_control: str, dias: int, variante=None):
        """
        Envía recordatorio por SMS/WhatsApp con variante A/B

        Args:
            telefono: str (9 dígitos)
            nombre_paciente: str
            tipo_control: str ('Control inmediato', 'Seguimiento 1 mes', etc.)
            dias: int (días hasta el control)
            variante: str ('A', 'B', 'C') o None para aleatorio

        Returns:
            Dict con resultado del envío
        """
        # Seleccionar variante aleatoria si no se especifica
        if variante is None:
            variante = random.choice(['A', 'B', 'C'])

        template = self.variantes[variante]
        
        # Calcular fecha del control
        from datetime import datetime, timedelta
        fecha_control = datetime.now() + timedelta(days=dias)

        asunto = template['asunto'].format(nombre=nombre_paciente)
        mensaje = template['mensaje'].format(
            nombre=nombre_paciente,
            fecha=fecha_control.strftime('%d/%m/%Y')
        )

        resultado = {
            'status': 'simulado',  # 'success' cuando implementes SMS real
            'telefono': telefono,
            'variante': variante,
            'nombre_variante': template['nombre'],
            'canal': template['canal'],
            'tipo_control': tipo_control,
            'dias_hasta_control': dias,
            'fecha_control': fecha_control.strftime('%d/%m/%Y'),
            'mensaje': mensaje,
            'timestamp': datetime.now().isoformat()
        }

        # Guardar log
        self.registrar_envio(resultado)

        return resultado

    def registrar_envio(self, resultado: dict):
        """Registra envío para análisis A/B"""
        log_file = Path('data/logs/nudges_ab_test.csv')
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # Crear archivo si no existe
        if not log_file.exists():
            with open(log_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'telefono', 'variante', 'canal', 
                    'tipo_control', 'dias', 'status'
                ])

        # Agregar registro
        with open(log_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                resultado['timestamp'],
                resultado['telefono'],
                resultado['variante'],
                resultado['canal'],
                resultado['tipo_control'],
                resultado['dias_hasta_control'],
                resultado['status']
            ])

    def programar_recordatorios_multiples(self, telefono: str, nombre_paciente: str, controles: list):
        """
        Programa múltiples recordatorios según calendario de controles

        Args:
            telefono: str
            nombre_paciente: str
            controles: list de dicts con {'tipo': str, 'dias': int}

        Returns:
            List de resultados de envío
        """
        resultados = []

        for control in controles:
            resultado = self.enviar_recordatorio(
                telefono=telefono,
                nombre_paciente=nombre_paciente,
                tipo_control=control['tipo'],
                dias=control['dias']
            )

            resultados.append(resultado)

        return resultados

    @staticmethod
    def obtener_estadisticas_ab():
        """Obtiene estadísticas de pruebas A/B"""
        log_file = Path('data/logs/nudges_ab_test.csv')
        
        if not log_file.exists():
            return None
        
        import pandas as pd
        df = pd.read_csv(log_file)
        
        stats = {
            'total_envios': len(df),
            'por_variante': df['variante'].value_counts().to_dict(),
            'por_canal': df['canal'].value_counts().to_dict(),
            'ultimo_envio': df['timestamp'].max() if len(df) > 0 else None
        }
        
        return stats
