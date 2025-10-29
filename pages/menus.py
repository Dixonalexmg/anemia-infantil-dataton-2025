# pages/menus.py
"""
HU-02: Menús Personalizados con Recomendador Inteligente
"""

import streamlit as st
from utils.menu_recommender import MenuRecommender
from utils.menu_substitutions import MenuSubstitutionEngine, crear_alerta_citrico
from utils.adherencia import registrar_adherencia
from utils.pdf_menu_generator import generar_pdf_menu, generar_pdf_semanal
from utils.whatsapp_sender import enviar_menu_whatsapp
from datetime import datetime
import uuid
import pandas as pd


def pagina_menus():
    """Página de menús personalizados con IA"""

    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem;'>
        <div style='display: flex; align-items: center; gap: 1rem;'>
            <div style='font-size: 3rem;'>🍽️</div>
            <div>
                <h1 style='color: white; margin: 0;'>Menús Personalizados NutriSenseIA</h1>
                <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;'>
                    Recomendaciones inteligentes basadas en hierro, costo y disponibilidad regional
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 👶 Datos del Niño/a")
    col1, col2, col3 = st.columns(3)
    with col1:
        edad_meses = st.number_input("Edad (meses)", 6, 59, 18, 1)
    with col2:
        departamento = st.selectbox("Departamento", 
            ["LIMA", "CUSCO", "PUNO", "AREQUIPA", "JUNIN", "AYACUCHO",
             "HUANCAVELICA", "CAJAMARCA", "PIURA", "LA LIBERTAD"])
    with col3:
        presupuesto_diario = st.number_input("Presupuesto diario (S/)", 5.0, 50.0, 15.0, 1.0)
    
    telefono_whatsapp = st.text_input("📱 WhatsApp (opcional, 9 dígitos)", max_chars=9, 
                                      help="Para enviar el menú por WhatsApp")
    
    if 'caso_id_menus' not in st.session_state:
        st.session_state.caso_id_menus = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    caso_id = st.session_state.caso_id_menus
    st.markdown("---")

    recomendador = MenuRecommender()
    motor_sustitucion = MenuSubstitutionEngine()
    contexto_paciente = {
        'departamento': departamento,
        'edad_meses': edad_meses,
        'presupuesto_diario_s': presupuesto_diario
    }

    # ========== MENÚS BASE COMPLETOS ==========
    menus_base = [
        {'id': 'desayuno_andino', 'nombre': 'Desayuno Andino Fortificado', 'tipo': 'desayuno',
         'plato_principal': 'Quinua con leche y huevo',
         'ingredientes': [{'id': 'quinua', 'cantidad_g': 80}, {'id': 'huevo', 'cantidad_g': 60}],
         'preparacion': 'Cocinar quinua en agua hasta que esté suave. Servir caliente con huevo sancochado picado.',
         'beneficio_educativo': '💪 Aporta 4.3 mg de hierro - cubre 43% del requerimiento diario. La quinua andina es proteína completa.'},
        
        {'id': 'desayuno_costero', 'nombre': 'Desayuno Costeño con Pescado', 'tipo': 'desayuno',
         'plato_principal': 'Tortilla de bonito',
         'ingredientes': [{'id': 'pescado_bonito', 'cantidad_g': 80}, {'id': 'huevo', 'cantidad_g': 60}],
         'preparacion': 'Desmenuzar bonito cocido, mezclar con huevo batido y hacer tortilla.',
         'beneficio_educativo': '🐟 Aporta 2.1 mg de hierro + omega-3 para el cerebro del bebé'},
        
        {'id': 'desayuno_economico', 'nombre': 'Desayuno Económico con Menestra', 'tipo': 'desayuno',
         'plato_principal': 'Frijoles con huevo',
         'ingredientes': [{'id': 'frijoles', 'cantidad_g': 100}, {'id': 'huevo', 'cantidad_g': 60}],
         'preparacion': 'Calentar frijoles cocidos, servir con huevo frito. Agregar limón.',
         'beneficio_educativo': '🍋 Aporta 3.2 mg de hierro - el limón aumenta absorción en 4x'},
        
        {'id': 'almuerzo_higado', 'nombre': 'Saltado de Hígado Nutritivo', 'tipo': 'almuerzo',
         'plato_principal': 'Hígado saltado con espinaca',
         'ingredientes': [{'id': 'higado_res', 'cantidad_g': 100}, {'id': 'espinaca', 'cantidad_g': 80}],
         'preparacion': 'Saltear hígado en trozos pequeños con cebolla. Agregar espinaca al final.',
         'beneficio_educativo': '🩸 Aporta 8.7 mg de hierro hemo - el más alto (87% del requerimiento diario)'},
        
        {'id': 'almuerzo_sangrecita', 'nombre': 'Guiso de Sangrecita Super Nutritivo', 'tipo': 'almuerzo',
         'plato_principal': 'Sangrecita con menestra',
         'ingredientes': [{'id': 'sangrecita', 'cantidad_g': 80}, {'id': 'lentejas', 'cantidad_g': 100}],
         'preparacion': 'Guisar sangrecita con ají amarillo. Servir con lentejas cocidas.',
         'beneficio_educativo': '⚡ Aporta 26.9 mg de hierro - récord absoluto (269% del requerimiento)'},
        
        {'id': 'almuerzo_bazo', 'nombre': 'Saltado de Bazo Económico', 'tipo': 'almuerzo',
         'plato_principal': 'Bazo con verduras',
         'ingredientes': [{'id': 'bazo', 'cantidad_g': 100}, {'id': 'espinaca', 'cantidad_g': 80}],
         'preparacion': 'Saltear bazo cortado en cubitos con verduras mixtas.',
         'beneficio_educativo': '💰 Aporta 6.8 mg de hierro - nutritivo y económico (68% del requerimiento)'},
        
        {'id': 'cena_menestra_citrico', 'nombre': 'Cena Vegetariana con Cítrico', 'tipo': 'cena',
         'plato_principal': 'Lentejas con limón',
         'ingredientes': [{'id': 'lentejas', 'cantidad_g': 150}, {'id': 'espinaca', 'cantidad_g': 80}],
         'preparacion': 'Cocinar lentejas con comino. Servir con espinaca cocida y mucho limón.',
         'beneficio_educativo': '🍋 Aporta 7.1 mg de hierro no hemo - el limón lo hace más absorbible'},
        
        {'id': 'cena_frijoles_naranja', 'nombre': 'Cena con Frijoles y Naranja', 'tipo': 'cena',
         'plato_principal': 'Frijoles con jugo de naranja',
         'ingredientes': [{'id': 'frijoles', 'cantidad_g': 150}],
         'preparacion': 'Cocinar frijoles con ajo. Servir con vaso de jugo de naranja natural.',
         'beneficio_educativo': '🍊 Aporta 3.8 mg de hierro - la vitamina C de la naranja mejora absorción 400%'},
        
        {'id': 'cena_cuy_tradicional', 'nombre': 'Cena Andina con Cuy', 'tipo': 'cena',
         'plato_principal': 'Cuy al horno tradicional',
         'ingredientes': [{'id': 'cuy', 'cantidad_g': 150}],
         'preparacion': 'Marinar cuy con hierbas andinas. Hornear hasta dorar.',
         'beneficio_educativo': '🏔️ Aporta 4.8 mg de hierro - tradición andina con alta proteína'}
    ]

    with st.spinner("🤖 Analizando mejores menús..."):
        top3_menus = recomendador.recomendar_top3(menus_base, contexto_paciente)

    if not top3_menus or len(top3_menus) < 3:
        st.error("❌ No se encontraron suficientes menús. Ajusta presupuesto o región.")
        return

    st.success(f"✅ {len(top3_menus)} menús optimizados para {departamento}")

    # ========== TABS DE MENÚS ==========
    tabs = st.tabs([f"🥇 {top3_menus[0]['nombre'][:25]}", f"🥈 {top3_menus[1]['nombre'][:25]}", 
                    f"🥉 {top3_menus[2]['nombre'][:25]}"])
    
    for idx, (tab, menu) in enumerate(zip(tabs, top3_menus), 1):
        with tab:
            col1, col2 = st.columns([1, 5])
            with col1:
                st.markdown(f"<div style='font-size:5rem;text-align:center'>{['🥇','🥈','🥉'][idx-1]}</div>", 
                           unsafe_allow_html=True)
            with col2:
                st.markdown(f"## {menu['nombre']}")
                st.caption(f"**{menu['tipo'].title()}** - {menu['plato_principal']}")
            
            st.markdown("---")
            desglose = menu['desglose']
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("🩸 Hierro", f"{desglose['hierro_mg']:.1f} mg")
            c2.metric("💰 Costo", f"S/ {desglose['costo_s']:.2f}")
            c3.metric("📊 Nutri", f"{desglose['score_nutri']:.0f}/100")
            c4.metric("⭐ Total", f"{menu['score']:.0f}/100")
            
            st.info(menu['beneficio_educativo'])
            
            with st.expander("🍳 Receta"):
                st.markdown("**Ingredientes:**")
                for ing in menu['ingredientes']:
                    info = recomendador.catalogo_dict.get(ing['id'])
                    if info:
                        st.caption(f"• {ing['cantidad_g']}g {info['nombre']}")
                st.markdown(f"**Preparación:** {menu['preparacion']}")
            
            with st.expander("🔄 ¿No tienes algún ingrediente? Ver alternativas"):
                hay_sustitutos = False
                for ing in menu['ingredientes']:
                    sust = motor_sustitucion.sugerir_sustituto(
                        ingrediente_faltante=ing['id'],
                        departamento=departamento,
                        presupuesto_max=presupuesto_diario/3,
                        prioridad="costo"
                    )
                    
                    if sust and len(sust) > 0:
                        hay_sustitutos = True
                        info_ing = recomendador.catalogo_dict.get(ing['id'])
                        ing_nombre = info_ing['nombre'] if info_ing else ing['id']
                        
                        st.markdown(f"**Si no tienes {ing_nombre}:**")
                        mejor_sustituto = sust[0]
                        mensaje = motor_sustitucion.generar_mensaje_sustitucion(
                            ing['id'], mejor_sustituto, contexto="simple"
                        )
                        st.markdown(mensaje)
                        
                        if len(sust) > 1:
                            otros = ", ".join([s['nombre'] for s in sust[1:]])
                            st.caption(f"💡 Otras opciones: {otros}")
                        st.markdown("---")
                
                if not hay_sustitutos:
                    st.info("✅ Todos los ingredientes de este menú son esenciales y no tienen sustitutos equivalentes.")
            
            # ========== DESCARGAR/ENVIAR ==========
            st.markdown("---")
            col_pdf, col_whats = st.columns(2)
            with col_pdf:
                if st.button(f"📄 Descargar PDF", key=f"pdf_{menu['id']}", use_container_width=True):
                    pdf_path = generar_pdf_menu(menu)
                    with open(pdf_path, "rb") as f:
                        st.download_button("⬇️ Descargar", f, file_name=f"menu_{menu['id']}.pdf", 
                                          mime="application/pdf", use_container_width=True)
            
            with col_whats:
                if telefono_whatsapp and len(telefono_whatsapp) == 9:
                    if st.button(f"📱 Enviar WhatsApp", key=f"whats_{menu['id']}", use_container_width=True):
                        with st.spinner("Enviando..."):
                            resultado = enviar_menu_whatsapp(telefono_whatsapp, menu)
                            st.success("✅ Enviado!") if resultado['exito'] else st.error(f"❌ Error: {resultado['mensaje']}")
                else:
                    st.caption("⚠️ Ingresa teléfono válido")

    # ========== MENÚ SEMANAL ==========
    st.markdown("---")
    st.markdown("### 🗓️ Menú Semanal Personalizado")
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    semanal = [{'dia': d, 'desayuno': top3_menus[i%3], 'almuerzo': top3_menus[(i+1)%3], 
                'cena': top3_menus[(i+2)%3]} for i, d in enumerate(dias)]
    
    tabla = pd.DataFrame([{'Día': m['dia'], 'Desayuno': m['desayuno']['nombre'], 
                           'Almuerzo': m['almuerzo']['nombre'], 'Cena': m['cena']['nombre']} 
                          for m in semanal])
    st.table(tabla)
    
    col_sem1, col_sem2 = st.columns(2)
    with col_sem1:
        if st.button("📄 Descargar Menú Semanal PDF", use_container_width=True):
            pdf_path = generar_pdf_semanal(semanal)
            with open(pdf_path, "rb") as f:
                st.download_button("⬇️ Descargar Semanal", f, "menu_semanal.pdf", 
                                  "application/pdf", use_container_width=True)
    
    with col_sem2:
        if telefono_whatsapp and len(telefono_whatsapp) == 9:
            if st.button("📱 Enviar Semanal por WhatsApp", use_container_width=True):
                with st.spinner("Enviando..."):
                    resultado = enviar_menu_whatsapp(telefono_whatsapp, semanal, es_semanal=True)
                    st.success("✅ Enviado!") if resultado['exito'] else st.error(f"❌ {resultado['mensaje']}")

    # ========== TIPS ==========
    st.markdown("---")
    st.markdown("## 💡 Tips para Mejorar Absorción de Hierro")
    c1, c2, c3 = st.columns(3)
    c1.markdown("### 🍋 Combinar con Vitamina C\n- Jugo de naranja\n- Limón\n**Aumenta 3-4x**")
    c2.markdown("### ⏰ Horarios Óptimos\n- Desayuno 9am\n- Almuerzo 12pm\n**Mejor digestión**")
    c3.markdown("### ❌ Evitar\n- Té o café\n- Leche simultánea\n**Bloquean absorción**")
