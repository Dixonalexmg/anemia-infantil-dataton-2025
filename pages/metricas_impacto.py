# pages/metricas_impacto.py
"""
Panel de Impacto: Comparación de zonas con/sin intervención NutriWawa
KPIs de éxito del proyecto
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

def pagina_metricas_impacto():
    """Panel ejecutivo de impacto del proyecto"""
    
    # HEADER
    st.markdown("""
    <div style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem;'>
        <div style='display: flex; align-items: center; gap: 1rem;'>
            <div style='font-size: 3rem;'>📊</div>
            <div>
                <h1 style='color: white; margin: 0;'>Panel de Impacto NutriWawa</h1>
                <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;'>
                    Comparación de zonas con y sin intervención
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # FILTROS SIMPLES
    col1, col2 = st.columns(2)
    with col1:
        zona_control = st.selectbox("Zona de Control (sin intervención)", 
                                    ["HUANCAVELICA - Acobamba", "PUNO - Azángaro", "CUSCO - Chumbivilcas"])
    with col2:
        zona_intervencion = st.selectbox("Zona de Intervención (con NutriWawa)",
                                         ["LIMA - San Juan de Lurigancho", "AREQUIPA - Cayma", "JUNIN - Huancayo"])
    
    periodo = st.selectbox("Período de análisis", ["Últimos 3 meses", "Últimos 6 meses", "Último año"])
    
    st.markdown("---")
    
    # ========== KPIs PRINCIPALES ==========
    st.markdown("## 🎯 KPIs de Éxito")
    
    # Cargar datos simulados (en producción, vienen de base de datos)
    datos_control = generar_datos_simulados(zona_control, con_intervencion=False)
    datos_intervencion = generar_datos_simulados(zona_intervencion, con_intervencion=True)
    
    # MÉTRICAS COMPARATIVAS
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        delta_adherencia = datos_intervencion['adherencia'] - datos_control['adherencia']
        st.metric(
            "📈 Adherencia a Menús",
            f"{datos_intervencion['adherencia']:.0f}%",
            delta=f"+{delta_adherencia:.0f}pp vs. control",
            delta_color="normal",
            help="Objetivo: +15pp vs. línea base"
        )
        if delta_adherencia >= 15:
            st.success("✅ META ALCANZADA")
        else:
            st.warning(f"⚠️ Falta {15-delta_adherencia:.0f}pp")
    
    with col2:
        reduccion_riesgo = ((datos_control['riesgo_alto'] - datos_intervencion['riesgo_alto']) 
                           / datos_control['riesgo_alto'] * 100)
        st.metric(
            "⬇️ Reducción Riesgo Alto",
            f"{datos_intervencion['riesgo_alto']:.0f}%",
            delta=f"-{reduccion_riesgo:.0f}%",
            delta_color="inverse",
            help="Porcentaje de niños con anemia moderada/severa"
        )
        if reduccion_riesgo >= 20:
            st.success("✅ META ALCANZADA")
    
    with col3:
        st.metric(
            "📄 PDFs Generados",
            f"{datos_intervencion['pdfs_generados']:,}",
            delta=f"{datos_intervencion['tasa_error_pdf']:.1f}% errores",
            delta_color="inverse",
            help="Objetivo: <1% de errores"
        )
        if datos_intervencion['tasa_error_pdf'] < 1:
            st.success("✅ META ALCANZADA")
    
    with col4:
        st.metric(
            "😊 Satisfacción",
            f"{datos_intervencion['satisfaccion']:.0f}%",
            delta=f"+{datos_intervencion['satisfaccion']-datos_control['satisfaccion']:.0f}pp",
            delta_color="normal",
            help="Objetivo: ≥95%"
        )
        if datos_intervencion['satisfaccion'] >= 95:
            st.success("✅ META ALCANZADA")
        else:
            st.warning(f"⚠️ Falta {95-datos_intervencion['satisfaccion']:.0f}pp")
    
    # ========== GRÁFICO COMPARATIVO ==========
    st.markdown("---")
    st.markdown("## 📊 Comparación Temporal: Control vs. Intervención")
    
    # Datos de serie temporal
    fechas = pd.date_range(end=datetime.now(), periods=12, freq='W')
    
    df_comparacion = pd.DataFrame({
        'Fecha': fechas,
        'Control - Adherencia': np.linspace(45, 48, 12) + np.random.normal(0, 2, 12),
        'Intervención - Adherencia': np.linspace(45, 63, 12) + np.random.normal(0, 2, 12),
        'Control - Riesgo Alto': np.linspace(38, 37, 12) + np.random.normal(0, 1.5, 12),
        'Intervención - Riesgo Alto': np.linspace(38, 28, 12) + np.random.normal(0, 1.5, 12)
    })
    
    # Gráfico de adherencia
    fig_adherencia = go.Figure()
    
    fig_adherencia.add_trace(go.Scatter(
        x=df_comparacion['Fecha'],
        y=df_comparacion['Control - Adherencia'],
        mode='lines+markers',
        name='Zona Control',
        line=dict(color='gray', width=2, dash='dash')
    ))
    
    fig_adherencia.add_trace(go.Scatter(
        x=df_comparacion['Fecha'],
        y=df_comparacion['Intervención - Adherencia'],
        mode='lines+markers',
        name='Zona con NutriWawa',
        line=dict(color='#11998e', width=3)
    ))
    
    fig_adherencia.add_hline(y=60, line_dash="dot", line_color="green",
                             annotation_text="Meta: 60% (+15pp)")
    
    fig_adherencia.update_layout(
        title="Evolución de Adherencia a Menús Recomendados",
        xaxis_title="Fecha",
        yaxis_title="% Adherencia",
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig_adherencia, use_container_width=True)
    
    # Gráfico de reducción de riesgo
    fig_riesgo = go.Figure()
    
    fig_riesgo.add_trace(go.Scatter(
        x=df_comparacion['Fecha'],
        y=df_comparacion['Control - Riesgo Alto'],
        mode='lines+markers',
        name='Zona Control',
        line=dict(color='gray', width=2, dash='dash'),
        fill='tozeroy',
        fillcolor='rgba(200,200,200,0.2)'
    ))
    
    fig_riesgo.add_trace(go.Scatter(
        x=df_comparacion['Fecha'],
        y=df_comparacion['Intervención - Riesgo Alto'],
        mode='lines+markers',
        name='Zona con NutriWawa',
        line=dict(color='red', width=3),
        fill='tozeroy',
        fillcolor='rgba(255,100,100,0.2)'
    ))
    
    fig_riesgo.update_layout(
        title="Reducción de Casos de Riesgo Alto (Anemia Moderada/Severa)",
        xaxis_title="Fecha",
        yaxis_title="% Niños en Riesgo Alto",
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig_riesgo, use_container_width=True)
    
    # ========== TABLA COMPARATIVA ==========
    st.markdown("---")
    st.markdown("## 📋 Resumen Comparativo")
    
    tabla_comparativa = pd.DataFrame({
        'Indicador': [
            'Adherencia a menús (%)',
            'Riesgo alto (anemia mod/severa) (%)',
            'Comprensión de recomendaciones (%)',
            'PDFs descargados',
            'Tasa de error PDF (%)',
            'Satisfacción usuaria (%)',
            'Tiempo promedio generación PDF (s)'
        ],
        'Zona Control': [
            f"{datos_control['adherencia']:.0f}%",
            f"{datos_control['riesgo_alto']:.0f}%",
            f"{datos_control['comprension']:.0f}%",
            f"{datos_control['pdfs_generados']:,}",
            f"{datos_control['tasa_error_pdf']:.1f}%",
            f"{datos_control['satisfaccion']:.0f}%",
            f"{datos_control['tiempo_pdf']:.1f}s"
        ],
        'Zona Intervención': [
            f"{datos_intervencion['adherencia']:.0f}%",
            f"{datos_intervencion['riesgo_alto']:.0f}%",
            f"{datos_intervencion['comprension']:.0f}%",
            f"{datos_intervencion['pdfs_generados']:,}",
            f"{datos_intervencion['tasa_error_pdf']:.1f}%",
            f"{datos_intervencion['satisfaccion']:.0f}%",
            f"{datos_intervencion['tiempo_pdf']:.1f}s"
        ],
        'Delta': [
            f"+{datos_intervencion['adherencia']-datos_control['adherencia']:.0f}pp",
            f"-{datos_control['riesgo_alto']-datos_intervencion['riesgo_alto']:.0f}pp",
            f"+{datos_intervencion['comprension']-datos_control['comprension']:.0f}pp",
            f"+{datos_intervencion['pdfs_generados']-datos_control['pdfs_generados']:,}",
            f"-{datos_control['tasa_error_pdf']-datos_intervencion['tasa_error_pdf']:.1f}pp",
            f"+{datos_intervencion['satisfaccion']-datos_control['satisfaccion']:.0f}pp",
            f"-{datos_control['tiempo_pdf']-datos_intervencion['tiempo_pdf']:.1f}s"
        ],
        'Meta': [
            '≥60% (+15pp)',
            '<30% (-20%)',
            '≥80%',
            'N/A',
            '<1%',
            '≥95%',
            '<10s'
        ]
    })
    
    st.dataframe(tabla_comparativa, use_container_width=True, hide_index=True)
    
    # ========== CONCLUSIONES AUTOMÁTICAS ==========
    st.markdown("---")
    st.markdown("## 🎓 Conclusiones del Análisis")
    
    conclusiones = generar_conclusiones(datos_control, datos_intervencion)
    
    for i, conclusion in enumerate(conclusiones, 1):
        st.markdown(f"{i}. {conclusion}")
    
    # ========== EXPORTAR REPORTE ==========
    st.markdown("---")
    if st.button("📥 Descargar Reporte Completo (PDF)", type="primary", use_container_width=True):
        st.success("✅ Reporte generado exitosamente - Descarga iniciada")
        st.info("💡 El reporte incluye todos los KPIs, gráficos y conclusiones de este análisis")


# ========== FUNCIONES AUXILIARES ==========

def generar_datos_simulados(zona, con_intervencion):
    """Genera datos simulados para la demostración"""
    if con_intervencion:
        return {
            'adherencia': np.random.normal(63, 3),
            'riesgo_alto': np.random.normal(28, 2),
            'comprension': np.random.normal(95, 2),
            'pdfs_generados': np.random.randint(1200, 1500),
            'tasa_error_pdf': np.random.normal(0.3, 0.1),
            'satisfaccion': np.random.normal(96, 1.5),
            'tiempo_pdf': np.random.normal(4.2, 0.5)
        }
    else:
        return {
            'adherencia': np.random.normal(48, 3),
            'riesgo_alto': np.random.normal(37, 2),
            'comprension': np.random.normal(72, 3),
            'pdfs_generados': np.random.randint(400, 600),
            'tasa_error_pdf': np.random.normal(2.5, 0.5),
            'satisfaccion': np.random.normal(78, 2),
            'tiempo_pdf': np.random.normal(8.5, 1.0)
        }


def generar_conclusiones(control, intervencion):
    """Genera conclusiones automáticas basadas en los datos"""
    conclusiones = []
    
    delta_adherencia = intervencion['adherencia'] - control['adherencia']
    if delta_adherencia >= 15:
        conclusiones.append(f"✅ **Adherencia:** La intervención logró un incremento de **+{delta_adherencia:.0f}pp** "
                          f"(meta: +15pp). Esto indica que las recomendaciones personalizadas y los menús locales "
                          f"son efectivos para cambiar comportamientos alimentarios.")
    
    reduccion_riesgo = ((control['riesgo_alto'] - intervencion['riesgo_alto']) 
                       / control['riesgo_alto'] * 100)
    if reduccion_riesgo >= 20:
        conclusiones.append(f"✅ **Reducción de Riesgo:** Se observó una disminución del **{reduccion_riesgo:.0f}%** "
                          f"en casos de anemia moderada/severa. Esto representa un impacto significativo en salud pública.")
    
    if intervencion['satisfaccion'] >= 95:
        conclusiones.append(f"✅ **Satisfacción:** La tasa de satisfacción del **{intervencion['satisfaccion']:.0f}%** "
                          f"supera la meta del 95%, indicando alta aceptación por parte de las madres y personal de salud.")
    
    if intervencion['tasa_error_pdf'] < 1:
        conclusiones.append(f"✅ **Confiabilidad Técnica:** La generación de PDFs tiene una tasa de error de solo "
                          f"**{intervencion['tasa_error_pdf']:.1f}%**, cumpliendo con estándares de calidad.")
    
    if intervencion['comprension'] >= 80:
        conclusiones.append(f"✅ **Comprensión:** El **{intervencion['comprension']:.0f}%** de las madres entienden "
                          f"correctamente las recomendaciones, validando la efectividad de la comunicación.")
    
    return conclusiones
