# auth/users.py
"""
Gestión de usuarios y autenticación
"""
from typing import Optional
from dataclasses import dataclass
from auth.security import hash_password, verify_password


@dataclass
class User:
    """Clase de usuario del sistema"""
    username: str
    full_name: str
    email: str
    role: str  # 'admin', 'medico', 'nutricionista', 'consulta'
    hashed_password: str
    is_active: bool = True
    
    def to_dict(self):
        """Convierte el usuario a diccionario (sin contraseña)"""
        return {
            "username": self.username,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active
        }


# Base de datos simulada de usuarios (en producción usar BD real)
USERS_DB = {
    "admin": User(
        username="admin",
        full_name="Administrador del Sistema",
        email="admin@minsa.gob.pe",
        role="admin",
        hashed_password=hash_password("admin123"),  # CAMBIAR EN PRODUCCIÓN
        is_active=True
    ),
    "medico_demo": User(
        username="medico_demo",
        full_name="Dr. Juan Pérez",
        email="jperez@minsa.gob.pe",
        role="medico",
        hashed_password=hash_password("demo123"),
        is_active=True
    ),
    "nutricionista_demo": User(
        username="nutricionista_demo",
        full_name="Lic. María García",
        email="mgarcia@minsa.gob.pe",
        role="nutricionista",
        hashed_password=hash_password("demo123"),
        is_active=True
    ),
    "consulta": User(
        username="consulta",
        full_name="Usuario de Consulta",
        email="consulta@minsa.gob.pe",
        role="consulta",
        hashed_password=hash_password("consulta123"),
        is_active=True
    )
}


def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    Autentica un usuario.
    
    Args:
        username: Nombre de usuario
        password: Contraseña en texto plano
        
    Returns:
        Usuario autenticado o None
    """
    user = USERS_DB.get(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


def get_user(username: str) -> Optional[User]:
    """
    Obtiene un usuario por username.
    
    Args:
        username: Nombre de usuario
        
    Returns:
        Usuario o None si no existe
    """
    return USERS_DB.get(username)


def get_all_users() -> list:
    """Obtiene todos los usuarios (sin contraseñas)"""
    return [user.to_dict() for user in USERS_DB.values()]
