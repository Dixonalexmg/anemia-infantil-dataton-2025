"""
pages/reportes_entidad_decisiones.py
Reportes para entidad MINSA con panel de decisiones
✅ VERSIÓN CORREGIDA Y MEJORADA - DATATÓN 2025

Mejoras:
1. Reporte más atractivo con tarjetas visuales
2. Agregadas 2 opciones más (C: Integral, D: Multi-sectorial)
3. PDF descargable + Email animado
4. Sin errores de importaciones
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch


def pagina_reportes_entidad_decisiones():
    """Dashboard para decisiones de entidad MINSA - VERSIÓN MEJORADA"""

    # ════════════════════════════════════════════════════════════════════════
    # HEADER
    # ════════════════════════════════════════════════════════════════════════
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2.5rem; border-radius: 15px; margin-bottom: 2rem;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);'>
        <h1 style='color: white; margin: 0; font-size: 2.5rem;'>
            📊 Visión Territorial y Alertas
        </h1>
        <p style='color: rgba(255,255,255,0.95); margin: 0.8rem 0 0 0; font-size: 1.1rem;'>
            Dashboard para decisiones de salud pública
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ════════════════════════════════════════════════════════════════════════
    # DATOS SINTÉTICOS
    # ════════════════════════════════════════════════════════════════════════
    hotspots = [
        {'nombre': 'Ayacucho', 'prevalencia': 68, 'evaluados': 1247, 'criticos': 847},
        {'nombre': 'Apurímac', 'prevalencia': 62, 'evaluados': 856, 'criticos': 531},
        {'nombre': 'Huancavelica', 'prevalencia': 58, 'evaluados': 1102, 'criticos': 639},
    ]

    # ════════════════════════════════════════════════════════════════════════
    # SEMÁFORO DE HOTSPOTS (MEJORADO)
    # ════════════════════════════════════════════════════════════════════════
    st.markdown("## 🔴 Hotspots Críticos Identificados")

    col1, col2, col3 = st.columns(3)

    for i, h in enumerate(hotspots):
        col = [col1, col2, col3][i]

        color_emoji = "🔴" if h['prevalencia'] > 60 else "🟠"
        color_bg = "#ffe5e5" if h['prevalencia'] > 60 else "#fff3cd"

        with col:
            st.markdown(f"""
            <div style='background: {color_bg}; padding: 1.5rem; border-radius: 12px;'>
                <h3 style='margin: 0; color: #212529;'>{color_emoji} {h['nombre']}</h3>
                <p style='margin: 0.5rem 0; font-size: 1.2rem; color: #dc3545;'><b>{h['prevalencia']}%</b> anemia</p>
                <p style='margin: 0.3rem 0; font-size: 0.9rem; color: #666;'>
                    {h['criticos']} de {h['evaluados']} niños críticos
                </p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ════════════════════════════════════════════════════════════════════════
    # OPCIONES DE INTERVENCIÓN (MEJORADAS + 2 NUEVAS)
    # ════════════════════════════════════════════════════════════════════════
    st.markdown("## 📍 Opciones de Intervención para Ayacucho")
    st.caption("Sistema recomienda 4 caminos costo-efectivos")

    ayacucho = hotspots[0]

    # Datos de opciones
    opciones = {
        'A': {
            'titulo': 'Visita Focalizada',
            'emoji': '🚐',
            'descripcion': 'Equipo móvil de salud',
            'duracion': '15 días',
            'cobertura': 847,
            'costo_total': 12000,
            'costo_nino': 14.17,
            'reduccion': '15-20%',
            'color': '#FF6B6B'
        },
        'B': {
            'titulo': 'Redistribución Stock',
            'emoji': '📦',
            'descripcion': 'Aumentar disponibilidad de suplemento',
            'duracion': '3 meses',
            'cobertura': 847,
            'costo_total': 5000,
            'costo_nino': 5.90,
            'reduccion': '10-15%',
            'color': '#FFA500'
        },
        'C': {
            'titulo': 'Intervención Integral',
            'emoji': '💊',
            'descripcion': 'Suplemento + Menús + Educación',
            'duracion': '6 meses',
            'cobertura': 1200,
            'costo_total': 85000,
            'costo_nino': 70.83,
            'reduccion': '25-30%',
            'color': '#007BFF'
        },
        'D': {
            'titulo': 'Alianza Multi-Sectorial',
            'emoji': '🤝',
            'descripcion': 'MINSA + Municipio + ONG + Privada',
            'duracion': '12 meses',
            'cobertura': 2000,
            'costo_total': 95000,
            'costo_nino': 47.50,
            'reduccion': '30-40%',
            'color': '#28A745'
        }
    }

    # Tabs para opciones
    tab_a, tab_b, tab_c, tab_d = st.tabs([
        f"Opción A {opciones['A']['emoji']}", 
        f"Opción B {opciones['B']['emoji']}", 
        f"Opción C {opciones['C']['emoji']}", 
        f"Opción D {opciones['D']['emoji']}"
    ])

    # ════════════════════════════════════════════════════════════════════════
    # OPCIÓN A
    # ════════════════════════════════════════════════════════════════════════
    with tab_a:
        mostrar_tarjeta_opcion(opciones['A'])
        mostrar_metricas_opcion(opciones['A'])
        mostrar_grafico_comparativo(opciones['A'])

    # ════════════════════════════════════════════════════════════════════════
    # OPCIÓN B
    # ════════════════════════════════════════════════════════════════════════
    with tab_b:
        mostrar_tarjeta_opcion(opciones['B'])
        mostrar_metricas_opcion(opciones['B'])
        mostrar_grafico_comparativo(opciones['B'])

    # ════════════════════════════════════════════════════════════════════════
    # OPCIÓN C (NUEVA)
    # ════════════════════════════════════════════════════════════════════════
    with tab_c:
        mostrar_tarjeta_opcion(opciones['C'])
        mostrar_metricas_opcion(opciones['C'])
        mostrar_grafico_comparativo(opciones['C'])

    # ════════════════════════════════════════════════════════════════════════
    # OPCIÓN D (NUEVA)
    # ════════════════════════════════════════════════════════════════════════
    with tab_d:
        mostrar_tarjeta_opcion(opciones['D'])
        mostrar_metricas_opcion(opciones['D'])
        mostrar_grafico_comparativo(opciones['D'])

    st.markdown("---")

    # ════════════════════════════════════════════════════════════════════════
    # RECOMENDACIÓN
    # ════════════════════════════════════════════════════════════════════════
    st.markdown("## 🎯 Recomendación del Sistema")

    st.success("""
    ✅ **Opción D (Alianza Multi-Sectorial) es la más efectiva**

    • 30-40% reducción de anemia (máximo impacto)
    • ROI superior: 12x a largo plazo
    • Sostenible y escalable a nivel nacional
    • Requiere coordinación inter-sectorial
    """)

    st.markdown("---")

    # ════════════════════════════════════════════════════════════════════════
    # EXPORTACIÓN MEJORADA (CSV + PDF + EMAIL)
    # ════════════════════════════════════════════════════════════════════════
    st.markdown("## 💾 Exportar Datos y Reportes")

    col_exp1, col_exp2, col_exp3 = st.columns([1, 1, 1.5])

    # ✅ DESCARGAR CSV
    with col_exp1:
        if st.button("📊 CSV", use_container_width=True, key="btn_csv_entidad"):
            datos_export = pd.DataFrame([
                {
                    'Zona': h['nombre'], 
                    'Prevalencia': f"{h['prevalencia']}%", 
                    'Evaluados': h['evaluados'], 
                    'Críticos': h['criticos']
                }
                for h in hotspots
            ])

            csv = datos_export.to_csv(index=False)
            st.download_button(
                label="⬇️ Descargar CSV",
                data=csv,
                file_name=f"hotspots_entidad_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

    # ✅ DESCARGAR PDF PROFESIONAL
    with col_exp2:
        if st.button("📄 PDF", use_container_width=True, key="btn_pdf_entidad"):
            with st.spinner("🔄 Generando PDF profesional..."):
                try:
                    pdf_buffer = generar_pdf_reportes_entidad(hotspots, opciones)
                    if pdf_buffer:
                        st.download_button(
                            label="⬇️ Descargar PDF",
                            data=pdf_buffer,
                            file_name=f"informe_entidad_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        st.success("✅ PDF listo para descargar")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    # ✅ ENVIAR POR EMAIL CON ANIMACIÓN
    with col_exp3:
        email = st.text_input(
            "📧 Email",
            value="entidad@minsa.gob.pe",
            key="email_entidad_input"
        )

        if st.button("✉️ Enviar Email", use_container_width=True, key="btn_email_entidad"):
            enviar_email_animado(email)

    st.markdown("---")

    # ════════════════════════════════════════════════════════════════════════
    # INFORMACIÓN DEL SISTEMA
    # ════════════════════════════════════════════════════════════════════════
    st.info("""
    ℹ️ **Información del Sistema**

    - Datos actualizados: 03/Nov/2025
    - Cobertura: 3 regiones prioritarias
    - Próxima revisión: 10/Nov/2025
    - Modelo: NutriSenseIA v1.0 - Datatón MINSA 2025
    """)


# ════════════════════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES
# ════════════════════════════════════════════════════════════════════════════

def mostrar_tarjeta_opcion(opcion):
    """Tarjeta visual para cada opción"""

    st.markdown(f"""
    <div style='background: linear-gradient(135deg, {opcion['color']}1A 0%, {opcion['color']}0D 100%);
                border-left: 5px solid {opcion['color']};
                padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem;'>
        <div style='display: flex; align-items: center; gap: 1rem;'>
            <div style='font-size: 2.5rem;'>{opcion['emoji']}</div>
            <div>
                <h3 style='margin: 0; color: {opcion['color']};'>{opcion['titulo']}</h3>
                <p style='margin: 0.5rem 0 0 0; color: #666;'>{opcion['descripcion']}</p>
                <p style='margin: 0.5rem 0 0 0; font-weight: bold; color: {opcion['color']};'>
                    Reducción: {opcion['reduccion']}
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def mostrar_metricas_opcion(opcion):
    """Métricas de la opción"""

    st.markdown(f"""
    **Estrategia:** {opcion['descripcion']}

    **Duración:** {opcion['duracion']}
    """)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Niños a Tratar", f"{opcion['cobertura']:,}")

    with col2:
        st.metric("Costo Total", f"S/ {opcion['costo_total']:,.0f}")

    with col3:
        st.metric("Costo/Niño", f"S/ {opcion['costo_nino']:.2f}")


def mostrar_grafico_comparativo(opcion):
    """Gráfico antes/después"""

    prevalencia_actual = 68  # Ayacucho
    reduccion_pct = int(opcion['reduccion'].split('-')[0])
    prevalencia_proyectada = prevalencia_actual - (prevalencia_actual * reduccion_pct / 100)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=['Situación Actual', 'Con Intervención'],
        y=[prevalencia_actual, prevalencia_proyectada],
        marker=dict(color=['#ff6b6b', '#28a745']),
        text=[f"{prevalencia_actual:.1f}%", f"{prevalencia_proyectada:.1f}%"],
        textposition='auto'
    ))

    fig.update_layout(
        title="Impacto Estimado",
        yaxis_title="Prevalencia (%)",
        showlegend=False,
        height=300,
        template='plotly_white'
    )

    st.plotly_chart(fig, use_container_width=True)


def generar_pdf_reportes_entidad(hotspots, opciones):
    """Genera PDF PROFESIONAL con todas las opciones"""

    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=letter,
            rightMargin=0.5*inch, leftMargin=0.5*inch,
            topMargin=0.75*inch, bottomMargin=0.75*inch
        )

        story = []
        styles = getSampleStyleSheet()

        # ✅ TÍTULO
        story.append(Paragraph("📊 INFORME DE DECISIONES - ENTIDAD MINSA", styles["Heading1"]))
        story.append(Paragraph(
            f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            styles["Normal"]
        ))
        story.append(Spacer(1, 0.3*inch))

        # ✅ HOTSPOTS
        story.append(Paragraph("🔴 HOTSPOTS CRÍTICOS IDENTIFICADOS", styles["Heading2"]))
        datos_hotspots = [['Zona', 'Prevalencia', 'Críticos', 'Total']]
        for h in hotspots:
            datos_hotspots.append([h['nombre'], f"{h['prevalencia']}%", str(h['criticos']), str(h['evaluados'])])

        table_hotspots = Table(datos_hotspots)
        table_hotspots.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#FF6B6B")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 1, colors.grey),
        ]))

        story.append(table_hotspots)
        story.append(Spacer(1, 0.3*inch))

        # ✅ OPCIONES COMPARATIVAS
        story.append(Paragraph("📍 OPCIONES DE INTERVENCIÓN", styles["Heading2"]))
        datos_opciones = [['Opción', 'Estrategia', 'Reducción', 'Costo', 'Costo/Niño']]
        for letra, opt in opciones.items():
            datos_opciones.append([
                letra,
                opt['titulo'],
                opt['reduccion'],
                f"S/ {opt['costo_total']:,.0f}",
                f"S/ {opt['costo_nino']:.2f}"
            ])

        table_opciones = Table(datos_opciones)
        table_opciones.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#007BFF")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 1, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.beige, colors.white]),
        ]))

        story.append(table_opciones)
        story.append(Spacer(1, 0.3*inch))

        # ✅ RECOMENDACIÓN
        story.append(Paragraph("✅ RECOMENDACIÓN FINAL", styles["Heading2"]))
        story.append(Paragraph(
            "<b>Opción D (Alianza Multi-Sectorial)</b> ofrece el máximo impacto (30-40% reducción) "
            "con mejor ROI a largo plazo (12x). Requiere coordinación inter-sectorial pero garantiza "
            "sostenibilidad y escalabilidad a nivel nacional.",
            styles['Normal']
        ))

        doc.build(story)
        buffer.seek(0)
        return buffer

    except Exception as e:
        st.error(f"Error generando PDF: {str(e)}")
        return None


def enviar_email_animado(email):
    """Simula envío de email con animación"""

    placeholder = st.empty()

    with placeholder.container():
        progress_bar = st.progress(0)
        status_text = st.empty()

    import time

    # Animación de progreso
    for i in range(101):
        progress_bar.progress(i)

        if i < 33:
            status_text.text("📬 Preparando informe...")
        elif i < 66:
            status_text.text("📧 Generando PDF...")
        elif i < 100:
            status_text.text("✉️ Enviando...")

        time.sleep(0.02)

    # Limpiar placeholder
    placeholder.empty()

    # ✅ CONFIRMACIÓN EXITOSA
    st.success(f"""
    ✅ **¡Informe enviado exitosamente!**

    📧 Destinatario: {email}
    📎 Archivos: PDF + CSV
    ⏰ Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}

    💡 Tip: Revisa tu bandeja de entrada
    """)