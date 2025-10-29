"""
pages/dashboard.py
Dashboard Nacional - Análisis de Equidad y Tendencias
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import subprocess

# Imports de utilidades REALES
from utils.data_loader import DataLoader

# Inicializar cargador de datos
data_loader = DataLoader()

# ============================================================================
# FUNCIONES DE CARGA CON CACHÉ
# ============================================================================

@st.cache_data(ttl=600)
def cargar_datos_brechas():
    """Carga datos de brechas con caché (10 min)"""
    return data_loader.load_brechas_departamento()

@st.cache_data(ttl=600)
def cargar_datos_tendencias():
    """Carga datos de tendencias con caché (10 min)"""
    return data_loader.load_tendencias_departamento()

@st.cache_data(ttl=600)
def cargar_reporte_equidad():
    """Carga reporte de equidad con caché (10 min)"""
    return data_loader.load_reporte_equidad()

# ============================================================================
# PÁGINA PRINCIPAL
# ============================================================================

def pagina_dashboard():
    """Dashboard con estadísticas nacionales y análisis de equidad"""
    
    st.title("📊 Dashboard Nacional de Anemia Infantil")
    st.markdown("Monitoreo de indicadores clave y análisis de equidad territorial.")
    
    st.markdown("---")
    
    # Cargar datos
    with st.spinner("Cargando datos..."):
        df_brechas = cargar_datos_brechas()
        df_tendencias = cargar_datos_tendencias()
        reporte_equidad = cargar_reporte_equidad()
    
    # Validación de datos
    if df_brechas is None or df_tendencias is None:
        st.warning("⚠️ Datos no disponibles. Genera primero los datos de ejemplo.")
        
        if st.button("🔄 Generar Datos de Ejemplo"):
            with st.spinner("Generando datos..."):
                try:
                    subprocess.run(["python", "scripts/generate_sample_data.py"], check=True)
                    st.success("✅ Datos generados. Recarga la página.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error generando datos: {e}")
        return
    
    # Verificar columnas requeridas
    required_cols = ['departamento', 'prevalencia_pct', 'brecha_q4_q1_pp']
    missing_cols = [col for col in required_cols if col not in df_brechas.columns]
    
    if missing_cols:
        st.error(f"❌ Columnas faltantes en datos: {missing_cols}")
        st.info(f"📋 Columnas disponibles: {list(df_brechas.columns)}")
        return
    
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
        if reporte_equidad and 'indice_concentracion' in reporte_equidad:
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
    
    # Tabs para análisis
    tab1, tab2, tab3 = st.tabs(["🗺️ Prevalencia", "⚖️ Brechas de Equidad", "📈 Tendencias"])
    
    with tab1:
        st.subheader("Prevalencia por Departamento")
        
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
            st.write("**🔴 Top 10 Mayores Brechas Internas:**")
            
            df_top_brechas = df_brechas.nlargest(10, 'brecha_q4_q1_pp')[
                ['departamento', 'brecha_q4_q1_pp', 'prevalencia_pct']
            ]
            df_top_brechas.columns = ['Departamento', 'Brecha (pp)', 'Prevalencia (%)']
            
            st.dataframe(df_top_brechas, use_container_width=True, hide_index=True)
        
        # Descomposición Oaxaca-Blinder
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
        
        # Departamentos críticos vs exitosos
        col_crit1, col_crit2 = st.columns(2)
        
        with col_crit1:
            st.write("**🚨 Departamentos con Mayor Crecimiento:**")
            df_creciente = df_tendencias.nlargest(5, 'tendencia_pp_mes')[
                ['departamento', 'tendencia_pp_mes', 'prevalencia_actual_pct']
            ]
            df_creciente.columns = ['Departamento', 'Tendencia (pp/mes)', 'Prevalencia Actual (%)']
            st.dataframe(df_creciente, use_container_width=True, hide_index=True)
        
        with col_crit2:
            st.write("**✅ Departamentos con Declive:**")
            df_decreciente = df_tendencias.nsmallest(5, 'tendencia_pp_mes')[
                ['departamento', 'tendencia_pp_mes', 'prevalencia_actual_pct']
            ]
            df_decreciente.columns = ['Departamento', 'Tendencia (pp/mes)', 'Prevalencia Actual (%)']
            st.dataframe(df_decreciente, use_container_width=True, hide_index=True)
