# pages/metricas_comprension.py
"""
Dashboard de métricas de producto
KPI Principal: % de comprensión del diagnóstico (objetivo ≥80%)
"""

import streamlit as st
import plotly.graph_objects as go
from utils.feedback import calcular_metrica_comprension
from utils.adherencia import calcular_adherencia_global


def pagina_metricas_comprension():
    """Dashboard de métricas clave del producto"""
    
    st.title("📊 Métricas de Producto - NutriWawa")
    st.markdown("**KPIs clave para medir el impacto del sistema**")
    
    st.markdown("---")
    
    # =====================================================
    # MÉTRICA 1: COMPRENSIÓN DEL DIAGNÓSTICO (HU-01)
    # =====================================================
    st.markdown("## 🧠 HU-01: Comprensión del Diagnóstico")
    st.caption("Objetivo: ≥80% de madres entienden claramente el diagnóstico")
    
    metricas_comprension = calcular_metrica_comprension()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        comprension_pct = metricas_comprension['comprension_pct']
        delta_objetivo = comprension_pct - 80
        
        st.metric(
            "📈 Comprensión Global",
            f"{comprension_pct:.1f}%",
            delta=f"{delta_objetivo:+.1f}pp",
            delta_color="normal" if comprension_pct >= 80 else "inverse"
        )
    
    with col2:
        st.metric("✅ Muy Claro", metricas_comprension['n_muy_claro'])
    
    with col3:
        st.metric("⚠️ Con Dudas", metricas_comprension['n_dudas'])
    
    with col4:
        st.metric("❌ No Entendieron", metricas_comprension['n_no_entendí'])
    
    # Gauge de progreso
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=comprension_pct,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "% Comprensión vs Objetivo", 'font': {'size': 20}},
        delta={'reference': 80, 'increasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1},
            'bar': {'color': "darkgreen" if comprension_pct >= 80 else "orange"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 60], 'color': '#ffebee'},
                {'range': [60, 80], 'color': '#fff9c4'},
                {'range': [80, 100], 'color': '#c8e6c9'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 80
            }
        }
    ))
    
    fig_gauge.update_layout(height=300)
    st.plotly_chart(fig_gauge, use_container_width=True)
    
    if metricas_comprension['objetivo_cumplido']:
        st.success("✅ **¡Objetivo cumplido!** El sistema es claro y comprensible.")
    else:
        gap = 80 - comprension_pct
        st.warning(f"⚠️ Faltan {gap:.1f}pp para alcanzar el objetivo. Revisar claridad de mensajes.")
    
    st.markdown("---")
    
    # =====================================================
    # MÉTRICA 2: ADHERENCIA A MENÚS (HU-02)
    # =====================================================
    st.markdown("## 🍽️ HU-02: Adherencia a Menús Personalizados")
    st.caption("Objetivo: +15pp vs baseline (57.3% ENDES 2023)")
    
    metricas_adherencia = calcular_adherencia_global()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        adherencia_pct = metricas_adherencia['adherencia_pct']
        mejora = metricas_adherencia['mejora_vs_baseline']
        
        st.metric(
            "📈 Adherencia Actual",
            f"{adherencia_pct:.1f}%",
            delta=f"{mejora:+.1f}pp vs baseline",
            delta_color="normal" if mejora >= 15 else "inverse"
        )
    
    with col2:
        st.metric("✅ Menús Preparados", metricas_adherencia['n_preparados'])
    
    with col3:
        st.metric("📊 Total Registros", metricas_adherencia['n_totales'])
    
    with col4:
        baseline = metricas_adherencia['baseline']
        st.metric("📉 Baseline ENDES", f"{baseline:.1f}%")
    
    # Gauge de mejora
    fig_mejora = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=mejora,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Mejora vs Baseline (objetivo +15pp)", 'font': {'size': 18}},
        delta={'reference': 15, 'increasing': {'color': "green"}},
        gauge={
            'axis': {'range': [-10, 30]},
            'bar': {'color': "darkgreen" if mejora >= 15 else "orange"},
            'steps': [
                {'range': [-10, 0], 'color': '#ffebee'},
                {'range': [0, 15], 'color': '#fff9c4'},
                {'range': [15, 30], 'color': '#c8e6c9'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 15
            }
        }
    ))
    
    fig_mejora.update_layout(height=300)
    st.plotly_chart(fig_mejora, use_container_width=True)
    
    if metricas_adherencia['objetivo_cumplido']:
        st.success(f"✅ **¡Objetivo cumplido!** Mejora de {mejora:.1f}pp vs baseline.")
    else:
        gap = 15 - mejora
        st.warning(f"⚠️ Faltan {gap:.1f}pp para alcanzar +15pp. Revisar accesibilidad y costo de menús.")
    
    # Adherencia por tipo de menú
    st.markdown("### 📋 Adherencia por Tipo de Comida")
    
    por_tipo = metricas_adherencia.get('por_tipo_menu', {})
    
    if por_tipo:
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            if 'desayuno' in por_tipo:
                st.metric(
                    "🍳 Desayuno",
                    f"{por_tipo['desayuno']['adherencia_pct']:.1f}%"
                )
        
        with col_b:
            if 'almuerzo' in por_tipo:
                st.metric(
                    "🍲 Almuerzo",
                    f"{por_tipo['almuerzo']['adherencia_pct']:.1f}%"
                )
        
        with col_c:
            if 'cena' in por_tipo:
                st.metric(
                    "🌙 Cena",
                    f"{por_tipo['cena']['adherencia_pct']:.1f}%"
                )
