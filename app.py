"""
app.py
Sistema de Combate a la Anemia Infantil - Datatón 2025
VERSIÓN FINAL CORREGIDA CON TODAS LAS HU
"""

import streamlit as st


# ============================================================================
# CONFIGURACIÓN (DEBE SER LO PRIMERO)
# ============================================================================

st.set_page_config(
    page_title="Sistema Anemia Infantil - MINSA",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.minsa.gob.pe',
        'Report a bug': None,
        'About': "Sistema de Predicción y Recomendaciones para Anemia Infantil - Datatón 2025"
    }
)

# Desactivar navegación automática de Streamlit si está disponible
try:
    st.set_option('client.showSidebarNavigation', False)
except Exception:
    pass


# ============================================================================
# CSS PERSONALIZADO
# ============================================================================

st.markdown("""
<style>
.main {
    padding: 2rem;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
}
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.5rem;
    border-radius: 10px;
    color: white;
    margin: 0.5rem 0;
}
.alert-critical { 
    background-color: #ff4b4b; 
    padding: 1rem; 
    border-radius: 5px; 
    color: white; 
    font-weight: bold; 
}
.alert-warning { 
    background-color: #ffa500; 
    padding: 1rem; 
    border-radius: 5px; 
    color: white; 
}
.alert-success { 
    background-color: #28a745; 
    padding: 1rem; 
    border-radius: 5px; 
    color: white; 
}
.stButton>button { 
    width: 100%; 
    border-radius: 5px; 
    height: 3rem; 
    font-weight: bold; 
}
.main-header {
    background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
    padding: 2rem;
    border-radius: 10px;
    color: white;
    margin-bottom: 2rem;
}
* { 
    animation-duration: 0.1s !important; 
    transition-duration: 0.1s !important; 
}
.js-plotly-plot { 
    will-change: auto; 
}
</style>
""", unsafe_allow_html=True)


# ============================================================================
# SESSION STATE
# ============================================================================

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'pagina_actual' not in st.session_state:
    st.session_state.pagina_actual = "🏠 Inicio"


# ============================================================================
# LOGIN
# ============================================================================

def pagina_login():
    """Página de autenticación"""
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 2rem; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <h1>🩺</h1>
            <h2>Sistema Anemia Infantil</h2>
            <p style='color: #666;'>Ministerio de Salud del Perú</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.subheader("Iniciar Sesión")
            username = st.text_input("👤 Usuario", placeholder="Ingrese su usuario")
            password = st.text_input("🔒 Contraseña", type="password", placeholder="Ingrese su contraseña")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submit = st.form_submit_button("🚀 Ingresar", use_container_width=True)
            with col_btn2:
                demo = st.form_submit_button("👁️ Ver Demo", use_container_width=True)
            
            if submit:
                from auth.users import authenticate_user
                user = authenticate_user(username, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user_role = user.role
                    st.session_state.username = user.username
                    st.success(f"¡Bienvenido, {user.full_name}!")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
            
            if demo:
                st.session_state.authenticated = True
                st.session_state.user_role = "demo"
                st.session_state.username = "demo"
                st.rerun()
        
        with st.expander("ℹ️ Usuarios de Prueba"):
            st.markdown("""
            | Usuario | Contraseña | Rol |
            |---------|------------|-----|
            | admin | admin123 | Administrador |
            | medico | demo123 | Médico |
            | nutricionista | demo123 | Nutricionista |
            """)


# ============================================================================
# SIDEBAR
# ============================================================================

def mostrar_sidebar():
    """Muestra el sidebar con navegación"""
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2382/2382461.png", width=100)
        
        st.markdown(f"""
        ### 👤 Usuario
        **{st.session_state.username}**
        Rol: *{st.session_state.user_role}*
        """)
        
        st.markdown("---")
        st.subheader("📋 Navegación")
        
        pagina = st.radio(
            "Selecciona una sección:",
            [
                "🏠 Inicio",
                "🔍 Diagnóstico Individual",
                "🍽️ Menús Personalizados",
                "🔮 ¿Qué pasaría si...?",  # HU-03 - NUEVA
                "🗺️ Mapa Territorial",
                "📈 Panel de Impacto",  # HU-03 Panel de Impacto - NUEVA
            ],
            key="navegacion_principal",
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.subheader("📊 Estadísticas")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Datos", "7 archivos")
        with col2:
            st.metric("Registros", "896K")
        
        st.markdown("---")
        if st.button("🚪 Cerrar Sesión", use_container_width=True, key="btn_logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        return pagina


# ============================================================================
# ENRUTADOR PRINCIPAL
# ============================================================================

def main():
    """Función principal de la aplicación"""
    
    if not st.session_state.authenticated:
        pagina_login()
        return
    
    pagina_seleccionada = mostrar_sidebar()
    st.session_state.pagina_actual = pagina_seleccionada
    
    try:
        if pagina_seleccionada == "🏠 Inicio":
            from pages.home import pagina_inicio
            pagina_inicio()
        
        elif pagina_seleccionada == "🔍 Diagnóstico Individual":
            from pages.diagnostico import pagina_diagnostico
            pagina_diagnostico()
        
        elif pagina_seleccionada == "🍽️ Menús Personalizados":
            from pages.menus import pagina_menus
            pagina_menus()
        
        elif pagina_seleccionada == "🔮 ¿Qué pasaría si...?":
            from pages.proyecciones import pagina_proyecciones
            pagina_proyecciones()
        
        elif pagina_seleccionada == "🗺️ Mapa Territorial":
            from pages.mapa import pagina_mapa_territorial
            pagina_mapa_territorial()
        
        elif pagina_seleccionada == "📈 Panel de Impacto":
            from pages.metricas_impacto import pagina_metricas_impacto
            pagina_metricas_impacto()
    
    except Exception as e:
        st.error(f"❌ Error al cargar la página: {str(e)}")
        with st.expander("🔍 Ver detalles del error"):
            import traceback
            st.code(traceback.format_exc())


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    main()
