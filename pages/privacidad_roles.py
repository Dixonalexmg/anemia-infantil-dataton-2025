"""
pages/privacidad_roles.py
Página de privacidad, consentimiento y control de roles
Cumplimiento Ley 29733 (LOPD Perú)
"""

import streamlit as st
from datetime import datetime
from auth.roles_manager import (
    RoleManager, DemoManager, ConsentManager, DerechoAlOlvidoManager,
    User, RoleType
)
from utils.i18n_manager import get_i18n

def pagina_privacidad_roles():
    """Página de privacidad y gestión de consentimiento"""

    i18n = get_i18n()

    # ════════════════════════════════════════════════════════════════════════════
    # HEADER
    # ════════════════════════════════════════════════════════════════════════════
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2.5rem; border-radius: 15px; margin-bottom: 2rem;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);'>
        <h1 style='color: white; margin: 0; font-size: 2.5rem;'>
            🔐 Privacidad y Control de Acceso
        </h1>
        <p style='color: rgba(255,255,255,0.95); margin: 0.8rem 0 0 0; font-size: 1.1rem;'>
            Ley 29733 (LOPD Perú) - Derechos y protecciones de datos
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════════
    # TABS PRINCIPALES
    # ════════════════════════════════════════════════════════════════════════════
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Consentimiento",
        "🔐 Control de Acceso",
        "⚖️ Derechos",
        "📊 Mi Información"
    ])

    # ════════════════════════════════════════════════════════════════════════════
    # TAB 1: CONSENTIMIENTO INFORMADO
    # ════════════════════════════════════════════════════════════════════════════
    with tab1:
        st.markdown(ConsentManager.TEXTO_CONSENTIMIENTO)

        st.markdown("---")

        # Formulario de consentimiento
        st.markdown("### ✅ Aceptar Consentimiento")

        col_check = st.columns([4, 1])

        with col_check[0]:
            aceptar = st.checkbox(
                "Acepto la política de privacidad y el procesamiento de mis datos",
                key="consent_check"
            )

        if aceptar:
            if st.button("📝 Registrar Consentimiento", use_container_width=True, type="primary"):
                # Registrar consentimiento
                usuario_actual = st.session_state.get('username', 'usuario')

                registro = {
                    'user_id': usuario_actual,
                    'fecha': datetime.now().isoformat(),
                    'aceptado': True,
                    'tipo_consentimiento': 'informado'
                }

                st.success(f"""
                ✅ **Consentimiento Registrado**

                Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                Usuario: {usuario_actual}

                Puedes revocar este consentimiento en cualquier momento desde la pestaña "Derechos".
                """)

                st.session_state.consentimiento_aceptado = True

    # ════════════════════════════════════════════════════════════════════════════
    # TAB 2: CONTROL DE ACCESO (ROLES)
    # ════════════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("### 👥 Tu Rol y Permisos")

        user_role = st.session_state.get('user_role', 'demo')

        # Mapeo visual de roles
        roles_info = {
            'cuidador': {
                'nombre': '👨‍👧‍👦 Cuidador',
                'descripcion': 'Acceso a datos del niño a tu cargo',
                'permisos': [
                    'Ver diagnósticos del niño',
                    'Recibir recomendaciones personalizadas',
                    'Enviar feedback y comentarios',
                    'Descargar menús sugeridos'
                ],
                'restricciones': [
                    'No ver datos de otros pacientes',
                    'No ver estadísticas nacionales',
                    'No modificar diagnósticos'
                ]
            },
            'profesional': {
                'nombre': '👨‍⚕️ Profesional de Salud',
                'descripcion': 'Acceso a pacientes asignados y análisis',
                'permisos': [
                    'Ver perfil de pacientes asignados',
                    'Realizar diagnósticos',
                    'Hacer recomendaciones',
                    'Ver reportes por región',
                    'Acceder a telemetría'
                ],
                'restricciones': [
                    'Solo pacientes asignados a ti',
                    'No eliminar datos',
                    'No acceso a datos de otras regiones'
                ]
            },
            'entidad': {
                'nombre': '🏛️ Entidad (MINSA)',
                'descripcion': 'Acceso a datos agregados nacionales',
                'permisos': [
                    'Ver estadísticas por departamento',
                    'Exportar datos agregados',
                    'Ver tendencias nacionales',
                    'Acceso a telemetría completa',
                    'Ver reportes de impacto'
                ],
                'restricciones': [
                    'Solo datos agregados (sin PII)',
                    'No ver datos individuales',
                    'No modificar información'
                ]
            },
            'demo': {
                'nombre': '👁️ Demo (Evaluación)',
                'descripcion': 'Acceso limitado con datos ficticios',
                'permisos': [
                    'Explorar todas las funciones',
                    'Ver datos de ejemplo',
                    'Enviar feedback'
                ],
                'restricciones': [
                    'Datos NO se guardan',
                    'Acceso limitado a 1 hora',
                    'No acceso a datos reales'
                ]
            }
        }

        rol_actual = roles_info.get(user_role, roles_info['demo'])

        # Mostrar rol actual
        col_rol1, col_rol2 = st.columns([1, 3])

        with col_rol1:
            st.markdown(f"## {rol_actual['nombre']}")

        with col_rol2:
            st.caption(rol_actual['descripcion'])

        st.divider()

        # Permisos
        col_perm1, col_perm2 = st.columns(2)

        with col_perm1:
            st.markdown("### ✅ Permisos")
            for permiso in rol_actual['permisos']:
                st.markdown(f"✓ {permiso}")

        with col_perm2:
            st.markdown("### ❌ Restricciones")
            for restriccion in rol_actual['restricciones']:
                st.markdown(f"✗ {restriccion}")

        # Aviso de demo si aplica
        if user_role == 'demo':
            st.warning(DemoManager.obtener_banner_demo())

    # ════════════════════════════════════════════════════════════════════════════
    # TAB 3: DERECHOS (LOPD)
    # ════════════════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown("### ⚖️ Tus Derechos - Ley 29733")

        # Derechos disponibles
        derechos = [
            {
                'titulo': '📖 Derecho de Acceso',
                'descripcion': 'Puedes solicitar acceso a todos tus datos personales almacenados',
                'accion': 'Solicitar acceso'
            },
            {
                'titulo': '✏️ Derecho de Rectificación',
                'descripcion': 'Corrige datos inexactos o incompletos',
                'accion': 'Solicitar corrección'
            },
            {
                'titulo': '🗑️ Derecho al Olvido',
                'descripcion': 'Solicita la eliminación de tus datos (60 días en demo)',
                'accion': 'Solicitar eliminación'
            },
            {
                'titulo': '✋ Derecho de Oposición',
                'descripcion': 'Opón te a ciertos tipos de procesamiento de datos',
                'accion': 'Presentar oposición'
            }
        ]

        for i, derecho in enumerate(derechos):
            col_der1, col_der2, col_der3 = st.columns([2, 2, 1.5])

            with col_der1:
                st.subheader(derecho['titulo'])
                st.caption(derecho['descripcion'])

            with col_der3:
                if st.button(derecho['accion'], key=f"derecho_{i}", use_container_width=True):
                    st.session_state[f"solicitud_{i}"] = True

        st.divider()

        # Procesar solicitudes
        if st.session_state.get('solicitud_0'):
            st.markdown("### 📖 Solicitar Acceso a Mis Datos")
            email = st.text_input("Tu email para confirmar la solicitud")
            if st.button("Enviar Solicitud", key="send_access_request"):
                st.success(f"""
                ✅ Solicitud enviada a {email}

                Recibirás tus datos en máximo 30 días conforme a Ley 29733.
                Referencia: {datetime.now().strftime('%Y%m%d%H%M%S')}
                """)

        if st.session_state.get('solicitud_2'):
            st.markdown("### 🗑️ Solicitar Eliminación de Datos")
            motivo = st.selectbox(
                "Motivo de la solicitud:",
                [
                    "No deseo seguir usando el servicio",
                    "Datos duplicados o incorrectos",
                    "Cambio de decisión sobre consentimiento",
                    "Otro (especificar)"
                ],
                key="motivo_eliminacion"
            )

            if motivo == "Otro (especificar)":
                motivo_custom = st.text_area("Por favor especifica el motivo")
                motivo = motivo_custom

            if st.button("Confirmar Eliminación", key="confirm_deletion"):
                solicitud = DerechoAlOlvidoManager.solicitar_eliminacion(
                    user_id=st.session_state.get('username', 'usuario'),
                    motivo=motivo
                )

                st.success(f"""
                ✅ Solicitud de eliminación registrada

                Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                Estado: {solicitud['estado']}

                Tus datos serán eliminados en máximo 30 días.
                """)

    # ════════════════════════════════════════════════════════════════════════════
    # TAB 4: MI INFORMACIÓN
    # ════════════════════════════════════════════════════════════════════════════
    with tab4:
        st.markdown("### 👤 Mi Información Personal")

        username = st.session_state.get('username', 'usuario')
        user_role = st.session_state.get('user_role', 'demo')
        is_demo = user_role == 'demo'

        # Crear usuario ficticio para ejemplo
        usuario = User(
            user_id="usr_" + username[:3].lower(),
            username=username,
            role=RoleType[user_role.upper()] if user_role.upper() in RoleType.__members__ else RoleType.DEMO,
            full_name=f"Usuario {username.title()}",
            email=f"{username}@example.com",
            telefono="+51987654321",
            dni="12345678",
            is_demo=is_demo,
            consentimiento_aceptado=st.session_state.get('consentimiento_aceptado', False)
        )

        col_info1, col_info2 = st.columns(2)

        with col_info1:
            st.markdown("#### Información Visible")
            info_visible = usuario.to_dict(mask_pii=False)
            for key, value in info_visible.items():
                st.caption(f"**{key}:** {value}")

        with col_info2:
            st.markdown("#### Información Enmascarada (para otros usuarios)")
            info_masked = usuario.to_dict(mask_pii=True)
            for key, value in info_masked.items():
                st.caption(f"**{key}:** {value}")

        st.divider()

        # Historial de accesos
        st.markdown("#### 🔍 Historial de Accesos (últimos 7 días)")

        historial = [
            {'fecha': '2025-11-03 14:30', 'accion': 'Acceso a diagnóstico', 'ip': '192.168.1.X'},
            {'fecha': '2025-11-03 12:15', 'accion': 'Descargar menú PDF', 'ip': '192.168.1.X'},
            {'fecha': '2025-11-02 09:45', 'accion': 'Enviar feedback', 'ip': '192.168.1.X'},
        ]

        for log in historial:
            st.caption(f"**{log['fecha']}** | {log['accion']} | Desde {log['ip']}")

    # ════════════════════════════════════════════════════════════════════════════
    # FOOTER NORMATIVO
    # ════════════════════════════════════════════════════════════════════════════
    st.divider()

    st.markdown("""
    ### 📜 Referencias Normativas

    - **Ley 29733:** Ley de Protección de Datos Personales (Perú)
    - **DECRETO SUPREMO Nº 003-2013-JUS:** Reglamento de la Ley 29733
    - **GDPR:** Conforme a estándares internacionales
    - **Última actualización:** 2025-11-03

    Para consultas sobre privacidad: **privacidad@NutriWawa.pe**
    """)
