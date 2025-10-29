"""
pages/simulador.py
Página del Simulador - HU-03
¿Qué pasaría si...? con proyección de cambio esperado
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Imports de servicios
from services.simulator import SimuladorIntervencion

# Imports de utilidades
from utils.constants import UMBRAL_ANEMIA, COLORES

# Inicializar simulador
simulador = SimuladorIntervencion()

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def crear_grafico_comparacion(escenarios):
    """Crea gráfico de barras comparando escenarios"""

    data = {
        'Escenario': [
            'Sin intervención',
            'Solo suplementación',
            'Solo alimentación',
            'Intervención completa',
            'Adherencia media'
        ],
        'Hb Final': [
            escenarios['sin_intervencion']['hb_proyectada'],
            escenarios['solo_suplementacion']['hb_proyectada'],
            escenarios['solo_alimentacion']['hb_proyectada'],
            escenarios['intervencion_completa']['hb_proyectada'],
            escenarios['intervencion_adherencia_media']['hb_proyectada']
        ],
        'Incremento': [
            escenarios['sin_intervencion']['incremento_total'],
            escenarios['solo_suplementacion']['incremento_total'],
            escenarios['solo_alimentacion']['incremento_total'],
            escenarios['intervencion_completa']['incremento_total'],
            escenarios['intervencion_adherencia_media']['incremento_total']
        ]
    }

    df = pd.DataFrame(data)

    # Clasificar por nivel
    df['Color'] = df['Incremento'].apply(
        lambda x: 'Excelente (≥0.5)' if x >= 0.5 
        else 'Bueno (≥0.3)' if x >= 0.3
        else 'Moderado (≥0.15)' if x >= 0.15
        else 'Bajo (<0.15)'
    )

    fig = px.bar(
        df,
        x='Incremento',
        y='Escenario',
        orientation='h',
        color='Color',
        color_discrete_map={
            'Excelente (≥0.5)': COLORES['exito'],
            'Bueno (≥0.3)': COLORES['info'],
            'Moderado (≥0.15)': COLORES['advertencia'],
            'Bajo (<0.15)': COLORES['gris']
        },
        title='Comparación de Incremento de Hemoglobina por Escenario',
        labels={'Incremento': 'Incremento esperado (g/dL)', 'Escenario': ''},
        height=400,
        text='Incremento'
    )

    fig.update_traces(texttemplate='%{text:.2f} g/dL', textposition='outside')
    fig.update_layout(showlegend=True, template='plotly_white')

    return fig

def crear_grafico_timeline(timeline_df, hb_actual):
    """Crea gráfico de línea con evolución proyectada"""

    fig = go.Figure()

    # Línea de evolución
    fig.add_trace(go.Scatter(
        x=timeline_df['semana'],
        y=timeline_df['hemoglobina'],
        mode='lines+markers',
        name='Hemoglobina proyectada',
        line=dict(color=COLORES['primario'], width=3),
        marker=dict(size=10),
        text=timeline_df['fecha'],
        hovertemplate='Semana %{x}<br>Hb: %{y:.2f} g/dL<br>Fecha: %{text}<extra></extra>'
    ))

    # Línea de umbral de anemia
    umbral = UMBRAL_ANEMIA['6-59_meses']
    fig.add_hline(
        y=umbral,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Umbral anemia ({umbral} g/dL)",
        annotation_position="right"
    )

    # Línea de Hb actual
    fig.add_hline(
        y=hb_actual,
        line_dash="dot",
        line_color="gray",
        annotation_text=f"Hb actual ({hb_actual:.1f} g/dL)",
        annotation_position="left"
    )

    fig.update_layout(
        title='Evolución Proyectada de Hemoglobina (Semanas)',
        xaxis_title='Semanas',
        yaxis_title='Hemoglobina (g/dL)',
        hovermode='x unified',
        height=450,
        template='plotly_white',
        showlegend=True
    )

    return fig

# ============================================================================
# PÁGINA PRINCIPAL
# ============================================================================

def pagina_simulador():
    """Página del simulador ¿Qué pasaría si...? - HU-03"""

    # Header
    st.markdown("""
    <div class="custom-header">
        <h1>🔮 Simulador: ¿Qué pasaría si...?</h1>
        <p>HU-03: Proyección de cambio esperado en hemoglobina según intervenciones</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    Simula el **impacto de diferentes intervenciones** en los niveles de hemoglobina.
    Proyecta el cambio esperado a **4-6 semanas** basado en evidencia clínica.
    """)

    st.markdown("---")

    # Formulario de configuración
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📊 Datos Actuales del Niño")

        hb_actual = st.number_input(
            "Hemoglobina actual (g/dL)",
            min_value=5.0,
            max_value=18.0,
            value=10.2,
            step=0.1,
            help="Nivel actual de hemoglobina"
        )

        edad_meses = st.number_input(
            "Edad (meses)",
            min_value=6,
            max_value=59,
            value=18,
            help="Edad del niño"
        )

        # Mostrar estado actual
        umbral = UMBRAL_ANEMIA['6-59_meses']
        diferencia = hb_actual - umbral

        if diferencia < 0:
            st.error(f"⚠️ **Con anemia** ({abs(diferencia):.1f} g/dL por debajo del umbral)")
        else:
            st.success(f"✅ **Sin anemia** ({diferencia:.1f} g/dL por encima del umbral)")

    with col2:
        st.subheader("⚙️ Configuración del Escenario")

        suplementacion = st.checkbox(
            "Suplementación con hierro",
            value=True,
            help="¿El niño recibirá suplementación diaria?"
        )

        alimentacion_mejorada = st.checkbox(
            "Alimentación optimizada",
            value=True,
            help="¿Seguirá menú rico en hierro?"
        )

        adherencia = st.select_slider(
            "Nivel de adherencia",
            options=['baja', 'media', 'alta'],
            value='alta',
            help="Nivel esperado de cumplimiento"
        )

        semanas = st.slider(
            "Tiempo de proyección (semanas)",
            min_value=4,
            max_value=8,
            value=6,
            help="Periodo de simulación"
        )

    # Botón de simulación
    if st.button("🚀 Simular Escenario", use_container_width=True, type="primary"):

        # Realizar simulación
        with st.spinner("🔄 Calculando proyección..."):
            resultado = simulador.simular_escenario(
                hb_actual=hb_actual,
                edad_meses=edad_meses,
                suplementacion=suplementacion,
                alimentacion_mejorada=alimentacion_mejorada,
                adherencia=adherencia,
                semanas=semanas
            )

            # Comparar con otros escenarios
            escenarios = simulador.comparar_escenarios(hb_actual, edad_meses)

            # Generar timeline
            timeline = simulador.generar_timeline(
                hb_actual, edad_meses,
                suplementacion, alimentacion_mejorada, adherencia
            )

        st.markdown("---")

        # RESULTADOS DE LA SIMULACIÓN
        st.subheader("📈 Resultados de la Proyección")

        # Tarjeta de resultado principal
        if resultado['incremento_total'] > 0:
            color_fondo = COLORES['exito'] if resultado['incremento_total'] >= 0.3 else COLORES['advertencia']
        else:
            color_fondo = COLORES['gris']

        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {color_fondo}22 0%, {color_fondo}44 100%);
            border-left: 5px solid {color_fondo};
            padding: 2rem;
            border-radius: 10px;
            margin: 1rem 0;
        ">
            <h2 style="margin: 0; color: {color_fondo};">
                {resultado['emoji']} Proyección: {resultado['nivel_mejora']}
            </h2>
            <p style="font-size: 1.5rem; margin: 1rem 0;">
                <strong>+{resultado['incremento_total']:.2f} g/dL</strong> en {semanas} semanas
            </p>
            <p style="margin: 0;">
                De <strong>{hb_actual:.1f} g/dL</strong> → <strong>{resultado['hb_proyectada']:.1f} g/dL</strong>
                (proyección al {resultado['fecha_proyeccion']})
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Métricas detalladas
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)

        with col_m1:
            st.metric(
                "Hemoglobina Final",
                f"{resultado['hb_proyectada']:.1f} g/dL",
                delta=f"+{resultado['incremento_total']:.2f} g/dL"
            )

        with col_m2:
            incremento_suplementacion = resultado['incremento_suplementacion']
            st.metric(
                "Por Suplementación",
                f"+{incremento_suplementacion:.2f} g/dL",
                delta=f"{(incremento_suplementacion/resultado['incremento_total']*100) if resultado['incremento_total'] > 0 else 0:.0f}% del total"
            )

        with col_m3:
            incremento_alimentacion = resultado['incremento_alimentacion']
            st.metric(
                "Por Alimentación",
                f"+{incremento_alimentacion:.2f} g/dL",
                delta=f"{(incremento_alimentacion/resultado['incremento_total']*100) if resultado['incremento_total'] > 0 else 0:.0f}% del total"
            )

        with col_m4:
            diferencia_final = resultado['hb_proyectada'] - umbral
            st.metric(
                "Vs. Umbral",
                f"{abs(diferencia_final):.1f} g/dL",
                delta="Por encima" if diferencia_final >= 0 else "Por debajo"
            )

        # Gráfico de evolución temporal
        st.subheader("📊 Evolución Proyectada Semana a Semana")

        fig_timeline = crear_grafico_timeline(timeline, hb_actual)
        st.plotly_chart(fig_timeline, use_container_width=True)

        # Interpretación
        st.info(f"""
        **💡 Interpretación:**

        Con este escenario de intervención ({adherencia} adherencia), 
        se espera que el niño **aumente su hemoglobina en {resultado['incremento_total']:.2f} g/dL** 
        en {semanas} semanas, alcanzando un valor de **{resultado['hb_proyectada']:.1f} g/dL**.

        {'✅ Esto lo ubicaría **por encima del umbral de anemia** ('+f'{umbral} g/dL).' if diferencia_final >= 0 
        else '⚠️ Aún estaría **por debajo del umbral de anemia**. Se recomienda reforzar la intervención.'}
        """)

        # Comparación de escenarios
        st.markdown("---")
        st.subheader("🔀 Comparación con Otros Escenarios")

        st.markdown("""
        Compara el escenario simulado con otras alternativas para tomar la mejor decisión.
        """)

        fig_comparacion = crear_grafico_comparacion(escenarios)
        st.plotly_chart(fig_comparacion, use_container_width=True)

        # Tabla de comparación
        with st.expander("📋 Ver tabla comparativa detallada"):
            df_comparacion = pd.DataFrame({
                'Escenario': [
                    'Sin intervención',
                    'Solo suplementación',
                    'Solo alimentación',
                    'Intervención completa',
                    'Adherencia media'
                ],
                'Hb Inicial': [hb_actual] * 5,
                'Hb Final (g/dL)': [
                    escenarios['sin_intervencion']['hb_proyectada'],
                    escenarios['solo_suplementacion']['hb_proyectada'],
                    escenarios['solo_alimentacion']['hb_proyectada'],
                    escenarios['intervencion_completa']['hb_proyectada'],
                    escenarios['intervencion_adherencia_media']['hb_proyectada']
                ],
                'Incremento (g/dL)': [
                    escenarios['sin_intervencion']['incremento_total'],
                    escenarios['solo_suplementacion']['incremento_total'],
                    escenarios['solo_alimentacion']['incremento_total'],
                    escenarios['intervencion_completa']['incremento_total'],
                    escenarios['intervencion_adherencia_media']['incremento_total']
                ],
                'Evaluación': [
                    escenarios['sin_intervencion']['nivel_mejora'],
                    escenarios['solo_suplementacion']['nivel_mejora'],
                    escenarios['solo_alimentacion']['nivel_mejora'],
                    escenarios['intervencion_completa']['nivel_mejora'],
                    escenarios['intervencion_adherencia_media']['nivel_mejora']
                ]
            })

            st.dataframe(
                df_comparacion,
                use_container_width=True,
                hide_index=True
            )

        # Recomendaciones
        st.markdown("---")
        st.subheader("💡 Recomendaciones Basadas en la Simulación")

        col_rec1, col_rec2 = st.columns(2)

        with col_rec1:
            st.markdown("""
            **Para maximizar resultados:**

            - ✅ Combinar suplementación + alimentación optimizada
            - ✅ Mantener adherencia **> 80%** (alta)
            - ✅ Control en 4 semanas para verificar evolución
            - ✅ Ajustar intervención si no hay mejora esperada
            """)

        with col_rec2:
            st.markdown(f"""
            **Meta realista en {semanas} semanas:**

            - 🎯 Incremento esperado: **+{resultado['incremento_total']:.2f} g/dL**
            - 🎯 Hemoglobina objetivo: **{resultado['hb_proyectada']:.1f} g/dL**
            - 🎯 Fecha de evaluación: **{resultado['fecha_proyeccion']}**
            - 🎯 Adherencia requerida: **{adherencia.capitalize()}**
            """)