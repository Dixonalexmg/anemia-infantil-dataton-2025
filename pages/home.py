"""
pages/home.py
VERSIÓN CORREGIDA - Home con 3 tarjetas guiadas (HU-01→HU-02→HU-03)
"""

import streamlit as st


def pagina_inicio():
    """Home con flujo guiado y CTAs claros"""
    
    # ============================================
    # HEADER PERSONALIZADO CON NOMBRE DE USUARIO
    # ============================================
    username = st.session_state.get('username', 'Usuario')
    
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2.5rem; border-radius: 15px; margin-bottom: 2rem;'>
        <h1 style='color: white; margin: 0; font-size: 2.2rem;'>
            Hola, {username} 👋
        </h1>
        <p style='color: rgba(255,255,255,0.9); margin: 0.8rem 0 0 0; font-size: 1.2rem;'>
            Te guío paso a paso
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # ============================================
    # 3 TARJETAS CON FLUJO CLARO (HU-01→HU-02→HU-03)
    # ============================================
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        st.markdown("""
        <div style='background: white; padding: 2rem; border-radius: 15px; 
                    box-shadow: 0 6px 12px rgba(0,0,0,0.1); height: 280px;
                    border-top: 5px solid #667eea;'>
            <div style='font-size: 3.5rem; text-align: center; margin-bottom: 1rem;'>🩺</div>
            <h3 style='color: #667eea; text-align: center; margin-bottom: 0.8rem;'>
                1) Perfil y Riesgo
            </h3>
            <p style='color: #666; text-align: center; line-height: 1.6;'>
                Completa o actualiza los datos del niño para estimar su riesgo.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("✅ **Empezar**", key="btn_diagnostico", use_container_width=True, type="primary"):
            st.session_state.pagina_actual = "🔍 Diagnóstico Individual"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div style='background: white; padding: 2rem; border-radius: 15px; 
                    box-shadow: 0 6px 12px rgba(0,0,0,0.1); height: 280px;
                    border-top: 5px solid #28a745;'>
            <div style='font-size: 3.5rem; text-align: center; margin-bottom: 1rem;'>🍽️</div>
            <h3 style='color: #28a745; text-align: center; margin-bottom: 0.8rem;'>
                2) Mis Menús
            </h3>
            <p style='color: #666; text-align: center; line-height: 1.6;'>
                Platos locales con hierro y opciones de sustitución.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🍴 **Ver mis menús**", key="btn_menus", use_container_width=True):
            st.session_state.pagina_actual = "🍽️ Menús Personalizados"
            st.rerun()
    
    with col3:
        st.markdown("""
        <div style='background: white; padding: 2rem; border-radius: 15px; 
                    box-shadow: 0 6px 12px rgba(0,0,0,0.1); height: 280px;
                    border-top: 5px solid #ffc107;'>
            <div style='font-size: 3.5rem; text-align: center; margin-bottom: 1rem;'>🔮</div>
            <h3 style='color: #f59e0b; text-align: center; margin-bottom: 0.8rem;'>
                3) ¿Qué pasaría si...?
            </h3>
            <p style='color: #666; text-align: center; line-height: 1.6;'>
                Compara tu situación actual vs. mejoras sugeridas.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🔍 **Comparar escenarios**", key="btn_simulador", use_container_width=True):
            st.session_state.pagina_actual = "🔮 ¿Qué pasaría si...?"
            st.rerun()
    
    # ============================================
    # EMPTY STATE (si no ha completado perfil)
    # ============================================
    st.markdown("---")
    
    if 'perfil_completado' not in st.session_state or not st.session_state.perfil_completado:
        st.info("""
        💡 **Aún no has completado el perfil del niño.**  
        Empecemos en menos de 1 minuto → Haz clic en **"Empezar"** en la tarjeta #1
        """)
    else:
        nombre_nino = st.session_state.get('nombre_nino', 'el niño')
        st.success(f"✅ **Perfil de {nombre_nino} completado.** Puedes actualizar datos o explorar los menús.")
    
    # ============================================
    # ESTADÍSTICAS DE IMPACTO (CONTEXTO)
    # ============================================
    st.markdown("---")
    st.markdown("### 📊 Impacto de NutriSenseIA a nivel nacional")
    
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    with col_stat1:
        st.metric("Familias atendidas", "1,245", delta="+128 esta semana", help="Familias usando NutriSenseIA activamente")
    
    with col_stat2:
        st.metric("Adherencia promedio", "63%", delta="+15pp vs control", help="Adherencia a menús personalizados")
    
    with col_stat3:
        st.metric("Reducción riesgo alto", "28%", delta="-14% vs basal", help="Reducción de casos en riesgo alto")
    
    with col_stat4:
        st.metric("Satisfacción", "96%", delta="+18pp", help="Satisfacción de madres y cuidadores")
    
    # ============================================
    # SECCIÓN INFORMATIVA (OPCIONAL - COLAPSABLE)
    # ============================================
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
            Todas las funciones + Dashboard Nacional
            
            **Gestores/MINSA:**  
            Dashboard + Mapa Territorial + Reportes PDF
            """)
