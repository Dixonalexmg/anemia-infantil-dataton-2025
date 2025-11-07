"""
pages/terminos_condiciones.py - Términos y Condiciones
Sistema de Combate a la Anemia Infantil - Datatón 2025
"""

import streamlit as st

def pagina_terminos_condiciones():
    """Página de Términos y Condiciones"""

    st.markdown("""
    # 📜 Términos y Condiciones

    **NutriSenseIA - Sistema de Prevención de Anemia Infantil**

    Datatón 2025 | Ministerio de Salud del Perú

    ---

    ## 1. Aceptación de Términos

    Al acceder y utilizar NutriSenseIA, aceptas cumplir con estos 
    términos y condiciones en su totalidad.


    ## 2. Descripción del Servicio

    NutriSenseIA es un sistema de demostración diseñado para:

    - Evaluar riesgo de anemia en niños menores de 5 años
    - Proporcionar recomendaciones de nutrición
    - Simular escenarios de mejora
    - Educación sobre prevención de anemia


    ## 3. Naturaleza Demostrativa

    ⚠️ **IMPORTANTE**: 

    - Este es un sistema de **DEMOSTRACIÓN**
    - Utiliza **DATOS FICTICIOS**
    - **NO** es un instrumento médico oficial
    - **NO** reemplaza la consulta médica
    - Las recomendaciones son ilustrativas


    ## 4. Limitación de Responsabilidad

    El Ministerio de Salud del Perú y los desarrolladores 
    **NO son responsables** por:

    - Pérdida de datos
    - Interrupciones del servicio
    - Daños resultantes del uso del sistema
    - Decisiones médicas basadas en este sistema

    **Siempre consulta con profesionales de salud para decisiones médicas reales.**


    ## 5. Propiedad Intelectual

    - Todo contenido es propiedad del Ministerio de Salud
    - Está protegido por derechos de autor
    - Solo para uso educativo y de demostración


    ## 6. Uso Aceptable

    Aceptas no:

    - Usar el sistema para fines ilegales
    - Intentar hackear o comprometer la seguridad
    - Distribuir información de acceso
    - Modificar o reproducir el código


    ## 7. Cuentas de Usuario

    - Eres responsable de mantener la confidencialidad
    - Un usuario puede tener múltiples cuentas
    - Las cuentas son para demostración


    ## 8. Modificaciones del Servicio

    Nos reservamos el derecho de:

    - Cambiar o descontinuar el servicio
    - Modificar características
    - Actualizar términos sin previo aviso


    ## 9. Ley Aplicable

    Estos términos se rigen por las leyes de la República del Perú.


    ## 10. Contacto

    Para dudas sobre estos términos:

    📧 dataton@minsa.gob.pe

    🏢 Ministerio de Salud del Perú


    ---

    **Última actualización:** Noviembre 2025

    **Versión:** 1.0 - Datatón 2025

    **Al ingresar, aceptas estos términos y condiciones.**
    """)

    st.markdown("---")
    if st.button("← Volver al Inicio"):
        st.session_state.pagina_actual = 'inicio'
        st.rerun()