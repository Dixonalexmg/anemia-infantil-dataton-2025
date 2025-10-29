"""
utils/cache_manager.py
Gestión de caché para optimizar rendimiento
"""
import streamlit as st
from functools import wraps

def cache_predictor(func):
    """Decorator para cachear el predictor"""
    @wraps(func)
    @st.cache_resource(show_spinner=False)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def cache_explainer(func):
    """Decorator para cachear el explainer SHAP"""
    @wraps(func)
    @st.cache_resource(show_spinner=False, ttl=3600)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
