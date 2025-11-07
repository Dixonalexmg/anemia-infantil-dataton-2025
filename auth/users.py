"""
auth/users.py
Módulo de autenticación - Base de datos de usuarios para testing
"""

from dataclasses import dataclass
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# ════════════════════════════════════════════════════════════════════════════════
# MODELO DE USUARIO AUTENTICADO
# ════════════════════════════════════════════════════════════════════════════════

@dataclass
class AuthUser:
    """Modelo de usuario autenticado"""
    username: str
    password: str
    full_name: str
    role: str  # 'cuidador', 'profesional', 'entidad', 'demo'
    email: str

    def __repr__(self):
        return f"<AuthUser {self.username} ({self.role})>"

# ════════════════════════════════════════════════════════════════════════════════
# BASE DE DATOS DE USUARIOS (para testing/demo)
# ════════════════════════════════════════════════════════════════════════════════

USUARIOS_DEMO = [
    AuthUser(
        username="cuidador1",
        password="pass123",
        full_name="María Pérez (Cuidadora)",
        role="cuidador",
        email="maria@example.com"
    ),
    AuthUser(
        username="medico1",
        password="pass123",
        full_name="Dr. Juan García (Médico)",
        role="profesional",
        email="juan@example.com"
    ),
    AuthUser(
        username="entidad1",
        password="pass123",
        full_name="MINSA - Entidad Nacional",
        role="entidad",
        email="minsa@example.com"
    ),
    AuthUser(
        username="demo",
        password="demo",
        full_name="Usuario Demostración",
        role="demo",
        email="demo@example.com"
    ),
    # Usuarios adicionales para testing
    AuthUser(
        username="admin",
        password="admin123",
        full_name="Administrador Sistema",
        role="admin",
        email="admin@example.com"
    ),
]

# ════════════════════════════════════════════════════════════════════════════════
# FUNCIONES DE AUTENTICACIÓN
# ════════════════════════════════════════════════════════════════════════════════

def authenticate_user(username: str, password: str) -> Optional[AuthUser]:
    """
    Autentica un usuario verificando credenciales

    Args:
        username: Nombre de usuario
        password: Contraseña

    Returns:
        AuthUser si credenciales son válidas, None si no
    """
    try:
        # Buscar usuario en base de datos
        for user in USUARIOS_DEMO:
            if user.username == username and user.password == password:
                logger.info(f"✅ Usuario autenticado: {username} ({user.role})")
                return user

        # Usuario no encontrado o contraseña incorrecta
        logger.warning(f"❌ Intento fallido de login: {username}")
        return None

    except Exception as e:
        logger.error(f"❌ Error en autenticación: {e}")
        return None

def get_user_by_username(username: str) -> Optional[AuthUser]:
    """
    Obtiene usuario por nombre de usuario

    Args:
        username: Nombre de usuario

    Returns:
        AuthUser si existe, None si no
    """
    for user in USUARIOS_DEMO:
        if user.username == username:
            return user
    return None

def user_exists(username: str) -> bool:
    """Verifica si un usuario existe"""
    return get_user_by_username(username) is not None

def obtener_todos_usuarios():
    """Devuelve lista de todos los usuarios para display"""
    return USUARIOS_DEMO

def obtener_usuarios_por_rol(role: str):
    """Obtiene usuarios de un rol específico"""
    return [u for u in USUARIOS_DEMO if u.role == role]