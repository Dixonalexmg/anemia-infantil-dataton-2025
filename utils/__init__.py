"""
utils/__init__.py
Módulo de utilidades para NutriSenseIA - Paquete de utilidades
Importa y expone todas las funciones y clases disponibles
"""

import logging

logger = logging.getLogger(__name__)

# ============================================================================
# IMPORTAR i18n_manager (CRÍTICO PARA app.py)
# ============================================================================
try:
    from .i18n_manager import get_i18n, I18nManager
    _i18n_available = True
    logger.info("✅ i18n_manager cargado correctamente")
except ImportError as e:
    logger.warning(f"⚠️ i18n_manager no disponible: {e}")
    _i18n_available = False

# ============================================================================
# IMPORTAR data_loader (CRÍTICO)
# ============================================================================
try:
    from .data_loader import DataLoader, data_loader
    _data_loader_available = True
    logger.info("✅ data_loader cargado correctamente")
except ImportError as e:
    logger.warning(f"⚠️ data_loader no disponible: {e}")
    _data_loader_available = False

# ============================================================================
# IMPORTAR validators (CRÍTICO)
# ============================================================================
try:
    from .validators import (
        validate_edad,
        validate_hemoglobina,
        validate_altitud,
        validate_presupuesto,
        validate_dni,
        validate_email
    )
    _validators_available = True
    logger.info("✅ validators cargado correctamente")
except ImportError as e:
    logger.warning(f"⚠️ validators no disponible: {e}")
    _validators_available = False
    # Definir stubs si no están disponibles
    def validate_edad(x): return True
    def validate_hemoglobina(x): return True
    def validate_altitud(x): return True
    def validate_presupuesto(x): return True
    def validate_dni(x): return True
    def validate_email(x): return True

# ============================================================================
# IMPORTAR OTROS MÓDULOS OPCIONALES
# ============================================================================

try:
    from .cache_manager import CacheManager
    _cache_available = True
except ImportError:
    _cache_available = False

try:
    from .clinical_recommendations import ClinicalRecommender
    _clinical_available = True
except ImportError:
    _clinical_available = False

try:
    from .constants import *
    _constants_available = True
except ImportError:
    _constants_available = False

# ============================================================================
# EXPORTAR PÚBLICAMENTE
# ============================================================================

__all__ = [
    # i18n
    'get_i18n',
    'I18nManager',

    # data_loader
    'DataLoader',
    'data_loader',

    # validators
    'validate_edad',
    'validate_hemoglobina',
    'validate_altitud',
    'validate_presupuesto',
    'validate_dni',
    'validate_email',
]

# Agregar opcionales si están disponibles
if _cache_available:
    __all__.append('CacheManager')

if _clinical_available:
    __all__.append('ClinicalRecommender')

if _constants_available:
    __all__.append('*')

__version__ = "1.0.0"
__author__ = "Datatón 2025 - MINSA"