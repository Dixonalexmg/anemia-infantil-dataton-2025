"""
app.py - VERSIÓN FINAL LIMPIA
Sistema de Combate a la Anemia Infantil - Datatón 2025
NAVEGACIÓN LIMPIA (8 items) + FOOTER
"""

import streamlit as st
from utils.i18n_manager import get_i18n
from auth.roles_manager import RoleManager, User, RoleType
import logging

logger = logging.getLogger(__name__)

# ════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Sistema Anemia Infantil - MINSA",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.minsa.gob.pe',
        'Report a bug': None,
        'About': "NutriSenseIA - Datatón 2025"
    }
)

try:
    st.set_option('client.showSidebarNavigation', False)
except Exception:
    pass

i18n = get_i18n()

# ════════════════════════════════════════════════════════════════════════════
# CSS PERSONALIZADO
# ════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
.main { padding: 2rem; overflow-y: auto; }
.metric-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
              padding: 1.5rem; border-radius: 10px; color: white; margin: 0.5rem 0; }
.alert-critical { background-color: #ff4b4b; padding: 1rem; border-radius: 5px; 
                  color: white; font-weight: bold; }
.alert-warning { background-color: #ffa500; padding: 1rem; border-radius: 5px; color: white; }
.alert-success { background-color: #28a745; padding: 1rem; border-radius: 5px; color: white; }
.stButton>button { width: 100%; border-radius: 5px; height: 3rem; font-weight: bold; }
.main-header { background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); 
              padding: 2rem; border-radius: 10px; color: white; margin-bottom: 2rem; }
* { animation-duration: 0.1s !important; transition-duration: 0.1s !important; }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ════════════════════════════════════════════════════════════════════════════

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'username' not in st.session_state:
    st.session_state.username = 'usuario'
if 'user_object' not in st.session_state:
    st.session_state.user_object = None
if 'consentimiento_aceptado' not in st.session_state:
    st.session_state.consentimiento_aceptado = False
if 'sustituciones' not in st.session_state:
    st.session_state.sustituciones = None
if 'pagina_actual' not in st.session_state:
    st.session_state.pagina_actual = 'inicio'

# ════════════════════════════════════════════════════════════════════════════
# CREAR USUARIO
# ════════════════════════════════════════════════════════════════════════════

def crear_usuario_sesion():
    """Crea objeto User basado en session_state"""
    try:
        role_str = st.session_state.get('user_role', 'demo').upper()
        role = RoleType[role_str] if role_str in RoleType.__members__ else RoleType.DEMO
    except:
        role = RoleType.DEMO

    user = User(
        user_id=f"usr_{st.session_state.get('username', 'anon')[:3]}",
        username=st.session_state.get('username', 'usuario'),
        role=role,
        full_name=f"Usuario {st.session_state.get('username', 'anon')}",
        email=f"{st.session_state.get('username', 'anon')}@example.com",
        telefono="+51987654321",
        dni="12345678",
        is_demo=st.session_state.get('user_role', 'demo') == 'demo',
        consentimiento_aceptado=st.session_state.get('consentimiento_aceptado', False)
    )
    return user

# ════════════════════════════════════════════════════════════════════════════
# LOGIN - LIMPIO SIN CHECKBOX
# ════════════════════════════════════════════════════════════════════════════

def pagina_login():
    """Página de autenticación - Limpia y directa"""
    col_lang = st.columns([6, 1])
    with col_lang[1]:
        i18n.render_language_selector("login")

    st.markdown("<br><br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 2rem; background: white; border-radius: 10px;'>
            <h1>🩺</h1>
            <h2>Sistema Anemia Infantil</h2>
            <p style='color: #666;'>Ministerio de Salud del Perú</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("login_form"):
            st.subheader("Iniciar Sesión")
            username = st.text_input("👤 Usuario", placeholder="Ingrese su usuario", value="medico1")
            password = st.text_input("🔒 Contraseña", type="password", placeholder="Ingrese su contraseña", value="pass123")

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submit = st.form_submit_button("🚀 Ingresar", use_container_width=True)
            with col_btn2:
                demo = st.form_submit_button("👁️ Ver Demo", use_container_width=True)

            if submit:
                try:
                    from auth.users import authenticate_user
                    user = authenticate_user(username, password)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user_role = str(user.role)
                        st.session_state.username = user.username
                        st.session_state.user_object = crear_usuario_sesion()
                        st.session_state.pagina_actual = 'inicio'
                        st.session_state.consentimiento_aceptado = True
                        st.success(f"¡Bienvenido, {user.full_name}!")
                        st.rerun()
                    else:
                        st.error("❌ Usuario o contraseña incorrectos")
                except Exception as e:
                    st.error(f"❌ Error de autenticación: {str(e)}")

            if demo:
                st.session_state.authenticated = True
                st.session_state.user_role = "demo"
                st.session_state.username = "demo_user"
                st.session_state.user_object = crear_usuario_sesion()
                st.session_state.pagina_actual = 'inicio'
                st.session_state.consentimiento_aceptado = True
                st.rerun()

        with st.expander("ℹ️ Usuarios de Prueba"):
            st.markdown("""
            | Usuario | Contraseña | Rol |
            |---------|------------|-----|
            | cuidador1 | pass123 | Cuidador |
            | medico1 | pass123 | Profesional |
            | entidad1 | pass123 | Entidad |
            """)

        st.markdown("---")
        st.caption("""
        🩺 **NutriSenseIA** - Sistema de Prevención de Anemia Infantil

        Datatón 2025 | Ministerio de Salud del Perú
        """)

# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR - NAVEGACIÓN LIMPIA (8 items)
# ════════════════════════════════════════════════════════════════════════════

def mostrar_sidebar():
    """Muestra sidebar con navegación limpia"""
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2382/2382461.png", width=100)

        st.markdown(f"""
        ### 👤 Usuario
        **{st.session_state.username}**
        Rol: *{st.session_state.user_role.upper()}*
        """)

        if st.session_state.user_object and st.session_state.user_object.is_demo:
            st.warning("⚠️ MODO DEMO - Datos ficticios")

        st.success("✅ Consentimiento aceptado")

        st.markdown("---")
        i18n.render_language_selector("sidebar")
        st.markdown("---")

        st.subheader("📋 Navegación")

        # ════════════════════════════════════════════════════════════════
        # OPCIONES DE NAVEGACIÓN - 8 ITEMS (LIMPIO)
        # ════════════════════════════════════════════════════════════════
        opciones = [
            ("🏠 Inicio", "inicio"),
            ("🔍 Diagnóstico Individual", "diagnostico"),
            ("🍽️ Menús Personalizados", "menus"),
            ("🔮 ¿Qué pasaría si...?", "simulador"),
             ("📍 Decisiones Entidad", "decisiones"),
            ("🗺️ Mapa Territorial", "mapa"),
            ("📊 Telemetría", "telemetria"),
            ("🔍 Explicabilidad del Modelo", "explicabilidad"),
        ]

        current_page = st.session_state.pagina_actual

        for label, key in opciones:
            is_active = current_page == key
            display_label = f"✨ {label}" if is_active else label

            if st.button(
                display_label,
                use_container_width=True,
                key=f"nav_{key}",
                type="primary" if is_active else "secondary"
            ):
                st.session_state.pagina_actual = key
                st.rerun()


        st.markdown("---")

        if st.button("🚪 Cerrar Sesión", use_container_width=True, key="btn_logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# ENRUTADOR PRINCIPAL
# ════════════════════════════════════════════════════════════════════════════

def enrutador():
    """Renderiza una página según session_state.pagina_actual"""

    pagina = st.session_state.pagina_actual

    try:
        if pagina == 'inicio':
            from pages.home import pagina_inicio
            pagina_inicio()

        elif pagina == 'diagnostico':
            user_obj = st.session_state.user_object
            if user_obj.is_demo or RoleManager.tiene_permiso(user_obj, 'read_own_data'):
                from pages.diagnostico import pagina_diagnostico
                pagina_diagnostico()
            else:
                st.error("❌ No tienes permiso para acceder a esta página")

        elif pagina == 'menus':
            user_obj = st.session_state.user_object
            if user_obj.is_demo or RoleManager.tiene_permiso(user_obj, 'read_own_data'):
                from pages.menus import pagina_menus
                pagina_menus()
            else:
                st.error("❌ No tienes permiso para acceder a esta página")

        elif pagina == 'explicabilidad':
            from pages.explicabilidad_modelo import pagina_explicabilidad
            pagina_explicabilidad()

        elif pagina == 'simulador':
            from pages.proyecciones import pagina_proyecciones
            pagina_proyecciones()

        elif pagina == 'mapa':
            user_obj = st.session_state.user_object
            if user_obj.is_demo or RoleManager.tiene_permiso(user_obj, 'read_assigned_patients'):
                from pages.mapa import pagina_mapa_territorial
                pagina_mapa_territorial()
            else:
                st.error("❌ No tienes permiso para acceder a esta página")

        elif pagina == 'telemetria':
            user_obj = st.session_state.user_object
            if user_obj.is_demo or RoleManager.tiene_permiso(user_obj, 'read_telemetry'):
                from pages.telemetria_dashboard import pagina_telemetria_dashboard
                pagina_telemetria_dashboard()
            else:
                st.error("❌ No tienes permiso para acceder a esta página")
        elif pagina == 'privacidad_politica':
            from pages.privacidad_politica import pagina_privacidad_politica
            pagina_privacidad_politica()

        elif pagina == 'terminos_condiciones':
            from pages.terminos_condiciones import pagina_terminos_condiciones
            pagina_terminos_condiciones()

        elif pagina == 'decisiones':
            user_obj = st.session_state.user_object
            if user_obj.is_demo or RoleManager.tiene_permiso(user_obj, 'read_aggregated_data'):
                from pages.reportes_entidad_decisiones import pagina_reportes_entidad_decisiones
                pagina_reportes_entidad_decisiones()
            else:
                st.error("❌ No tienes permiso para acceder a esta página")

    except Exception as e:
        st.error(f"❌ Error al cargar la página: {str(e)}")
        with st.expander("🔍 Ver detalles del error"):
            import traceback
            st.code(traceback.format_exc())

# ════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════

def main():
    """Función principal"""

    if not st.session_state.authenticated:
        pagina_login()
        return

    if st.session_state.user_object is None:
        st.session_state.user_object = crear_usuario_sesion()

    mostrar_sidebar()
    enrutador()

if __name__ == "__main__":
    main()