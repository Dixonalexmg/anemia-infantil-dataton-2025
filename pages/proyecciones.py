# pages/proyecciones.py
"""
HU-03: Simulador "¿Qué pasaría si...?" con Delta Esperado
Compara situación actual vs. recomendada con cambio esperado en Hb/IMC
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd

def pagina_proyecciones():
    """Simulador de impacto nutricional con proyecciones realistas"""
    
    # HEADER
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem;'>
        <div style='display: flex; align-items: center; gap: 1rem;'>
            <div style='font-size: 3rem;'>🔮</div>
            <div>
                <h1 style='color: white; margin: 0;'>¿Qué pasaría si...?</h1>
                <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;'>
                    Simula el impacto de cambios en la alimentación de tu hijo/a
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ========== DATOS DEL NIÑO/A ==========
    st.markdown("### 📊 Situación Actual")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        edad_meses = st.number_input("Edad (meses)", 6, 59, 18, 1)
    with col2:
        hb_actual = st.number_input("Hemoglobina actual (g/dL)", 6.0, 18.0, 11.2, 0.1)
    with col3:
        peso_actual = st.number_input("Peso actual (kg)", 3.0, 30.0, 10.5, 0.1)
    
    # Clasificar estado actual
    clasificacion_hb = clasificar_anemia(hb_actual, edad_meses)
    estado_nutricional = clasificar_estado_nutricional(peso_actual, edad_meses)
    
    col_hb, col_peso = st.columns(2)
    with col_hb:
        color_hb = {"Normal": "green", "Anemia leve": "orange", "Anemia moderada": "red", 
                    "Anemia severa": "darkred"}[clasificacion_hb]
        st.markdown(f"**Estado:** <span style='color:{color_hb};font-weight:bold'>{clasificacion_hb}</span>", 
                   unsafe_allow_html=True)
    with col_peso:
        st.markdown(f"**Estado Nutricional:** {estado_nutricional}")
    
    st.markdown("---")
    
    # ========== CONFIGURACIÓN DEL ESCENARIO ==========
    st.markdown("### 🎯 Planifica tus cambios")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("#### 📅 Situación Actual")
        freq_carne_actual = st.slider("Raciones de carne/semana (actual)", 0, 7, 2, 1, 
                                      key="actual_carne")
        freq_menestra_actual = st.slider("Raciones de menestras/semana (actual)", 0, 7, 3, 1,
                                         key="actual_menestra")
        suplemento_actual = st.checkbox("¿Toma suplemento de hierro?", value=False, 
                                       key="actual_supl")
        freq_citrico_actual = st.slider("Veces que come con cítrico/semana (actual)", 0, 21, 5, 1,
                                       key="actual_citrico")
    
    with col_b:
        st.markdown("#### 🚀 Situación Recomendada")
        freq_carne_objetivo = st.slider("Raciones de carne/semana (objetivo)", 0, 7, 4, 1,
                                        key="objetivo_carne")
        freq_menestra_objetivo = st.slider("Raciones de menestras/semana (objetivo)", 0, 7, 5, 1,
                                           key="objetivo_menestra")
        suplemento_objetivo = st.checkbox("¿Tomarás suplemento de hierro?", value=True,
                                         key="objetivo_supl")
        freq_citrico_objetivo = st.slider("Veces que comerá con cítrico/semana (objetivo)", 0, 21, 14, 1,
                                         key="objetivo_citrico")
    
    # Horizonte temporal
    st.markdown("---")
    semanas_proyeccion = st.slider("**⏱️ Horizonte de proyección (semanas)**", 2, 12, 6, 1,
                                   help="Tiempo para evaluar el impacto esperado")
    
    # ========== CALCULAR IMPACTO ==========
    if st.button("🔮 Calcular impacto esperado", type="primary", use_container_width=True):
        with st.spinner("Calculando proyecciones..."):
            
            # Calcular deltas
            resultado = calcular_impacto_esperado(
                hb_actual, peso_actual, edad_meses,
                freq_carne_actual, freq_carne_objetivo,
                freq_menestra_actual, freq_menestra_objetivo,
                suplemento_actual, suplemento_objetivo,
                freq_citrico_actual, freq_citrico_objetivo,
                semanas_proyeccion
            )
            
            # ========== MOSTRAR RESULTADOS ==========
            st.markdown("---")
            st.markdown("## 📈 Resultados de la Simulación")
            
            # COMPARATIVA PRINCIPAL
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "🩸 Hemoglobina Proyectada",
                    f"{resultado['hb_proyectada']:.1f} g/dL",
                    delta=f"+{resultado['delta_hb']:.2f} g/dL",
                    delta_color="normal"
                )
            
            with col2:
                st.metric(
                    "⚖️ Peso Proyectado",
                    f"{resultado['peso_proyectado']:.1f} kg",
                    delta=f"+{resultado['delta_peso']:.2f} kg",
                    delta_color="normal"
                )
            
            with col3:
                st.metric(
                    "📅 En",
                    f"{semanas_proyeccion} semanas",
                    delta=f"{resultado['confianza']}% confianza"
                )
            
            # MENSAJE INTERPRETATIVO
            if resultado['delta_hb'] >= 0.3:
                st.success(f"✅ **¡Excelente!** Si sigues estas recomendaciones, tu hijo/a podría mejorar su hemoglobina en **+{resultado['delta_hb']:.2f} g/dL** en {semanas_proyeccion} semanas. Esto lo llevaría a **{resultado['clasificacion_futura']}**.")
            elif resultado['delta_hb'] >= 0.1:
                st.info(f"💡 **Mejora moderada**: Se espera un aumento de **+{resultado['delta_hb']:.2f} g/dL**. Considera aumentar la frecuencia de alimentos ricos en hierro.")
            else:
                st.warning(f"⚠️ **Cambio mínimo**: El impacto esperado es de solo **+{resultado['delta_hb']:.2f} g/dL**. Se recomienda incrementar significativamente el consumo de proteína animal y suplementos.")
            
            # GRÁFICO DE PROYECCIÓN
            st.markdown("---")
            st.markdown("### 📊 Evolución Esperada de Hemoglobina")
            
            fig = crear_grafico_proyeccion(hb_actual, resultado['hb_proyectada'], 
                                          semanas_proyeccion, edad_meses)
            st.plotly_chart(fig, use_container_width=True)
            
            # DESGLOSE DE CONTRIBUCIONES
            st.markdown("---")
            st.markdown("### 🧮 ¿De dónde viene la mejora?")
            
            contribuciones = [
                {'factor': 'Aumento de carne/pescado', 'delta': resultado['contribucion_carne'], 
                 'emoji': '🥩'},
                {'factor': 'Aumento de menestras con cítrico', 'delta': resultado['contribucion_menestra'],
                 'emoji': '🫘'},
                {'factor': 'Suplemento de hierro', 'delta': resultado['contribucion_suplemento'],
                 'emoji': '💊'},
                {'factor': 'Mejora en absorción (cítricos)', 'delta': resultado['contribucion_citrico'],
                 'emoji': '🍋'}
            ]
            
            for cont in contribuciones:
                if cont['delta'] > 0:
                    porcentaje = (cont['delta'] / resultado['delta_hb'] * 100) if resultado['delta_hb'] > 0 else 0
                    st.markdown(
                        f"{cont['emoji']} **{cont['factor']}**: +{cont['delta']:.2f} g/dL "
                        f"({porcentaje:.0f}% del total)"
                    )
            
            # RECOMENDACIONES PERSONALIZADAS
            st.markdown("---")
            st.markdown("### 💡 Recomendaciones para Maximizar el Impacto")
            
            recomendaciones = generar_recomendaciones(
                resultado, freq_carne_objetivo, freq_menestra_objetivo,
                suplemento_objetivo, freq_citrico_objetivo
            )
            
            for i, rec in enumerate(recomendaciones, 1):
                st.markdown(f"{i}. {rec}")


# ========== FUNCIONES AUXILIARES ==========

def clasificar_anemia(hb, edad_meses):
    """Clasifica anemia según OMS 2024"""
    if edad_meses < 24:
        if hb >= 11.0:
            return "Normal"
        elif hb >= 10.0:
            return "Anemia leve"
        elif hb >= 7.0:
            return "Anemia moderada"
        else:
            return "Anemia severa"
    else:
        if hb >= 11.5:
            return "Normal"
        elif hb >= 10.0:
            return "Anemia leve"
        elif hb >= 7.0:
            return "Anemia moderada"
        else:
            return "Anemia severa"


def clasificar_estado_nutricional(peso, edad_meses):
    """Clasificación simple de estado nutricional"""
    # Promedios OMS simplificados
    peso_esperado = 7 + (edad_meses * 0.25)
    
    if peso >= peso_esperado * 0.9:
        return "Adecuado"
    elif peso >= peso_esperado * 0.8:
        return "Riesgo de desnutrición"
    else:
        return "Desnutrición"


def calcular_impacto_esperado(hb_actual, peso_actual, edad_meses,
                               freq_carne_actual, freq_carne_objetivo,
                               freq_menestra_actual, freq_menestra_objetivo,
                               suplemento_actual, suplemento_objetivo,
                               freq_citrico_actual, freq_citrico_objetivo,
                               semanas):
    """
    Calcula el impacto esperado basado en evidencia científica:
    - Carne/pescado: +0.12 g/dL Hb por ración adicional/semana
    - Menestra + cítrico: +0.08 g/dL Hb por ración adicional/semana
    - Suplemento hierro: +0.4 g/dL en 6 semanas (OMS)
    - Cítrico: +30% absorción de hierro no hemo
    """
    
    # Deltas de frecuencia
    delta_carne = max(0, freq_carne_objetivo - freq_carne_actual)
    delta_menestra = max(0, freq_menestra_objetivo - freq_menestra_actual)
    delta_citrico = max(0, freq_citrico_objetivo - freq_citrico_actual)
    
    # Contribuciones (ajustadas por tiempo)
    factor_tiempo = min(semanas / 6, 1.0)  # Máximo efecto a 6 semanas
    
    # Hierro hemo (carne/pescado)
    contrib_carne = delta_carne * 0.12 * factor_tiempo
    
    # Hierro no hemo (menestras) con efecto cítrico
    factor_citrico = 1 + (0.3 * (freq_citrico_objetivo / 21))  # Hasta +30% si come con cítrico siempre
    contrib_menestra = delta_menestra * 0.08 * factor_citrico * factor_tiempo
    
    # Suplemento
    contrib_suplemento = 0
    if suplemento_objetivo and not suplemento_actual:
        contrib_suplemento = 0.4 * factor_tiempo
    
    # Mejora en absorción por cítricos
    contrib_citrico_extra = (delta_citrico / 21) * 0.15 * factor_tiempo
    
    # Delta total
    delta_hb_total = contrib_carne + contrib_menestra + contrib_suplemento + contrib_citrico_extra
    hb_proyectada = hb_actual + delta_hb_total
    
    # Proyección de peso (crecimiento normal + mejora nutricional)
    crecimiento_basal = (semanas / 4) * 0.3  # ~300g/mes
    mejora_nutricional = delta_hb_total * 0.5  # Relación empírica
    delta_peso = crecimiento_basal + mejora_nutricional
    peso_proyectado = peso_actual + delta_peso
    
    # Confianza (basada en adherencia esperada)
    confianza = min(95, 65 + (delta_carne * 5) + (delta_menestra * 3) + (suplemento_objetivo * 10))
    
    return {
        'hb_proyectada': hb_proyectada,
        'delta_hb': delta_hb_total,
        'peso_proyectado': peso_proyectado,
        'delta_peso': delta_peso,
        'confianza': int(confianza),
        'clasificacion_futura': clasificar_anemia(hb_proyectada, edad_meses),
        'contribucion_carne': contrib_carne,
        'contribucion_menestra': contrib_menestra,
        'contribucion_suplemento': contrib_suplemento,
        'contribucion_citrico': contrib_citrico_extra
    }


def crear_grafico_proyeccion(hb_inicial, hb_final, semanas, edad_meses):
    """Crea gráfico de proyección temporal"""
    
    # Generar curva de evolución
    semanas_array = list(range(0, semanas + 1))
    hb_proyectada = [hb_inicial + (hb_final - hb_inicial) * (s / semanas) ** 0.7 
                     for s in semanas_array]
    
    # Umbrales de anemia
    umbral_normal = 11.0 if edad_meses < 24 else 11.5
    
    fig = go.Figure()
    
    # Línea de proyección
    fig.add_trace(go.Scatter(
        x=semanas_array,
        y=hb_proyectada,
        mode='lines+markers',
        name='Hb proyectada',
        line=dict(color='#667eea', width=3),
        marker=dict(size=8)
    ))
    
    # Línea de umbral normal
    fig.add_hline(y=umbral_normal, line_dash="dash", line_color="green",
                  annotation_text="Nivel normal (sin anemia)")
    
    # Zona de anemia
    fig.add_hrect(y0=0, y1=umbral_normal, fillcolor="red", opacity=0.1,
                  annotation_text="Zona de anemia", annotation_position="top left")
    
    fig.update_layout(
        title="Evolución Esperada de Hemoglobina",
        xaxis_title="Semanas",
        yaxis_title="Hemoglobina (g/dL)",
        hovermode='x unified',
        height=400
    )
    
    return fig


def generar_recomendaciones(resultado, freq_carne, freq_menestra, suplemento, freq_citrico):
    """Genera recomendaciones personalizadas"""
    recs = []
    
    if resultado['contribucion_carne'] > resultado['contribucion_menestra']:
        recs.append("🥩 **Prioriza las carnes rojas y pescado** - son tu mayor fuente de mejora")
    
    if freq_citrico < 14:
        recs.append("🍋 **Aumenta el uso de limón/naranja** en cada comida - mejora absorción en 3-4x")
    
    if not suplemento:
        recs.append("💊 **Considera iniciar suplementación** - podría aportar +0.4 g/dL adicional")
    
    if freq_menestra >= 4:
        recs.append("🫘 **Excelente consumo de menestras** - mantén esta frecuencia")
    
    if resultado['delta_hb'] < 0.3:
        recs.append("⚠️ **Incrementa la frecuencia de alimentos ricos en hierro** para mayor impacto")
    
    return recs
