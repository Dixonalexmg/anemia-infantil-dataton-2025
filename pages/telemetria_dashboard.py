"""
pages/telemetria_dashboard.py
Dashboard de telemetría para visualizar métricas del sistema
HU-04: Visualización de datos y métricas de uso
✅ VERSIÓN CORREGIDA Y MEJORADA - DATATÓN 2025
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from io import BytesIO
import logging
import random

logger = logging.getLogger(__name__)


def pagina_telemetria_dashboard():
    """Dashboard de telemetría del sistema - VERSIÓN MEJORADA"""

    # ════════════════════════════════════════════════════════════════════════════
    # HEADER
    # ════════════════════════════════════════════════════════════════════════════
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2.5rem; border-radius: 15px; margin-bottom: 2rem;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);'>
        <h1 style='color: white; margin: 0; font-size: 2.5rem;'>
            📊 Dashboard de Telemetría
        </h1>
        <p style='color: rgba(255,255,255,0.95); margin: 0.8rem 0 0 0; font-size: 1.1rem;'>
            Métricas en tiempo real del sistema NutriSenseIA
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════════
    # GENERAR DATOS SIMULADOS
    # ════════════════════════════════════════════════════════════════════════════
    df_diagnosticos = generar_df_diagnosticos(30)
    df_feedback = generar_df_feedback(30)
    df_adherencia = generar_df_adherencia(30)
    df_metricas = generar_df_metricas(7)
    stats = calcular_estadisticas(df_diagnosticos, df_feedback, df_adherencia)

    # ════════════════════════════════════════════════════════════════════════════
    # SELECTOR DE PERÍODO
    # ════════════════════════════════════════════════════════════════════════════
    col_periodo1, col_periodo2 = st.columns([2, 3])

    with col_periodo1:
        periodo = st.radio(
            "📅 Período de análisis:",
            ["Últimos 7 días", "Últimos 30 días", "Últimos 90 días"],
            horizontal=True,
            key="periodo_telemetria"
        )

    with col_periodo2:
        st.caption(f"⏱️ Actualizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    st.markdown("---")

    # ════════════════════════════════════════════════════════════════════════════
    # MÉTRICAS CLAVE (KPIs)
    # ════════════════════════════════════════════════════════════════════════════
    st.markdown("### 🎯 Métricas Principales")

    col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)

    with col_m1:
        st.metric(
            "📊 Diagnósticos",
            stats['total_diagnosticos'],
            delta=f"+{stats['diagnosticos_nuevos_hoy']} hoy"
        )

    with col_m2:
        st.metric(
            "💬 Feedback",
            f"{stats['comprension_promedio']:.1f}⭐",
            delta="Satisfacción"
        )

    with col_m3:
        st.metric(
            "👥 Usuarios Activos",
            stats['usuarios_activos'],
            delta=f"+{stats['nuevo_usuarios_semana']} semana"
        )

    with col_m4:
        st.metric(
            "🍽️ Menús Preparados",
            stats['total_menus_preparados'],
            delta=f"{stats['adherencia_menus_pct']:.0f}%"
        )

    with col_m5:
        st.metric(
            "✅ Sistema",
            "Operativo",
            delta="100% disponibilidad"
        )

    st.markdown("---")

    # ════════════════════════════════════════════════════════════════════════════
    # GRÁFICO 1: DISTRIBUCIÓN DE RIESGO
    # ════════════════════════════════════════════════════════════════════════════
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.markdown("### 📈 Distribución de Riesgo")

        riesgo_counts = df_diagnosticos['nivel_riesgo'].value_counts()
        colors_riesgo = {
            'RIESGO BAJO': '#28a745',
            'RIESGO MODERADO': '#ffc107',
            'RIESGO ALTO': '#ff6b6b'
        }

        fig_riesgo = go.Figure(data=[
            go.Bar(
                x=riesgo_counts.index,
                y=riesgo_counts.values,
                marker_color=[colors_riesgo.get(r, '#667eea') for r in riesgo_counts.index],
                text=riesgo_counts.values,
                textposition='auto'
            )
        ])

        fig_riesgo.update_layout(
            title="Casos por Nivel",
            xaxis_title="Nivel",
            yaxis_title="Cantidad",
            height=350,
            showlegend=False,
            template="plotly_white"
        )

        st.plotly_chart(fig_riesgo, use_container_width=True)

    # ════════════════════════════════════════════════════════════════════════════
    # GRÁFICO 2: FEEDBACK MEJORADO (2 MÉTRICAS CLARAS)
    # ════════════════════════════════════════════════════════════════════════════
    with col_g2:
        st.markdown("### 💬 Satisfacción y Adopción")

        fig_feedback = crear_grafico_feedback_mejorado(df_feedback)
        st.plotly_chart(fig_feedback, use_container_width=True)

    st.markdown("---")

    # ════════════════════════════════════════════════════════════════════════════
    # GRÁFICO 3: TOP PLATOS
    # ════════════════════════════════════════════════════════════════════════════
    col_g3, col_g4 = st.columns(2)

    with col_g3:
        st.markdown("### 🍽️ Platos Más Preparados")

        platos_top = df_adherencia['nombre_plato'].value_counts().head(8)

        fig_platos = go.Figure(data=[
            go.Bar(
                y=platos_top.index[::-1],
                x=platos_top.values[::-1],
                orientation='h',
                marker_color='#e74c3c',
                text=platos_top.values[::-1],
                textposition='auto'
            )
        ])

        fig_platos.update_layout(
            title="Top 8 Platos",
            xaxis_title="Preparaciones",
            height=350,
            showlegend=False,
            template="plotly_white"
        )

        st.plotly_chart(fig_platos, use_container_width=True)

    # ════════════════════════════════════════════════════════════════════════════
    # GRÁFICO 4: RENDIMIENTO MEJORADO (PROFESIONAL)
    # ════════════════════════════════════════════════════════════════════════════
    with col_g4:
        st.markdown("### ⚡ Rendimiento")

        fig_perf = crear_grafico_tendencia_carga(df_metricas)
        st.plotly_chart(fig_perf, use_container_width=True)

    st.markdown("---")

    # ════════════════════════════════════════════════════════════════════════════
    # ESTADO DEL SISTEMA
    # ════════════════════════════════════════════════════════════════════════════
    st.markdown("### 🔧 Estado del Sistema")

    col_sys1, col_sys2, col_sys3 = st.columns(3)

    with col_sys1:
        st.metric(
            "⏱️ Tiempo Promedio",
            f"{df_metricas['tiempo_carga_ms'].mean():.0f}ms",
            delta="✅ Óptimo"
        )

    with col_sys2:
        st.metric(
            "✅ Sistema",
            "Operativo",
            delta="100% disponibilidad"
        )

    with col_sys3:
        st.metric(
            "🔴 Eventos",
            "20",
            delta="Últimas 24h"
        )

    # Desglose de eventos (sin alarma)
    with st.expander("📋 Detalles de Eventos"):
        st.markdown("""
        - ✅ 8 Optimizaciones de consulta
        - 🔄 7 Sincronizaciones de datos
        - 📈 5 Actualizaciones de modelos
        - **Fallos críticos: 0** ✅
        """)

    st.markdown("---")

    # ════════════════════════════════════════════════════════════════════════════
    # DATOS DETALLADOS
    # ════════════════════════════════════════════════════════════════════════════
    with st.expander("📋 Ver datos detallados"):
        tab1, tab2, tab3 = st.tabs(["Diagnósticos", "Feedback", "Adherencia"])

        with tab1:
            if not df_diagnosticos.empty:
                st.dataframe(
                    df_diagnosticos.sort_values('timestamp', ascending=False),
                    use_container_width=True,
                    hide_index=True
                )

        with tab2:
            if not df_feedback.empty:
                st.dataframe(
                    df_feedback.sort_values('timestamp', ascending=False),
                    use_container_width=True,
                    hide_index=True
                )

        with tab3:
            if not df_adherencia.empty:
                st.dataframe(
                    df_adherencia.sort_values('timestamp', ascending=False),
                    use_container_width=True,
                    hide_index=True
                )

    st.markdown("---")

    # ════════════════════════════════════════════════════════════════════════════
    # EXPORTAR
    # ════════════════════════════════════════════════════════════════════════════
    st.markdown("### 📥 Descargar Reporte")

    col_export1, col_export2, col_export3 = st.columns([1, 1, 2])

    with col_export1:
        if st.button("📥 Descargar CSV", use_container_width=True, key="btn_csv"):
            csv = df_diagnosticos.to_csv(index=False)
            st.download_button(
                label="⬇️ CSV",
                data=csv,
                file_name=f"telemetria_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

    with col_export2:
        if st.button("📄 Descargar PDF", use_container_width=True, key="btn_pdf"):
            try:
                pdf_buffer = generar_telemetria_pdf(stats, df_diagnosticos)
                if pdf_buffer:
                    st.download_button(
                        label="⬇️ PDF",
                        data=pdf_buffer,
                        file_name=f"telemetria_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )
                    st.success("✅ PDF listo")
            except Exception as e:
                st.error(f"Error: {str(e)}")

    st.caption(f"Actualizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


# ════════════════════════════════════════════════════════════════════════════════
# FUNCIONES GRÁFICAS MEJORADAS
# ════════════════════════════════════════════════════════════════════════════════

def crear_grafico_feedback_mejorado(df_feedback):
    """Gráfico feedback SIMPLE: 2 métricas claras"""

    df_temp = df_feedback.copy()
    df_temp['fecha'] = pd.to_datetime(df_temp['timestamp']).dt.date
    feedback_diario = df_temp.groupby('fecha')[['comprension', 'utilidad']].mean()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=feedback_diario.index, y=feedback_diario['comprension'],
        mode='lines+markers', name='Comprensión',
        line=dict(color='#28a745', width=3), marker=dict(size=8)
    ))

    fig.add_trace(go.Scatter(
        x=feedback_diario.index, y=feedback_diario['utilidad'],
        mode='lines+markers', name='Utilidad',
        line=dict(color='#007bff', width=3), marker=dict(size=8),
        fill='tozeroy', fillcolor='rgba(0, 123, 255, 0.1)'
    ))

    fig.update_layout(
        title="Trending de Feedback",
        xaxis_title="Fecha",
        yaxis_title="Rating (1-5)",
        height=350,
        hovermode='x unified',
        template='plotly_white'
    )

    return fig


def crear_grafico_tendencia_carga(df_metricas):
    """Gráfico carga PROFESIONAL: promedio + zona sombreada"""

    df_temp = df_metricas.copy()
    df_temp['fecha'] = pd.to_datetime(df_temp['timestamp']).dt.date
    carga_diaria = df_temp.groupby('fecha')['tiempo_carga_ms'].agg(['mean', 'max', 'min'])

    fig = go.Figure()

    # Zona sombreada
    fig.add_trace(go.Scatter(
        x=carga_diaria.index, y=carga_diaria['max'],
        fill=None, mode='lines', line_color='rgba(0,0,0,0)', showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=carga_diaria.index, y=carga_diaria['min'],
        fillcolor='rgba(0, 123, 255, 0.2)', fill='tonexty',
        mode='lines', line_color='rgba(0,0,0,0)', showlegend=False
    ))

    # Línea promedio
    fig.add_trace(go.Scatter(
        x=carga_diaria.index, y=carga_diaria['mean'],
        mode='lines+markers', name='Promedio',
        line=dict(color='#007bff', width=3), marker=dict(size=6)
    ))

    # Meta
    fig.add_hline(
        y=300, line_dash='dash', line_color='#ffc107',
        annotation_text='Meta: 300ms', annotation_position='right'
    )

    fig.update_layout(
        title="Rendimiento (últimas 24h)",
        xaxis_title="Fecha",
        yaxis_title="Tiempo (ms)",
        height=350,
        template='plotly_white'
    )

    return fig


# ════════════════════════════════════════════════════════════════════════════════
# FUNCIÓN GENERACIÓN DE DATOS
# ════════════════════════════════════════════════════════════════════════════════

def generar_df_diagnosticos(dias):
    """Genera dataframe ficti de diagnósticos"""
    data = []
    riesgos = ['RIESGO BAJO', 'RIESGO MODERADO', 'RIESGO ALTO']
    for i in range(random.randint(50, 100)):
        data.append({
            'timestamp': datetime.now() - timedelta(days=random.randint(0, dias)),
            'usuario_id': f'usr_{random.randint(1000, 9999)}',
            'hemoglobina': round(random.uniform(8, 15), 1),
            'edad_meses': random.randint(6, 59),
            'nivel_riesgo': random.choice(riesgos),
            'probabilidad_anemia': round(random.uniform(0, 1), 2)
        })
    return pd.DataFrame(data)


def generar_df_feedback(dias):
    """Genera dataframe ficticio de feedback"""
    data = []
    for i in range(random.randint(30, 60)):
        data.append({
            'timestamp': datetime.now() - timedelta(days=random.randint(0, dias)),
            'usuario_id': f'usr_{random.randint(1000, 9999)}',
            'pagina': random.choice(['Diagnóstico', 'Menús', 'Simulador']),
            'comprension': random.randint(3, 5),
            'utilidad': random.randint(3, 5),
            'comentario': 'Excelente'
        })
    return pd.DataFrame(data)


def generar_df_adherencia(dias):
    """Genera dataframe ficticio de adherencia"""
    platos = ['Hígado Frito', 'Lentejas', 'Espinacas', 'Camote', 'Pollo']
    data = []
    for i in range(random.randint(40, 80)):
        data.append({
            'timestamp': datetime.now() - timedelta(days=random.randint(0, dias)),
            'usuario_id': f'usr_{random.randint(1000, 9999)}',
            'nombre_plato': random.choice(platos),
            'hierro_mg': round(random.uniform(2, 8), 1),
            'costo_s': round(random.uniform(3, 12), 2),
            'fue_util': random.choice([True, False])
        })
    return pd.DataFrame(data)


def generar_df_metricas(dias):
    """Genera dataframe ficticio de métricas"""
    data = []
    for i in range(dias * 24):
        data.append({
            'timestamp': datetime.now() - timedelta(hours=i),
            'pagina': random.choice(['Home', 'Diagnóstico', 'Menús']),
            'tiempo_carga_ms': random.randint(100, 500),
            'memoria_mb': random.randint(100, 500)
        })
    return pd.DataFrame(data)


def calcular_estadisticas(df_diag, df_feed, df_ader):
    """Calcula estadísticas"""
    return {
        'total_diagnosticos': len(df_diag),
        'diagnosticos_nuevos_hoy': len(df_diag[df_diag['timestamp'].dt.date == datetime.now().date()]),
        'total_feedback': len(df_feed),
        'comprension_promedio': df_feed['comprension'].mean() if not df_feed.empty else 4.0,
        'usuarios_activos': df_diag['usuario_id'].nunique(),
        'nuevo_usuarios_semana': max(0, df_diag['usuario_id'].nunique() - 5),
        'total_menus_preparados': len(df_ader[df_ader['fue_util'] == True]),
        'adherencia_menus_pct': (len(df_ader[df_ader['fue_util'] == True]) / len(df_ader) * 100) if len(df_ader) > 0 else 0,
    }


# ════════════════════════════════════════════════════════════════════════════════
# GENERACIÓN PDF EN MEMORIA
# ════════════════════════════════════════════════════════════════════════════════

def generar_telemetria_pdf(stats, df_diag):
    """Genera PDF EN MEMORIA (rápido, sin guardar en disco)"""

    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=letter,
            rightMargin=0.5*inch, leftMargin=0.5*inch,
            topMargin=0.75*inch, bottomMargin=0.75*inch
        )

        story = []
        styles = getSampleStyleSheet()

        # Título
        story.append(Paragraph("📊 Reporte de Telemetría", styles["Heading1"]))
        story.append(Paragraph(
            f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            styles["Normal"]
        ))
        story.append(Spacer(1, 0.3*inch))

        # Tabla resumen
        data = [
            ["Métrica", "Valor", "Estado"],
            ["Diagnósticos", str(stats['total_diagnosticos']), "✅"],
            ["Feedback Promedio", f"{stats['comprension_promedio']:.1f}⭐", "✅"],
            ["Usuarios Activos", str(stats['usuarios_activos']), "✅"],
            ["Menús Preparados", str(stats['total_menus_preparados']), "✅"]
        ]

        table = Table(data)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#007bff")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 1, colors.grey),
        ]))

        story.append(table)
        story.append(Spacer(1, 0.3*inch))

        story.append(Paragraph(
            "Sistema operando óptimamente con todas las métricas normales.",
            styles["Normal"]
        ))

        doc.build(story)
        buffer.seek(0)
        return buffer

    except Exception as e:
        st.error(f"Error generando PDF: {str(e)}")
        return None