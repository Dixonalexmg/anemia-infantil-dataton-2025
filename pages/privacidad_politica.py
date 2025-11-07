"""
pages/privacidad_politica.py - Política de Privacidad
Sistema de Combate a la Anemia Infantil - Datatón 2025
"""

import streamlit as st

def pagina_privacidad_politica():
    """Página de Política de Privacidad"""

    st.markdown("""
    # 📋 Política de Privacidad

    **NutriSenseIA - Sistema de Prevención de Anemia Infantil**

    Datatón 2025 | Ministerio de Salud del Perú

    ---

    ## 1. Introducción

    NutriSenseIA es un sistema de demostración desarrollado para el Datatón 2025 
    del Ministerio de Salud del Perú. Este documento describe cómo manejamos 
    la privacidad y protección de datos.


    ## 2. Naturaleza de los Datos

    ⚠️ **IMPORTANTE**: Este es un sistema de **demostración** que utiliza 
    **datos ficticios** para propósitos educativos y de presentación.

    - Todos los datos son ejemplos ficticios
    - NO se recopilan datos reales de usuarios
    - NO hay conexión a sistemas reales de MINSA
    - Los resultados son simulaciones


    ## 3. Recolección de Datos

    Durante el uso del sistema, podemos recopilar:

    - Nombre de usuario
    - Rol asignado
    - Acciones dentro del sistema
    - Preferencias de idioma

    **Estos datos se usan SOLO para:**
    - Proporcionar la funcionalidad del sistema
    - Mejorar la experiencia de usuario
    - Fines de demostración


    ## 4. Almacenamiento de Datos

    - Datos almacenados localmente en la sesión
    - NO se persisten después de cerrar sesión
    - NO se envían a servidores externos
    - NO se comparten con terceros


    ## 5. Seguridad

    Aunque este es un sistema de demostración:

    - Usamos autenticación básica
    - Control de roles por usuario
    - Datos ficticios para proteger privacidad


    ## 6. Derechos del Usuario

    Como usuario puedes:

    - Acceder a tus datos en cualquier momento
    - Solicitar la eliminación de datos
    - Obtener información sobre el sistema


    ## 7. Contacto

    Para preguntas sobre privacidad:

    📧 dataton@minsa.gob.pe

    🏢 Ministerio de Salud del Perú


    ## 8. Cambios a Esta Política

    Nos reservamos el derecho de actualizar esta política 
    en cualquier momento. Los cambios entrarán en vigencia 
    inmediatamente después de su publicación.


    ---

    **Última actualización:** Noviembre 2025

    **Versión:** 1.0 - Datatón 2025
    """)

    st.markdown("---")
    if st.button("← Volver al Inicio"):
        st.session_state.pagina_actual = 'inicio'
        st.rerun()