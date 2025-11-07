"""
auth/roles_manager.py
Gestor de roles y control de acceso - Cumplimiento Ley 29733 (LOPD Perú)
VERSIÓN CORREGIDA - Sin errores de .value en Enum
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# ════════════════════════════════════════════════════════════════════════════════
# ENUMERACIONES
# ════════════════════════════════════════════════════════════════════════════════

class RoleType(Enum):
    """Roles disponibles en el sistema"""
    CUIDADOR = "cuidador"
    PROFESIONAL = "profesional"
    ENTIDAD = "entidad"
    ADMIN = "admin"
    DEMO = "demo"

class PermissionType(Enum):
    """Permisos del sistema"""
    # Lectura
    READ_OWN_DATA = "read_own_data"
    READ_ASSIGNED_PATIENTS = "read_assigned_patients"
    READ_AGGREGATED_DATA = "read_aggregated_data"
    READ_TELEMETRY = "read_telemetry"

    # Escritura
    WRITE_OWN_DATA = "write_own_data"
    WRITE_RECOMMENDATIONS = "write_recommendations"
    WRITE_FEEDBACK = "write_feedback"

    # Administración
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    DELETE_DATA = "delete_data"
    EXPORT_DATA = "export_data"

# ════════════════════════════════════════════════════════════════════════════════
# MODELO DE USUARIO
# ════════════════════════════════════════════════════════════════════════════════

@dataclass
class User:
    """Modelo de usuario del sistema"""
    user_id: str
    username: str
    role: RoleType
    full_name: str
    email: str
    telefono: str
    dni: str
    is_demo: bool = False
    fecha_creacion: str = None
    consentimiento_aceptado: bool = False
    consentimiento_fecha: str = None

    def __post_init__(self):
        if self.fecha_creacion is None:
            self.fecha_creacion = datetime.now().isoformat()

    def to_dict(self, mask_pii: bool = False) -> Dict[str, Any]:
        """Convierte usuario a dict, opcionalmente enmascarando PII"""
        data = {
            'user_id': self.user_id,
            'username': self.username,
            'role': self.role.name if isinstance(self.role, RoleType) else str(self.role),
            'full_name': self.full_name if not mask_pii else self._mask_name(),
            'email': self.email if not mask_pii else self._mask_email(),
            'is_demo': self.is_demo
        }
        return data

    def _mask_name(self) -> str:
        """Enmascara nombre completo"""
        if len(self.full_name) < 2:
            return "***"
        return f"{self.full_name[0]}**** {self.full_name.split()[-1][:1]}****"

    def _mask_email(self) -> str:
        """Enmascara email"""
        if '@' not in self.email:
            return "****@****"
        local, domain = self.email.split('@')
        return f"{local[0]}****@{domain}"

    def _mask_phone(self) -> str:
        """Enmascara teléfono"""
        if len(self.telefono) < 4:
            return "****"
        return f"51-****-{self.telefono[-2:]}"

    def _mask_dni(self) -> str:
        """Enmascara DNI"""
        if len(self.dni) < 2:
            return "XXXXXX"
        return f"XXXXXX{self.dni[-2:]}"

# ════════════════════════════════════════════════════════════════════════════════
# GESTOR DE ROLES
# ════════════════════════════════════════════════════════════════════════════════

class RoleManager:
    """Gestor centralizado de roles y permisos"""

    # Definición de permisos por rol
    ROLE_PERMISSIONS = {
        RoleType.CUIDADOR: [
            PermissionType.READ_OWN_DATA,
            PermissionType.WRITE_OWN_DATA,
            PermissionType.WRITE_FEEDBACK,
        ],
        RoleType.PROFESIONAL: [
            PermissionType.READ_OWN_DATA,
            PermissionType.READ_ASSIGNED_PATIENTS,
            PermissionType.WRITE_OWN_DATA,
            PermissionType.WRITE_RECOMMENDATIONS,
            PermissionType.WRITE_FEEDBACK,
            PermissionType.READ_TELEMETRY,
        ],
        RoleType.ENTIDAD: [
            PermissionType.READ_AGGREGATED_DATA,
            PermissionType.READ_TELEMETRY,
            PermissionType.EXPORT_DATA,
        ],
        RoleType.ADMIN: [
            p for p in PermissionType  # Todos los permisos
        ],
        RoleType.DEMO: [
            PermissionType.READ_OWN_DATA,
            PermissionType.WRITE_FEEDBACK,
        ],
    }

    # Visibilidad de datos por rol
    VISIBILITY_RULES = {
        RoleType.CUIDADOR: {
            'puede_ver': ['own_data', 'own_children'],
            'enmascara_pii': False,
            've_agregados': False
        },
        RoleType.PROFESIONAL: {
            'puede_ver': ['assigned_patients', 'aggregated_region'],
            'enmascara_pii': False,
            've_agregados': True
        },
        RoleType.ENTIDAD: {
            'puede_ver': ['national_aggregated'],
            'enmascara_pii': True,
            've_agregados': True
        },
        RoleType.DEMO: {
            'puede_ver': ['demo_data'],
            'enmascara_pii': True,
            've_agregados': False
        },
    }

    @staticmethod
    def tiene_permiso(user: User, permission) -> bool:
        """
        Verifica si usuario tiene permiso específico

        Args:
            user: Objeto User
            permission: PermissionType o string del permiso
        """
        # Convertir string a PermissionType si es necesario
        if isinstance(permission, str):
            try:
                permission = PermissionType[permission.upper()]
            except KeyError:
                logger.warning(f"Permiso desconocido: {permission}")
                return False

        permisos_usuario = RoleManager.ROLE_PERMISSIONS.get(user.role, [])
        tiene = permission in permisos_usuario

        # ✅ CORREGIDO: Usar .name en lugar de .value
        logger.info(f"Permiso {permission.name} para {user.username}: {tiene}")
        return tiene

    @staticmethod
    def puede_ver_dato(user: User, tipo_dato: str) -> bool:
        """Verifica si usuario puede ver un tipo de dato"""
        reglas = RoleManager.VISIBILITY_RULES.get(user.role, {})
        puede = tipo_dato in reglas.get('puede_ver', [])

        return puede

    @staticmethod
    def debe_enmascarar_pii(user: User) -> bool:
        """Determina si se deben enmascarar datos PII para este usuario"""
        reglas = RoleManager.VISIBILITY_RULES.get(user.role, {})
        return reglas.get('enmascara_pii', True)

    @staticmethod
    def obtener_vista_personalizada(user: User, datos: Dict) -> Dict:
        """
        Filtra y personaliza datos según rol del usuario

        Args:
            user: Usuario que solicita datos
            datos: Datos completos a filtrar

        Returns:
            Datos filtrados según permisos del usuario
        """
        vista = datos.copy()
        enmascara = RoleManager.debe_enmascarar_pii(user)

        # Enmascarar PII si es necesario
        if enmascara and 'usuario' in vista:
            vista['usuario'] = {
                'user_id': vista['usuario'].get('user_id'),
                'nombre': f"Paciente #{vista['usuario'].get('user_id', '****')[-4:]}",
                'email': vista['usuario'].get('email', '').replace(
                    vista['usuario'].get('email', '').split('@')[0],
                    'p****'
                ) if '@' in vista['usuario'].get('email', '') else 'p****@****'
            }

        # Remover datos según visibilidad
        if user.role == RoleType.ENTIDAD:
            # Entidades solo ven agregados, sin datos individuales
            vista.pop('diagnostico_individual', None)
            vista.pop('menus_personales', None)

        return vista

    @staticmethod
    def generar_audit_log(user: User, accion: str, recurso: str, resultado: bool):
        """Genera log de auditoría para cumplimiento normativo"""
        # ✅ CORREGIDO: Usar .name en lugar de .value
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user.user_id,
            'username': user.username,
            'role': user.role.name,
            'accion': accion,
            'recurso': recurso,
            'resultado': resultado,
            'is_demo': user.is_demo
        }
        logger.info(f"AUDIT: {log_entry}")
        return log_entry

# ════════════════════════════════════════════════════════════════════════════════
# GESTOR DE DEMO
# ════════════════════════════════════════════════════════════════════════════════

class DemoManager:
    """Gestor de modo demo seguro"""

    DEMO_USER = User(
        user_id="demo_001",
        username="demo_user",
        role=RoleType.DEMO,
        full_name="Usuario Demostración",
        email="demo@example.com",
        telefono="+51987654321",
        dni="12345678",
        is_demo=True,
        consentimiento_aceptado=True
    )

    @staticmethod
    def generar_datos_demo() -> Dict[str, Any]:
        """Genera dataset completo ficticio para demo"""
        import random

        return {
            'paciente': {
                'nombre': f"Niño #{random.randint(1000, 9999)}",
                'edad_meses': random.randint(6, 59),
                'sexo': random.choice(['M', 'F'])
            },
            'diagnostico': {
                'hemoglobina': round(random.uniform(8.0, 14.0), 1),
                'nivel_riesgo': random.choice(['RIESGO BAJO', 'RIESGO MODERADO', 'RIESGO ALTO']),
                'probabilidad': round(random.uniform(0.0, 1.0), 2)
            },
            'menus_sugeridos': [
                {'nombre': 'Desayuno Andino', 'hierro_mg': 4.3},
                {'nombre': 'Almuerzo con Hígado', 'hierro_mg': 8.7},
                {'nombre': 'Cena Vegetariana', 'hierro_mg': 3.5}
            ]
        }

    @staticmethod
    def obtener_banner_demo() -> str:
        """Devuelve banner a mostrar en modo demo"""
        return """
        ⚠️ **MODO DEMOSTRACIÓN**

        Los datos mostrados son **ficticios y generados aleatoriamente**.
        Este es un entorno de prueba para explorar la funcionalidad de NutriSenseIA.

        **Datos NO se guardan en servidor.**

        🔐 **Privacidad:** Se aplica Ley 29733 (LOPD Perú) en todo momento.
        """

    @staticmethod
    def debe_mostrar_demo_warning() -> bool:
        """Determina si debe mostrar aviso de demo"""
        import streamlit as st
        user_role = st.session_state.get('user_role', 'demo')
        return user_role == 'demo'

# ════════════════════════════════════════════════════════════════════════════════
# GESTOR DE CONSENTIMIENTO (LEY 29733)
# ════════════════════════════════════════════════════════════════════════════════

class ConsentManager:
    """Gestor de consentimiento informado - Ley 29733"""

    TEXTO_CONSENTIMIENTO = """
    ## 📋 Consentimiento Informado - Ley 29733 (LOPD Perú)

    **NutriSenseIA** recopila y procesa datos personales de salud conforme a la Ley 29733.

    ### Derechos reconocidos:
    ✅ **Acceso:** Puedes solicitar acceso a tus datos en cualquier momento
    ✅ **Rectificación:** Corrección de datos inexactos
    ✅ **Cancelación:** Eliminación de tus datos (dentro de 60 días en demostración)
    ✅ **Oposición:** A ciertos tipos de procesamiento

    ### Protecciones implementadas:
    🔒 **Minimización:** Solo recopilamos datos esenciales
    🔒 **Encriptación:** Datos en tránsito y reposo (AES-256)
    🔒 **Retención:** Máximo 60 días en demostración, conforme a normativa
    🔒 **Auditoría:** Log completo de accesos y cambios

    ### Responsable de datos:
    📧 **Contacto:** privacidad@nutrisenseIA.pe
    📞 **Teléfono:** +51 (1) 2345-6789

    Al aceptar, confirmas que:
    - Has leído y entendido esta política
    - Autorizas el procesamiento de tus datos personales
    - Entiendes que puedes revocar este consentimiento en cualquier momento
    """

    @staticmethod
    def crear_consentimiento(user: User) -> Dict[str, Any]:
        """Crea registro de consentimiento para usuario"""
        return {
            'user_id': user.user_id,
            'fecha_consentimiento': datetime.now().isoformat(),
            'version_politica': '1.0',
            'aceptado': True,
            'tipo_datos': ['perfil', 'diagnostico', 'menus', 'feedback'],
            'propositos': ['diagnostico', 'recomendacion', 'mejora_sistema'],
            'revocacion_url': 'https://nutrisenseIA.pe/revocar-consentimiento'
        }

    @staticmethod
    def verificar_consentimiento(user: User) -> bool:
        """Verifica si usuario tiene consentimiento válido"""
        return user.consentimiento_aceptado

# ════════════════════════════════════════════════════════════════════════════════
# GESTOR DE DERECHO AL OLVIDO
# ════════════════════════════════════════════════════════════════════════════════

class DerechoAlOlvidoManager:
    """Implementa derecho al olvido (Ley 29733)"""

    @staticmethod
    def solicitar_eliminacion(user_id: str, motivo: str) -> Dict[str, Any]:
        """
        Procesa solicitud de eliminación de datos

        Args:
            user_id: ID del usuario
            motivo: Motivo de la solicitud

        Returns:
            Confirmación de solicitud
        """
        solicitud = {
            'user_id': user_id,
            'fecha_solicitud': datetime.now().isoformat(),
            'motivo': motivo,
            'estado': 'pendiente',
            'fecha_procesamiento': None,
            'datos_eliminados': []
        }

        logger.info(f"Solicitud de eliminación: {solicitud}")
        return solicitud

    @staticmethod
    def obtener_plazo_retencion(is_demo: bool = False) -> int:
        """
        Devuelve plazo de retención según normativa

        - Demo: 60 días
        - Producción: 5 años o conforme a retención médica
        """
        return 60 if is_demo else (365 * 5)