"""
pages/home.py - VERSIÓN FUNCIONAL CON 4 TARJETAS
Home con tarjetas que redirigen correctamente (2 filas x 2 columnas)
"""


import streamlit as st
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def pagina_inicio():
    """Home con 4 tarjetas de acción funcionales"""


    username = st.session_state.get('username', 'Usuario')
    hora_actual = datetime.now().hour


    if 5 <= hora_actual < 12:
        saludo = "Buenos días"
        emoji_hora = "☀️"
    elif 12 <= hora_actual < 19:
        saludo = "Buenas tardes"
        emoji_hora = "🌤️"
    else:
        saludo = "Buenas noches"
        emoji_hora = "🌙"


    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2.5rem; border-radius: 15px; margin-bottom: 2rem;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);'>
        <h1 style='color: white; margin: 0; font-size: 2.2rem;'>
            {saludo}, {username} {emoji_hora}
        </h1>
        <p style='color: rgba(255,255,255,0.95); margin: 0.8rem 0 0 0; font-size: 1.2rem;'>
            Te saluda NutriSenseIA, tu asistente inteligente contra la anemia infantil
        </p>
    </div>
    """, unsafe_allow_html=True)


    st.markdown("---")
    st.markdown("### 🎯 Tu Plan de Acción")


    # ════════════════════════════════════════════════════════════════════════════
    # FILA 1: DIAGNÓSTICO + MENÚS
    # ════════════════════════════════════════════════════════════════════════════

    col1, col2 = st.columns(2, gap="large")


    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TARJETA 1: DIAGNÓSTICO
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    with col1:
        st.markdown("""
        <div style='background: white; padding: 2rem; border-radius: 15px; 
                    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3); 
                    border-top: 5px solid #667eea;
                    text-align: center;
                    height: 350px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;'>
            <div style='font-size: 3.5rem; margin-bottom: 1rem;'>🩺</div>
            <h3 style='color: #667eea; margin-bottom: 1rem; font-size: 1.4rem;'>
                Perfil y Riesgo
            </h3>
            <p style='color: #666; line-height: 1.6; font-size: 0.95rem; margin-bottom: 1.5rem;'>
                Evalúa el riesgo de anemia en menos de 2 minutos y obtén recomendaciones personalizadas.
            </p>
        </div>
        """, unsafe_allow_html=True)


        if st.button("📊 Empezar Evaluación", use_container_width=True, key="btn_home_diag"):
            logger.info("✅ Navegando a: Diagnóstico")
            st.session_state.pagina_actual = "diagnostico"
            st.rerun()


    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TARJETA 2: MENÚS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    with col2:
        st.markdown("""
        <div style='background: white; padding: 2rem; border-radius: 15px; 
                    box-shadow: 0 10px 30px rgba(40, 167, 69, 0.3); 
                    border-top: 5px solid #28a745;
                    text-align: center;
                    height: 350px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;'>
            <div style='font-size: 3.5rem; margin-bottom: 1rem;'>🍽️</div>
            <h3 style='color: #28a745; margin-bottom: 1rem; font-size: 1.4rem;'>
                Mis Menús
            </h3>
            <p style='color: #666; line-height: 1.6; font-size: 0.95rem; margin-bottom: 1.5rem;'>
                Descubre platos locales ricos en hierro, adaptados a tu presupuesto y región.
            </p>
        </div>
        """, unsafe_allow_html=True)


        if st.button("🍴 Ver Mis Menús", use_container_width=True, key="btn_home_menu"):
            logger.info("✅ Navegando a: Menús")
            st.session_state.pagina_actual = "menus"
            st.rerun()


    # ════════════════════════════════════════════════════════════════════════════
    # FILA 2: SIMULADOR + DECISIONES ENTIDAD
    # ════════════════════════════════════════════════════════════════════════════

    col3, col4 = st.columns(2, gap="large")


    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TARJETA 3: SIMULADOR
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    with col3:
        st.markdown("""
        <div style='background: white; padding: 2rem; border-radius: 15px; 
                    box-shadow: 0 10px 30px rgba(245, 158, 11, 0.3); 
                    border-top: 5px solid #f59e0b;
                    text-align: center;
                    height: 350px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;'>
            <div style='font-size: 3.5rem; margin-bottom: 1rem;'>🔮</div>
            <h3 style='color: #f59e0b; margin-bottom: 1rem; font-size: 1.4rem;'>
                ¿Qué pasaría si...?
            </h3>
            <p style='color: #666; line-height: 1.6; font-size: 0.95rem; margin-bottom: 1.5rem;'>
                Proyecta mejoras en hemoglobina según cambios alimentarios y suplementación.
            </p>
        </div>
        """, unsafe_allow_html=True)


        if st.button("📈 Simular Escenarios", use_container_width=True, key="btn_home_sim"):
            logger.info("✅ Navegando a: Simulador")
            st.session_state.pagina_actual = "simulador"
            st.rerun()


    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TARJETA 4: DECISIONES DE ENTIDAD
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    with col4:
        st.markdown("""
        <div style='background: white; padding: 2rem; border-radius: 15px; 
                    box-shadow: 0 10px 30px rgba(220, 53, 69, 0.3); 
                    border-top: 5px solid #dc3545;
                    text-align: center;
                    height: 350px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;'>
            <div style='font-size: 3.5rem; margin-bottom: 1rem;'>🏢</div>
            <h3 style='color: #dc3545; margin-bottom: 1rem; font-size: 1.4rem;'>
                Decisiones de Entidad
            </h3>
            <p style='color: #666; line-height: 1.6; font-size: 0.95rem; margin-bottom: 1.5rem;'>
                Dashboard territorial, hotspots críticos y alertas para gestores de salud.
            </p>
        </div>
        """, unsafe_allow_html=True)


        if st.button("🗺️ Ver Dashboard", use_container_width=True, key="btn_home_entidad"):
            logger.info("✅ Navegando a: Decisiones de Entidad")
            st.session_state.pagina_actual = "decisiones"
            st.rerun()


    st.markdown("---")


    st.markdown("### 📊 Impacto de NutriSenseIA a nivel nacional")


    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)


    with col_stat1:
        st.metric("Familias atendidas", "1,245", delta="+128 esta semana")


    with col_stat2:
        st.metric("Adherencia promedio", "63%", delta="+15pp vs control")


    with col_stat3:
        st.metric("Reducción riesgo alto", "28%", delta="-14% vs basal")


    with col_stat4:
        st.metric("Satisfacción", "96%", delta="+18pp")


    st.markdown("---")


    with st.expander("ℹ️ **¿Cómo funciona NutriSenseIA?**"):
        col_info1, col_info2 = st.columns(2)


        with col_info1:
            st.markdown("""
            #### 🎯 Objetivos del Sistema


            1. **Diagnóstico Temprano**  
               Predicción de anemia con IA y ajuste por altitud OMS 2024


            2. **Recomendaciones Personalizadas**  
               Menús adaptados por edad, presupuesto y región


            3. **Simulador de Impacto**  
               Proyecta mejoras en Hb e IMC según cambios alimentarios
            """)


        with col_info2:
            st.markdown("""
            #### 📚 Roles y Funciones


            **Madres/Cuidadores:**  
            Diagnóstico + Menús + Simulador


            **Profesionales de Salud:**  
            Todas las funciones + Explicabilidad SHAP


            **Gestores/MINSA:**  
            Dashboard + Mapa Territorial + Hotspots + Alertas
            """)


    st.markdown("---")


    # Footer CENTRADO
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <div style='display: flex; justify-content: center; gap: 2rem;'></div>
    </div>
    """, unsafe_allow_html=True)


    col1, col2, col3 = st.columns([1, 1, 1], gap="large")


    with col1:
        st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
        if st.button("📋 Política de Privacidad", use_container_width=False, key="btn_privacy"):
            logger.info("✅ Navegando a: Política de Privacidad")
            st.session_state.pagina_actual = 'privacidad_politica'
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


    with col2:
        st.markdown("""
        <div style='text-align: center;'>
            <strong>🩺 NutriSenseIA</strong><br>
            <span style='font-size: 0.9rem; color: #666;'>Sistema de Prevención de Anemia Infantil</span><br>
            <span style='font-size: 0.8rem; color: #999;'>Datatón 2025 | Ministerio de Salud del Perú</span>
        </div>
        """, unsafe_allow_html=True)


    with col3:
        st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
        if st.button("📜 Términos y Condiciones", use_container_width=False, key="btn_terms"):
            logger.info("✅ Navegando a: Términos y Condiciones")
            st.session_state.pagina_actual = 'terminos_condiciones'
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    pagina_inicio()