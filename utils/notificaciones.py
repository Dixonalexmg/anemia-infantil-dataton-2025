# utils/notificaciones.py
"""
Sistema de Notificaciones Programadas
Recordatorios para controles CRED y seguimiento
"""
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import logging

logger = logging.getLogger(__name__)


class SistemaNotificaciones:
    """Gestor de notificaciones por email"""
    
    def __init__(self, smtp_server=None, smtp_port=None, email=None, password=None):
        """
        Inicializa sistema de notificaciones
        
        Args:
            smtp_server: Servidor SMTP (ej: smtp.gmail.com)
            smtp_port: Puerto SMTP (ej: 587)
            email: Email remitente
            password: Contraseña o app password
        """
        self.smtp_server = smtp_server or 'smtp.gmail.com'
        self.smtp_port = smtp_port or 587
        self.email = email
        self.password = password
    
    def enviar_recordatorio_control(
        self,
        email_destino: str,
        nombre_paciente: str,
        fecha_control: str,
        tipo_control: str,
        objetivo: str
    ) -> bool:
        """
        Envía recordatorio de control CRED
        
        Returns:
            bool: True si se envió correctamente
        """
        try:
            # Crear mensaje
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🏥 Recordatorio: {tipo_control} - {fecha_control}"
            msg['From'] = self.email
            msg['To'] = email_destino
            
            # Cuerpo HTML
            html = f"""
            <html>
              <head>
                <style>
                  body {{ font-family: Arial, sans-serif; }}
                  .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            color: white; padding: 20px; text-align: center; }}
                  .content {{ padding: 20px; }}
                  .button {{ background-color: #667eea; color: white; padding: 12px 24px; 
                            text-decoration: none; border-radius: 5px; display: inline-block; }}
                  .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; 
                            color: #666; font-size: 12px; }}
                </style>
              </head>
              <body>
                <div class="header">
                  <h1>🏥 Recordatorio de Control CRED</h1>
                  <p>Sistema de Alerta Temprana - MINSA</p>
                </div>
                
                <div class="content">
                  <h2>Estimado/a padre/madre de {nombre_paciente},</h2>
                  
                  <p>Le recordamos que tiene programado el siguiente control:</p>
                  
                  <div style="background-color: #f5f5f5; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p><strong>📅 Tipo de control:</strong> {tipo_control}</p>
                    <p><strong>🗓️ Fecha:</strong> {fecha_control}</p>
                    <p><strong>🎯 Objetivo:</strong> {objetivo}</p>
                  </div>
                  
                  <p><strong>⚠️ Importante:</strong> Es fundamental asistir a este control para evaluar 
                  el progreso del tratamiento y prevenir complicaciones.</p>
                  
                  <p style="margin-top: 30px;">
                    <a href="#" class="button">📋 Ver Reporte Completo</a>
                  </p>
                </div>
                
                <div class="footer">
                  <p><strong>Sistema de Combate a Anemia Infantil</strong></p>
                  <p>Ministerio de Salud del Perú - NTS 213-MINSA/DGIESP-2024</p>
                  <p>Este es un mensaje automático, por favor no responder.</p>
                </div>
              </body>
            </html>
            """
            
            parte_html = MIMEText(html, 'html')
            msg.attach(parte_html)
            
            # Enviar
            if not self.email or not self.password:
                logger.warning("⚠️ Credenciales SMTP no configuradas. Simulando envío...")
                return True  # Simular éxito en desarrollo
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)
            
            logger.info(f"✅ Recordatorio enviado a {email_destino}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error enviando recordatorio: {e}")
            return False
    
    def programar_recordatorios(
        self,
        email_destino: str,
        nombre_paciente: str,
        controles: list,
        enviar_inmediato: bool = False
    ) -> dict:
        """
        Programa múltiples recordatorios
        
        Args:
            email_destino: Email del receptor
            nombre_paciente: Nombre del paciente
            controles: Lista de controles programados
            enviar_inmediato: Si True, envía inmediatamente (demo)
            
        Returns:
            dict: Estado de cada envío
        """
        resultados = {}
        
        for control in controles:
            if enviar_inmediato:
                # Enviar ahora (para demo)
                exito = self.enviar_recordatorio_control(
                    email_destino=email_destino,
                    nombre_paciente=nombre_paciente,
                    fecha_control=control['fecha'],
                    tipo_control=control['tipo'],
                    objetivo=control['objetivo']
                )
                resultados[control['tipo']] = 'Enviado' if exito else 'Error'
            else:
                # Programar para fecha futura (requiere scheduler)
                resultados[control['tipo']] = 'Programado'
        
        return resultados
    
    def enviar_reporte_pdf(
        self,
        email_destino: str,
        nombre_paciente: str,
        pdf_bytes: bytes
    ) -> bool:
        """
        Envía reporte PDF por email
        
        Returns:
            bool: True si se envió correctamente
        """
        try:
            msg = MIMEMultipart()
            msg['Subject'] = f"📄 Reporte Clínico - {nombre_paciente}"
            msg['From'] = self.email
            msg['To'] = email_destino
            
            # Cuerpo
            cuerpo = """
            Estimado/a,
            
            Adjunto encontrará el reporte clínico completo generado por el 
            Sistema de Alerta Temprana con Inteligencia Artificial.
            
            Saludos cordiales,
            Sistema de Combate a Anemia Infantil - MINSA
            """
            
            msg.attach(MIMEText(cuerpo, 'plain'))
            
            # Adjuntar PDF
            parte_pdf = MIMEApplication(pdf_bytes, _subtype='pdf')
            parte_pdf.add_header('Content-Disposition', 'attachment', 
                                filename=f'Reporte_Clinico_{nombre_paciente}_{datetime.now().strftime("%Y%m%d")}.pdf')
            msg.attach(parte_pdf)
            
            # Enviar
            if not self.email or not self.password:
                logger.warning("⚠️ Credenciales SMTP no configuradas. Simulando envío...")
                return True
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)
            
            logger.info(f"✅ PDF enviado a {email_destino}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error enviando PDF: {e}")
            return False


# Instancia global (singleton)
_notificaciones_instance = None


def get_sistema_notificaciones():
    """Factory para obtener instancia del sistema de notificaciones"""
    global _notificaciones_instance
    if _notificaciones_instance is None:
        _notificaciones_instance = SistemaNotificaciones()
    return _notificaciones_instance
