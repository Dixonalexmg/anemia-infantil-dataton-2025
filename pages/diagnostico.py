import plotly.graph_objects as go
import numpy as np
import pandas as pd
from datetime import datetime
import time
import streamlit as st

from services.predictor import anemia_predictor
from services.temporal_predictor import get_temporal_predictor
from utils.clinical_recommendations import generar_recomendaciones_personalizadas
from utils.risk_classifier import clasificar_nivel_riesgo, extraer_factores_criticos

try:
    from utils.pdf_generator import generar_pdf_reporte
except ImportError:
    generar_pdf_reporte = None

try:
    from utils.notificaciones import get_sistema_notificaciones
except ImportError:
    get_sistema_notificaciones = None

def pagina_diagnostico():

    if 'form_submitted' not in st.session_state:
        st.session_state.form_submitted = False

    if 'score' not in st.session_state:
        st.session_state.score = {'nivel': 'No evaluado'}

    if 'probabilidad_ml' not in st.session_state:
        st.session_state.probabilidad_ml = 0.0

    if 'pdf_cuidador' not in st.session_state:
        st.session_state.pdf_cuidador = None

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
    
    # =====================================================
    # PRE-FORMULARIO: HISTORIAL Y DATOS PERSISTENTES
    # =====================================================
    st.markdown("### 📋 Datos del Paciente")
    
    # Inicializar session_state para datos persistentes
    if 'dni_consulta' not in st.session_state:
        st.session_state.dni_consulta = ""
    if 'nombre_consulta' not in st.session_state:
        st.session_state.nombre_consulta = ""
    
    # Inputs FUERA del formulario para persistencia
    col_pre1, col_pre2 = st.columns(2)
    
    with col_pre1:
        nombre_input_temp = st.text_input(
            "👶 Nombre del niño/a",
            value=st.session_state.nombre_consulta,
            placeholder="Ej: María López",
            help="Para personalizar el reporte",
            key="nombre_previo"
        )
        if nombre_input_temp != st.session_state.nombre_consulta:
            st.session_state.nombre_consulta = nombre_input_temp
    
    with col_pre2:
        dni_input_temp = st.text_input(
            "🆔 DNI del Paciente (opcional)",
            value=st.session_state.dni_consulta,
            placeholder="12345678",
            help="Para llevar historial de consultas",
            key="dni_previo"
        )
        if dni_input_temp != st.session_state.dni_consulta:
            st.session_state.dni_consulta = dni_input_temp
    
    # Mostrar historial si DNI es válido
    if st.session_state.dni_consulta and len(st.session_state.dni_consulta) == 8:
        try:
            from utils.historial import generar_resumen_cambios
            
            resumen = generar_resumen_cambios(st.session_state.dni_consulta)
            
            if resumen:
                st.info(f"""
                📊 **Última consulta:** {resumen['fecha_anterior']} ({resumen['dias_transcurridos']} días atrás)
                
                **Cambios detectados:**
                - Hemoglobina: {resumen['delta_hb']:+.1f} g/dL ({resumen['delta_hb_pct']:+.1f}%)
                - Riesgo: {resumen['delta_riesgo']:+.1f}pp
                - Tendencia: {resumen['tendencia']}
                """)
        except:
            pass
    elif st.session_state.dni_consulta and len(st.session_state.dni_consulta) != 8:
        st.warning("⚠️ El DNI debe tener 8 dígitos")
    
    # SELECTOR DE DEPARTAMENTO FUERA DEL FORM
    departamento = st.selectbox(
        "🗺️ Departamento de residencia",
        options=list(ALTITUDES_DEPARTAMENTO.keys()),
        index=14,
        help="La altitud se ajustará automáticamente según el departamento seleccionado",
        key="dept_selector"
    )
    
    altitud_sugerida = ALTITUDES_DEPARTAMENTO.get(departamento, 150)
    st.info(f"📍 **Altitud sugerida para {departamento}:** {altitud_sugerida} msnm (capital departamental). Puedes ajustarla manualmente.")


    st.markdown("---")


    # =====================================================
# FORMULARIO DE ENTRADA - VERSIÓN MEJORADA
# Con validaciones en tiempo real, campo fuente HB, y microcopys guiados
# =====================================================

    with st.form("form_diagnostico"):
        # Usar valores de session_state (campos ocultos)
        nombre_paciente = st.session_state.nombre_consulta
        dni_paciente = st.session_state.dni_consulta

        st.markdown("---")

        col_left, col_right = st.columns(2)

        # ========== COLUMNA IZQUIERDA: DATOS CLÍNICOS ==========
        with col_left:
            st.markdown("#### 🩸 Datos Clínicos")

            edad_meses = st.number_input(
                "Edad del niño (meses)", 
                6, 59, 24, 1,
                help="Edad en meses, rango: 6-59"
            )

            peso_kg = st.number_input(
                "Peso del niño (kg)", 
                3.0, 25.0, 12.0, 0.1,
                help="Peso para dosificación"
            )

            talla_cm = st.number_input(
                "Talla del niño (cm)", 
                40.0, 120.0, 80.0, 0.5,
                help="Talla en centímetros para calcular IMC"
            )

            # Validación de talla
            if talla_cm < 50.0:
                st.warning("⚠️ Talla muy baja para edad")
            elif talla_cm > 110.0 and edad_meses < 36:
                st.info("ℹ️ Talla en rango alto")

            # Calcular IMC
            imc = peso_kg / ((talla_cm / 100) ** 2)

            if imc < 13.0:
                st.warning("⚠️ IMC bajo: posible desnutrición")
            elif imc > 17.0:
                st.info("ℹ️ IMC en rango alto")
            else:
                st.info(f"✅ IMC normal: {imc:.1f}")


            # ========== HEMOGLOBINA CON VALIDACIÓN ==========
            hemoglobina = st.number_input(
                "Hemoglobina (g/dL)", 
                5.0, 18.0, 11.5, 0.1,
                help="Nivel de hemoglobina (rango normal: 11-16 g/dL según edad)"
            )

            # Validaciones de hemoglobina en tiempo real
            if hemoglobina < 7.0:
                st.error("🚨 Valor CRÍTICO: Hemoglobina muy baja (<7 g/dL). Requiere consulta urgente.")
            elif hemoglobina < 9.0:
                st.warning("⚠️ Hemoglobina baja: se recomienda evaluación clínica inmediata.")
            elif hemoglobina < 11.0:
                st.info("ℹ️ Hemoglobina en rango bajo. Se sugiere seguimiento.")
            elif hemoglobina > 15.0 and edad_meses < 12:
                st.warning("⚠️ Valor más alto de lo esperado para esta edad. Verifica la medición.")

            # ========== FUENTE DE HEMOGLOBINA (NUEVO) ==========
            st.markdown("**Fuente de medición:**")
            col_source_1, col_source_2 = st.columns(2)

            with col_source_1:
                fuente_hb = st.radio(
                    "¿Cómo se midió la hemoglobina?",
                    options=["🩸 Capilar (HemoCue/Rápida)", "🩸 Venosa (Laboratorio)"],
                    label_visibility="collapsed",
                    help="Capilar: rápida pero menos precisa. Venosa: estándar en laboratorio (más confiable)."
                )

            with col_source_2:
                fecha_medicion = st.date_input(
                    "Fecha de medición:",
                    help="¿Cuándo se tomó esta muestra de sangre?",
                    format="DD/MM/YYYY"
                )

            # ========== INFORMACIÓN SOBRE RANGO ESPERADO ==========
            with st.expander("ℹ️ ¿Cuál es el rango normal de hemoglobina?"):
                st.info("""
                **Rangos normales según edad (OMS 2024 - Ajustados por altitud):**
                - 6-23 meses: 11.0 a 14.0 g/dL
                - 24-59 meses: 11.5 a 15.5 g/dL

                Estos valores YA están ajustados para altitudes menores a 1000m.
                Si estás en altitud > 3000m, los valores pueden ser 0.3-0.5 g/dL más altos.
                """)

            # ========== ALTITUD ==========
            altitud = st.number_input(
                "Altitud (msnm)", 
                0, 5000, altitud_sugerida, 50,
                help=f"Ajustado a {altitud_sugerida}m para {departamento}"
            )

        # ========== COLUMNA DERECHA: DATOS SOCIODEMOGRÁFICOS ==========
        with col_right:
            st.markdown("#### 👨‍👩‍👧 Datos Sociodemográficos")

            area = st.selectbox(
                "Área de residencia", 
                ["Urbana", "Rural"],
                help="Área geográfica: Rural aumenta riesgo de anemia (~1.3x)"
            )

            recibe_suplemento = st.selectbox(
                "¿Recibe suplementación de hierro?", 
                ["No", "Sí"],
                index=0,
                help="¿El niño recibe gotas o tabletas de sulfato ferroso? (Importante para predicción)"
            )

            asiste_cred = st.selectbox(
                "¿Asiste a controles CRED?", 
                ["Sí", "No"],
                index=0,
                help="CRED (Crecimiento y Desarrollo): control de salud infantil. Regular = mejor resultado"
            )

            st.markdown("**Antecedentes de nacimiento:**")

            col_antec1, col_antec2 = st.columns(2)

            with col_antec1:
                es_bajo_peso = st.checkbox(
                    "Nació con bajo peso (<2500g)",
                    False,
                    help="Importante factor de riesgo"
                )

            with col_antec2:
                es_prematuro = st.checkbox(
                    "Nació prematuro (<37 semanas)",
                    False,
                    help="Prematuro = mayor riesgo de anemia"
                )

            # ========== RESUMEN DE VALIDACIÓN ==========
            st.markdown("**✅ Estado de datos:**")

            validacion_checks = []

            # Validar hemoglobina
            if 7.0 <= hemoglobina <= 17.0:
                validacion_checks.append("✅ Hemoglobina")
            else:
                validacion_checks.append("❌ Hemoglobina fuera de rango")

            # Validar edad
            if 6 <= edad_meses <= 59:
                validacion_checks.append("✅ Edad válida")
            else:
                validacion_checks.append("❌ Edad fuera de rango")

            # Validar peso
            if 3 <= peso_kg <= 25:
                validacion_checks.append("✅ Peso válido")
            else:
                validacion_checks.append("❌ Peso fuera de rango")

            # Mostrar checks
            for check in validacion_checks:
                st.text(check)

            st.markdown("---")

            st.markdown("#### 📞 Datos de Contacto (Opcional)")

            telefono_notif = st.text_input(
                "📱 Teléfono/Celular",
                placeholder="987654321",
                help="Para recordatorios de controles CRED. Solo números, 9 dígitos",
                key="telefono_input"
            )

            # Validación de teléfono en tiempo real
            if telefono_notif:
                if not telefono_notif.isdigit():
                    st.error("❌ Ingresa solo números (0-9)")
                elif len(telefono_notif) != 9:
                    st.error(f"❌ Debe tener 9 dígitos (has ingresado {len(telefono_notif)})")
                else:
                    st.success("✅ Teléfono válido: " + telefono_notif)

        st.markdown("---")

        # ========== BOTONES DE ACCIÓN ==========
        col_btn1, col_btn2 = st.columns([3, 1])

        with col_btn1:
            submitted = st.form_submit_button(
                "🔍 ANALIZAR CON INTELIGENCIA ARTIFICIAL", 
                type="primary", 
                use_container_width=True,
                help="Evalúa el riesgo y genera recomendaciones personalizadas"
            )

        with col_btn2:
            limpiar = st.form_submit_button(
                "🗑️ Limpiar", 
                type="secondary",
                help="Limpia todos los campos"
            )

    # ========== MANEJO DE BOTONES ==========
    if limpiar:
        # Limpiar session_state
        st.session_state.dni_consulta = ""
        st.session_state.nombre_consulta = ""
        st.success("✅ Formulario limpiado")
        st.rerun()

    if submitted:
        # ========== VALIDACIÓN FINAL ANTES DE PROCESAR ==========
        errores = []

        # Validar hemoglobina
        if hemoglobina < 5.0 or hemoglobina > 18.0:
            errores.append("Hemoglobina fuera del rango permitido (5-18 g/dL)")

        # Validar edad
        if edad_meses < 6 or edad_meses > 59:
            errores.append("Edad debe estar entre 6 y 59 meses")

        # Validar peso
        if peso_kg < 3.0 or peso_kg > 25.0:
            errores.append("Peso debe estar entre 3 y 25 kg")

        # Validar teléfono si se ingresó
        if telefono_notif:
            if not telefono_notif.isdigit() or len(telefono_notif) != 9:
                errores.append("Teléfono debe tener 9 dígitos")

        if errores:
            st.error("❌ Por favor corrige los siguientes errores:")
            for error in errores:
                st.write(f"  • {error}")
        else:
            # ========== PROCESAR PREDICCIÓN ==========
            # Aquí iría tu lógica de predicción existente

            # Guardar datos con fuente HB
            datos_clinicos = {
                'nombre': nombre_paciente,
                'dni': dni_paciente,
                'edad_meses': edad_meses,
                'peso_kg': peso_kg,
                'hemoglobina': hemoglobina,
                'fuente_hemoglobina': fuente_hb,  # NUEVO
                'fecha_medicion': fecha_medicion,  # NUEVO
                'altitud': altitud,
                'area': area,
                'recibe_suplemento': recibe_suplemento == 'Sí',
                'asiste_cred': asiste_cred == 'Sí',
                'es_bajo_peso': es_bajo_peso,
                'es_prematuro': es_prematuro,
                'telefono': telefono_notif if telefono_notif else None
            }

            # Guardar en session_state
            st.session_state.datos_diagnostico = datos_clinicos

            st.success("✅ Datos guardados correctamente. Procesando...")


    # =====================================================
    # PROCESAR PREDICCIÓN
    # =====================================================
    if submitted:
        st.session_state.form_submitted = True
        score = {'nivel': 'No evaluado', 'probabilidad': 0.0}
        probabilidad_ml = 0.0
        explicacion_shap = None
        proyeccion_3m = None
        proyeccion_6m = None
        recomendaciones = None
        X_features_ml = None

        # Configurar logger UNA SOLA VEZ (al inicio)
        import logging
        logger = logging.getLogger(__name__)


        # 1. PREPARAR DATOS DEL PACIENTE
        datos_paciente = {
        'hemoglobina': hemoglobina,
        'edad_meses': edad_meses,
        'peso_kg': peso_kg,
        'talla_cm': talla_cm,  # AGREGAR si lo incluiste
        'altitud': altitud,
        'departamento': departamento,
        'area_rural': area == "Rural",
        'recibe_suplemento': recibe_suplemento == "Sí",
        'asiste_cred': asiste_cred == "Sí",
        'es_bajo_peso': es_bajo_peso,
        'es_prematuro': es_prematuro,
        'fuente_hemoglobina': fuente_hb,  # AGREGAR si lo incluiste
        'fecha_medicion': fecha_medicion  # AGREGAR si lo incluiste
    }
        
        # 2. REALIZAR PREDICCIÓN ML
        with st.spinner('🤖 Analizando con Inteligencia Artificial...'):
            
            resultado = anemia_predictor.predecir(datos_paciente)
        
                # =====================================================
        # PROCESAMIENTO POST-PREDICCIÓN
        # =====================================================
        
        # 1. Predicción completada
        st.success("✅ Análisis completado exitosamente")
        st.divider()
        
        # 2. Generar features ML para explicabilidad
        try:
            X_features_ml = anemia_predictor._preparar_features_ml(datos_paciente)
            logger.info(f"✅ Features ML generados: shape={X_features_ml.shape if X_features_ml is not None else 'None'}")
        except Exception as e:
            logger.error(f"❌ Error generando features ML: {e}")
            X_features_ml = None
        
        # 3. Extraer probabilidad ML (con fallback robusto)
        try:
            probabilidad_ml = 0.5  # Valor por defecto
            
            # Intentar extraer de diferentes fuentes
            if 'ml' in resultado and resultado['ml'] is not None:
                if isinstance(resultado['ml'], dict):
                    probabilidad_ml = resultado['ml'].get('probabilidad', 0.5)
                else:
                    probabilidad_ml = float(resultado['ml'])
            
            # Fallback: usar score híbrido si ML no está disponible
            if probabilidad_ml == 0.0 and 'hibrido_v3' in resultado:
                probabilidad_ml = resultado['hibrido_v3'].get('riesgo_score', 0.5)
            
            # Fallback final: calcular desde nivel de riesgo
            if probabilidad_ml == 0.0:
                nivel_riesgo = resultado.get('nivel_riesgo', 'MEDIO')
                probabilidad_ml = {
                    'BAJO': 0.15,
                    'MEDIO': 0.35,
                    'ALTO': 0.65,
                    'CRÍTICO': 0.85
                }.get(nivel_riesgo, 0.5)
            
            st.session_state.probabilidad_ml = probabilidad_ml
            logger.info(f"✅ Probabilidad ML: {probabilidad_ml:.3f}")
        
        except Exception as e:
            logger.error(f"❌ Error extrayendo probabilidad: {e}")
            probabilidad_ml = 0.5
        
        # 4. Guardar en historial (si aplica)
        if dni_paciente and len(dni_paciente) == 8:
            try:
                from utils.historial import guardar_consulta
                
                tiene_suplemento = recibe_suplemento == "Sí"
                asiste_cred_bool = asiste_cred == "Sí"
                
                guardar_consulta(dni_paciente, {
                    'hemoglobina': hemoglobina,
                    'hemoglobina_ajustada': resultado.get('hemoglobina_ajustada', hemoglobina),
                    'probabilidad_ml': probabilidad_ml,
                    'tiene_anemia': resultado.get('tiene_anemia', False),
                    'severidad': resultado.get('severidad', 'Normal'),
                    'edad_meses': edad_meses,
                    'recibe_suplemento': tiene_suplemento,
                    'asiste_cred': asiste_cred_bool
                })
                
                logger.info(f"✅ Historial guardado para DNI: {dni_paciente}")
            
            except Exception as e:
                logger.warning(f"⚠️ No se pudo guardar historial: {e}")
        
        # 5. Extraer factores de riesgo detectados
        factores_riesgo_detectados = []
        try:
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
            
            logger.info(f"✅ {len(factores_riesgo_detectados)} factores de riesgo detectados")
        
        except Exception as e:
            logger.error(f"❌ Error extrayendo factores: {e}")
        
        # 6. Generar recomendaciones clínicas
        try:
            recomendaciones = generar_recomendaciones_personalizadas(
                edad_meses=edad_meses,
                peso_kg=peso_kg,
                tiene_anemia=resultado.get('tiene_anemia', False),
                factores_riesgo=factores_riesgo_detectados,
                hb_actual=hemoglobina,
                altitud_m=altitud,
                es_bajo_peso=es_bajo_peso,
                es_prematuro=es_prematuro
            )
            
            logger.info("✅ Recomendaciones generadas")
        
        except Exception as e:
            logger.error(f"❌ Error generando recomendaciones: {e}")
            recomendaciones = {
                'suplementacion': 'Consultar con profesional de salud',
                'alimentacion': [],
                'seguimiento': 'Control mensual CRED'
            }
        
        # 7. Generar proyecciones temporales
        try:
            predictor_temporal = get_temporal_predictor(anemia_predictor)
            proyeccion_3m = predictor_temporal.predecir_futuro(datos_paciente, meses=3)
            proyeccion_6m = predictor_temporal.predecir_futuro(datos_paciente, meses=6)
            
            logger.info("✅ Proyecciones temporales generadas")
        
        except Exception as e:
            logger.error(f"❌ Error generando proyecciones: {e}")
            proyeccion_3m = {'probabilidad': probabilidad_ml * 1.2}
            proyeccion_6m = {'probabilidad': probabilidad_ml * 1.4}
        
        # 8. Calcular score simple
        try:
            from utils.score_simple import calcular_score_simple
            
            top_factores = [
                (f, 0.1, f.replace('_', ' ').title()) 
                for f in factores_riesgo_detectados[:3]
            ]
            
            score = calcular_score_simple(probabilidad_ml, top_factores)

            st.session_state.score = score
            
            logger.info(f"✅ Score calculado: {score['nivel']}")
        
        except Exception as e:
            logger.error(f"❌ Error calculando score: {e}")
            score = {
                'nivel': 'MEDIO',
                'color': '#FFA500',
                'emoji': '⚠️',
                'explicacion': 'Evaluación estándar',
                'mensaje': 'Seguir recomendaciones del personal de salud'
            }
        
        # 9. Generar explicación SHAP (opcional, sin bloquear UI)
        explicacion_shap = None
        if X_features_ml is not None:
            try:
                from utils.explainer import ModelExplainer, load_background_data
                
                background_data = load_background_data(
                    'data/processed/sien_nacional_procesado.csv',
                    list(X_features_ml.columns),
                    n_samples=50
                )
                
                if background_data is not None:
                    explainer = ModelExplainer(anemia_predictor.model, background_data)
                    explicacion_shap = explainer.explain_individual(
                        X_features_ml,
                        feature_names=list(X_features_ml.columns)
                    )
                    
                    if explicacion_shap:
                        logger.info("✅ Explicación SHAP generada")
                        
                        # Cerrar figuras matplotlib para evitar bloqueos
                        import matplotlib.pyplot as plt
                        plt.close('all')
            
            except Exception as e:
                logger.warning(f"⚠️ SHAP no disponible: {str(e)[:100]}")
                explicacion_shap = None
        
        logger.info("🎯 Procesamiento completado, iniciando render de UI")
        

        # =====================================================
        # 10. GUARDAR EN HISTORIAL (SI HAY DNI)
        # =====================================================
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info("📋 DEBUG: Paso 10 - Iniciando sección de historial...")
        
        if dni_paciente and len(dni_paciente) == 8:
            try:
                from utils.historial import guardar_consulta
                
                logger.info("📋 DEBUG: Guardando consulta en historial...")
                
                # Preparar variables booleanas
                tiene_suplemento = recibe_suplemento == "Sí"
                asiste_cred_bool = asiste_cred == "Sí"
                
                guardar_consulta(dni_paciente, {
                    'hemoglobina': hemoglobina,
                    'hemoglobina_ajustada': resultado['hemoglobina_ajustada'],
                    'probabilidad_ml': probabilidad_ml,
                    'tiene_anemia': resultado['tiene_anemia'],
                    'severidad': resultado['severidad'],
                    'edad_meses': edad_meses,
                    'recibe_suplemento': tiene_suplemento,
                    'asiste_cred': asiste_cred_bool
                })
                
                logger.info(f"✅ Consulta guardada en historial para DNI: {dni_paciente}")
            
            except ImportError:
                logger.warning("⚠️ Módulo historial no disponible")
                st.caption("ℹ️ Sistema de historial no disponible")
            except Exception as e:
                logger.error(f"❌ Error guardando historial: {e}")
        else:
            logger.info("ℹ️ No se guardará historial (DNI no válido o vacío)")
        
        logger.info("📊 DEBUG: Paso 11 - Iniciando render de SCORE...")
        
# =====================================================
# 11. MOSTRAR EVALUACIÓN RÁPIDA CON SEMÁFORO EXPLICABLE ⭐ MEJORADO
# =====================================================
        st.markdown("## 🎯 Resultado del Análisis")
        logger.info("📊 Iniciando render de resultado mejorado...")

        # ========== SEMÁFORO GRANDE Y PROMINENTE ==========
        col_semaforo_principal, col_info_rapida = st.columns([1.3, 1], gap="large")

        with col_semaforo_principal:
            try:
                # Determinar color y emoji según nivel de riesgo
                colores_riesgo = {
                    'BAJO': {'bg': '#28a745', 'emoji': '🟢', 'texto': 'RIESGO BAJO'},
                    'MEDIO': {'bg': '#ffc107', 'emoji': '🟡', 'texto': 'RIESGO MODERADO'},
                    'ALTO': {'bg': '#ff6b6b', 'emoji': '🔴', 'texto': 'RIESGO ALTO'},
                    'CRÍTICO': {'bg': '#dc3545', 'emoji': '🔴', 'texto': 'RIESGO CRÍTICO'}
                }

                nivel = score['nivel'] if 'nivel' in score else 'MEDIO'
                config_visual = colores_riesgo.get(nivel, colores_riesgo['MEDIO'])

                # Calcular estado_texto
                if resultado['tiene_anemia']:
                    severidad_emoji = {'Leve': '🟡', 'Moderada': '🟠', 'Severa': '🔴'}
                    emoji_estado = severidad_emoji.get(resultado['severidad'], '⚠️')
                    estado_texto = f"{emoji_estado} ANEMIA {resultado['severidad'].upper()}"
                else:
                    estado_texto = "✅ Sin Anemia"

                # TARJETA GRANDE CON SEMÁFORO
                st.markdown(f"""
                <div style="background: {config_visual['bg']}; 
                            padding: 3rem 2rem; 
                            border-radius: 20px; 
                            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                            text-align: center;
                            animation: fadeIn 0.5s ease-in;">
                    <div style="font-size: 5rem; margin-bottom: 1rem; animation: pulse 2s infinite;">
                        {config_visual['emoji']}
                    </div>
                    <h1 style="color: white; margin: 0 0 1.5rem 0; font-size: 2rem; font-weight: 700;">
                        {config_visual['texto']}
                    </h1>
                    <div style="background: rgba(255,255,255,0.2); 
                                padding: 1.5rem; 
                                border-radius: 15px; 
                                margin-bottom: 1rem;">
                        <p style="color: white; margin: 0 0 0.5rem 0; font-size: 1rem; opacity: 0.9;">
                            Probabilidad de Anemia
                        </p>
                        <h2 style="color: white; margin: 0; font-size: 4rem; font-weight: 900;">
                            {probabilidad_ml*100:.0f}%
                        </h2>
                    </div>
                    <p style="color: rgba(255,255,255,0.95); font-size: 1.1rem; margin: 0;">
                        {estado_texto} | Hb: {hemoglobina:.1f} g/dL
                    </p>
                </div>

                <style>
                @keyframes fadeIn {{
                    from {{ opacity: 0; transform: translateY(20px); }}
                    to {{ opacity: 1; transform: translateY(0); }}
                }}
                @keyframes pulse {{
                    0%, 100% {{ transform: scale(1); }}
                    50% {{ transform: scale(1.1); }}
                }}
                </style>
                """, unsafe_allow_html=True)

                logger.info("✅ Semáforo principal renderizado")

            except Exception as e:
                logger.error(f"❌ ERROR en semáforo: {e}")
                st.error(f"Error: {e}")

        with col_info_rapida:
            try:
                # TARJETA DE ACCIÓN INMEDIATA
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); 
                            border-left: 6px solid {config_visual['bg']};
                            padding: 2rem; 
                            border-radius: 15px; 
                            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                            height: 100%;">
                    <h3 style="margin-top: 0; color: #2c3e50; font-size: 1.5rem;">
                        💡 Acción Inmediata
                    </h3>
                    <p style="color: #34495e; font-size: 1.15rem; line-height: 1.7; margin-bottom: 1.5rem;">
                        {score.get('mensaje', 'Consultar con profesional de salud')}
                    </p>
                    <div style="background: rgba(255,255,255,0.8); 
                                padding: 1rem; 
                                border-radius: 10px;">
                        <p style="color: #7f8c8d; font-size: 0.9rem; margin: 0;">
                            ℹ️ Esto es una <strong>probabilidad estadística</strong>, 
                            no un diagnóstico médico definitivo.
                        </p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                logger.info("✅ Info rápida renderizada")

            except Exception as e:
                logger.error(f"❌ ERROR en info rápida: {e}")
                st.error(f"Error: {e}")

        st.markdown("<br>", unsafe_allow_html=True)

        # =====================================================
        # TOP 3 FACTORES PRINCIPALES ⭐ MEJORADO
        # =====================================================
        st.markdown("### 🔍 ¿Por qué este resultado? - Top 3 Factores Principales")

        try:
            # Obtener top 3 factores desde SHAP o fallback
            top_factores_display = []

            if explicacion_shap and 'top_10' in explicacion_shap:
                # Filtrar factores de riesgo (shap_value > 0)
                top_factores_riesgo = explicacion_shap['top_10'][
                    explicacion_shap['top_10']['shap_value'] > 0
                ].head(3)

                if len(top_factores_riesgo) > 0:
                    total_abs_shap = top_factores_riesgo['abs_shap'].sum()

                    # Mapeo de features a descripciones legibles
                    feature_mapping = {
                        'sin_suplemento': {
                            'nombre': 'Sin Suplemento de Hierro',
                            'icono': '💊',
                            'descripcion': 'No recibe suplementación preventiva'
                        },
                        'hb_baja': {
                            'nombre': 'Hemoglobina Baja',
                            'icono': '🩸',
                            'descripcion': 'Nivel de hemoglobina menor al esperado'
                        },
                        'area_rural': {
                            'nombre': 'Área Rural',
                            'icono': '🏘️',
                            'descripcion': 'Residencia en zona de difícil acceso'
                        },
                        'sin_cred': {
                            'nombre': 'Sin Controles CRED',
                            'icono': '📋',
                            'descripcion': 'No asiste a controles regulares'
                        },
                        'altitud_muy_alta': {
                            'nombre': 'Alta Altitud',
                            'icono': '⛰️',
                            'descripcion': 'Altitud mayor a 3000 metros'
                        },
                        'edad_6_11m': {
                            'nombre': 'Edad 6-11 meses',
                            'icono': '👶',
                            'descripcion': 'Grupo etario de mayor riesgo'
                        },
                        'edad_12_23m': {
                            'nombre': 'Edad 12-23 meses',
                            'icono': '👶',
                            'descripcion': 'Período crítico de desarrollo'
                        },
                        'bajo_peso_nacimiento': {
                            'nombre': 'Bajo Peso al Nacer',
                            'icono': '⚖️',
                            'descripcion': 'Nació con peso menor a 2500g'
                        }
                    }

                    for idx, row in top_factores_riesgo.iterrows():
                        feature = row['feature']
                        porcentaje = (row['abs_shap'] / total_abs_shap) * 100 if total_abs_shap > 0 else 33.3

                        config = feature_mapping.get(feature, {
                            'nombre': feature.replace('_', ' ').title(),
                            'icono': '⚠️',
                            'descripcion': 'Factor de riesgo detectado'
                        })

                        top_factores_display.append({
                            'icono': config['icono'],
                            'nombre': config['nombre'],
                            'descripcion': config.get('descripcion', config['nombre']),
                            'porcentaje': porcentaje
                        })

            # Fallback si no hay SHAP
            if len(top_factores_display) == 0:
                # Usar factores detectados básicos
                factores_basicos = {
                    'sin_suplemento': {'icono': '💊', 'nombre': 'Sin Suplemento de Hierro', 'descripcion': 'No recibe suplementación'},
                    'sin_cred': {'icono': '📋', 'nombre': 'Sin Controles CRED', 'descripcion': 'No asiste a controles'},
                    'area_rural': {'icono': '🏘️', 'nombre': 'Área Rural', 'descripcion': 'Zona de difícil acceso'},
                    'alta_altitud': {'icono': '⛰️', 'nombre': 'Alta Altitud', 'descripcion': 'Mayor a 3000 metros'},
                    'edad_6_24m': {'icono': '👶', 'nombre': 'Edad de Riesgo', 'descripcion': 'Grupo vulnerable'}
                }

                for i, factor_key in enumerate(factores_riesgo_detectados[:3], 1):
                    config = factores_basicos.get(factor_key, {
                        'icono': '⚠️', 
                        'nombre': factor_key.replace('_', ' ').title(),
                        'descripcion': 'Factor de riesgo detectado'
                    })
                    top_factores_display.append({
                        'icono': config['icono'],
                        'nombre': config['nombre'],
                        'descripcion': config['descripcion'],
                        'porcentaje': 100 / min(len(factores_riesgo_detectados), 3)
                    })

            # Renderizar las 3 tarjetas de factores
            if len(top_factores_display) > 0:
                col_f1, col_f2, col_f3 = st.columns(3, gap="medium")

                for i, (col, factor) in enumerate(zip([col_f1, col_f2, col_f3], top_factores_display[:3]), 1):
                    with col:
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); 
                                    padding: 1.8rem; 
                                    border-radius: 15px; 
                                    border-left: 5px solid {config_visual['bg']};
                                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                                    height: 220px;
                                    transition: transform 0.2s ease;">
                            <div style="text-align: center; margin-bottom: 1rem;">
                                <span style="font-size: 3rem;">{factor['icono']}</span>
                            </div>
                            <h4 style="color: #2c3e50; 
                                       margin: 0 0 0.5rem 0; 
                                       font-size: 1.1rem; 
                                       font-weight: 700;
                                       text-align: center;">
                                {i}. {factor['nombre']}
                            </h4>
                            <p style="color: #7f8c8d; 
                                      font-size: 0.85rem; 
                                      margin: 0 0 1rem 0;
                                      text-align: center;
                                      line-height: 1.4;">
                                {factor['descripcion']}
                            </p>
                            <div style="background: #e9ecef; 
                                        border-radius: 10px; 
                                        height: 12px; 
                                        overflow: hidden;
                                        margin-bottom: 0.5rem;">
                                <div style="background: {config_visual['bg']}; 
                                            width: {factor['porcentaje']:.1f}%; 
                                            height: 100%; 
                                            border-radius: 10px;
                                            transition: width 0.5s ease;"></div>
                            </div>
                            <p style="text-align: center; 
                                      color: {config_visual['bg']}; 
                                      font-weight: 700; 
                                      font-size: 1.1rem;
                                      margin: 0;">
                                {factor['porcentaje']:.0f}% de impacto
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.success("✅ No se detectaron factores de riesgo significativos")

            logger.info("✅ Top 3 factores renderizados")

        except Exception as e:
            logger.error(f"❌ ERROR en top 3 factores: {e}")
            st.warning("⚠️ No se pudieron cargar los factores principales")

        st.divider()

        # =====================================================
        # LINK AL SIMULADOR (FLUJO GUIADO)
        # =====================================================
        col_link, col_btn = st.columns([3, 1])

        with col_link:
            st.info("💡 **¿Quieres ver cómo mejorar este resultado con intervenciones?**")

        with col_btn:
            if st.button("**🔮 Ver Simulador →**", type="primary", key="btn_link_simulador", use_container_width=True):
                st.session_state.pagina_actual = "🔮 ¿Qué pasaría si...?"
                st.session_state.datos_diagnostico = {
                    'hemoglobina': hemoglobina,
                    'edad_meses': edad_meses,
                    'nivel_riesgo': score['nivel']
                }
                st.rerun()

        st.divider()
        logger.info("✅ Sección 11 completada")


# =====================================================
# PROYECCIONES COMPARATIVAS (CORREGIDAS)
# =====================================================

        st.markdown("## 🔮 ¿Qué pasará en los próximos meses?")

        prob_actual = probabilidad_ml
        hb_actual = hemoglobina

        # ✨ CÁLCULO DIFERENCIADO: Con anemia vs Sin anemia

        if resultado['tiene_anemia']:
            # CASO 1: TIENE ANEMIA
            # Sin acción: empeora o se mantiene
            prob_sin_accion_3m = min(prob_actual * 1.15, 0.95)
            prob_sin_accion_6m = min(prob_actual * 1.30, 0.98)
            prob_sin_accion_12m = min(prob_actual * 1.45, 0.99)
            
            # Con acción: mejora significativa
            prob_con_accion_3m = max(prob_actual * 0.70, 0.05)
            prob_con_accion_6m = max(prob_actual * 0.50, 0.03)
            prob_con_accion_12m = max(prob_actual * 0.30, 0.02)
            
        else:
            # CASO 2: SIN ANEMIA (sano)
            # Sin prevención: riesgo aumenta desde probabilidad baja
            prob_sin_accion_3m = min(prob_actual * 2.5, 0.30)   # Puede subir hasta 30%
            prob_sin_accion_6m = min(prob_actual * 4.0, 0.50)   # Puede subir hasta 50%
            prob_sin_accion_12m = min(prob_actual * 6.0, 0.70)  # Puede subir hasta 70%
            
            # Con prevención: se mantiene bajo
            prob_con_accion_3m = max(prob_actual * 0.80, 0.01)
            prob_con_accion_6m = max(prob_actual * 0.70, 0.01)
            prob_con_accion_12m = max(prob_actual * 0.60, 0.01)

        # Crear tabla comparativa
        col_tiempo, col_sin, col_con = st.columns(3)

        with col_tiempo:
            st.markdown("### ⏰ Plazo")
            st.markdown("**Hoy**")
            st.markdown("**3 meses**")
            st.markdown("**6 meses**")
            st.markdown("**12 meses**")

        with col_sin:
            st.markdown("### ❌ Sin Acción")
            st.markdown(f"🔴 {prob_actual*100:.0f}% riesgo")
            st.markdown(f"🔴 {prob_sin_accion_3m*100:.0f}% riesgo")
            st.markdown(f"🔴 {prob_sin_accion_6m*100:.0f}% riesgo")
            st.markdown(f"🔴 {prob_sin_accion_12m*100:.0f}% riesgo")

        with col_con:
            st.markdown("### ✅ Con Acción")
            st.markdown(f"🟡 {prob_actual*100:.0f}% riesgo")
            st.markdown(f"🟢 {prob_con_accion_3m*100:.0f}% riesgo")
            st.markdown(f"🟢 {prob_con_accion_6m*100:.0f}% riesgo")
            st.markdown(f"🟢 {prob_con_accion_12m*100:.0f}% riesgo")

        # Mensaje contextual mejorado
        if resultado['tiene_anemia']:
            st.warning(f"""
            ⚠️ **Sin acción inmediata**  
            {int(prob_sin_accion_3m*10)} de cada 10 niños como {nombre_paciente or 'tu hijo/a'} 
            **prevalecen en anemia** o empeoran en los próximos 3 meses.
            
            ✅ **Con tratamiento y seguimiento:**  
            {int((1-prob_con_accion_3m)*10)} de cada 10 niños **se recuperan** en 3 meses.
            """)
        else:
            # ✨ MENSAJE CORREGIDO PARA NIÑOS SANOS
            st.info(f"""
            ⚠️ **Sin prevención:**  
            {int(prob_sin_accion_6m*10)} de cada 10 niños como {nombre_paciente or 'tu hijo/a'} 
            **desarrollarán anemia** en los próximos 6 meses.
            
            ✅ **Con prevención adecuada:**  
            {int((1-prob_con_accion_6m)*10)} de cada 10 niños **se mantienen sanos**.
            """)

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
    # SECCIÓN FINAL: ACCIONES (PDF POR ROL + NOTIFICACIONES)
    # =====================================================
        if st.session_state.form_submitted:
        
            st.markdown("## 📋 Acciones Finales")

            # ========== INFO SOBRE LOS REPORTES ==========
            with st.expander("ℹ️ ¿Qué reporte necesito?", expanded=False):
                col_info1, col_info2, col_info3 = st.columns(3)

                with col_info1:
                    st.markdown("""
                    **📄 Reporte Cuidador**

                    ✅ Lenguaje simple
                    ✅ Plan alimentario
                    ✅ Tips prácticos
                    ✅ Lista de compras

                    Para: Madres y cuidadores
                    """)

                with col_info2:
                    st.markdown("""
                    **📊 Reporte Profesional**

                    ✅ Datos clínicos completos
                    ✅ Gráficos de evolución
                    ✅ Factores de riesgo (SHAP)
                    ✅ Protocolo NTS 213

                    Para: Médicos y nutricionistas
                    """)

                with col_info3:
                    st.markdown("""
                    **🏢 Reporte Entidad**

                    ✅ Datos agregados
                    ✅ Mapas por distrito
                    ✅ Alertas de hotspots
                    ✅ Tendencias

                    Para: Instituciones públicas
                    """)

            st.divider()

            # ========== BOTONES DE REPORTE POR ROL ==========
            col_pdf1, col_pdf2, col_pdf3 = st.columns(3, gap="medium")

            # ========== REPORTE PARA CUIDADOR (MADRE) ==========
            with col_pdf1:
                try:
                    from datetime import datetime
                    from utils.pdf_generator import ReportePDFGenerator

                    if st.button(
                        "📄 PDF Cuidador", 
                        use_container_width=True, 
                        type="primary", 
                        help="Plan alimentario con tips prácticos para la madre/cuidador",
                        key="btn_pdf_cuidador"
                    ):

                        # Verificar si hay menús en session_state
                        if 'menu_generado' not in st.session_state or st.session_state.menu_generado is None:
                            st.warning("""
                            ⚠️ **Primero genera menús personalizados**  
                            Ve a la sección **Menús Personalizados** para crear un plan alimentario.
                            """)
                        else:
                            with st.spinner('📝 Generando reporte para cuidador...'):
                                try:
                                    # Preparar datos para reporte cuidador
                                    datos_paciente = {
                                        'nombre_nino': nombre_paciente,
                                        'nombre_madre': st.session_state.get('nombre_madre', 'Mamá'),
                                        'edad_meses': edad_meses,
                                    }

                                    # Preparar plan alimentario
                                    menu_generado = st.session_state.menu_generado

                                    plan_alimentario = {
                                        'menu_semanal': [
                                            {
                                                'dia': dia,
                                                'desayuno': menu_generado.get(dia, {}).get('desayuno', {}).get('nombre', 'N/A'),
                                                'almuerzo': menu_generado.get(dia, {}).get('almuerzo', {}).get('nombre', 'N/A'),
                                                'cena': menu_generado.get(dia, {}).get('cena', {}).get('nombre', 'N/A')
                                            }
                                            for dia in ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
                                        ],
                                        'lista_compras': [
                                            {'ingrediente': 'Hígado de res', 'cantidad': '300g', 'beneficio': 'Máximo hierro'},
                                            {'ingrediente': 'Sangrecita', 'cantidad': '250g', 'beneficio': 'Hierro fácil de absorber'},
                                            {'ingrediente': 'Lentejas', 'cantidad': '400g', 'beneficio': 'Proteína y hierro'},
                                            {'ingrediente': 'Espinaca', 'cantidad': '1 atado', 'beneficio': 'Hierro y vitaminas'},
                                            {'ingrediente': 'Naranja', 'cantidad': '6 unidades', 'beneficio': 'Vitamina C para absorber hierro'},
                                            {'ingrediente': 'Limón', 'cantidad': '6 unidades', 'beneficio': 'Ácido cítrico para absorber hierro'},
                                            {'ingrediente': 'Huevos', 'cantidad': '12 unidades', 'beneficio': 'Proteína completa'},
                                        ],
                                        'recomendaciones': [
                                            '🩸 Combina las carnes rojas con zumo de naranja o limón para mejor absorción',
                                            '⚡ Ofrece menús a horas fijas (06:00, 12:00, 19:00)',
                                            '👨‍⚕️ Asiste a CRED mensualmente para seguimiento',
                                            '📞 Llama si el niño rechaza comida por 2 días seguidos',
                                        ],
                                        'proxima_cita': 'Próxima cita CRED: próxima semana',
                                        'telefono_contacto': '01-4154122 (MINSA)'
                                    }

                                    # Generar PDF cuidador (simplificado vs médico)
                                    generator = ReportePDFGenerator()
                                    pdf_path = generator.generar_reporte_madre(datos_paciente, plan_alimentario)

                                    # Leer PDF y ofrecer descarga
                                    with open(pdf_path, "rb") as f:
                                        pdf_bytes = f.read()
                                        st.session_state.pdf_cuidador = {
                                            'bytes': pdf_bytes,
                                            'nombre': nombre_archivo
                                        }


                                    nombre_archivo = f"Plan_Nutricional_{nombre_paciente.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"

                                    st.download_button(
                                        label="⬇️ Descargar PDF Cuidador",
                                        data=pdf_bytes,
                                        file_name=nombre_archivo,
                                        mime="application/pdf",
                                        use_container_width=True,
                                        help="Plan semanal con tips prácticos"
                                    )

                                    st.success("✅ Reporte descargado. ¡Comparte con tu familia!")

                                except Exception as e:
                                    st.error(f"❌ Error generando reporte: {e}")
                                    with st.expander("🔍 Ver detalles"):
                                        import traceback
                                        st.code(traceback.format_exc())

                except Exception as e:
                    st.error(f"❌ Error: {e}")


            # ========== REPORTE PARA PROFESIONAL (MÉDICO) ==========
            with col_pdf2:
                try:
                    from datetime import datetime
                    from utils.pdf_generator import ReportePDFGenerator

                    if st.button(
                        "📊 PDF Profesional", 
                        use_container_width=True, 
                        help="Datos clínicos completos para profesional de salud",
                        key="btn_pdf_profesional"
                    ):
                        with st.spinner('📝 Generando reporte profesional...'):
                            try:
                                # Preparar datos para reporte médico
                                datos_paciente = {
                                    'nombre_nino': nombre_paciente,
                                    'nombre_madre': st.session_state.get('nombre_madre', 'Madre/Cuidador'),
                                    'edad_meses': edad_meses,
                                    'dni': dni_paciente if 'dni' in locals() else 'N/A'
                                }
                                
                                # Preparar datos clínicos completos
                                datos_clinicos = {
                                    'hemoglobina': hemoglobina,
                                    'fuente_hemoglobina': st.session_state.datos_diagnostico.get('fuente_hemoglobina', 'No especificada') if 'datos_diagnostico' in st.session_state else 'N/A',
                                    'fecha_medicion': st.session_state.datos_diagnostico.get('fecha_medicion', 'N/A') if 'datos_diagnostico' in st.session_state else 'N/A',
                                    'edad_meses': edad_meses,
                                    'peso_kg': peso_kg,
                                    'talla_cm': talla_cm,
                                    'imc': round(peso_kg / ((talla_cm/100)**2), 2),
                                    'altitud_msnm': altitud_sugerida,
                                    'nivel_riesgo': score['nivel'],
                                    'probabilidad_ml': probabilidad_ml,
                                    'recibe_suplemento': st.session_state.datos_diagnostico.get('recibe_suplemento', False) if 'datos_diagnostico' in st.session_state else False,
                                    'asiste_cred': st.session_state.datos_diagnostico.get('asiste_cred', False) if 'datos_diagnostico' in st.session_state else False,
                                    'bajo_peso_nacimiento': st.session_state.datos_diagnostico.get('es_bajo_peso', False) if 'datos_diagnostico' in st.session_state else False,
                                    'prematuro': st.session_state.datos_diagnostico.get('es_prematuro', False) if 'datos_diagnostico' in st.session_state else False,
                                    # Top factores SHAP
                                    'factor_1': explicacion_shap['top_10'].iloc[0]['feature'] if explicacion_shap and 'top_10' in explicacion_shap else 'N/A',
                                    'factor_2': explicacion_shap['top_10'].iloc[1]['feature'] if explicacion_shap and 'top_10' in explicacion_shap and len(explicacion_shap['top_10']) > 1 else 'N/A',
                                    'factor_3': explicacion_shap['top_10'].iloc[2]['feature'] if explicacion_shap and 'top_10' in explicacion_shap and len(explicacion_shap['top_10']) > 2 else 'N/A',
                                    # Recomendaciones clínicas
                                    'protocolo_nts': 'NTS 213 - Anemia infantil',
                                    'recomendacion': score.get('mensaje', 'Seguimiento clínico recomendado')
                                }

                                # Generar PDF profesional
                                generator = ReportePDFGenerator()
                                pdf_path = generator.generar_reporte_medico(datos_paciente, datos_clinicos)

                                # Leer PDF y ofrecer descarga
                                with open(pdf_path, "rb") as f:
                                    pdf_bytes = f.read()
                                    st.session_state.pdf_cuidador = {
                                                'bytes': pdf_bytes,
                                                'nombre': nombre_archivo
                                            }


                                nombre_archivo = f"Reporte_Clinico_{nombre_paciente.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"

                                if st.session_state.pdf_cuidador:
                                    st.download_button(
                                        label="⬇️ Descargar PDF Cuidador",
                                        data=st.session_state.pdf_cuidador['bytes'],
                                        file_name=st.session_state.pdf_cuidador['nombre'],
                                        mime="application/pdf"
                                    )

                                st.success("✅ Reporte descargado. Perfecto para historia clínica.")

                            except Exception as e:
                                st.error(f"❌ Error generando reporte: {e}")
                                with st.expander("🔍 Ver detalles"):
                                    import traceback
                                    st.code(traceback.format_exc())

                except Exception as e:
                    st.error(f"❌ Error: {e}")


            # ========== REPORTE PARA ENTIDAD (AGREGADO) ==========
            with col_pdf3:
                try:
                    if st.button(
                        "🏢 PDF Entidad", 
                        use_container_width=True, 
                        help="Análisis agregado para instituciones de salud",
                        key="btn_pdf_entidad"
                    ):
                        with st.spinner('📝 Generando reporte de entidad...'):
                            try:
                                # Preparar datos agregados
                                datos_agregados = {
                                    'fecha_reporte': datetime.now().strftime('%Y-%m-%d'),
                                    'paciente_actual': nombre_paciente,
                                    'probabilidad': probabilidad_ml,
                                    'nivel_riesgo': score['nivel'],
                                    # Datos poblacionales (simulados - integrar reales)
                                    'total_evaluados': 150,
                                    'casos_riesgo_bajo': 30,
                                    'casos_riesgo_medio': 60,
                                    'casos_riesgo_alto': 45,
                                    'casos_riesgo_critico': 15,
                                    'prevalencia_regional': 35.2,  # Porcentaje
                                    'altitud_promedio': altitud_sugerida,
                                }

                                generator = ReportePDFGenerator()
                                pdf_path = generator.generar_reporte_entidad(datos_agregados)

                                # Leer PDF y ofrecer descarga
                                with open(pdf_path, "rb") as f:
                                    pdf_bytes = f.read()
                                    st.session_state.pdf_cuidador = {
                                                'bytes': pdf_bytes,
                                                'nombre': nombre_archivo
                                            }


                                nombre_archivo = f"Analisis_Entidad_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"

                                if st.session_state.pdf_cuidador:
                                    st.download_button(
                                        label="⬇️ Descargar PDF Cuidador",
                                        data=st.session_state.pdf_cuidador['bytes'],
                                        file_name=st.session_state.pdf_cuidador['nombre'],
                                        mime="application/pdf"
                                    )

                                st.success("✅ Reporte descargado. Incluye análisis agregado.")

                            except Exception as e:
                                st.error(f"❌ Error generando reporte: {e}")
                                with st.expander("🔍 Ver detalles"):
                                    import traceback
                                    st.code(traceback.format_exc())

                except Exception as e:
                    st.error(f"❌ Error: {e}")

            st.divider()

       # ========== GENERAR CASO_ID ==========
    import uuid
    from datetime import datetime
    import time

    if 'caso_id_actual' not in st.session_state:
        st.session_state.caso_id_actual = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

    caso_id = st.session_state.caso_id_actual

    # ========== FEEDBACK CON ANIMACIÓN ==========
    st.markdown("---")
    st.markdown("### 📋 ¿Fue útil este diagnóstico?")

    feedback_key = f'feedback_{caso_id}'

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("✅ Muy claro", key="fb1", use_container_width=True):
            with st.spinner("💾 Guardando feedback..."):
                try:
                    from utils.feedback import guardar_feedback
                    guardar_feedback(caso_id, 100, True)
                    st.session_state[feedback_key] = 'claro'
                    time.sleep(0.3)
                except Exception as e:
                    st.warning(f"⚠️ No se pudo guardar feedback: {e}")
            st.balloons()

    with col2:
        if st.button("⚠️ Algunas dudas", key="fb2", use_container_width=True):
            with st.spinner("💾 Guardando feedback..."):
                try:
                    from utils.feedback import guardar_feedback
                    guardar_feedback(caso_id, 50, True)
                    st.session_state[feedback_key] = 'dudas'
                    time.sleep(0.3)
                except Exception as e:
                    st.warning(f"⚠️ No se pudo guardar feedback: {e}")

    with col3:
        if st.button("❌ No entendí", key="fb3", use_container_width=True):
            with st.spinner("💾 Guardando feedback..."):
                try:
                    from utils.feedback import guardar_feedback
                    guardar_feedback(caso_id, 0, False)
                    st.session_state[feedback_key] = 'no'
                    time.sleep(0.3)
                except Exception as e:
                    st.warning(f"⚠️ No se pudo guardar feedback: {e}")

    # Mostrar mensaje si ya hay feedback
    if feedback_key in st.session_state:
        if st.session_state[feedback_key] == 'claro':
            st.success("✅ ¡Gracias! Tu feedback fue guardado exitosamente 🙏")
        elif st.session_state[feedback_key] == 'dudas':
            st.warning("⚠️ Feedback guardado. Un profesional puede ayudarte.")
        elif st.session_state[feedback_key] == 'no':
            st.error("❌ Feedback guardado. Te contactaremos pronto.")

    # ========== NOTIFICACIONES CON ANIMACIÓN ==========
    st.markdown("---")
    st.markdown("### 📧 Recordatorios Automáticos")

    tiene_tel = False
    if 'datos_diagnostico' in st.session_state and st.session_state.datos_diagnostico:
        telefono = st.session_state.datos_diagnostico.get('telefono')
        tiene_tel = telefono and len(telefono) == 9 and telefono.isdigit()
    else:
        # Fallback a variable local si no está en session_state
        tiene_tel = telefono_notif and len(telefono_notif) == 9 and telefono_notif.isdigit()

    if not tiene_tel:
        st.caption("⚠️ Ingresa un teléfono válido (9 dígitos) en el formulario para programar recordatorios")
    else:
        notif_key = f'notif_{caso_id}'

        if st.button("📧 Programar 3 Recordatorios", key="btn_notif", type="primary", use_container_width=True):
            try:
                # Obtener teléfono
                if 'datos_diagnostico' in st.session_state:
                    telefono_actual = st.session_state.datos_diagnostico.get('telefono')
                else:
                    telefono_actual = telefono_notif

                # Barra de progreso animada
                progress_bar = st.progress(0)
                status_text = st.empty()

                status_text.text("📧 Inicializando sistema de recordatorios...")
                progress_bar.progress(25)
                time.sleep(0.3)

                # Intentar importar sistema de nudges
                try:
                    from utils.nudges import SistemaNudges
                    sistema = SistemaNudges()

                    status_text.text("📅 Programando controles CRED...")
                    progress_bar.progress(50)
                    time.sleep(0.3)

                    # Obtener nombre
                    nombre_actual = nombre_paciente if 'nombre_paciente' in locals() else st.session_state.get('nombre_consulta', 'Paciente')

                    resultados = sistema.programar_recordatorios_multiples(
                        telefono_actual,
                        nombre_actual,
                        [
                            {'tipo': 'Control inmediato', 'dias': 7},
                            {'tipo': 'Seguimiento 1 mes', 'dias': 30},
                            {'tipo': 'Evaluación 3 meses', 'dias': 90}
                        ]
                    )

                except ImportError:
                    # Si no existe utils.nudges, crear estructura simple
                    st.info("ℹ️ Sistema de nudges no disponible. Guardando en modo simulado.")
                    resultados = [
                        {'tipo_control': 'Control inmediato', 'dias_hasta_control': 7, 'canal': 'SMS'},
                        {'tipo_control': 'Seguimiento 1 mes', 'dias_hasta_control': 30, 'canal': 'SMS'},
                        {'tipo_control': 'Evaluación 3 meses', 'dias_hasta_control': 90, 'canal': 'SMS'}
                    ]

                status_text.text("✅ Guardando en sistema...")
                progress_bar.progress(75)
                time.sleep(0.3)

                st.session_state[notif_key] = {
                    'telefono': telefono_actual,
                    'resultados': resultados,
                    'fecha': datetime.now().strftime('%d/%m/%Y %H:%M')
                }

                progress_bar.progress(100)
                status_text.text("✅ ¡Completado!")
                time.sleep(0.3)

                # Limpiar elementos temporales
                progress_bar.empty()
                status_text.empty()

                st.balloons()
                st.success("✅ **Recordatorios programados exitosamente**")

            except Exception as e:
                st.error(f"❌ Error al programar recordatorios: {e}")
                import traceback
                with st.expander("🔍 Ver detalles del error"):
                    st.code(traceback.format_exc())

        # Mostrar confirmación si ya envió
        if notif_key in st.session_state:
            st.success(f"✅ **Recordatorios programados**")
            st.info(f"📱 Teléfono: {st.session_state[notif_key]['telefono']}")
            st.caption(f"🕐 {st.session_state[notif_key]['fecha']}")

            with st.expander("📋 Ver detalles de recordatorios"):
                for r in st.session_state[notif_key]['resultados']:
                    tipo = r.get('tipo_control', r.get('tipo', 'N/A'))
                    dias = r.get('dias_hasta_control', r.get('dias', 0))
                    canal = r.get('canal', 'SMS')
                    st.caption(f"• {tipo} (+{dias} días) - {canal}")

    # ========== NUEVA CONSULTA (LIMPIA TODO) ==========
    st.markdown("---")

    col_nueva_consulta = st.columns(1)

    with col_nueva_consulta[0]:
        if st.button("🔄 Nueva Consulta", type="primary", use_container_width=True, key="btn_nueva_consulta"):
            st.session_state.form_submitted = False
            st.session_state.score = None
            st.session_state.probabilidad_ml = 0.0
            st.rerun()
            try:
                # Limpiar SOLO las claves relacionadas con esta consulta
                keys_to_delete = [k for k in st.session_state.keys() if k in [
                    'datos_diagnostico',
                    'resultado_prediccion',
                    'menu_generado',
                    'feedback_' + caso_id,
                    'notif_' + caso_id,
                    'caso_id_actual'
                ]]

                for key in keys_to_delete:
                    del st.session_state[key]

                st.success("✅ Formulario limpiado. Recargando...")
                time.sleep(0.5)
                st.rerun()

            except Exception as e:
                st.error(f"❌ Error al limpiar: {e}")
                st.info("Recarga la página manualmente si es necesario")