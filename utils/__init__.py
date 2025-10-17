# utils/__init__.py
"""
Módulo de utilidades para la aplicación
"""
from .data_loader import DataLoader, data_loader
from .validators import (
    validate_edad,
    validate_hemoglobina,
    validate_altitud,
    validate_presupuesto,
    validate_dni,
    validate_email
)

__all__ = [
    'DataLoader',
    'data_loader',
    'validate_edad',
    'validate_hemoglobina',
    'validate_altitud',
    'validate_presupuesto',
    'validate_dni',
    'validate_email'
]
