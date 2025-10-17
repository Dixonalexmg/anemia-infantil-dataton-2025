# services/__init__.py
"""
Servicios de negocio de la aplicación
"""
from .predictor import AnemiaPredictor, anemia_predictor
from .menu_generator import MenuGenerator, menu_generator

__all__ = [
    'AnemiaPredictor',
    'anemia_predictor',
    'MenuGenerator',
    'menu_generator'
]
