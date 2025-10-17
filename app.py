# app_streamlit.py
"""
Aplicación Streamlit - Sistema de Combate a la Anemia Infantil
Datatón Exprésate Perú con Datos 2025
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import requests
import json

from services.temporal_predictor import get_temporal_predictor

# Después de los imports, antes de st.set_page_config()

# Configurar caché para mejorar rendimiento
@st.cache_data(ttl=600)  # Cache por 10 minutos
def cargar_datos_brechas():
    """Carga datos de brechas con caché"""
    return data_loader.load_brechas_departamento()

@st.cache_data(ttl=600)
def cargar_datos_tendencias():
    """Carga datos de tendencias con caché"""
    return data_loader.load_tendencias_departamento()

@st.cache_data(ttl=600)
def cargar_datos_proyecciones():
    """Carga datos de proyecciones con caché"""
    return data_loader.load_proyecciones()

@st.cache_data(ttl=600)
def cargar_reporte_temporal():
    """Carga reporte temporal con caché"""
    return data_loader.load_reporte_temporal()

@st.cache_data(ttl=600)
def cargar_reporte_equidad():
    """Carga reporte de equidad con caché"""
    return data_loader.load_reporte_equidad()



# Configuración de página (DEBE SER LA PRIMERA LLAMADA DE STREAMLIT)
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

# Importar servicios locales
from services.predictor import anemia_predictor
from services.menu_generator import menu_generator
from utils.data_loader import data_loader
from utils.validators import (
    validate_edad,
    validate_hemoglobina,
    validate_altitud,
    validate_presupuesto
)

# ============================================================================
# CONFIGURACIÓN Y ESTILOS
# ============================================================================

# CSS personalizado para mejorar UX
st.markdown("""
<style>
    /* Mejorar legibilidad */
    .main {
        padding: 2rem;
    }
    
    /* Tarjetas de métricas */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    
    /* Alertas */
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
    
    /* Botones personalizados */
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3rem;
        font-weight: bold;
    }
    
    /* Header */
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# FUNCIONES AUXILIARES
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
    """Crea un gauge visual para hemoglobina (optimizado)"""
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


def crear_grafico_menu(menu_data):
    """Crea visualización del menú generado"""
    items = menu_data['menu_items']
    
    if not items:
        return None
    
    df = pd.DataFrame(items)
    
    fig = px.bar(
        df,
        x='alimento',
        y='hierro_mg',
        color='tipo',
        title=f"Contenido de Hierro por Alimento (Total: {menu_data['hierro_aportado_mg']:.1f} mg)",
        labels={'hierro_mg': 'Hierro (mg)', 'alimento': 'Alimento'},
        color_discrete_map={'hemo': '#e74c3c', 'no_hemo': '#3498db'},
        height=400
    )
    
    fig.add_hline(
        y=menu_data['requerimiento_hierro_mg'],
        line_dash="dash",
        line_color="green",
        annotation_text=f"Requerimiento: {menu_data['requerimiento_hierro_mg']:.1f} mg"
    )
    
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Hierro (mg)",
        showlegend=True,
        legend_title="Tipo de Hierro"
    )
    
    return fig

# ============================================================================
# INICIALIZACIÓN DE SESIÓN
# ============================================================================

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'username' not in st.session_state:
    st.session_state.username = None

# ============================================================================
# PÁGINA DE LOGIN
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
                # Autenticar
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
        
        # Información de usuarios demo
        with st.expander("ℹ️ Usuarios de Prueba"):
            st.markdown("""
            **Usuarios disponibles:**
            
            | Usuario | Contraseña | Rol |
            |---------|------------|-----|
            | admin | admin123 | Administrador |
            | medico | demo123 | Médico |
            | nutricionista | demo123 | Nutricionista |
            
            O haz clic en **"Ver Demo"** para acceso rápido.
            """)

# ============================================================================
# SIDEBAR
# ============================================================================

def mostrar_sidebar():
    """Muestra el sidebar con navegación y información del usuario"""
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2382/2382461.png", width=100)
        
        st.markdown(f"""
        ### 👤 Usuario
        **{st.session_state.username}**  
        Rol: *{st.session_state.user_role}*
        """)
        
        st.markdown("---")
        
        # Navegación con key único para evitar recargas
        st.subheader("📋 Navegación")
        
        # Usar session_state para persistir selección
        if 'pagina_actual' not in st.session_state:
            st.session_state.pagina_actual = "🏠 Inicio"
        
        pagina = st.radio(
            "Selecciona una sección:",
            [
                "🏠 Inicio",
                "🔍 Diagnóstico Individual",
                "🍽️ Menús Personalizados",
                "📊 Dashboard Nacional",
                "📈 Proyecciones",
                "🗺️ Mapa Territorial"
            ],
            key="navegacion_principal",
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Estadísticas rápidas (simplificadas para ser más rápido)
        st.subheader("📊 Estadísticas")
        
        # Usar métricas estáticas para evitar carga
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Datos", "7 archivos")
        with col2:
            st.metric("Registros", "896K")
        
        st.markdown("---")
        
        if st.button("🚪 Cerrar Sesión", use_container_width=True, key="btn_logout"):
            st.session_state.authenticated = False
            st.session_state.user_role = None
            st.session_state.username = None
            st.session_state.pagina_actual = "🏠 Inicio"
            st.rerun()
        
        return pagina


# ============================================================================
# PÁGINA: INICIO
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

        
def pagina_diagnostico():
    """
    🚀 DIAGNÓSTICO INDIVIDUAL CON IA - VERSIÓN MEJORADA
    
    ORDEN REORGANIZADO (Storytelling Clínico):
    1. 🎯 Evaluación Rápida (Semáforo)
    2. 🔮 Proyección Prospectiva 3-6 meses ⭐ INNOVACIÓN
    3. ⚠️ Factores Críticos
    4. 💊 Protocolo Clínico
    5. 🔬 Explicabilidad IA + Detalles Técnicos ⭐ INNOVACIÓN
    6. 📊 Métricas del Modelo
    7. 📄 PDF + 📧 Notificaciones ⭐ NUEVO
    """
    import plotly.graph_objects as go
    import numpy as np
    import pandas as pd
    from services.predictor import anemia_predictor
    from services.temporal_predictor import get_temporal_predictor
    from utils.clinical_recommendations import generar_recomendaciones_personalizadas
    from utils.risk_classifier import clasificar_nivel_riesgo, extraer_factores_criticos
    from utils.pdf_generator import generar_pdf_reporte  # ← NUEVO
    from utils.notificaciones import get_sistema_notificaciones  # ← NUEVO
    import base64
    
    # === HEADER CON BADGE DE IA ===
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);'>
        <div style='display: flex; align-items: center; gap: 1rem;'>
            <div style='font-size: 3rem;'>🤖</div>
            <div>
                <h1 style='color: white; margin: 0; font-size: 2rem;'>
                    Diagnóstico Individual con Inteligencia Artificial
                </h1>
                <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.1rem;'>
                    Sistema de Alerta Temprana con Protocolos Clínicos Personalizados
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # === DICCIONARIO DE ALTITUDES POR DEPARTAMENTO ===
    ALTITUDES_DEPARTAMENTO = {
        'AMAZONAS': 2300, 'ANCASH': 3100, 'APURIMAC': 2900, 'AREQUIPA': 2350,
        'AYACUCHO': 2750, 'CAJAMARCA': 2750, 'CALLAO': 10, 'CUSCO': 3400,
        'HUANCAVELICA': 3680, 'HUANUCO': 1900, 'ICA': 400, 'JUNIN': 3250,
        'LA LIBERTAD': 2800, 'LAMBAYEQUE': 30, 'LIMA': 150, 'LORETO': 120,
        'MADRE DE DIOS': 260, 'MOQUEGUA': 1400, 'PASCO': 4350, 'PIURA': 30,
        'PUNO': 3850, 'SAN MARTIN': 280, 'TACNA': 560, 'TUMBES': 10, 'UCAYALI': 150
    }
    
    st.markdown("### 📋 Datos del Paciente")
    
    # SELECTOR DE DEPARTAMENTO FUERA DEL FORM
    departamento = st.selectbox(
        "🗺️ Departamento de residencia",
        options=list(ALTITUDES_DEPARTAMENTO.keys()),
        index=14,
        help="La altitud se ajustará automáticamente según el departamento seleccionado"
    )
    
    altitud_sugerida = ALTITUDES_DEPARTAMENTO.get(departamento, 150)
    st.info(f"📍 **Altitud sugerida para {departamento}:** {altitud_sugerida} msnm (capital departamental). Puedes ajustarla manualmente.")
    
    # === FORMULARIO DE ENTRADA ===
    with st.form("form_diagnostico"):
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("#### Datos Clínicos")
            edad_meses = st.number_input("Edad del niño (meses)", 6, 59, 24, 1, help="Edad en meses, rango: 6-59")
            peso_kg = st.number_input("Peso del niño (kg)", 3.0, 25.0, 12.0, 0.1, help="Peso para dosificación")
            hemoglobina = st.number_input("Hemoglobina (g/dL)", 5.0, 18.0, 11.5, 0.1, help="Nivel de hemoglobina")
            altitud = st.number_input("Altitud (msnm)", 0, 5000, altitud_sugerida, 50, 
                                     help=f"Ajustado a {altitud_sugerida}m para {departamento}")
        
        with col_right:
            st.markdown("#### Datos Sociodemográficos")
            area = st.selectbox("Área de residencia", ["Urbana", "Rural"], help="Área geográfica")
            recibe_suplemento = st.selectbox("Recibe suplementación de hierro", ["Sí", "No"], index=1)
            asiste_cred = st.selectbox("Asiste a controles CRED", ["Sí", "No"], index=0)
            es_bajo_peso = st.checkbox("Nació con bajo peso (<2500g)", False)
            es_prematuro = st.checkbox("Nació prematuro (<37 semanas)", False)
            
            # ← NUEVO: Campos para notificaciones
            st.markdown("##### 📧 Notificaciones (Opcional)")
            email_notif = st.text_input("Email para recordatorios", placeholder="ejemplo@correo.com")
            nombre_paciente = st.text_input("Nombre del paciente", placeholder="Nombre del niño/a")
        
        st.markdown("---")
        col_btn1, col_btn2 = st.columns([3, 1])
        with col_btn1:
            submitted = st.form_submit_button("🔍 ANALIZAR CON INTELIGENCIA ARTIFICIAL", 
                                             type="primary", use_container_width=True)
        with col_btn2:
            st.form_submit_button("🔄 Limpiar", type="secondary")
    
    # === PROCESAR PREDICCIÓN ===
    if submitted:
        datos_paciente = {
            'hemoglobina': hemoglobina,
            'edad_meses': edad_meses,
            'peso_kg': peso_kg,
            'altitud': altitud,
            'departamento': departamento,
            'area_rural': area == "Rural",
            'recibe_suplemento': recibe_suplemento == "Sí",
            'asiste_cred': asiste_cred == "Sí",
            'es_bajo_peso': es_bajo_peso,
            'es_prematuro': es_prematuro
        }
        
        with st.spinner('🤖 Analizando con Inteligencia Artificial...'):
            import time
            time.sleep(0.5)
            resultado = anemia_predictor.predecir(datos_paciente)
        
        st.success("✅ Análisis completado exitosamente")
        st.divider()
        
        # Extraer factores de riesgo detectados
        factores_riesgo_detectados = []
        if not datos_paciente['recibe_suplemento']:
            factores_riesgo_detectados.append('sin_suplemento')
        if not datos_paciente['asiste_cred']:
            factores_riesgo_detectados.append('sin_cred')
        if datos_paciente['area_rural']:
            factores_riesgo_detectados.append('area_rural')
        if altitud > 3000:
            factores_riesgo_detectados.append('alta_altitud')
        if 6 <= edad_meses <= 24:
            factores_riesgo_detectados.append('edad_6_24m')
        if es_bajo_peso:
            factores_riesgo_detectados.append('bajo_peso')
        if es_prematuro:
            factores_riesgo_detectados.append('prematuro')
        
        probabilidad_ml = resultado.get('ml', {}).get('probabilidad', 0.0) if 'ml' in resultado else 0.0
        
        semaforo = clasificar_nivel_riesgo(
            probabilidad_ml=probabilidad_ml,
            tiene_anemia=resultado['tiene_anemia'],
            edad_meses=edad_meses,
            factores_riesgo=factores_riesgo_detectados,
            hb_actual=hemoglobina
        )
        
        recomendaciones = generar_recomendaciones_personalizadas(
            edad_meses=edad_meses,
            peso_kg=peso_kg,
            tiene_anemia=resultado['tiene_anemia'],
            factores_riesgo=factores_riesgo_detectados,
            hb_actual=hemoglobina,
            altitud_m=altitud,
            es_bajo_peso=es_bajo_peso,
            es_prematuro=es_prematuro
        )
        
        # Generar proyecciones
        predictor_temporal = get_temporal_predictor(anemia_predictor)
        proyeccion_3m = predictor_temporal.predecir_futuro(datos_paciente, meses=3)
        proyeccion_6m = predictor_temporal.predecir_futuro(datos_paciente, meses=6)
        
        # =====================================================
        # 1️⃣ EVALUACIÓN RÁPIDA (SEMÁFORO)
        # =====================================================
        st.markdown("## 🎯 Evaluación y Plan de Acción Inmediato")
        
        col_resultado, col_accion = st.columns([1.2, 1])
        
        with col_resultado:
            if resultado['tiene_anemia']:
                severidad_emoji = {'Leve': '🟡', 'Moderada': '🟠', 'Severa': '🔴'}
                emoji_estado = severidad_emoji.get(resultado['severidad'], '⚠️')
                estado_texto = f"ANEMIA {resultado['severidad'].upper()}"
            else:
                emoji_estado = '✅'
                estado_texto = "SIN ANEMIA"
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {semaforo['background']} 0%, {semaforo['background']}dd 100%);
                        padding: 25px; border-radius: 12px; box-shadow: 0 6px 12px rgba(0,0,0,0.15);">
                <h2 style="color: white; margin: 0; font-size: 2.2em;">
                    {semaforo['emoji']} {semaforo['nivel']}
                </h2>
                <p style="color: white; font-size: 1.3em; margin: 12px 0 0 0;">
                    {emoji_estado} {estado_texto} | Hb: {hemoglobina:.1f} g/dL<br>
                    🤖 Riesgo ML: {probabilidad_ml*100:.1f}%
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_accion:
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.95); border-left: 5px solid {semaforo['background']};
                        padding: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                <h3 style="margin-top: 0; color: #333;">💡 ACCIÓN INMEDIATA</h3>
                <p style="color: #555; font-size: 1.1em; line-height: 1.5;">
                    {semaforo['accion_inmediata']}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # =====================================================
        # 2️⃣ PROYECCIÓN PROSPECTIVA ⭐ INNOVACIÓN
        # =====================================================
        st.markdown("## 🔮 Proyección Prospectiva de Riesgo")
        st.markdown("*Predicción de evolución del riesgo de anemia basada en factores actuales - **INNOVACIÓN DEL SISTEMA***")
        
        tab3m, tab6m = st.tabs(["📊 Proyección 3 Meses", "📈 Proyección 6 Meses"])
        
        with tab3m:
            # Métricas principales
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🩺 Hb Actual", f"{proyeccion_3m['hemoglobina_actual']} g/dL")
            with col2:
                st.metric("🔮 Hb en 3 meses", f"{proyeccion_3m['hemoglobina_proyectada']} g/dL",
                         delta=f"{proyeccion_3m['delta_hemoglobina']:+.2f}",
                         delta_color="normal" if proyeccion_3m['delta_hemoglobina'] > 0 else "inverse")
            with col3:
                st.metric("📈 Prob. Actual", f"{proyeccion_3m['probabilidad_actual']*100:.1f}%")
            with col4:
                st.metric("🎯 Prob. 3 meses", f"{proyeccion_3m['probabilidad_futura']*100:.1f}%",
                         delta=f"{proyeccion_3m['cambio_probabilidad']:+.1f}%", delta_color="inverse")
            
            # Gráfico de evolución
            st.markdown("### 📉 Evolución Proyectada de Hemoglobina")
            
            x_points = ['Hoy', '1 mes', '2 meses', '3 meses']
            y_points = [
                proyeccion_3m['hemoglobina_actual'],
                proyeccion_3m['hemoglobina_actual'] + (proyeccion_3m['delta_hemoglobina'] * 0.33),
                proyeccion_3m['hemoglobina_actual'] + (proyeccion_3m['delta_hemoglobina'] * 0.66),
                proyeccion_3m['hemoglobina_proyectada']
            ]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=x_points, y=y_points, mode='lines+markers', name='Hemoglobina proyectada',
                line=dict(color=proyeccion_3m['tendencia_color'], width=4), marker=dict(size=10),
                hovertemplate='%{x}<br>Hb: %{y:.2f} g/dL<extra></extra>'
            ))
            fig.add_hline(y=11.0, line_dash="dash", line_color="orange",
                         annotation_text="Umbral OMS (11.0 g/dL)", annotation_position="right")
            fig.add_hrect(y0=10.0, y1=11.0, fillcolor="orange", opacity=0.1,
                         annotation_text="Anemia Leve", annotation_position="top left")
            fig.add_hrect(y0=7.0, y1=10.0, fillcolor="red", opacity=0.1,
                         annotation_text="Anemia Moderada", annotation_position="top left")
            fig.update_layout(
                title=f"Tendencia: {proyeccion_3m['tendencia']} {proyeccion_3m['tendencia_emoji']}",
                xaxis_title="Tiempo", yaxis_title="Hemoglobina (g/dL)", height=450, hovermode='x unified',
                yaxis=dict(range=[max(6, min(y_points)-1), min(16, max(y_points)+1)])
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Factores de deterioro
            st.markdown("### ⚠️ Factores de Riesgo Temporal")
            col_fact1, col_fact2 = st.columns([2, 1])
            with col_fact1:
                for i, factor in enumerate(proyeccion_3m['factores_deterioro'], 1):
                    st.markdown(f"{i}. {factor}")
            with col_fact2:
                urgencia = proyeccion_3m['nivel_urgencia']
                if '🔴' in urgencia:
                    st.error(f"**{urgencia}**")
                elif '🟠' in urgencia:
                    st.warning(f"**{urgencia}**")
                elif '🟡' in urgencia:
                    st.info(f"**{urgencia}**")
                else:
                    st.success(f"**{urgencia}**")
                st.metric("Severidad Proyectada", proyeccion_3m['severidad_futura'])
            
            # Calendario de controles
            st.markdown("### 📅 Calendario de Seguimiento Recomendado")
            for control in proyeccion_3m['controles_recomendados']:
                with st.expander(f"{control['tipo']} - {control['fecha']}", expanded=True):
                    st.markdown(f"**Objetivo:** {control['objetivo']}")
                    st.markdown(f"**Acción:** {control['accion']}")
        
        with tab6m:
            # Métricas principales
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🩺 Hb Actual", f"{proyeccion_6m['hemoglobina_actual']} g/dL")
            with col2:
                st.metric("🔮 Hb en 6 meses", f"{proyeccion_6m['hemoglobina_proyectada']} g/dL",
                         delta=f"{proyeccion_6m['delta_hemoglobina']:+.2f}",
                         delta_color="normal" if proyeccion_6m['delta_hemoglobina'] > 0 else "inverse")
            with col3:
                st.metric("📈 Prob. Actual", f"{proyeccion_6m['probabilidad_actual']*100:.1f}%")
            with col4:
                st.metric("🎯 Prob. 6 meses", f"{proyeccion_6m['probabilidad_futura']*100:.1f}%",
                         delta=f"{proyeccion_6m['cambio_probabilidad']:+.1f}%", delta_color="inverse")
            
            # Gráfico de evolución a 6 meses
            st.markdown("### 📉 Evolución Proyectada de Hemoglobina (6 meses)")
            x_points_6m = ['Hoy', '2 meses', '4 meses', '6 meses']
            y_points_6m = [
                proyeccion_6m['hemoglobina_actual'],
                proyeccion_6m['hemoglobina_actual'] + (proyeccion_6m['delta_hemoglobina'] * 0.33),
                proyeccion_6m['hemoglobina_actual'] + (proyeccion_6m['delta_hemoglobina'] * 0.66),
                proyeccion_6m['hemoglobina_proyectada']
            ]
            
            fig6m = go.Figure()
            fig6m.add_trace(go.Scatter(
                x=x_points_6m, y=y_points_6m, mode='lines+markers', name='Hemoglobina proyectada',
                line=dict(color=proyeccion_6m['tendencia_color'], width=4), marker=dict(size=10),
                hovertemplate='%{x}<br>Hb: %{y:.2f} g/dL<extra></extra>'
            ))
            fig6m.add_hline(y=11.0, line_dash="dash", line_color="orange",
                           annotation_text="Umbral OMS (11.0 g/dL)")
            fig6m.add_hrect(y0=10.0, y1=11.0, fillcolor="orange", opacity=0.1,
                           annotation_text="Anemia Leve", annotation_position="top left")
            fig6m.add_hrect(y0=7.0, y1=10.0, fillcolor="red", opacity=0.1,
                           annotation_text="Anemia Moderada", annotation_position="top left")
            fig6m.update_layout(
                title=f"Tendencia: {proyeccion_6m['tendencia']} {proyeccion_6m['tendencia_emoji']}",
                xaxis_title="Tiempo", yaxis_title="Hemoglobina (g/dL)", height=450, hovermode='x unified',
                yaxis=dict(range=[max(6, min(y_points_6m)-1), min(16, max(y_points_6m)+1)])
            )
            st.plotly_chart(fig6m, use_container_width=True)
            
            # Factores y controles
            st.markdown("### ⚠️ Factores de Riesgo Temporal")
            col_fact1, col_fact2 = st.columns([2, 1])
            with col_fact1:
                for i, factor in enumerate(proyeccion_6m['factores_deterioro'], 1):
                    st.markdown(f"{i}. {factor}")
            with col_fact2:
                urgencia = proyeccion_6m['nivel_urgencia']
                if '🔴' in urgencia:
                    st.error(f"**{urgencia}**")
                elif '🟠' in urgencia:
                    st.warning(f"**{urgencia}**")
                elif '🟡' in urgencia:
                    st.info(f"**{urgencia}**")
                else:
                    st.success(f"**{urgencia}**")
                st.metric("Severidad Proyectada", proyeccion_6m['severidad_futura'])
            
            st.markdown("### 📅 Calendario de Seguimiento Recomendado")
            for control in proyeccion_6m['controles_recomendados']:
                with st.expander(f"{control['tipo']} - {control['fecha']}", expanded=True):
                    st.markdown(f"**Objetivo:** {control['objetivo']}")
                    st.markdown(f"**Acción:** {control['accion']}")
        
        st.divider()
        
        # =====================================================
        # 3️⃣ FACTORES CRÍTICOS
        # =====================================================
        st.markdown("## ⚠️ Factores Críticos y Plan de Acción")
        
        factores_criticos = extraer_factores_criticos(factores_riesgo_detectados, top_n=3)
        
        if factores_criticos:
            for i, factor in enumerate(factores_criticos, 1):
                criticidad_color = {
                    1: {'bg': '#ffebee', 'border': '#d32f2f', 'badge': '🔴 CRÍTICO'},
                    2: {'bg': '#fff3e0', 'border': '#ff9800', 'badge': '🟠 ALTO'},
                    3: {'bg': '#fff9c4', 'border': '#fbc02d', 'badge': '🟡 MODERADO'},
                    4: {'bg': '#e8f5e9', 'border': '#4caf50', 'badge': '🟢 BAJO'}
                }
                estilo = criticidad_color.get(factor['criticidad'], criticidad_color[3])
                
                acciones_especificas = {
                    'sin_suplemento': '🚨 Iniciar sulfato ferroso HOY (2mg/kg/día preventivo o 3mg/kg/día tratamiento)',
                    'edad_6_24m': '👶 Reforzar alimentación complementaria + seguimiento mensual CRED',
                    'alta_altitud': f'⛰️ Ajuste de Hb aplicado ({altitud}m). Monitoreo estricto + oximetría si <90%',
                    'sin_cred': '📋 Programar control CRED dentro de 7 días. Visita domiciliaria',
                    'area_rural': '🏘️ Coordinar con promotor de salud local para seguimiento',
                    'bajo_peso': '⚖️ Protocolo diferenciado. Iniciar desde 30 días de vida',
                    'prematuro': '🍼 Seguimiento especializado. Dosis según peso corregido'
                }
                accion = acciones_especificas.get(factor.get('factor_key', list(acciones_especificas.keys())[i-1]), 
                                                  'Seguimiento según protocolo NTS 213-2024')
                
                with st.expander(f"{factor['emoji']} {factor['nombre']} {estilo['badge']}", 
                                expanded=(factor['criticidad'] <= 2)):
                    st.markdown(f"""
                    <div style="background: {estilo['bg']}; padding: 15px; border-radius: 8px; 
                                border-left: 4px solid {estilo['border']}; margin-bottom: 10px;">
                        <p style="margin: 0 0 10px 0; color: #333;"><strong>📝 Descripción:</strong> 
                           {factor.get('descripcion', factor.get('nombre', 'Factor de riesgo detectado'))}</p>
                        <p style="margin: 0; color: #333;"><strong>✅ Plan de acción:</strong> {accion}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.success("✅ No se detectaron factores de riesgo críticos. Continuar con controles preventivos.")
        
        st.divider()
        
        # =====================================================
        # 4️⃣ PROTOCOLO CLÍNICO
        # =====================================================
        with st.expander(f"💊 Protocolo Clínico Completo - {recomendaciones['grupo_etario'].replace('_', '-').upper()}", 
                         expanded=resultado['tiene_anemia']):
            
            st.caption(f"Basado en {recomendaciones['normativa']}")
            
            if recomendaciones['tipo_intervencion'] == 'TRATAMIENTO':
                st.error(f"🔴 **TRATAMIENTO** (Anemia confirmada con Hb {hemoglobina:.1f} g/dL)")
            else:
                st.info(f"🛡️ **PREVENCIÓN** (Sin anemia, riesgo controlado)")
            
            st.markdown("---")
            
            col_sup1, col_sup2 = st.columns([2.5, 1])
            with col_sup1:
                st.markdown("#### 💊 Suplementación de Hierro")
                st.markdown(f"**Presentación:** {recomendaciones['dosis_config']['presentacion']}")
                st.markdown(f"**Dosis prescrita:** {recomendaciones['dosis_config']['dosis']}")
                
                if recomendaciones['dosis_calculada']:
                    dosis_info = recomendaciones['dosis_calculada']
                    st.success(f"""**Dosis individualizada ({peso_kg} kg):**
                    - **{dosis_info['dosis_mg']} mg/día** de hierro elemental
                    - **{dosis_info['dosis_ml']} ml** ({int(dosis_info['dosis_gotas'])} gotas)""")
                
                st.markdown(f"**Duración:** {recomendaciones['dosis_config']['duracion_meses']} meses continuos")
            
            with col_sup2:
                st.info("""📝 **Indicaciones:**
                - En ayunas
                - Con cítricos
                - Lejos de lácteos
                - Heces oscuras (normal)""")
            
            st.markdown("#### 🍽️ Alimentación Recomendada")
            st.info(f"💡 {recomendaciones['alimentacion']['nota']}")
            
            col_ali1, col_ali2 = st.columns(2)
            with col_ali1:
                st.markdown("**✅ Alimentos a INCLUIR:**")
                for alimento in recomendaciones['alimentacion']['principal'][:5]:
                    st.markdown(f"- {alimento}")
            with col_ali2:
                st.markdown("**⚠️ Recomendaciones:**")
                for item in recomendaciones['alimentacion']['evitar'][:3]:
                    st.markdown(f"- {item}")
            
            st.markdown("#### 📅 Calendario de Seguimiento")
            for key, value in list(recomendaciones['frecuencia_controles'].items())[:3]:
                st.markdown(f"- **{key.replace('_', ' ').title()}:** {value}")
        
        st.divider()
        
        # =====================================================
        # 5️⃣ EXPLICABILIDAD IA + DETALLES TÉCNICOS ⭐ INNOVACIÓN
        # =====================================================
        with st.expander("🔬 Detalles Técnicos y Diagnóstico Completo (Especialistas)", expanded=False):
            
            st.markdown("### 🏥 Diagnóstico Clínico (OMS 2024)")
            col_hb1, col_hb2, col_hb3 = st.columns(3)
            with col_hb1:
                st.metric("Hb Observada", f"{resultado['hemoglobina_observada']:.1f} g/dL")
            with col_hb2:
                st.metric("Hb Ajustada", f"{resultado['hemoglobina_ajustada']:.1f} g/dL")
            with col_hb3:
                ajuste = resultado['hemoglobina_observada'] - resultado['hemoglobina_ajustada']
                st.metric("Ajuste Altitud", f"{ajuste:.2f} g/dL", help=f"Altitud: {altitud}m")
            
            if resultado['tiene_anemia']:
                st.error(f"⚠️ **Déficit de hemoglobina:** {resultado.get('deficit_g_dl', 0):.2f} g/dL")
            
            st.markdown("---")
            
            if 'ml' in resultado and resultado['ml']:
                st.markdown("### 🤖 Análisis de Inteligencia Artificial")
                col_ml1, col_ml2 = st.columns([1.5, 1])
                
                with col_ml1:
                    prob = resultado['ml']['probabilidad']
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number", value=prob * 100, domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "Probabilidad de Anemia (%)", 'font': {'size': 14}},
                        number={'suffix': "%", 'font': {'size': 32}},
                        gauge={
                            'axis': {'range': [None, 100]},
                            'bar': {'color': "#667eea" if prob < 0.5 else "#ff6b6b"},
                            'steps': [
                                {'range': [0, 30], 'color': '#d4edda'},
                                {'range': [30, 70], 'color': '#fff3cd'},
                                {'range': [70, 100], 'color': '#f8d7da'}
                            ],
                            'threshold': {'line': {'color': "red", 'width': 4}, 'value': 81.31}
                        }
                    ))
                    fig.update_layout(height=220, margin=dict(l=10, r=10, t=40, b=10))
                    st.plotly_chart(fig, use_container_width=True)
                
                with col_ml2:
                    st.metric("Confianza del Modelo", f"{resultado['ml']['confianza']}%")
                    categoria = resultado['ml']['categoria_riesgo_ml']
                    emoji_cat = {'Bajo': '🟢', 'Medio': '🟡', 'Alto': '🔴'}.get(categoria, '⚪')
                    st.metric("Categoría de Riesgo", f"{emoji_cat} {categoria}")
                    st.caption("**Modelo:** RandomForest  \n**Datos:** 895,982 registros SIEN")
            
            st.markdown("---")
            st.markdown("### 🔬 Explicabilidad del Modelo (SHAP)")
            
            try:
                from utils import explainer as explainer_module
                import pickle
                from pathlib import Path
                
                model_path = Path("models/predictor_anemia_ml.pkl")
                
                if model_path.exists():
                    with open(model_path, 'rb') as f:
                        model_package = pickle.load(f)
                    
                    modelo_ml = model_package['model']
                    features_list = model_package['features']
                    
                    X_background = explainer_module.load_background_data(
                        'data/processed/sien_modelo_limpio.csv', features_list, n_samples=50
                    )
                    
                    if X_background is not None:
                        mi_explainer = explainer_module.ModelExplainer(modelo_ml, X_background)
                        X_sample_prepared = anemia_predictor._preparar_features_ml(datos_paciente)
                        
                        if X_sample_prepared is not None:
                            clean_data = {}
                            for col in features_list:
                                if col in X_sample_prepared.columns:
                                    val = X_sample_prepared[col].iloc[0]
                                    if isinstance(val, (list, tuple)):
                                        clean_val = float(val[0]) if len(val) > 0 else 0.0
                                    elif isinstance(val, np.ndarray):
                                        clean_val = float(val.flat[0]) if val.size > 0 else 0.0
                                    else:
                                        clean_val = float(val) if not pd.isna(val) else 0.0
                                else:
                                    clean_val = 0.0
                                clean_data[col] = clean_val
                            
                            X_sample_prepared = pd.DataFrame([clean_data], columns=features_list)
                            explicacion = mi_explainer.explain_individual(X_sample_prepared, features_list)
                            
                            if explicacion:
                                st.info(explicacion['texto_explicacion'])
                                col_shap1, col_shap2 = st.columns(2)
                                with col_shap1:
                                    st.markdown("**Gráfico de Barras**")
                                    st.pyplot(explicacion['fig_bar'])
                                with col_shap2:
                                    st.markdown("**Gráfico Waterfall**")
                                    st.pyplot(explicacion['fig_waterfall'])
                                with st.expander("📊 Tabla detallada de factores"):
                                    st.dataframe(explicacion['shap_df'].head(15), use_container_width=True)
                            else:
                                st.warning("⚠️ No se pudo generar explicación SHAP")
                        else:
                            st.info("ℹ️ Features no preparadas para SHAP")
                    else:
                        st.info("ℹ️ Background data no disponible")
                else:
                    st.info("ℹ️ Modelo ML no encontrado")
            except Exception as e:
                st.error(f"❌ Error SHAP: {str(e)}")
        
        st.divider()
        
        # =====================================================
        # 6️⃣ MÉTRICAS DEL MODELO
        # =====================================================
        with st.expander("📊 Información del Modelo y Métricas", expanded=False):
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            with col_m1:
                st.metric("🎯 Precisión", "99.9%", help="De cada 100 predicciones positivas, 99.9 son correctas")
            with col_m2:
                st.metric("📈 Recall", "85.0%", help="Detecta 85 de cada 100 casos reales")
            with col_m3:
                st.metric("⚖️ F1-Score", "91.8%", help="Balance óptimo")
            with col_m4:
                st.metric("🔬 AUC-ROC", "0.999", help="Capacidad de discriminación")
            
            st.caption("**Normativa:** NTS 213-MINSA/DGIESP-2024 | **Modelo:** RandomForest | **Datos:** 895,982 registros | **Método:** OMS 2024")
        
        st.divider()
        
                # =====================================================
        # 7️⃣ ACCIONES FINALES: PDF + NOTIFICACIONES ⭐ NUEVO
        # =====================================================
        st.markdown("## 📄 Acciones Finales")
        
        col_pdf, col_notif = st.columns(2)
        
        # ========== BOTÓN PDF (SIN RECARGA) ==========
        with col_pdf:
            with st.spinner('📝 Generando reporte PDF...'):
                try:
                    from datetime import datetime
                    
                    pdf_bytes = generar_pdf_reporte(
                        datos_paciente, resultado, recomendaciones,
                        proyeccion_3m, proyeccion_6m, semaforo
                    )
                    
                    nombre_archivo = f"Reporte_Anemia_{nombre_paciente or 'Paciente'}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                    
                    # ← USAR download_button EN VEZ DE button
                    st.download_button(
                        label="📄 Descargar Reporte PDF",
                        data=pdf_bytes,
                        file_name=nombre_archivo,
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True,
                        help="Descarga el reporte completo en PDF"
                    )
                    
                    st.success("✅ Reporte PDF generado correctamente")
                    
                except Exception as e:
                    st.error(f"❌ Error generando PDF: {e}")
                    st.info("💡 Verifica que los archivos `utils/pdf_generator.py` y `utils/notificaciones.py` existan")
        
        # ========== SISTEMA DE NOTIFICACIONES ==========
        with col_notif:
            # Usar session_state para evitar recargas
            if 'notif_enviada' not in st.session_state:
                st.session_state.notif_enviada = False
            
            # Mostrar formulario de notificaciones
            if not st.session_state.notif_enviada:
                notif_button = st.button(
                    "📧 Enviar Recordatorios",
                    type="secondary",
                    use_container_width=True,
                    help="Envía recordatorios de controles CRED por email"
                )
                
                if notif_button:
                    if not email_notif or '@' not in email_notif:
                        st.warning("⚠️ Por favor ingresa un email válido en el formulario arriba")
                    else:
                        with st.spinner('📧 Enviando recordatorios...'):
                            try:
                                sistema_notif = get_sistema_notificaciones()
                                resultados = sistema_notif.programar_recordatorios(
                                    email_destino=email_notif,
                                    nombre_paciente=nombre_paciente or "Paciente",
                                    controles=proyeccion_3m['controles_recomendados'],
                                    enviar_inmediato=True
                                )
                                
                                st.session_state.notif_enviada = True
                                st.success(f"✅ Recordatorios enviados a {email_notif}")
                                
                                with st.expander("📋 Detalle de envíos", expanded=True):
                                    for tipo, estado in resultados.items():
                                        st.caption(f"• {tipo}: {estado}")
                                
                            except Exception as e:
                                st.error(f"❌ Error: {e}")
            else:
                # Ya se enviaron las notificaciones
                st.success(f"✅ Recordatorios ya enviados a {email_notif}")
                
                if st.button("🔄 Reenviar", type="secondary", use_container_width=True):
                    st.session_state.notif_enviada = False
                    st.rerun()
        
        # ========== INFORMACIÓN ADICIONAL ==========
        st.markdown("---")
        st.info("""
        **💡 Nota:** 
        - El PDF contiene todo el análisis, proyecciones y recomendaciones
        - Los recordatorios incluyen: Control CRED inmediato, seguimiento 1 mes y evaluación 3 meses
        - Para configurar email real, edita `utils/notificaciones.py` con credenciales SMTP
        """)


# ============================================================================
# PÁGINA: MENÚS PERSONALIZADOS
# ============================================================================

def pagina_menus():
    """Página de generación de menús personalizados"""
    st.title("🍽️ Generador de Menús Personalizados")
    st.markdown("Crea menús nutricionales optimizados según edad, presupuesto y región del niño.")
    
    st.markdown("---")
    
    # Formulario
    with st.form("formulario_menu"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👶 Datos del Niño")
            
            edad_meses = st.number_input(
                "Edad (meses)",
                min_value=6,
                max_value=59,
                value=18,
                help="Edad del niño entre 6 y 59 meses"
            )
            
            # Mostrar requerimiento automático
            req_hierro = menu_generator.calcular_requerimiento_hierro(edad_meses)
            st.info(f"📊 Requerimiento de hierro para {edad_meses} meses: **{req_hierro:.1f} mg/día**")
        
        with col2:
            st.subheader("⚙️ Configuración")
            
            presupuesto = st.number_input(
                "Presupuesto Diario (S/)",
                min_value=1.0,
                max_value=20.0,
                value=5.0,
                step=0.5,
                help="Presupuesto disponible en soles por día"
            )
            
            region = st.selectbox(
                "Región",
                ["Costa", "Sierra", "Selva"],
                help="Región del Perú para ajustar disponibilidad de alimentos"
            )
        
        # Opciones avanzadas
        with st.expander("🔧 Opciones Avanzadas"):
            col_adv1, col_adv2 = st.columns(2)
            
            with col_adv1:
                st.write("**Preferencias (opcional):**")
                pref_sangrecita = st.checkbox("Sangrecita", value=True)
                pref_higado = st.checkbox("Hígado", value=True)
                pref_lentejas = st.checkbox("Lentejas", value=True)
            
            with col_adv2:
                st.write("**Excluir Alimentos:**")
                excluir_visceras = st.checkbox("Excluir vísceras")
                excluir_menestras = st.checkbox("Excluir menestras")
        
        submitted = st.form_submit_button("🍳 Generar Menú", use_container_width=True)
    
    if submitted:
        # Validar presupuesto
        valido, msg = validate_presupuesto(presupuesto)
        if not valido:
            st.error(f"❌ {msg}")
            return
        
        # Preparar listas de preferencias/exclusiones
        preferencias = []
        if pref_sangrecita:
            preferencias.append("Sangrecita de pollo")
        if pref_higado:
            preferencias.append("Hígado de pollo")
        if pref_lentejas:
            preferencias.append("Lentejas")
        
        excluir = []
        if excluir_visceras:
            excluir.extend(["Sangrecita de pollo", "Hígado de pollo", "Bazo de res"])
        if excluir_menestras:
            excluir.extend(["Lentejas", "Garbanzos", "Frijoles"])
        
        # Generar menú
        with st.spinner("Generando menú optimizado..."):
            menu = menu_generator.generar_menu(
                edad_meses=edad_meses,
                presupuesto_diario=presupuesto,
                region=region,
                preferencias=preferencias if preferencias else None,
                excluir=excluir if excluir else None
            )
        
        st.markdown("---")
        st.subheader("📋 Menú Generado")
        
        # Métricas del menú
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        with col_m1:
            st.metric(
                "Hierro Total",
                f"{menu['hierro_aportado_mg']:.1f} mg",
                delta=f"{menu['cobertura_pct']:.0f}% de cobertura"
            )
        
        with col_m2:
            st.metric(
                "Costo Total",
                f"S/ {menu['costo_total']:.2f}",
                delta=f"S/ {presupuesto - menu['costo_total']:.2f} restante"
            )
        
        with col_m3:
            st.metric(
                "Alimentos",
                len(menu['menu_items']),
                delta="en el menú"
            )
        
        with col_m4:
            # Icono según evaluación
            if "EXCELENTE" in menu['evaluacion']:
                icon = "⭐⭐⭐"
            elif "MUY BUENO" in menu['evaluacion']:
                icon = "⭐⭐"
            elif "BUENO" in menu['evaluacion']:
                icon = "⭐"
            else:
                icon = "⚠️"
            
            st.metric("Evaluación", icon)
        
        # Evaluación del menú
        if menu['cumple_requerimiento']:
            st.success(f"✅ {menu['evaluacion']}")
        else:
            st.warning(f"⚠️ {menu['evaluacion']}")
        
        # Gráfico de contenido de hierro
        if menu['menu_items']:
            fig_menu = crear_grafico_menu(menu)
            st.plotly_chart(fig_menu, use_container_width=True)
        
        # Tabla detallada de alimentos
        st.subheader("🥘 Alimentos Incluidos")
        
        df_menu = pd.DataFrame(menu['menu_items'])
        df_menu['precio_formatted'] = df_menu['precio'].apply(lambda x: f"S/ {x:.2f}")
        df_menu['hierro_formatted'] = df_menu['hierro_mg'].apply(lambda x: f"{x:.1f} mg")
        
        st.dataframe(
            df_menu[['alimento', 'categoria', 'hierro_formatted', 'precio_formatted', 'porcion']],
            use_container_width=True,
            hide_index=True,
            column_config={
                'alimento': st.column_config.TextColumn('Alimento', width='medium'),
                'categoria': st.column_config.TextColumn('Categoría', width='small'),
                'hierro_formatted': st.column_config.TextColumn('Hierro', width='small'),
                'precio_formatted': st.column_config.TextColumn('Precio', width='small'),
                'porcion': st.column_config.TextColumn('Porción', width='small')
            }
        )
        
        # Preparaciones sugeridas
        if menu['preparaciones']:
            st.subheader("👨‍🍳 Preparaciones Sugeridas")
            for prep in menu['preparaciones']:
                st.info(prep)
        
        # Consejos adicionales
        st.subheader("💡 Consejos Nutricionales")
        
        col_tip1, col_tip2 = st.columns(2)
        
        with col_tip1:
            st.markdown("""
            **Para mejorar la absorción:**
            - ✅ Combinar con alimentos ricos en **vitamina C** (naranja, limón, tomate)
            - ✅ Evitar té o café durante las comidas
            - ✅ Cocinar en ollas de hierro cuando sea posible
            """)
        
        with col_tip2:
            st.markdown("""
            **Frecuencia recomendada:**
            - 🍖 Alimentos con hierro hemo: **3-4 veces/semana**
            - 🌱 Alimentos con hierro no-hemo: **diariamente**
            - 💊 Continuar con suplementación según indicación médica
            """)

# ============================================================================
# PÁGINA: DASHBOARD NACIONAL
# ============================================================================

def pagina_dashboard():
    """Dashboard con estadísticas nacionales y análisis de equidad"""
    st.title("📊 Dashboard Nacional de Anemia Infantil")
    st.markdown("Monitoreo de indicadores clave y análisis de equidad territorial.")
    
    st.markdown("---")
    
    # Cargar datos con caché
    with st.spinner("Cargando datos..."):
        df_brechas = cargar_datos_brechas()
        df_tendencias = cargar_datos_tendencias()
        reporte_equidad = cargar_reporte_equidad()
    
    # Validación mejorada
    if df_brechas is None or df_tendencias is None:
        st.warning("⚠️ Datos no disponibles. Genera primero los datos de ejemplo.")
        
        if st.button("🔄 Generar Datos de Ejemplo"):
            with st.spinner("Generando datos..."):
                import subprocess
                subprocess.run(["python", "scripts/generate_sample_data.py"])
                st.success("✅ Datos generados. Recarga la página.")
                st.rerun()
        return
    
    # Verificar que las columnas existen
    required_cols = ['departamento', 'prevalencia_pct', 'brecha_q4_q1_pp']
    missing_cols = [col for col in required_cols if col not in df_brechas.columns]
    
    if missing_cols:
        st.error(f"❌ Columnas faltantes en datos: {missing_cols}")
        st.info(f"Columnas disponibles: {list(df_brechas.columns)}")
        return
    
    # Resto del código sigue igual...

    
    # Indicadores nacionales
    st.subheader("🇵🇪 Indicadores Nacionales")
    
    col_ind1, col_ind2, col_ind3, col_ind4 = st.columns(4)
    
    with col_ind1:
        st.metric(
            "Prevalencia Promedio",
            f"{df_brechas['prevalencia_pct'].mean():.1f}%",
            delta=f"±{df_brechas['prevalencia_pct'].std():.1f}pp DE"
        )
    
    with col_ind2:
        st.metric(
            "Brecha Máxima",
            f"{df_brechas['brecha_q4_q1_pp'].max():.1f} pp",
            delta="Q4 vs Q1",
            delta_color="inverse"
        )
    
    with col_ind3:
        if reporte_equidad:
            st.metric(
                "Índice de Concentración",
                f"{reporte_equidad['indice_concentracion']:.4f}",
                delta="Desigualdad moderada"
            )
        else:
            st.metric("Índice de Concentración", "N/D")
    
    with col_ind4:
        dept_criticos = len(df_tendencias[df_tendencias['tendencia_pp_mes'] > 1.0])
        st.metric(
            "Departamentos Críticos",
            dept_criticos,
            delta="Tendencia >1.0 pp/mes",
            delta_color="inverse"
        )
    
    st.markdown("---")
    
    # Tabs para diferentes análisis
    tab1, tab2, tab3 = st.tabs(["🗺️ Prevalencia", "⚖️ Brechas de Equidad", "📈 Tendencias"])
    
    with tab1:
        st.subheader("Prevalencia por Departamento")
        
        # Gráfico de barras
        df_sorted = df_brechas.sort_values('prevalencia_pct', ascending=False)
        
        fig_prev = px.bar(
            df_sorted.head(15),
            x='departamento',
            y='prevalencia_pct',
            title="Top 15 Departamentos con Mayor Prevalencia",
            labels={'prevalencia_pct': 'Prevalencia (%)', 'departamento': 'Departamento'},
            color='prevalencia_pct',
            color_continuous_scale='Reds'
        )
        
        fig_prev.add_hline(
            y=df_brechas['prevalencia_pct'].mean(),
            line_dash="dash",
            annotation_text="Promedio Nacional",
            line_color="blue"
        )
        
        fig_prev.update_layout(showlegend=False, height=500)
        st.plotly_chart(fig_prev, use_container_width=True)
    
    with tab2:
        st.subheader("Análisis de Equidad")
        
        col_eq1, col_eq2 = st.columns(2)
        
        with col_eq1:
            # Scatter: Prevalencia vs Brecha
            fig_scatter = px.scatter(
                df_brechas,
                x='prevalencia_pct',
                y='brecha_q4_q1_pp',
                size='prevalencia_pct',
                color='indice_concentracion',
                hover_name='departamento',
                title="Prevalencia vs Brecha Interna (Q4-Q1)",
                labels={
                    'prevalencia_pct': 'Prevalencia (%)',
                    'brecha_q4_q1_pp': 'Brecha Q4-Q1 (pp)',
                    'indice_concentracion': 'Índice Concentración'
                },
                color_continuous_scale='RdYlGn_r'
            )
            
            fig_scatter.update_layout(height=400)
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        with col_eq2:
            # Top 10 mayores brechas
            st.write("**🔴 Top 10 Mayores Brechas Internas:**")
            
            df_top_brechas = df_brechas.nlargest(10, 'brecha_q4_q1_pp')[['departamento', 'brecha_q4_q1_pp', 'prevalencia_pct']]
            df_top_brechas.columns = ['Departamento', 'Brecha (pp)', 'Prevalencia (%)']
            
            st.dataframe(
                df_top_brechas,
                use_container_width=True,
                hide_index=True
            )
        
        # Descomposición Oaxaca-Blinder (si disponible)
        if reporte_equidad and 'descomposicion_oaxaca_blinder' in reporte_equidad:
            st.markdown("---")
            st.subheader("🔬 Descomposición de Oaxaca-Blinder")
            
            oaxaca = reporte_equidad['descomposicion_oaxaca_blinder']
            
            col_oax1, col_oax2, col_oax3 = st.columns(3)
            
            with col_oax1:
                st.metric("Brecha Total", f"{oaxaca['brecha_total_pp']:.2f} pp")
            
            with col_oax2:
                st.metric("Explicada", f"{oaxaca['explicada_pp']:.2f} pp")
            
            with col_oax3:
                st.metric(
                    "NO Explicada",
                    f"{oaxaca['no_explicada_pp']:.2f} pp",
                    delta=f"{oaxaca['no_explicada_pct']:.0f}%"
                )
            
            st.info("""
            ℹ️ **Interpretación:** El **132%** de la brecha NO está explicado por factores socioeconómicos. 
            Esto indica barreras sistémicas (acceso a servicios, discriminación, calidad de atención) 
            que requieren intervenciones más allá de mejoras económicas.
            """)
    
    with tab3:
        st.subheader("Tendencias Temporales")
        
        # Gráfico de tendencias
        df_tend_sorted = df_tendencias.sort_values('tendencia_pp_mes', ascending=False)
        
        fig_tend = px.bar(
            df_tend_sorted,
            x='departamento',
            y='tendencia_pp_mes',
            title="Tendencia Mensual por Departamento (pp/mes)",
            labels={'tendencia_pp_mes': 'Tendencia (pp/mes)', 'departamento': 'Departamento'},
            color='tendencia_pp_mes',
            color_continuous_scale='RdYlGn_r'
        )
        
        fig_tend.add_hline(y=0, line_dash="dash", line_color="black", annotation_text="Sin cambio")
        fig_tend.update_layout(height=500, showlegend=False)
        
        st.plotly_chart(fig_tend, use_container_width=True)
        
        # Departamentos críticos
        col_crit1, col_crit2 = st.columns(2)
        
        with col_crit1:
            st.write("**🚨 Departamentos con Mayor Crecimiento:**")
            df_creciente = df_tendencias.nlargest(5, 'tendencia_pp_mes')[['departamento', 'tendencia_pp_mes', 'prevalencia_actual_pct']]
            df_creciente.columns = ['Departamento', 'Tendencia (pp/mes)', 'Prevalencia Actual (%)']
            st.dataframe(df_creciente, use_container_width=True, hide_index=True)
        
        with col_crit2:
            st.write("**✅ Departamentos con Declive:**")
            df_decreciente = df_tendencias.nsmallest(5, 'tendencia_pp_mes')[['departamento', 'tendencia_pp_mes', 'prevalencia_actual_pct']]
            df_decreciente.columns = ['Departamento', 'Tendencia (pp/mes)', 'Prevalencia Actual (%)']
            st.dataframe(df_decreciente, use_container_width=True, hide_index=True)

# ============================================================================
# PÁGINA: PROYECCIONES
# ============================================================================

def pagina_proyecciones():
    """Página de proyecciones temporales y escenarios"""
    st.title("📈 Proyecciones y Escenarios de Intervención")
    st.markdown("Análisis de tendencias futuras y simulación de impacto de intervenciones.")
    
    st.markdown("---")
    
    # Cargar datos
    df_proyecciones = cargar_datos_proyecciones()
    reporte_temporal = cargar_reporte_temporal()
    
    if df_proyecciones is None or reporte_temporal is None:
        st.warning("⚠️ Datos no disponibles. Ejecuta primero el Notebook 6.")
        return
    
    # Métricas de serie temporal
    st.subheader("📊 Serie Temporal Nacional")
    
    col_st1, col_st2, col_st3, col_st4 = st.columns(4)
    
    stats = reporte_temporal['estadisticas_serie']
    
    with col_st1:
        st.metric(
            "Prevalencia Promedio",
            f"{stats['prevalencia_promedio_pct']:.1f}%",
            delta=f"±{stats['desviacion_estandar_pp']:.1f}pp DE"
        )
    
    with col_st2:
        st.metric(
            "Variación Total",
            f"+{stats['variacion_absoluta_pp']:.1f} pp",
            delta=f"+{stats['variacion_relativa_pct']:.0f}%"
        )
    
    with col_st3:
        tendencia = reporte_temporal['tendencia_nacional']
        st.metric(
            "Tendencia Mensual",
            f"+{tendencia['pendiente_pp_mes']:.2f} pp/mes",
            delta=f"R²={tendencia['r_cuadrado']:.2f}"
        )
    
    with col_st4:
        st.metric(
            "Rango Observado",
            f"{stats['prevalencia_minima_pct']:.1f}% - {stats['prevalencia_maxima_pct']:.1f}%",
            delta=f"{stats['prevalencia_maxima_pct'] - stats['prevalencia_minima_pct']:.1f}pp"
        )
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["🔮 Proyecciones", "🎯 Escenarios", "🚨 Alertas"])
    
    with tab1:
        st.subheader("Proyecciones a 3 Meses (Ensamble de Modelos)")
        
        # Gráfico de proyecciones
        fig_proy = go.Figure()
        
        # Líneas de cada modelo
        fig_proy.add_trace(go.Scatter(
            x=df_proyecciones['periodo'],
            y=df_proyecciones['SES'],
            name='SES (Simple)',
            line=dict(dash='dot'),
            mode='lines+markers'
        ))
        
        fig_proy.add_trace(go.Scatter(
            x=df_proyecciones['periodo'],
            y=df_proyecciones['Holt_Winters'],
            name='Holt-Winters',
            line=dict(dash='dash'),
            mode='lines+markers'
        ))
        
        fig_proy.add_trace(go.Scatter(
            x=df_proyecciones['periodo'],
            y=df_proyecciones['Lineal'],
            name='Regresión Lineal',
            line=dict(dash='dashdot'),
            mode='lines+markers'
        ))
        
        fig_proy.add_trace(go.Scatter(
            x=df_proyecciones['periodo'],
            y=df_proyecciones['Ensamble'],
            name='Ensamble (Recomendado)',
            line=dict(width=3),
            mode='lines+markers',
            marker=dict(size=10)
        ))
        
        fig_proy.update_layout(
            title="Proyecciones de Prevalencia - Múltiples Modelos",
            xaxis_title="Periodo",
            yaxis_title="Prevalencia (%)",
            height=500,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_proy, use_container_width=True)
        
        # Tabla de proyecciones
        st.write("**Valores Proyectados:**")
        st.dataframe(df_proyecciones, use_container_width=True, hide_index=True)
    
    with tab2:
        st.subheader("Simulación de Escenarios de Intervención")
        
        st.info("""
        📌 **Escenarios evaluados:**
        - **Sin intervención:** Continúa tendencia actual
        - **Intervención Baja:** Suplementación básica (-0.3 pp/mes)
        - **Intervención Media:** Suplementación + consejería (-0.6 pp/mes)
        - **Intervención Alta:** Enfoque multisectorial (-1.0 pp/mes)
        """)
        
        # Simulador interactivo
        st.write("### 🎛️ Simulador de Escenarios")
        
        col_sim1, col_sim2 = st.columns(2)
        
        with col_sim1:
            prev_actual = st.number_input(
                "Prevalencia Actual (%)",
                min_value=5.0,
                max_value=30.0,
                value=16.3,
                step=0.1
            )
            
            tendencia_base = st.number_input(
                "Tendencia Actual (pp/mes)",
                min_value=-2.0,
                max_value=3.0,
                value=2.2,
                step=0.1
            )
        
        with col_sim2:
            impacto_intervencion = st.slider(
                "Impacto de Intervención (pp/mes)",
                min_value=-2.0,
                max_value=0.0,
                value=-1.0,
                step=0.1,
                help="Reducción esperada por mes (negativo = mejora)"
            )
            
            meses_proyectar = st.slider(
                "Meses a Proyectar",
                min_value=3,
                max_value=12,
                value=6
            )
        
        # Calcular proyección
        meses = list(range(meses_proyectar + 1))
        
        sin_interv = [prev_actual + (tendencia_base * m) for m in meses]
        con_interv = [prev_actual + ((tendencia_base + impacto_intervencion) * m) for m in meses]
        
        # Gráfico comparativo
        fig_sim = go.Figure()
        
        fig_sim.add_trace(go.Scatter(
            x=meses,
            y=sin_interv,
            name='Sin Intervención',
            line=dict(color='red', width=3),
            mode='lines+markers'
        ))
        
        fig_sim.add_trace(go.Scatter(
            x=meses,
            y=con_interv,
            name='Con Intervención',
            line=dict(color='green', width=3),
            mode='lines+markers'
        ))
        
        fig_sim.add_hline(
            y=8.0,
            line_dash="dash",
            line_color="blue",
            annotation_text="Meta Nacional (<8%)"
        )
        
        fig_sim.update_layout(
            title="Comparación de Escenarios",
            xaxis_title="Meses",
            yaxis_title="Prevalencia (%)",
            height=400
        )
        
        st.plotly_chart(fig_sim, use_container_width=True)
        
        # Resultados
        col_res1, col_res2, col_res3 = st.columns(3)
        
        with col_res1:
            st.metric(
                "Sin Intervención",
                f"{sin_interv[-1]:.1f}%",
                delta=f"+{sin_interv[-1] - prev_actual:.1f}pp"
            )
        
        with col_res2:
            st.metric(
                "Con Intervención",
                f"{con_interv[-1]:.1f}%",
                delta=f"{con_interv[-1] - prev_actual:+.1f}pp"
            )
        
        with col_res3:
            diferencia = sin_interv[-1] - con_interv[-1]
            st.metric(
                "Impacto",
                f"-{diferencia:.1f} pp",
                delta="vs sin intervención"
            )
    
    with tab3:
        st.subheader("🚨 Alertas del Sistema")
        
        if 'alertas' in reporte_temporal:
            for alerta in reporte_temporal['alertas']:
                tipo = alerta['tipo']
                mensaje = alerta['mensaje']
                
                if tipo == "CRÍTICO":
                    st.error(f"🚨 **{tipo}:** {mensaje}")
                elif tipo == "ADVERTENCIA":
                    st.warning(f"⚡ **{tipo}:** {mensaje}")
                else:
                    st.info(f"ℹ️ **{tipo}:** {mensaje}")
        else:
            st.success("✅ No hay alertas críticas en este momento.")

# ============================================================================
# PÁGINA: MAPA TERRITORIAL
# ============================================================================
def pagina_mapa_territorial():
    """
    Mapa de riesgo geoespacial - Anemia Infantil Perú
    Con mapa geográfico y proyecciones temporales
    """
    import plotly.express as px
    import plotly.graph_objects as go
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    import json
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem;'>
        <h1 style='color: white; margin: 0;'>🗺️ Mapa de Riesgo Geoespacial</h1>
        <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;'>
            Anemia Infantil en Perú - 895,982 registros SIEN Nacional
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # === CARGAR DATOS ===
    @st.cache_data
    def cargar_y_procesar_datos():
        df = pd.read_csv('data/processed/sien_nacional_procesado.csv')
        
        df_dept = df.groupby('DepartamentoREN').agg({
            'tiene_anemia': ['sum', 'count', 'mean'],
            'Hemoglobina_OMS2024': 'mean',
            'AlturaREN': 'mean',
            'EdadMeses': 'mean',
            'area_rural': 'mean',
            'suplementacion_bin': 'mean',
            'cred_bin': 'mean'
        }).reset_index()
        
        df_dept.columns = [
            'departamento', 'casos_anemia', 'total_ninos', 'prevalencia',
            'hb_promedio', 'altitud_promedio', 'edad_promedio',
            'prop_rural', 'prop_suplemento', 'prop_cred'
        ]
        
        df_dept['prevalencia_pct'] = df_dept['prevalencia'] * 100
        
        def categorizar_riesgo(prev):
            if prev >= 60: return 'Muy Alto'
            elif prev >= 45: return 'Alto'
            elif prev >= 30: return 'Medio'
            else: return 'Bajo'
        
        df_dept['riesgo'] = df_dept['prevalencia_pct'].apply(categorizar_riesgo)
        df_dept['departamento'] = df_dept['departamento'].str.upper().str.strip()
        
        return df_dept
    
    with st.spinner('📊 Procesando 895K registros...'):
        df_prev = cargar_y_procesar_datos()
    
    st.success(f"✅ {len(df_prev)} departamentos | {df_prev['total_ninos'].sum():,} niños evaluados")
    
    # === CREAR TABS AQUÍ (IMPORTANTE) ===
    tab1, tab2, tab3 = st.tabs(["🗺️ Mapa Geográfico", "📊 Análisis Departamental", "📈 Proyecciones Temporales"])
    
    # ==========================================
    # TAB 1: MAPA GEOGRÁFICO
    # ==========================================
    with tab1:
        st.markdown("### 🌎 Mapa Coroplético del Perú")
        
        # Mapeo de nombres (GEOJSON → Dataset)
        nombre_mapping = {
            'LIMA': 'LIMA',
            'CUSCO': 'CUSCO',
            'AREQUIPA': 'AREQUIPA',
            'LA LIBERTAD': 'LA LIBERTAD',
            'PIURA': 'PIURA',
            'JUNIN': 'JUNIN',
            'CAJAMARCA': 'CAJAMARCA',
            'PUNO': 'PUNO',
            'LAMBAYEQUE': 'LAMBAYEQUE',
            'ANCASH': 'ANCASH',
            'LORETO': 'LORETO',
            'HUANUCO': 'HUANUCO',
            'AYACUCHO': 'AYACUCHO',
            'SAN MARTIN': 'SAN MARTIN',
            'ICA': 'ICA',
            'UCAYALI': 'UCAYALI',
            'APURIMAC': 'APURIMAC',
            'HUANCAVELICA': 'HUANCAVELICA',
            'AMAZONAS': 'AMAZONAS',
            'TACNA': 'TACNA',
            'PASCO': 'PASCO',
            'TUMBES': 'TUMBES',
            'MOQUEGUA': 'MOQUEGUA',
            'MADRE DE DIOS': 'MADRE DE DIOS',
            'CALLAO': 'CALLAO'
        }
        
        # Crear dataset para el mapa
        df_mapa = df_prev.copy()
        df_mapa['DEPARTAMENTO'] = df_mapa['departamento'].map(nombre_mapping)
        
        # Crear mapa con Plotly (usando geojson local)
        try:
            # Cargar GeoJSON local
            geojson_path = 'data/geojson/peru_departamentos_oficial.geojson'
            
            with st.spinner('Cargando mapa del Perú...'):
                with open(geojson_path, 'r', encoding='utf-8') as f:
                    peru_geojson = json.load(f)
            
            # Crear mapa coroplético
            fig_mapa = px.choropleth(
                df_mapa,
                geojson=peru_geojson,
                locations='DEPARTAMENTO',
                featureidkey='properties.NOMBDEP',
                color='prevalencia_pct',
                color_continuous_scale=[
                    [0, '#2ecc71'],
                    [0.3, '#f1c40f'],
                    [0.6, '#e67e22'],
                    [1, '#e74c3c']
                ],
                labels={'prevalencia_pct': 'Prevalencia (%)'},
                hover_data={
                    'DEPARTAMENTO': True,
                    'prevalencia_pct': ':.1f',
                    'casos_anemia': ':,.0f',
                    'total_ninos': ':,.0f',
                    'riesgo': True
                }
            )
            
            fig_mapa.update_geos(
                fitbounds="locations",
                visible=False,
                showcountries=False,
                showcoastlines=False,
                showland=False,
                showlakes=False
            )
            
            fig_mapa.update_layout(
                height=700,
                margin={"r":0,"t":40,"l":0,"b":0},
                title="Prevalencia de Anemia Infantil por Departamento",
                coloraxis_colorbar=dict(
                    title="Prevalencia (%)",
                    ticksuffix="%",
                    len=0.7
                )
            )
            
            st.plotly_chart(fig_mapa, use_container_width=True)
            
        except FileNotFoundError:
            st.warning(f"⚠️ No se encontró el archivo GeoJSON en: {geojson_path}")
            st.info("📊 Mostrando gráfico de barras alternativo:")
            
            # Fallback: Mapa de barras horizontal
            df_sorted = df_prev.sort_values('prevalencia_pct', ascending=True)
            
            fig_fallback = go.Figure(go.Bar(
                x=df_sorted['prevalencia_pct'],
                y=df_sorted['departamento'],
                orientation='h',
                marker=dict(
                    color=df_sorted['prevalencia_pct'],
                    colorscale='RdYlGn_r',
                    showscale=True,
                    colorbar=dict(title="Prevalencia (%)")
                ),
                text=df_sorted['prevalencia_pct'].apply(lambda x: f'{x:.1f}%'),
                textposition='auto'
            ))
            
            fig_fallback.update_layout(
                height=800,
                title="Prevalencia de Anemia por Departamento",
                xaxis_title="Prevalencia (%)",
                yaxis_title="",
                showlegend=False
            )
            
            st.plotly_chart(fig_fallback, use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Error al cargar el mapa: {str(e)}")
        
        # Estadísticas del mapa
        col_m1, col_m2, col_m3 = st.columns(3)
        
        with col_m1:
            max_prev = df_prev.loc[df_prev['prevalencia_pct'].idxmax()]
            st.metric(
                "🔴 Mayor Prevalencia",
                f"{max_prev['departamento']}",
                f"{max_prev['prevalencia_pct']:.1f}%"
            )
        
        with col_m2:
            min_prev = df_prev.loc[df_prev['prevalencia_pct'].idxmin()]
            st.metric(
                "🟢 Menor Prevalencia",
                f"{min_prev['departamento']}",
                f"{min_prev['prevalencia_pct']:.1f}%"
            )
        
        with col_m3:
            promedio = df_prev['prevalencia_pct'].mean()
            st.metric(
                "📊 Promedio Nacional",
                f"{promedio:.1f}%",
                delta=f"{promedio - 20:.1f}% vs Meta OMS",
                delta_color="inverse"
            )
    
    # ==========================================
    # TAB 2: ANÁLISIS DEPARTAMENTAL
    # ==========================================
    with tab2:
        st.markdown("### 📊 Análisis Departamental Detallado")
        
        # === FILTROS ===
        col_f1, col_f2 = st.columns(2)
        
        with col_f1:
            filtro_riesgo = st.multiselect(
                "Filtrar por Riesgo",
                options=['Bajo', 'Medio', 'Alto', 'Muy Alto'],
                default=['Bajo', 'Medio', 'Alto', 'Muy Alto']
            )
        
        with col_f2:
            slider_prev = st.slider(
                "Prevalencia mínima (%)",
                min_value=0.0,
                max_value=float(df_prev['prevalencia_pct'].max()),
                value=0.0,
                step=1.0
            )
        
        # Aplicar filtros
        df_filtered = df_prev[
            (df_prev['riesgo'].isin(filtro_riesgo)) &
            (df_prev['prevalencia_pct'] >= slider_prev)
        ].copy()
        
        st.info(f"📌 Mostrando {len(df_filtered)} de {len(df_prev)} departamentos")
        
        # === GRÁFICO PRINCIPAL ===
        st.markdown("#### 📊 Prevalencia de Anemia por Departamento")
        
        fig = px.bar(
            df_filtered,
            x='departamento',
            y='prevalencia_pct',
            color='prevalencia_pct',
            color_continuous_scale=[
                [0, '#2ecc71'], [0.3, '#f1c40f'],
                [0.6, '#e67e22'], [1, '#e74c3c']
            ],
            hover_data={
                'departamento': True,
                'prevalencia_pct': ':.1f',
                'casos_anemia': ':,.0f',
                'total_ninos': ':,.0f',
                'hb_promedio': ':.2f',
                'riesgo': True
            },
            labels={
                'prevalencia_pct': 'Prevalencia (%)',
                'casos_anemia': 'Casos',
                'total_ninos': 'Evaluados',
                'hb_promedio': 'Hemoglobina (g/dL)'
            }
        )
        
        fig.update_layout(
            height=600,
            xaxis_tickangle=-45,
            xaxis_title="Departamento",
            yaxis_title="Prevalencia (%)",
            showlegend=False,
            coloraxis_colorbar=dict(title="Prevalencia<br>(%)", ticksuffix="%")
        )
        
        fig.add_hline(y=40, line_dash="dash", line_color="red",
                      annotation_text="Problema salud pública (OMS)",
                      annotation_position="right")
        fig.add_hline(y=20, line_dash="dash", line_color="green",
                      annotation_text="Meta OMS", annotation_position="right")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # === ANÁLISIS ===
        st.divider()
        st.markdown("#### 🔍 Análisis de Factores")
        
        col_a1, col_a2 = st.columns(2)
        
        with col_a1:
            fig_alt = px.scatter(
                df_filtered,
                x='altitud_promedio',
                y='prevalencia_pct',
                size='total_ninos',
                color='riesgo',
                hover_name='departamento',
                labels={'altitud_promedio': 'Altitud (msnm)',
                       'prevalencia_pct': 'Prevalencia (%)'},
                title="Altitud vs Prevalencia",
                color_discrete_map={
                    'Bajo': '#2ecc71', 'Medio': '#f1c40f',
                    'Alto': '#e67e22', 'Muy Alto': '#e74c3c'
                }
            )
            fig_alt.update_layout(height=450)
            st.plotly_chart(fig_alt, use_container_width=True)
        
        with col_a2:
            top5 = df_prev.nlargest(5, 'prevalencia_pct')
            
            fig_top = go.Figure(go.Bar(
                x=top5['prevalencia_pct'],
                y=top5['departamento'],
                orientation='h',
                marker=dict(color=top5['prevalencia_pct'],
                           colorscale='Reds', showscale=False),
                text=top5['prevalencia_pct'].apply(lambda x: f'{x:.1f}%'),
                textposition='auto'
            ))
            
            fig_top.update_layout(
                title="Top 5 Departamentos",
                xaxis_title="Prevalencia (%)",
                height=450
            )
            st.plotly_chart(fig_top, use_container_width=True)
    
    # ==========================================
    # TAB 3: PROYECCIONES TEMPORALES
    # ==========================================
    with tab3:
        st.markdown("### 📈 Proyecciones de Prevalencia")
        
        st.info("""
        **Metodología de proyección:**
        - Tendencia histórica basada en reducción anual del 2-5%
        - Factores: Programas de intervención, suplementación, clima
        - Escenarios: Optimista, Base, Pesimista
        """)
        
        # Seleccionar departamento
        dept_seleccionado = st.selectbox(
            "Selecciona un departamento:",
            options=sorted(df_prev['departamento'].unique()),
            index=0
        )
        
        # Obtener datos actuales
        datos_actuales = df_prev[df_prev['departamento'] == dept_seleccionado].iloc[0]
        prev_actual = datos_actuales['prevalencia_pct']
        
        # Crear proyecciones (3, 6, 12 meses)
        meses = np.array([0, 3, 6, 12])
        
        # Escenarios
        reduccion_optimista = 0.08  # 8% reducción anual
        reduccion_base = 0.05       # 5% reducción anual
        reduccion_pesimista = 0.02  # 2% reducción anual
        
        # Calcular proyecciones
        prev_optimista = prev_actual * (1 - reduccion_optimista * meses / 12)
        prev_base = prev_actual * (1 - reduccion_base * meses / 12)
        prev_pesimista = prev_actual * (1 - reduccion_pesimista * meses / 12)
        
        # Crear DataFrame
        df_proyeccion = pd.DataFrame({
            'Meses': meses,
            'Optimista': prev_optimista,
            'Base': prev_base,
            'Pesimista': prev_pesimista,
            'Actual': prev_actual
        })
        
        # Gráfico de proyecciones
        fig_proy = go.Figure()
        
        fig_proy.add_trace(go.Scatter(
            x=df_proyeccion['Meses'],
            y=df_proyeccion['Optimista'],
            mode='lines+markers',
            name='Escenario Optimista',
            line=dict(color='#2ecc71', width=3),
            marker=dict(size=10)
        ))
        
        fig_proy.add_trace(go.Scatter(
            x=df_proyeccion['Meses'],
            y=df_proyeccion['Base'],
            mode='lines+markers',
            name='Escenario Base',
            line=dict(color='#f39c12', width=3),
            marker=dict(size=10)
        ))
        
        fig_proy.add_trace(go.Scatter(
            x=df_proyeccion['Meses'],
            y=df_proyeccion['Pesimista'],
            mode='lines+markers',
            name='Escenario Pesimista',
            line=dict(color='#e74c3c', width=3),
            marker=dict(size=10)
        ))
        
        # Línea de meta OMS
        fig_proy.add_hline(
            y=20,
            line_dash="dash",
            line_color="green",
            annotation_text="Meta OMS (20%)",
            annotation_position="right"
        )
        
        fig_proy.update_layout(
            title=f"Proyección de Prevalencia - {dept_seleccionado}",
            xaxis_title="Meses desde ahora",
            yaxis_title="Prevalencia (%)",
            height=500,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_proy, use_container_width=True)
        
        # Comparación nacional
        st.divider()
        st.markdown("#### 🌍 Proyección Nacional (Top 15 Departamentos)")
        
        # Calcular proyección nacional a 6 meses
        df_prev_copy = df_prev.copy()
        df_prev_copy['proyeccion_6m_base'] = df_prev_copy['prevalencia_pct'] * (1 - 0.05 * 6 / 12)
        
        # Gráfico comparativo
        fig_comp = go.Figure()
        
        df_sorted = df_prev_copy.sort_values('prevalencia_pct', ascending=False).head(15)
        
        fig_comp.add_trace(go.Bar(
            name='Actual (2024)',
            x=df_sorted['departamento'],
            y=df_sorted['prevalencia_pct'],
            marker_color='#3498db'
        ))
        
        fig_comp.add_trace(go.Bar(
            name='Proyección 6 meses',
            x=df_sorted['departamento'],
            y=df_sorted['proyeccion_6m_base'],
            marker_color='#2ecc71'
        ))
        
        fig_comp.update_layout(
            barmode='group',
            title="Top 15 Departamentos - Proyección a 6 Meses",
            xaxis_tickangle=-45,
            height=500,
            yaxis_title="Prevalencia (%)"
        )
        
        st.plotly_chart(fig_comp, use_container_width=True)

# ============================================================================
# FLUJO PRINCIPAL DE LA APLICACIÓN
# ============================================================================

def main():
    """Función principal de la aplicación"""
    
    # Si no está autenticado, mostrar login
    if not st.session_state.authenticated:
        pagina_login()
        return
    
    # Mostrar sidebar y obtener página seleccionada
    pagina_seleccionada = mostrar_sidebar()
    
    # Enrutar a la página correspondiente
    if pagina_seleccionada == "🏠 Inicio":
        pagina_inicio()
    elif pagina_seleccionada == "🔍 Diagnóstico Individual":
        pagina_diagnostico()
    elif pagina_seleccionada == "🍽️ Menús Personalizados":
        pagina_menus()
    elif pagina_seleccionada == "📊 Dashboard Nacional":
        pagina_dashboard()
    elif pagina_seleccionada == "📈 Proyecciones":
        pagina_proyecciones()
    elif pagina_seleccionada == "🗺️ Mapa Territorial":
        pagina_mapa_territorial()

# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

st.markdown("""
<style>
    /* Desactivar animaciones pesadas */
    * {
        animation-duration: 0s !important;
        transition-duration: 0s !important;
    }
    
    /* Mejorar rendimiento de scrolling */
    .main {
        overflow-y: auto;
        -webkit-overflow-scrolling: touch;
    }
    
    /* Optimizar renderizado de gráficos */
    .js-plotly-plot {
        will-change: auto;
    }
</style>
""", unsafe_allow_html=True)



if __name__ == "__main__":
    main()
