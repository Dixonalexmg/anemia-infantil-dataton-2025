"""
auth/users.py
Sistema de autenticación - Compatible con tu código existente
"""

from auth.security import hash_password, verify_password
from dataclasses import dataclass

@dataclass
class User:
    """Clase de usuario compatible con tu código"""
    username: str
    full_name: str
    role: str
    password_hash: str

# Base de datos de usuarios
USERS_DB = {
    "admin": User(
        username="admin",
        full_name="Administrador del Sistema",
        role="Administrador",
        password_hash=hash_password("admin123")
    ),
    "medico": User(
        username="medico",
        full_name="Dr. Juan Pérez",
        role="Médico",
        password_hash=hash_password("demo123")
    ),
    "nutricionista": User(
        username="nutricionista",
        full_name="Lic. María García",
        role="Nutricionista",
        password_hash=hash_password("demo123")
    ),
    "demo": User(
        username="demo",
        full_name="Usuario Demo",
        role="demo",
        password_hash=hash_password("demo")
    )
}

def authenticate_user(username: str, password: str):
    """
    Autentica usuario - Compatible con tu código existente

    Returns:
        User object si es válido, None si no
    """
    user = USERS_DB.get(username)

    if user and verify_password(password, user.password_hash):
        return user

    return None