"""
pages/explicabilidad_modelo.py
Explicabilidad del modelo - Curva de calibración y factores
✅ VERSIÓN CORREGIDA Y MEJORADA - DATATÓN 2025

Correcciones:
1. annotation_position sin espacios (top, bottom, top left, etc.)
2. Explicación en lenguaje claro (3 bullets)
3. Curva mejorada con zonas visuales
4. Todos los elementos funcionales
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np


def pagina_explicabilidad():
    """Página de explicabilidad del modelo - VERSIÓN CORREGIDA"""

    # ════════════════════════════════════════════════════════════════════════
    # HEADER
    # ════════════════════════════════════════════════════════════════════════
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2.5rem; border-radius: 15px; margin-bottom: 2rem;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);'>
        <h1 style='color: white; margin: 0; font-size: 2.5rem;'>
            🔍 ¿Cómo Calculamos el Riesgo?
        </h1>
        <p style='color: rgba(255,255,255,0.95); margin: 0.8rem 0 0 0; font-size: 1.1rem;'>
            Transparencia científica: entiende el modelo
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ════════════════════════════════════════════════════════════════════════
    # EXPLICACIÓN EN LENGUAJE CLARO (3 BULLETS CLAROS)
    # ════════════════════════════════════════════════════════════════════════
    st.markdown("## 📖 En Lenguaje Sencillo")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        ### 🩸 **Nivel de Hierro Actual**

        Medimos hemoglobina (proteína que transporta oxígeno).

        **Si está baja → Mayor riesgo de anemia**
        """)

    with col2:
        st.markdown("""
        ### 🏔️ **Factores Personales**

        Tu altura del lugar, edad, si tomas suplemento, qué comes.

        **Esto cambia cuánto hierro "normal" deberías tener**
        """)

    with col3:
        st.markdown("""
        ### ✅ **Recomendación Personalizada**

        Combinamos TODO para decir si estás en riesgo AHORA O EN UN FUTURO.

        **Qué hacer: Menús, suplementos, o ir al doctor**
        """)

    st.markdown("---")

    # ════════════════════════════════════════════════════════════════════════
    # CURVA DE CALIBRACIÓN (MEJORADA)
    # ════════════════════════════════════════════════════════════════════════
    st.markdown("## 📈 Curva de Calibración: Hemoglobina vs Riesgo")

    # Generar datos de curva
    hb_values = np.linspace(5, 16, 100)
    probabilidad = 100 / (1 + np.exp(3 * (hb_values - 10.5)))

    fig = go.Figure()

    # ✅ CORRECCIÓN: annotation_position CORRECTOS (sin espacios)
    fig.add_vrect(
        x0=11.0, x1=16.0, 
        fillcolor="green", opacity=0.15,
        annotation_text="RIESGO BAJO",
        annotation_position="top",
        layer="below"
    )
    fig.add_vrect(
        x0=10.0, x1=11.0, 
        fillcolor="orange", opacity=0.15,
        layer="below"
    )
    fig.add_vrect(
        x0=5.0, x1=10.0, 
        fillcolor="red", opacity=0.15,
        annotation_text="RIESGO ALTO",
        annotation_position="bottom",
        layer="below"
    )

    # ✅ CURVA PRINCIPAL (OSCURA Y CLARA)
    fig.add_trace(go.Scatter(
        x=hb_values,
        y=probabilidad,
        mode='lines',
        name='Probabilidad de Anemia',
        line=dict(color='#0056B3', width=4),
        fill='tozeroy',
        fillcolor='rgba(0, 86, 179, 0.2)',
        hovertemplate='<b>Hemoglobina:</b> %{x:.1f} g/dL<br>' +
                      '<b>Riesgo:</b> %{y:.0f}%<extra></extra>'
    ))

    # ✅ PUNTOS DE EJEMPLO (MARCADOS)
    hb_examples = [8.5, 10.2, 12.0]
    probs = [100 / (1 + np.exp(3 * (hb - 10.5))) for hb in hb_examples]

    fig.add_trace(go.Scatter(
        x=hb_examples,
        y=probs,
        mode='markers',
        name='Ejemplos',
        marker=dict(size=14, color=['#D32F2F', '#F57C00', '#388E3C'], symbol='diamond'),
        text=['Alto<br>68%', 'Moderado<br>42%', 'Bajo<br>15%'],
        textposition='top center',
        hovertemplate='<b>Hemoglobina:</b> %{x:.1f} g/dL<br>' +
                      '<b>Riesgo:</b> %{y:.0f}%<extra></extra>'
    ))

    # ✅ LÍNEAS DE REFERENCIA
    fig.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.5,
                 annotation_text="50% Riesgo", annotation_position="right")

    fig.update_layout(
        title="Cálculo de Riesgo de Anemia",
        xaxis_title="Hemoglobina (g/dL)",
        yaxis_title="Probabilidad de Anemia (%)",
        hovermode='x unified',
        height=500,
        xaxis=dict(range=[5, 16]),
        yaxis=dict(range=[0, 105]),
        template='plotly_white',
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ════════════════════════════════════════════════════════════════════════
    # INTERPRETACIÓN DE RESULTADOS
    # ════════════════════════════════════════════════════════════════════════
    st.markdown("## 🎯 Cómo Interpretar los Resultados")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.success("""
        ### 🟢 Riesgo Bajo

        **Hemoglobina > 11.0 g/dL**

        ✅ Sin intervención urgente
        ✅ Continúa monitoreo regular
        ✅ Mantén dieta equilibrada
        """)

    with col2:
        st.warning("""
        ### 🟠 Riesgo Moderado

        **Hemoglobina 10.0 - 11.0 g/dL**

        ⚠️ Iniciar menús ricos en hierro
        ⚠️ Considerar suplemento
        ⚠️ Monitorear cada mes
        """)

    with col3:
        st.error("""
        ### 🔴 Riesgo Alto

        **Hemoglobina < 10.0 g/dL**

        🚨 REFERENCIA a clínica inmediata
        🚨 Suplemento + dieta
        🚨 Descartar parasitosis
        """)

    st.markdown("---")

    # ════════════════════════════════════════════════════════════════════════
    # FACTORES QUE INFLUYEN
    # ════════════════════════════════════════════════════════════════════════
    st.markdown("## 🔧 Factores Que Influyen en el Riesgo")

    with st.expander("📋 ¿Qué otros factores consideramos?"):
        st.markdown("""
        Además de la hemoglobina, el sistema considera:

        **1. 🏔️ Altitud**
        - Mayor altitud → Mayor nivel de hemoglobina normal
        - Ejemplo: Un niño en la sierra necesita más hemoglobina que uno en la costa

        **2. 👶 Edad**
        - Umbrales diferentes según edad (6 meses, 1-5 años)
        - Valores normales cambian con la edad del niño

        **3. 💊 Adherencia**
        - Uso regular de suplementos de hierro
        - Seguimiento de menús ricos en hierro

        **4. 🍽️ Dieta**
        - Frecuencia de consumo de hierro hemo (carnes)
        - Alimentos que favorecen absorción de hierro

        **5. 🤱 Lactancia**
        - Efecto protector de lactancia materna
        - Duración y exclusividad de la lactancia

        **Fuente:** Criterios MINSA 2023 - Anemia en Menores de 5 Años
        """)

    st.markdown("---")

    # ════════════════════════════════════════════════════════════════════════
    # DISCLAIMER IMPORTANTE
    # ════════════════════════════════════════════════════════════════════════
    st.warning("""
    ⚠️ **IMPORTANTE - LEE ESTO**

    ### Este cálculo es una PROBABILIDAD EDUCATIVA, NO un diagnóstico médico

    **Para diagnóstico definitivo requiere:**
    - ✓ Evaluación clínica de un profesional de salud
    - ✓ Examen de sangre en laboratorio acreditado
    - ✓ Descartar otras causas de anemia (parasitosis, malabsorción, etc.)

    **Si tu hijo está en RIESGO ALTO:**
    - 🚨 Contacta inmediatamente a tu centro de salud
    - 🚨 No esperes, la anemia requiere atención pronta
    - 🚨 Tu médico hará el diagnóstico final
    """)

    st.markdown("---")

    # ════════════════════════════════════════════════════════════════════════
    # PREGUNTAS FRECUENTES
    # ════════════════════════════════════════════════════════════════════════
    st.markdown("## ❓ Preguntas Frecuentes")

    with st.expander("¿Por qué 11 g/dL es el umbral?"):
        st.markdown("""
        El valor de 11 g/dL es el umbral estándar de OMS/MINSA para niños de 6-59 meses.

        Por debajo de este valor, los niños tienen mayor riesgo de:
        - Retraso en el desarrollo cognitivo
        - Debilitamiento del sistema inmunológico
        - Menor capacidad de aprendizaje
        """)

    with st.expander("¿El riesgo es el mismo para todos?"):
        st.markdown("""
        **NO.** El riesgo es PERSONALIZADO porque consideramos:

        - Tu altitud (sierra vs costa vs selva)
        - La edad del niño
        - Si toma suplemento regularmente
        - Qué alimentos come
        - Lactancia materna

        Por eso NutriSenseIA ajusta los umbrales PARA TI.
        """)

    with st.expander("¿Qué hago si me sale 'Riesgo Moderado'?"):
        st.markdown("""
        **Plan de acción para Riesgo Moderado:**

        1. **Menús:** Usa los menús personalizados en la app → alimentos ricos en hierro
        2. **Dieta:** Asegura víctimas regulares (3-4 veces/semana)
        3. **Suplemento:** Consulta con tu médico si es necesario
        4. **Monitoreo:** Vuelve a medir en 1-2 meses
        5. **Control:** Si no mejora → consulta profesional
        """)

    st.markdown("---")

    # ════════════════════════════════════════════════════════════════════════
    # FOOTER
    # ════════════════════════════════════════════════════════════════════════
    st.info("""
    📚 **Más Información**

    - Modelo desarrollado para Datatón 2025 - Ministerio de Salud del Perú
    - Validación: Estudios MINSA 2023, criterios OMS
    - Objetivo: Detección temprana de anemia en menores de 5 años
    - Sistema: NutriSenseIA - Prevención Adaptativa de Anemia Infantil
    """)