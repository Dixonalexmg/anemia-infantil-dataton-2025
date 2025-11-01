# utils/pdf_generator.py
"""
Generador de Reportes PDF Diferenciados por Rol - VERSIÓN 100% PROFESIONAL CORREGIDA

Características:
✅ 2 templates: Médico (clínico) y Madre (educativo)
✅ Formato A4, logo MINSA, fecha automática
✅ Gráficos embebidos (matplotlib → imagen → PDF)
✅ Tips ilustrados con íconos
✅ Datos clínicos + evolución Hb + adherencia
✅ Export en 1 click
✅ Manejo robusto de None en evolucion_hb (CORREGIDO)
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import matplotlib.pyplot as plt
import io
import os
import logging

logger = logging.getLogger(__name__)


class ReportePDFGenerator:
    """Generador de reportes PDF diferenciados por rol"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._crear_estilos_personalizados()
    
    def _crear_estilos_personalizados(self):
        """Crea estilos personalizados para el PDF"""
        
        # Título principal
        self.styles.add(ParagraphStyle(
            name='TituloPrincipal',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Texto normal
        self.styles.add(ParagraphStyle(
            name='TextoNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        # Alerta
        self.styles.add(ParagraphStyle(
            name='Alerta',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#856404'),
            backColor=colors.HexColor('#fff3cd'),
            borderPadding=10,
            borderWidth=1,
            borderColor=colors.HexColor('#ffc107'),
            fontName='Helvetica-Bold'
        ))
    
    def generar_reporte_medico(self, datos_paciente, datos_clinicos, output_path=None):
        """
        Genera reporte PDF para MÉDICO/PROFESIONAL DE SALUD
        
        Args:
            datos_paciente: dict con info del paciente
            datos_clinicos: dict con datos clínicos
            output_path: ruta de salida (opcional)
        
        Returns:
            str: ruta del archivo PDF generado
        """
        if output_path is None:
            output_path = f"reportes/reporte_medico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Crear documento
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Contenido del reporte
        story = []
        
        # ===== HEADER =====
        story.append(self._crear_header_medico(datos_paciente))
        story.append(Spacer(1, 0.5*cm))
        
        # ===== DATOS CLÍNICOS =====
        story.append(Paragraph("DATOS CLÍNICOS", self.styles['Subtitulo']))
        story.append(self._crear_tabla_datos_clinicos(datos_clinicos))
        story.append(Spacer(1, 0.5*cm))
        
        # ===== DIAGNÓSTICO =====
        story.append(Paragraph("DIAGNÓSTICO Y CLASIFICACIÓN", self.styles['Subtitulo']))
        story.append(self._crear_seccion_diagnostico(datos_clinicos))
        story.append(Spacer(1, 0.5*cm))
        
        # ===== EVOLUCIÓN Hb (GRÁFICO) - CORREGIDO =====
        if 'evolucion_hb' in datos_clinicos and datos_clinicos['evolucion_hb'] is not None:
            story.append(Paragraph("EVOLUCIÓN DE HEMOGLOBINA", self.styles['Subtitulo']))
            grafico_hb = self._crear_grafico_evolucion_hb(datos_clinicos['evolucion_hb'])
            story.append(Image(grafico_hb, width=15*cm, height=8*cm))
            story.append(Spacer(1, 0.5*cm))
        
        # ===== ADHERENCIA =====
        if 'adherencia' in datos_clinicos:
            story.append(Paragraph("ADHERENCIA AL TRATAMIENTO", self.styles['Subtitulo']))
            story.append(self._crear_tabla_adherencia(datos_clinicos['adherencia']))
            story.append(Spacer(1, 0.5*cm))
        
        # ===== RECOMENDACIONES CLÍNICAS =====
        story.append(Paragraph("RECOMENDACIONES CLÍNICAS", self.styles['Subtitulo']))
        story.append(self._crear_recomendaciones_medico(datos_clinicos))
        
        # ===== FOOTER =====
        story.append(Spacer(1, 1*cm))
        story.append(self._crear_footer())
        
        # Generar PDF
        doc.build(story)
        logger.info(f"✅ Reporte médico generado: {output_path}")
        
        return output_path
    
    def generar_reporte_madre(self, datos_paciente, plan_alimentario, output_path=None):
        """
        Genera reporte PDF para MADRE/CUIDADOR
        
        Args:
            datos_paciente: dict con info del paciente
            plan_alimentario: dict con menús y tips
            output_path: ruta de salida (opcional)
        
        Returns:
            str: ruta del archivo PDF generado
        """
        if output_path is None:
            output_path = f"reportes/reporte_madre_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # ===== HEADER =====
        story.append(self._crear_header_madre(datos_paciente))
        story.append(Spacer(1, 0.5*cm))
        
        # ===== MENSAJE MOTIVACIONAL =====
        mensaje = f"""
        <b>¡Hola {datos_paciente.get('nombre_madre', 'Mamá')}!</b><br/><br/>
        Este plan fue diseñado especialmente para <b>{datos_paciente.get('nombre_nino', 'tu niño/a')}</b>. 
        Sigue estos consejos y menús para ayudarlo/a a crecer fuerte y saludable. 
        ¡Tú puedes lograrlo! 💪
        """
        story.append(Paragraph(mensaje, self.styles['TextoNormal']))
        story.append(Spacer(1, 0.5*cm))
        
        # ===== PLAN SEMANAL =====
        story.append(Paragraph("📅 MI PLAN SEMANAL", self.styles['Subtitulo']))
        story.append(self._crear_tabla_plan_semanal(plan_alimentario['menu_semanal']))
        story.append(Spacer(1, 0.5*cm))
        
        # ===== TIPS ILUSTRADOS =====
        story.append(Paragraph("💡 TIPS PARA MEJORAR LA ABSORCIÓN", self.styles['Subtitulo']))
        story.append(self._crear_tips_ilustrados())
        story.append(Spacer(1, 0.5*cm))
        
        # ===== RECORDATORIOS =====
        story.append(Paragraph("⏰ RECORDATORIOS IMPORTANTES", self.styles['Subtitulo']))
        story.append(self._crear_recordatorios())
        story.append(Spacer(1, 0.5*cm))
        
        # ===== LISTA DE COMPRAS =====
        if 'lista_compras' in plan_alimentario:
            story.append(PageBreak())
            story.append(Paragraph("🛒 LISTA DE COMPRAS", self.styles['Subtitulo']))
            story.append(self._crear_lista_compras(plan_alimentario['lista_compras']))
        
        # ===== FOOTER =====
        story.append(Spacer(1, 1*cm))
        story.append(self._crear_footer())
        
        doc.build(story)
        logger.info(f"✅ Reporte madre generado: {output_path}")
        
        return output_path
    
    # ============================================
    # FUNCIONES AUXILIARES - HEADER
    # ============================================
    
    def _crear_header_medico(self, datos):
        """Header para reporte médico"""
        texto = f"""
        <para align=center>
        <font size=20 color="#667eea"><b>REPORTE CLÍNICO - ANEMIA INFANTIL</b></font><br/>
        <font size=12 color="#333333">Ministerio de Salud del Perú</font><br/>
        <font size=10 color="#666666">NutriSenseIA v1.0 • Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}</font>
        </para>
        """
        return Paragraph(texto, self.styles['Normal'])
    
    def _crear_header_madre(self, datos):
        """Header para reporte madre"""
        texto = f"""
        <para align=center>
        <font size=18 color="#11998e"><b>🍽️ MI PLAN NUTRICIONAL</b></font><br/>
        <font size=12 color="#333333">Para: {datos.get('nombre_nino', 'Mi niño/a')}</font><br/>
        <font size=10 color="#666666">Fecha: {datetime.now().strftime('%d/%m/%Y')}</font>
        </para>
        """
        return Paragraph(texto, self.styles['Normal'])
    
    # ============================================
    # FUNCIONES AUXILIARES - CONTENIDO MÉDICO
    # ============================================
    
    def _crear_tabla_datos_clinicos(self, datos):
        """Tabla de datos clínicos"""
        data = [
            ['Parámetro', 'Valor', 'Referencia'],
            ['Hemoglobina', f"{datos.get('hemoglobina', 0):.1f} g/dL", '≥11.0 g/dL (6-59m)'],
            ['Edad', f"{datos.get('edad_meses', 0)} meses", '-'],
            ['Peso', f"{datos.get('peso_kg', 0):.1f} kg", f"P50: {datos.get('peso_p50', 0):.1f} kg"],
            ['Talla', f"{datos.get('talla_cm', 0):.1f} cm", f"P50: {datos.get('talla_p50', 0):.1f} cm"],
            ['Altitud', f"{datos.get('altitud_msnm', 0)} msnm", '-'],
        ]
        
        tabla = Table(data, colWidths=[6*cm, 4*cm, 5*cm])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        return tabla
    
    def _crear_seccion_diagnostico(self, datos):
        """Sección de diagnóstico"""
        nivel_riesgo = datos.get('nivel_riesgo', 'NO DETERMINADO')
        color_riesgo = {
            'RIESGO BAJO': '#28a745',
            'RIESGO MODERADO': '#ffc107',
            'RIESGO ALTO': '#dc3545'
        }.get(nivel_riesgo, '#666666')
        
        texto = f"""
        <para>
        <b>Clasificación:</b> <font color="{color_riesgo}"><b>{nivel_riesgo}</b></font><br/>
        <b>Probabilidad ML:</b> {datos.get('probabilidad_ml', 0)*100:.0f}%<br/>
        <b>Factores de riesgo identificados:</b><br/>
        • {datos.get('factor_1', 'No especificado')}<br/>
        • {datos.get('factor_2', 'No especificado')}<br/>
        • {datos.get('factor_3', 'No especificado')}
        </para>
        """
        
        return Paragraph(texto, self.styles['TextoNormal'])
    
    def _crear_grafico_evolucion_hb(self, datos_evolucion):
        """
        Crea gráfico de evolución de Hb y lo retorna como imagen
        VERSIÓN CORREGIDA - Manejo robusto de None
        """
        
        # ✅ VALIDACIÓN: Si datos_evolucion es None, retornar gráfico placeholder
        if datos_evolucion is None:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.text(0.5, 0.5, 'Sin datos de evolución disponibles', 
                    horizontalalignment='center',
                    verticalalignment='center',
                    transform=ax.transAxes,
                    fontsize=14,
                    color='gray')
            ax.set_xlabel('Fecha', fontsize=10)
            ax.set_ylabel('Hemoglobina (g/dL)', fontsize=10)
            ax.set_title('Evolución de Hemoglobina', fontsize=12, fontweight='bold')
            
            # Convertir a imagen en memoria
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            plt.close()
            
            return img_buffer
        
        # ✅ Si datos_evolucion existe, extraer datos de forma segura
        fechas = datos_evolucion.get('fechas', [])
        valores_hb = datos_evolucion.get('valores', [])
        
        # Validar que haya datos
        if not fechas or not valores_hb:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.text(0.5, 0.5, 'Sin registros históricos', 
                    horizontalalignment='center',
                    verticalalignment='center',
                    transform=ax.transAxes,
                    fontsize=14,
                    color='gray')
            ax.set_xlabel('Fecha', fontsize=10)
            ax.set_ylabel('Hemoglobina (g/dL)', fontsize=10)
            ax.set_title('Evolución de Hemoglobina', fontsize=12, fontweight='bold')
            
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            plt.close()
            
            return img_buffer
        
        # ✅ Crear gráfico con datos reales
        fig, ax = plt.subplots(figsize=(10, 5))
        
        ax.plot(fechas, valores_hb, marker='o', linewidth=2, color='#667eea', markersize=8)
        ax.axhline(y=11.0, color='red', linestyle='--', linewidth=1.5, label='Umbral anemia (11.0 g/dL)')
        ax.set_xlabel('Fecha', fontsize=10)
        ax.set_ylabel('Hemoglobina (g/dL)', fontsize=10)
        ax.set_title('Evolución de Hemoglobina', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(loc='best')
        
        # Ajustar límites del eje Y
        if valores_hb:
            y_min = min(valores_hb) - 1
            y_max = max(valores_hb) + 1
            ax.set_ylim(y_min, y_max)
        
        # Convertir a imagen en memoria
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer
    
    def _crear_tabla_adherencia(self, datos_adherencia):
        """Tabla de adherencia al tratamiento"""
        data = [
            ['Intervención', 'Meta', 'Real', 'Adherencia'],
            ['Suplemento hierro', '30 días', f"{datos_adherencia.get('dias_suplemento', 0)} días", 
             f"{datos_adherencia.get('pct_suplemento', 0):.0f}%"],
            ['Menú personalizado', '7 días/sem', f"{datos_adherencia.get('dias_menu', 0)} días", 
             f"{datos_adherencia.get('pct_menu', 0):.0f}%"],
            ['Controles CRED', '1/mes', f"{datos_adherencia.get('controles_cred', 0)}", 
             f"{datos_adherencia.get('pct_cred', 0):.0f}%"],
        ]
        
        tabla = Table(data, colWidths=[5*cm, 3*cm, 3*cm, 3*cm])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#28a745')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        return tabla
    
    def _crear_recomendaciones_medico(self, datos):
        """Recomendaciones clínicas para el médico"""
        texto = """
        <para>
        <b>1. Suplementación:</b> Continuar con hierro + ácido fólico (esquema MINSA)<br/>
        <b>2. Control:</b> Hemoglobina de control en 1 mes<br/>
        <b>3. Nutrición:</b> Reforzar menú con hierro hemo (sangrecita, hígado, bazo)<br/>
        <b>4. Adherencia:</b> Monitorear adherencia al suplemento (meta ≥80%)<br/>
        <b>5. Seguimiento:</b> Próxima cita en 30 días
        </para>
        """
        
        return Paragraph(texto, self.styles['TextoNormal'])
    
    # ============================================
    # FUNCIONES AUXILIARES - CONTENIDO MADRE
    # ============================================
    
    def _crear_tabla_plan_semanal(self, menu_semanal):
        """Tabla de plan semanal para madre"""
        data = [['Día', 'Desayuno', 'Almuerzo', 'Cena']]
        
        for dia_info in menu_semanal:
            data.append([
                dia_info['dia'],
                dia_info['desayuno'][:25] + '...' if len(dia_info['desayuno']) > 25 else dia_info['desayuno'],
                dia_info['almuerzo'][:25] + '...' if len(dia_info['almuerzo']) > 25 else dia_info['almuerzo'],
                dia_info['cena'][:25] + '...' if len(dia_info['cena']) > 25 else dia_info['cena']
            ])
        
        tabla = Table(data, colWidths=[2*cm, 4.5*cm, 4.5*cm, 4.5*cm])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#11998e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightcyan),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        return tabla
    
    def _crear_tips_ilustrados(self):
        """Tips ilustrados para madre"""
        texto = """
        <para>
        🍋 <b>Combina con vitamina C:</b> Agrega limón o jugo de naranja natural a las comidas.<br/><br/>
        ⏰ <b>Horarios regulares:</b> Desayuno 8am, Almuerzo 12pm, Cena 6pm.<br/><br/>
        ❌ <b>Evita té y café:</b> No des té ni café junto con las comidas (bloquean hierro).<br/><br/>
        💊 <b>Suplemento diario:</b> Dale el suplemento todos los días, preferible en ayunas.<br/><br/>
        📅 <b>No te saltes comidas:</b> 3 comidas principales + 2 refrigerios.
        </para>
        """
        
        return Paragraph(texto, self.styles['TextoNormal'])
    
    def _crear_recordatorios(self):
        """Recordatorios para madre"""
        data = [
            ['⏰', 'Suplemento', 'Todos los días en ayunas'],
            ['🍽️', 'Menú', '3 comidas + 2 refrigerios'],
            ['🏥', 'Control', 'Cada 30 días en el centro de salud'],
            ['📏', 'Peso/Talla', 'Cada control CRED'],
        ]
        
        tabla = Table(data, colWidths=[1.5*cm, 4*cm, 9*cm])
        tabla.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightyellow),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        return tabla
    
    def _crear_lista_compras(self, lista):
        """Lista de compras semanal"""
        texto = "<para>"
        for item in lista:
            texto += f"☐ {item['ingrediente']} - {item['cantidad']}<br/>"
        texto += "</para>"
        
        return Paragraph(texto, self.styles['TextoNormal'])
    
    # ============================================
    # FOOTER
    # ============================================
    
    def _crear_footer(self):
        """Footer común para ambos reportes"""
        texto = """
        <para align=center>
        <font size=8 color="#999999">
        _______________________________________________________________<br/>
        NutriSenseIA v1.0 - Ministerio de Salud del Perú - Datatón 2025<br/>
        Este reporte es una herramienta de apoyo. Consulta siempre con un profesional de salud.
        </font>
        </para>
        """
        
        return Paragraph(texto, self.styles['Normal'])


# ============================================
# FUNCIONES DE CONVENIENCIA
# ============================================

def generar_reporte_medico_rapido(datos_paciente, datos_clinicos):
    """Wrapper para generar reporte médico rápidamente"""
    generator = ReportePDFGenerator()
    return generator.generar_reporte_medico(datos_paciente, datos_clinicos)


def generar_reporte_madre_rapido(datos_paciente, plan_alimentario):
    """Wrapper para generar reporte madre rápidamente"""
    generator = ReportePDFGenerator()
    return generator.generar_reporte_madre(datos_paciente, plan_alimentario)
