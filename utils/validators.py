# utils/validators.py
"""
Validadores de entrada para la aplicación
"""
from typing import Optional, Tuple
import re


def validate_edad(edad: int) -> Tuple[bool, str]:
    """
    Valida edad del niño
    
    Args:
        edad: Edad en meses
        
    Returns:
        (es_valida, mensaje_error)
    """
    if edad < 6:
        return False, "La edad mínima es 6 meses"
    if edad > 59:
        return False, "La edad máxima es 59 meses (4 años 11 meses)"
    return True, ""


def validate_hemoglobina(hb: float, altitud: int = 0) -> Tuple[bool, str]:
    """
    Valida valor de hemoglobina
    
    Args:
        hb: Hemoglobina en g/dL
        altitud: Altitud en metros
        
    Returns:
        (es_valida, mensaje_error)
    """
    if hb < 3.0:
        return False, "Hemoglobina demasiado baja (< 3.0 g/dL). Verificar medición."
    if hb > 22.0:
        return False, "Hemoglobina demasiado alta (> 22.0 g/dL). Verificar medición."
    
    # Valores esperados según edad y altitud
    if hb < 7.0:
        return True, "⚠️ Anemia severa detectada - Requiere atención médica urgente"
    
    return True, ""


def validate_altitud(altitud: int) -> Tuple[bool, str]:
    """
    Valida altitud
    
    Args:
        altitud: Altitud en metros sobre nivel del mar
        
    Returns:
        (es_valida, mensaje_error)
    """
    if altitud < 0:
        return False, "La altitud no puede ser negativa"
    if altitud > 6000:
        return False, "Altitud fuera de rango para Perú (máx 6000 msnm)"
    return True, ""


def validate_presupuesto(presupuesto: float) -> Tuple[bool, str]:
    """
    Valida presupuesto diario
    
    Args:
        presupuesto: Presupuesto en soles
        
    Returns:
        (es_valida, mensaje_error)
    """
    if presupuesto < 1.0:
        return False, "El presupuesto mínimo es S/ 1.00 por día"
    if presupuesto > 100.0:
        return False, "Presupuesto fuera de rango (máx S/ 100.00)"
    return True, ""


def validate_dni(dni: str) -> Tuple[bool, str]:
    """
    Valida formato de DNI peruano
    
    Args:
        dni: DNI como string
        
    Returns:
        (es_valido, mensaje_error)
    """
    if not dni:
        return True, ""  # DNI es opcional
    
    # DNI debe tener 8 dígitos
    if not re.match(r'^\d{8}$', dni):
        return False, "DNI debe tener 8 dígitos"
    
    return True, ""


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Valida formato de email
    
    Args:
        email: Email como string
        
    Returns:
        (es_valido, mensaje_error)
    """
    if not email:
        return True, ""  # Email es opcional
    
    # Regex simple para email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Formato de email inválido"
    
    return True, ""
