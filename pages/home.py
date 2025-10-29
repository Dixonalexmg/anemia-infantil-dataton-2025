"""
pages/home.py
Página de inicio - EXTRAÍDO de tu código original
"""

import streamlit as st
import plotly.graph_objects as go

# ============================================================================
# FUNCIONES AUXILIARES (TU CÓDIGO ORIGINAL)
# ============================================================================

def mostrar_header():
    """Muestra el header principal de la aplicación"""
    st.markdown("""
    <div class="main-header">
        <h1>🩺 Sistema de Combate a la Anemia Infantil</h1>
        <p style='font-size: 1.2rem; margin-top: 0.5rem;'>
            Ministerio de Salud - Datatón Exprésate Perú con Datos 2025
        </p>
        <p style='font-size: 0.9rem; opacity: 0.9;'>
            Diagnóstico inteligente • Recomendaciones personalizadas • Priorización territorial
        </p>
    </div>
    """, unsafe_allow_html=True)

def crear_gauge_hemoglobina(hb_ajustada, umbral=11.0):
    """Crea un gauge visual para hemoglobina"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=hb_ajustada,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Hemoglobina Ajustada (g/dL)", 'font': {'size': 16}},
        gauge={
            'axis': {'range': [None, 16]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 7], 'color': '#ff4b4b'},
                {'range': [7, 10], 'color': '#ffa500'},
                {'range': [10, 11], 'color': '#ffeb3b'},
                {'range': [11, 16], 'color': '#28a745'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 3},
                'thickness': 0.75,
                'value': umbral
            }
        }
    ))

    fig.update_layout(
        height=250,
        margin=dict(l=10, r=10, t=40, b=10)
    )

    return fig

# ============================================================================
# PÁGINA PRINCIPAL (TU CÓDIGO ORIGINAL)
# ============================================================================

def pagina_inicio():
    """Página de inicio con información general"""
    mostrar_header()

    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="📊 Prevalencia Nacional",
            value="11.9%",
            delta="+48.8% vs enero",
            delta_color="inverse"
        )

    with col2:
        st.metric(
            label="👶 Niños Evaluados",
            value="896K",
            delta="Enero-Junio 2025"
        )

    with col3:
        st.metric(
            label="🎯 Meta Nacional",
            value="< 8%",
            delta="Brecha: 3.9 pp"
        )

    with col4:
        st.metric(
            label="🚨 Departamentos Críticos",
            value="5",
            delta="Tendencia creciente"
        )

    st.markdown("---")

    # Información del sistema
    col_info1, col_info2 = st.columns(2)

    with col_info1:
        st.subheader("🎯 Objetivos del Sistema")
        st.markdown("""
        Este sistema integral permite:

        1. **🔍 Diagnóstico Temprano**
           - Predicción de anemia con IA
           - Ajuste por altitud (OMS 2024)
           - Clasificación por severidad

        2. **🍽️ Recomendaciones Personalizadas**
           - Menús adaptados por edad
           - Optimización de presupuesto
           - Alimentos ricos en hierro hemo

        3. **📊 Priorización Territorial**
           - Identificación de hot spots
           - Análisis de equidad
           - Focalización de recursos

        4. **📈 Monitoreo de Tendencias**
           - Proyecciones a 3-6 meses
           - Alertas automáticas
           - Escenarios de intervención
        """)

    with col_info2:
        st.subheader("📚 Guía de Uso Rápida")
        st.markdown("""
        ### Para Médicos/Enfermeras:
        1. Ve a **🔍 Diagnóstico Individual**
        2. Ingresa datos del niño
        3. Obtén diagnóstico y recomendaciones

        ### Para Nutricionistas:
        1. Ve a **🍽️ Menús Personalizados**
        2. Configura edad y presupuesto
        3. Genera menú optimizado

        ### Para Gestores/Directores:
        1. Ve a **📊 Dashboard Nacional**
        2. Revisa brechas de equidad
        3. Prioriza intervenciones

        ### Para Planificadores:
        1. Ve a **📈 Proyecciones**
        2. Analiza tendencias
        3. Simula escenarios
        """)

    st.markdown("---")

    # Alertas importantes
    st.subheader("🚨 Alertas Actuales")

    col_alert1, col_alert2, col_alert3 = st.columns(3)

    with col_alert1:
        st.markdown("""
        <div class="alert-critical">
            <h4>⚠️ CRÍTICO</h4>
            <p>Incremento de <strong>48.8%</strong> en prevalencia (enero-junio 2025)</p>
        </div>
        """, unsafe_allow_html=True)

    with col_alert2:
        st.markdown("""
        <div class="alert-warning">
            <h4>⚡ ADVERTENCIA</h4>
            <p>5 departamentos con tendencia creciente <strong>>1.2 pp/mes</strong></p>
        </div>
        """, unsafe_allow_html=True)

    with col_alert3:
        st.markdown("""
        <div class="alert-success">
            <h4>✅ OPORTUNIDAD</h4>
            <p>TACNA muestra declive sostenido: <strong>-0.86 pp/mes</strong></p>
        </div>
        """, unsafe_allow_html=True)