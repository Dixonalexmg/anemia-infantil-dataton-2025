# pages/mapa.py
"""
HU-04: Mapa Territorial con Alertas de Hotspots y Pronóstico de Stock
Filtrado simple: Distrito + Mes
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def pagina_mapa_territorial():
    """Mapa de calor territorial con detección de hotspots"""
    
    # HEADER
    st.markdown("""
    <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem;'>
        <div style='display: flex; align-items: center; gap: 1rem;'>
            <div style='font-size: 3rem;'>🗺️</div>
            <div>
                <h1 style='color: white; margin: 0;'>Mapa Territorial de Anemia</h1>
                <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;'>
                    Detección de zonas críticas y alertas de stock
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ========== FILTROS SIMPLES (SOLO 2) ==========
    st.markdown("### 🔍 Filtros")
    col1, col2 = st.columns(2)
    
    with col1:
        departamento_seleccionado = st.selectbox(
            "Departamento",
            ["TODOS"] + [
                "AMAZONAS", "ANCASH", "APURIMAC", "AREQUIPA", "AYACUCHO",
                "CAJAMARCA", "CUSCO", "HUANCAVELICA", "HUANUCO", "ICA",
                "JUNIN", "LA LIBERTAD", "LAMBAYEQUE", "LIMA", "LORETO",
                "MADRE DE DIOS", "MOQUEGUA", "PASCO", "PIURA", "PUNO",
                "SAN MARTIN", "TACNA", "TUMBES", "UCAYALI"
            ]
        )
    
    with col2:
        mes_seleccionado = st.selectbox(
            "Mes de análisis",
            ["Octubre 2025", "Septiembre 2025", "Agosto 2025", 
             "Julio 2025", "Junio 2025", "Mayo 2025"]
        )
    
    st.markdown("---")
    
    # ========== CARGAR DATOS ==========
    df_territorial = cargar_datos_territoriales(departamento_seleccionado, mes_seleccionado)
    
    # ========== ALERTAS DE HOTSPOTS ==========
    st.markdown("## 🚨 Alertas de Zonas Críticas")
    
    hotspots = detectar_hotspots(df_territorial, umbral_critico=45)
    
    if len(hotspots) > 0:
        st.error(f"⚠️ **{len(hotspots)} ZONAS EN ESTADO CRÍTICO** - Prevalencia >45%")
        
        for idx, zona in hotspots.iterrows():
            col_a, col_b, col_c = st.columns([3, 2, 2])
            with col_a:
                st.markdown(f"**🔴 {zona['distrito']}**")
            with col_b:
                st.metric("Prevalencia", f"{zona['prevalencia']:.1f}%", delta=f"{zona['tendencia']:.1f}pp")
            with col_c:
                st.metric("Casos", int(zona['casos_estimados']))
        
        st.markdown("---")
    else:
        st.success("✅ No se detectaron zonas en estado crítico en este período")
    
    # ========== MAPA DE CALOR ==========
    st.markdown("## 🗺️ Mapa de Calor de Prevalencia")
    
    fig_mapa = crear_mapa_calor(df_territorial, departamento_seleccionado)
    st.plotly_chart(fig_mapa, use_container_width=True)
    
    # ========== RANKING DE DISTRITOS ==========
    st.markdown("---")
    st.markdown("## 📊 Ranking de Distritos por Prevalencia")
    
    df_ranking = df_territorial.sort_values('prevalencia', ascending=False).head(10)
    
    fig_ranking = go.Figure()
    
    colores = ['#ff4444' if p >= 45 else '#ffa500' if p >= 35 else '#4CAF50' 
               for p in df_ranking['prevalencia']]
    
    fig_ranking.add_trace(go.Bar(
        x=df_ranking['prevalencia'],
        y=df_ranking['distrito'],
        orientation='h',
        marker=dict(color=colores),
        text=df_ranking['prevalencia'].apply(lambda x: f"{x:.1f}%"),
        textposition='outside'
    ))
    
    fig_ranking.update_layout(
        title="Top 10 Distritos con Mayor Prevalencia de Anemia",
        xaxis_title="Prevalencia (%)",
        yaxis_title="",
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig_ranking, use_container_width=True)
    
    # ========== PRONÓSTICO DE STOCK ==========
    st.markdown("---")
    st.markdown("## 📦 Pronóstico de Quiebre de Stock")
    
    with st.expander("ℹ️ ¿Qué es el pronóstico de stock?"):
        st.markdown("""
        Este módulo alerta sobre posibles quiebres de stock de **suplementos de hierro** 
        y **alimentos fortificados** en establecimientos de salud.
        
        **Semáforo:**
        - 🟢 Verde: Stock >60% del consumo mensual
        - 🟡 Amarillo: Stock 30-60% (reposición recomendada)
        - 🔴 Rojo: Stock <30% (crítico - reposición urgente)
        """)
    
    # Tabs por tipo de insumo
    tab_hierro, tab_alimentos = st.tabs(["💊 Suplementos de Hierro", "🥫 Alimentos Fortificados"])
    
    with tab_hierro:
        st.markdown("### Estado de Stock de Suplementos de Hierro")
        df_stock_hierro = generar_datos_stock("hierro", departamento_seleccionado)
        mostrar_alertas_stock(df_stock_hierro)
    
    with tab_alimentos:
        st.markdown("### Estado de Stock de Alimentos Fortificados")
        df_stock_alimentos = generar_datos_stock("alimentos", departamento_seleccionado)
        mostrar_alertas_stock(df_stock_alimentos)
    
    # ========== DESCARGA DE REPORTE PDF POR ROL ==========
    st.markdown("---")
    st.markdown("## 📥 Descargar Reporte por Rol")
    
    col_rol, col_btn = st.columns([2, 1])
    
    with col_rol:
        rol_reporte = st.selectbox(
            "Selecciona el tipo de reporte:",
            [
                "👨‍⚕️ Reporte para Profesional de Salud",
                "🏛️ Reporte para Entidad (DIRESA/GERESA)",
                "👩‍👧 Reporte para Madre/Cuidador"
            ]
        )
    
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📄 Generar PDF", use_container_width=True, type="primary"):
            with st.spinner("Generando reporte..."):
                pdf_path = generar_reporte_pdf_rol(
                    rol_reporte, 
                    df_territorial, 
                    hotspots, 
                    departamento_seleccionado, 
                    mes_seleccionado
                )
                
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        "⬇️ Descargar Reporte",
                        f,
                        file_name=f"reporte_{rol_reporte.split()[0]}_{mes_seleccionado.replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                
                st.success("✅ Reporte generado exitosamente")


# ========== FUNCIONES AUXILIARES ==========

def cargar_datos_territoriales(departamento, mes):
    """Carga datos territoriales simulados"""
    # En producción, esto vendría de una base de datos real
    
    distritos = [
        "Acobamba", "Angaraes", "Castrovirreyna", "Churcampa", "Huancavelica",
        "Huaytará", "Tayacaja", "Azángaro", "Carabaya", "Chucuito", "El Collao",
        "Huancané", "Lampa", "Melgar", "Moho", "Puno", "San Antonio de Putina",
        "San Román", "Sandia", "Yunguyo", "Chumbivilcas", "Espinar", "La Convención",
        "Quispicanchi", "Urubamba"
    ]
    
    np.random.seed(42)
    
    data = []
    for distrito in distritos:
        if departamento != "TODOS":
            if not any(d in distrito for d in ["Aco", "Ang", "Cast", "Chur", "Hua", "Huay", "Tay"]):
                continue
        
        data.append({
            'distrito': distrito,
            'prevalencia': np.random.normal(42, 8),
            'casos_estimados': np.random.randint(100, 800),
            'tendencia': np.random.normal(-2, 3),
            'cobertura_suplemento': np.random.normal(65, 15),
            'lat': np.random.uniform(-14, -12),
            'lon': np.random.uniform(-75, -73)
        })
    
    return pd.DataFrame(data)


def detectar_hotspots(df, umbral_critico=45):
    """Detecta zonas críticas automáticamente"""
    hotspots = df[df['prevalencia'] >= umbral_critico].copy()
    hotspots = hotspots.sort_values('prevalencia', ascending=False)
    return hotspots


def crear_mapa_calor(df, departamento):
    """Crea mapa de calor con Plotly"""
    
    fig = px.scatter_geo(
        df,
        lat='lat',
        lon='lon',
        size='casos_estimados',
        color='prevalencia',
        hover_name='distrito',
        hover_data={
            'prevalencia': ':.1f',
            'casos_estimados': ':,',
            'tendencia': ':.1f',
            'lat': False,
            'lon': False
        },
        color_continuous_scale=[
            [0, '#4CAF50'],      # Verde (baja prevalencia)
            [0.5, '#FFC107'],    # Amarillo (media)
            [1, '#F44336']       # Rojo (alta)
        ],
        range_color=[20, 60],
        title=f"Mapa de Calor - Prevalencia de Anemia ({departamento})"
    )
    
    fig.update_geos(
        visible=False,
        resolution=50,
        scope="south america",
        showcountries=True,
        countrycolor="lightgray",
        center=dict(lat=-12, lon=-75),
        projection_scale=8
    )
    
    fig.update_layout(height=500, coloraxis_colorbar=dict(title="Prevalencia (%)"))
    
    return fig


def generar_datos_stock(tipo_insumo, departamento):
    """Genera datos simulados de stock"""
    establecimientos = [
        "Hospital Regional",
        "Centro de Salud A",
        "Centro de Salud B",
        "Puesto de Salud 1",
        "Puesto de Salud 2",
        "Puesto de Salud 3"
    ]
    
    np.random.seed(42)
    
    data = []
    for est in establecimientos:
        consumo_mensual = np.random.randint(500, 2000)
        stock_actual = np.random.randint(100, 1500)
        dias_stock = (stock_actual / consumo_mensual) * 30
        
        # Clasificar por semáforo
        if dias_stock > 18:  # >60% del mes
            nivel = "🟢 Normal"
            color = "success"
        elif dias_stock > 9:  # 30-60%
            nivel = "🟡 Alerta"
            color = "warning"
        else:
            nivel = "🔴 Crítico"
            color = "error"
        
        data.append({
            'establecimiento': est,
            'stock_actual': stock_actual,
            'consumo_mensual': consumo_mensual,
            'dias_stock': dias_stock,
            'nivel': nivel,
            'color': color
        })
    
    return pd.DataFrame(data)


def mostrar_alertas_stock(df_stock):
    """Muestra alertas de stock por establecimiento"""
    
    for idx, row in df_stock.iterrows():
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        
        with col1:
            st.markdown(f"**{row['establecimiento']}**")
        
        with col2:
            st.markdown(f"{row['nivel']}")
        
        with col3:
            st.metric("Stock Actual", f"{row['stock_actual']:,} unidades")
        
        with col4:
            st.metric("Días restantes", f"{row['dias_stock']:.0f} días")
        
        if row['color'] == 'error':
            st.error(f"⚠️ **REPOSICIÓN URGENTE REQUERIDA** - Stock crítico en {row['establecimiento']}")
        elif row['color'] == 'warning':
            st.warning(f"💡 Reposición recomendada en las próximas 2 semanas")


def generar_reporte_pdf_rol(rol, df_territorial, hotspots, departamento, mes):
    """Genera PDF personalizado por rol"""
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    import io
    
    # Crear PDF en memoria
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # HEADER
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 50, f"Reporte de Anemia Infantil - {departamento}")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 75, f"Período: {mes}")
    c.drawString(50, height - 95, f"Tipo de Reporte: {rol}")
    c.drawString(50, height - 115, f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    # LÍNEA SEPARADORA
    c.line(50, height - 130, width - 50, height - 130)
    
    y_pos = height - 160
    
    # CONTENIDO POR ROL
    if "Profesional" in rol:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_pos, "📊 Resumen para Profesional de Salud")
        y_pos -= 30
        
        c.setFont("Helvetica", 11)
        c.drawString(70, y_pos, f"• Zonas críticas detectadas: {len(hotspots)}")
        y_pos -= 20
        c.drawString(70, y_pos, f"• Prevalencia promedio: {df_territorial['prevalencia'].mean():.1f}%")
        y_pos -= 20
        c.drawString(70, y_pos, f"• Casos estimados totales: {df_territorial['casos_estimados'].sum():,}")
        y_pos -= 30
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_pos, "Recomendaciones Clínicas:")
        y_pos -= 20
        c.setFont("Helvetica", 10)
        c.drawString(70, y_pos, "1. Intensificar suplementación en zonas críticas")
        y_pos -= 15
        c.drawString(70, y_pos, "2. Aumentar consejería nutricional a madres")
        y_pos -= 15
        c.drawString(70, y_pos, "3. Coordinar con nutricionistas para menús personalizados")
    
    elif "Entidad" in rol:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_pos, "🏛️ Resumen para Entidad (DIRESA/GERESA)")
        y_pos -= 30
        
        c.setFont("Helvetica", 11)
        c.drawString(70, y_pos, f"• Departamentos con mayor prevalencia: {len(hotspots)}")
        y_pos -= 20
        c.drawString(70, y_pos, "• Presupuesto recomendado para intervención: S/ 450,000")
        y_pos -= 20
        c.drawString(70, y_pos, "• Personal adicional requerido: 12 nutricionistas")
        y_pos -= 30
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_pos, "Acciones Estratégicas:")
        y_pos -= 20
        c.setFont("Helvetica", 10)
        c.drawString(70, y_pos, "1. Asignar recursos prioritarios a hotspots")
        y_pos -= 15
        c.drawString(70, y_pos, "2. Implementar NutriSenseIA en zonas críticas")
        y_pos -= 15
        c.drawString(70, y_pos, "3. Monitoreo mensual de indicadores")
    
    else:  # Madre/Cuidador
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_pos, "👩‍👧 Reporte para Madre/Cuidador")
        y_pos -= 30
        
        c.setFont("Helvetica", 11)
        c.drawString(70, y_pos, "Tu zona tiene una prevalencia de anemia del 42.3%")
        y_pos -= 20
        c.drawString(70, y_pos, "Esto significa que 4 de cada 10 niños tienen anemia")
        y_pos -= 30
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_pos, "¿Qué puedes hacer?")
        y_pos -= 20
        c.setFont("Helvetica", 10)
        c.drawString(70, y_pos, "✓ Seguir los menús personalizados de NutriSenseIA")
        y_pos -= 15
        c.drawString(70, y_pos, "✓ Dar el suplemento de hierro diariamente")
        y_pos -= 15
        c.drawString(70, y_pos, "✓ Incluir limón o naranja en las comidas")
        y_pos -= 15
        c.drawString(70, y_pos, "✓ Asistir a los controles de crecimiento")
    
    # FOOTER
    c.line(50, 50, width - 50, 50)
    c.setFont("Helvetica", 8)
    c.drawString(50, 35, "NutriSenseIA - Sistema de Prevención de Anemia Infantil")
    c.drawString(width - 200, 35, "MINSA - Datatón 2025")
    
    c.save()
    buffer.seek(0)
    
    # Guardar temporalmente
    pdf_filename = f"data/reports/reporte_{rol.split()[0]}_{mes.replace(' ', '_')}.pdf"
    with open(pdf_filename, "wb") as f:
        f.write(buffer.getvalue())
    
    return pdf_filename
