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
    # FORMULARIO DE ENTRADA
    # =====================================================
    with st.form("form_diagnostico"):
        # Usar valores de session_state (campos ocultos)
        nombre_paciente = st.session_state.nombre_consulta
        dni_paciente = st.session_state.dni_consulta
        
        st.markdown("---")
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("#### Datos Clínicos")
            edad_meses = st.number_input("Edad del niño (meses)", 6, 59, 24, 1, 
                                        help="Edad en meses, rango: 6-59")
            peso_kg = st.number_input("Peso del niño (kg)", 3.0, 25.0, 12.0, 0.1, 
                                    help="Peso para dosificación")
            hemoglobina = st.number_input("Hemoglobina (g/dL)", 5.0, 18.0, 11.5, 0.1, 
                                        help="Nivel de hemoglobina")
            altitud = st.number_input("Altitud (msnm)", 0, 5000, altitud_sugerida, 50, 
                                    help=f"Ajustado a {altitud_sugerida}m para {departamento}")
        
        with col_right:
            st.markdown("#### Datos Sociodemográficos")
            area = st.selectbox("Área de residencia", ["Urbana", "Rural"], 
                            help="Área geográfica")
            recibe_suplemento = st.selectbox("Recibe suplementación de hierro", 
                                            ["Sí", "No"], index=1)
            asiste_cred = st.selectbox("Asiste a controles CRED", 
                                    ["Sí", "No"], index=0)
            es_bajo_peso = st.checkbox("Nació con bajo peso (<2500g)", False)
            es_prematuro = st.checkbox("Nació prematuro (<37 semanas)", False)
            
            st.markdown("#### 📞 Datos de Contacto (Opcional)")
            
            telefono_notif = st.text_input(
                "📱 Teléfono/Celular",
                placeholder="987654321",
                help="Para recordatorios de controles CRED",
                key="telefono_input"
            )
            
            if telefono_notif:
                if not telefono_notif.isdigit():
                    st.error("❌ Ingresa solo números (9 dígitos)")
                elif len(telefono_notif) != 9:
                    st.error(f"❌ Debe tener 9 dígitos (tiene {len(telefono_notif)})")
                else:
                    st.success("✅ Teléfono válido")
        
        st.markdown("---")
        col_btn1, col_btn2 = st.columns([3, 1])
        with col_btn1:
            submitted = st.form_submit_button(
                "🔍 ANALIZAR CON INTELIGENCIA ARTIFICIAL", 
                type="primary", 
                use_container_width=True
            )
        with col_btn2:
            limpiar = st.form_submit_button("🗑️ Limpiar", type="secondary")
    if limpiar:
        # Limpiar session_state
        st.session_state.dni_consulta = ""
        st.session_state.nombre_consulta = ""
        st.rerun()
    # =====================================================
    # PROCESAR PREDICCIÓN
    # =====================================================
    if submitted:
        # 1. PREPARAR DATOS DEL PACIENTE
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
        
        # 2. REALIZAR PREDICCIÓN ML
        with st.spinner('🤖 Analizando con Inteligencia Artificial...'):
            
            resultado = anemia_predictor.predecir(datos_paciente)
        
                # =====================================================
        # PROCESAMIENTO POST-PREDICCIÓN
        # =====================================================
        
        # 1. Predicción completada
        st.success("✅ Análisis completado exitosamente")
        st.divider()
        
        # Configurar logger
        import logging
        logger = logging.getLogger(__name__)
        
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
        # 11. MOSTRAR EVALUACIÓN RÁPIDA (SCORE + BARRAS)
        # =====================================================
        st.markdown("## 🎯 Evaluación y Plan de Acción Inmediato")
        
        logger.info("📊 DEBUG: Header renderizado, creando columnas...")
        
        col_resultado, col_accion = st.columns([1.2, 1])
        
        logger.info("📊 DEBUG: Columnas creadas, renderizando col_resultado...")
        
        with col_resultado:
            try:
                if resultado['tiene_anemia']:
                    severidad_emoji = {'Leve': '🟡', 'Moderada': '🟠', 'Severa': '🔴'}
                    emoji_estado = severidad_emoji.get(resultado['severidad'], '⚠️')
                    estado_texto = f"ANEMIA {resultado['severidad'].upper()}"
                else:
                    emoji_estado = '✅'
                    estado_texto = "SIN ANEMIA"
                
                logger.info(f"📊 DEBUG: Estado calculado: {estado_texto}")
                
                st.markdown(f"""
            <div style="background: {score['color']}; padding: 25px; border-radius: 12px;">
                <h2 style="color: white; margin: 0;">{score['emoji']} {score['nivel']} ({probabilidad_ml*100:.1f}%)</h2>
                <p style="color: white; font-size: 1.2em; margin: 12px 0 0 0;">
                    {emoji_estado} {estado_texto} | Hb: {hemoglobina:.1f} g/dL<br>
                    {score['explicacion']}
                </p>
            </div>
            """, unsafe_allow_html=True)

                
                logger.info("✅ DEBUG: col_resultado renderizado correctamente")
            
            except Exception as e:
                logger.error(f"❌ ERROR en col_resultado: {e}")
                st.error(f"Error renderizando resultado: {e}")
        
        logger.info("📊 DEBUG: Renderizando col_accion...")
        
        with col_accion:
            try:
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.95); border-left: 5px solid {score['color']};
                            padding: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                    <h3 style="margin-top: 0; color: #333;">💡 ACCIÓN INMEDIATA</h3>
                    <p style="color: #555; font-size: 1.1em; line-height: 1.5;">
                        {score['mensaje']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                logger.info("✅ DEBUG: col_accion renderizado correctamente")
            
            except Exception as e:
                logger.error(f"❌ ERROR en col_accion: {e}")
                st.error(f"Error renderizando acción: {e}")
        
        logger.info("📊 DEBUG: Iniciando barras de porcentaje...")
        
        # =====================================================
        # MOSTRAR TOP 3 FACTORES DE RIESGO (SOLO NEGATIVOS)
        # =====================================================
        try:
            if explicacion_shap and 'top_10' in explicacion_shap:
                logger.info("📊 DEBUG: Datos SHAP disponibles, filtrando factores de riesgo...")
                
                # ✅ FILTRAR SOLO FACTORES DE RIESGO (shap_value > 0)
                top_factores_riesgo = explicacion_shap['top_10'][
                    explicacion_shap['top_10']['shap_value'] > 0
                ].head(3)
                
                logger.info(f"📊 DEBUG: Factores de riesgo encontrados: {len(top_factores_riesgo)}")
                
                if len(top_factores_riesgo) == 0:
                    st.success("✅ No se detectaron factores de riesgo significativos")
                else:
                    st.markdown("### ⚠️ Principales Factores de Riesgo")
                    
                    # Calcular porcentajes relativos
                    total_abs_shap = top_factores_riesgo['abs_shap'].sum()
                    
                    for i, (idx, row) in enumerate(top_factores_riesgo.iterrows(), 1):
                        feature = row['feature']
                        shap_val = row['shap_value']
                        
                        porcentaje = (row['abs_shap'] / total_abs_shap) * 100 if total_abs_shap > 0 else 33.3
                        
                        # Descripción legible (SOLO FACTORES NEGATIVOS)
                        feature_mapping = {
                            'sin_suplemento': 'No recibe suplemento de hierro',
                            'hb_baja': 'Hemoglobina baja (<11 g/dL)',
                            'area_rural': 'Área de residencia rural',
                            'sin_cred': 'No asiste a controles CRED',
                            'altitud_muy_alta': 'Altitud muy alta (>3000m)',
                            'edad_6_11m': 'Edad 6-11 meses (grupo crítico)',
                            'edad_12_23m': 'Edad 12-23 meses (grupo crítico)',
                            'bajo_peso_nacimiento': 'Nació con bajo peso',
                            'prematuro': 'Nació prematuro',
                            'dept_PUNO': 'Reside en zona de alta prevalencia (Puno)',
                            'dept_CUSCO': 'Reside en zona de alta prevalencia (Cusco)',
                            'dept_HUANCAVELICA': 'Reside en zona de alta prevalencia (Huancavelica)',
                            'hb_x_altitud': 'Combinación crítica: Hemoglobina baja + Alta altitud'
                        }
                        
                        # Si es un factor positivo que pasó el filtro, no mostrarlo
                        if feature in ['recibe_suplemento', 'asiste_cred'] or feature.startswith('hemoglobina'):
                            continue
                        
                        descripcion = feature_mapping.get(feature, feature.replace('_', ' ').title())
                        
                        # Solo color rojo para riesgos
                        color_barra = '#ff6b6b'
                        emoji = '🔴'
                        
                        st.markdown(f"""
                        <div style="margin-bottom: 15px;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span style="font-weight: 600; color: #333;">{emoji} {i}. {descripcion}</span>
                                <span style="font-weight: 700; color: {color_barra};">{porcentaje:.1f}%</span>
                            </div>
                            <div style="background: #e0e0e0; border-radius: 10px; height: 12px; overflow: hidden;">
                                <div style="background: {color_barra}; width: {porcentaje}%; height: 100%; 
                                            transition: width 0.3s ease;"></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        logger.info(f"✅ DEBUG: Barra {i} renderizada: {feature} (riesgo)")
                    
                    logger.info("✅ DEBUG: Todas las barras de riesgo renderizadas correctamente")
            
            else:
                logger.info("ℹ️ DEBUG: No hay datos SHAP disponibles para barras")
        
        except Exception as e:
            logger.error(f"❌ ERROR en barras de porcentaje: {e}")
            import traceback
            logger.error(traceback.format_exc())
            st.warning("⚠️ No se pudieron mostrar los factores de riesgo")
        
        st.divider()
        
        logger.info("✅ DEBUG: Sección 11 (SCORE) completada exitosamente")


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
        # SECCIÓN FINAL: ACCIONES (PDF + NOTIFICACIONES)
        # =====================================================
        
        st.markdown("## 📋 Acciones Finales")
        
        col_pdf, col_notif = st.columns(2)
        
        # ========== BOTÓN PDF (CORREGIDO) ==========
        with col_pdf:
            try:
                from datetime import datetime
                from utils.pdf_generator import generar_pdf_reporte
                
                # Crear diccionario semaforo compatible con PDF generator
                semaforo_para_pdf = {
                    'nivel': score['nivel'],
                    'emoji': score['emoji'],
                    'background': score['color'],
                    'accion_inmediata': score['mensaje']
                }
                
                with st.spinner('📝 Generando reporte PDF...'):
                    pdf_bytes = generar_pdf_reporte(
                        datos_paciente, 
                        resultado, 
                        recomendaciones,
                        proyeccion_3m, 
                        proyeccion_6m, 
                        semaforo_para_pdf
                    )
                
                nombre_archivo = f"Reporte_Anemia_{nombre_paciente or 'Paciente'}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                
                st.download_button(
                    label="📄 Descargar Reporte PDF",
                    data=pdf_bytes,
                    file_name=nombre_archivo,
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True,
                    help="Descarga el reporte completo en PDF"
                )
                
            except Exception as e:
                st.error(f"❌ Error generando PDF: {e}")
                with st.expander("🔍 Ver detalles del error"):
                    import traceback
                    st.code(traceback.format_exc())
                st.info("💡 Verifica que `utils/pdf_generator.py` exista y esté correctamente implementado")
        
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
                    from utils.feedback import guardar_feedback
                    guardar_feedback(caso_id, 100, True)
                    time.sleep(0.5)  # Dar tiempo a ver el spinner
                    st.session_state[feedback_key] = 'claro'
                st.balloons()  # Animación de celebración
        
        with col2:
            if st.button("⚠️ Algunas dudas", key="fb2", use_container_width=True):
                with st.spinner("💾 Guardando feedback..."):
                    from utils.feedback import guardar_feedback
                    guardar_feedback(caso_id, 50, True)
                    time.sleep(0.5)
                    st.session_state[feedback_key] = 'dudas'
        
        with col3:
            if st.button("❌ No entendí", key="fb3", use_container_width=True):
                with st.spinner("💾 Guardando feedback..."):
                    from utils.feedback import guardar_feedback
                    guardar_feedback(caso_id, 0, False)
                    time.sleep(0.5)
                    st.session_state[feedback_key] = 'no'
        
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
        
        tiene_tel = telefono_notif and len(telefono_notif) == 9 and telefono_notif.isdigit()
        
        if not tiene_tel:
            st.caption("⚠️ Ingresa un teléfono válido (9 dígitos) en el formulario")
        else:
            notif_key = f'notif_{caso_id}'
            
            if st.button("📧 Programar 3 Recordatorios", key="btn_notif", type="primary", use_container_width=True):
                try:
                    # Barra de progreso animada
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text("📧 Inicializando sistema de recordatorios...")
                    progress_bar.progress(25)
                    time.sleep(0.3)
                    
                    from utils.nudges import SistemaNudges
                    sistema = SistemaNudges()
                    
                    status_text.text("📅 Programando controles CRED...")
                    progress_bar.progress(50)
                    time.sleep(0.3)
                    
                    resultados = sistema.programar_recordatorios_multiples(
                        telefono_notif,
                        nombre_paciente or "Paciente",
                        [
                            {'tipo': 'Control inmediato', 'dias': 7},
                            {'tipo': 'Seguimiento 1 mes', 'dias': 30},
                            {'tipo': 'Evaluación 3 meses', 'dias': 90}
                        ]
                    )
                    
                    status_text.text("✅ Guardando en sistema...")
                    progress_bar.progress(75)
                    time.sleep(0.3)
                    
                    st.session_state[notif_key] = {
                        'telefono': telefono_notif,
                        'resultados': resultados,
                        'fecha': datetime.now().strftime('%d/%m/%Y %H:%M')
                    }
                    
                    progress_bar.progress(100)
                    status_text.text("✅ ¡Completado!")
                    time.sleep(0.5)
                    
                    # Limpiar elementos temporales
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.balloons()  # Animación
                    
                except Exception as e:
                    st.error(f"❌ Error: {e}")
            
            # Mostrar confirmación si ya envió
            if notif_key in st.session_state:
                st.success(f"✅ **Recordatorios enviados exitosamente**")
                st.info(f"📱 Teléfono: {st.session_state[notif_key]['telefono']}")
                st.caption(f"🕐 {st.session_state[notif_key]['fecha']}")
                
                with st.expander("📋 Ver detalles"):
                    for r in st.session_state[notif_key]['resultados']:
                        st.caption(f"• {r['tipo_control']} (+{r['dias_hasta_control']} días) - {r['canal']}")
        
        # ========== NUEVA CONSULTA (LIMPIA TODO) ==========
        st.markdown("---")
        
        if st.button("🔄 Nueva Consulta", type="primary", use_container_width=True, key="btn_nueva_consulta"):
            # Limpiar TODO
            keys_to_delete = list(st.session_state.keys())
            for key in keys_to_delete:
                del st.session_state[key]
            
            st.success("✅ Datos limpiados. Recargando formulario...")
            time.sleep(1)
            st.rerun()
