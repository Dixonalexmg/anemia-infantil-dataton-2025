# utils/i18n.py - Sistema de internacionalización
import json
import streamlit as st
from functools import lru_cache

@lru_cache(maxsize=1)
def load_i18n(idioma='es'):
    """Carga diccionario de traducción con caché"""
    try:
        with open(f'data/i18n_{idioma}.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback a español
        with open('data/i18n_es.json', 'r', encoding='utf-8') as f:
            return json.load(f)

# Instancia global
_i18n_dict = load_i18n()

def t(clave, **kwargs):
    """
    Traducción lazy con interpolación
    Uso: t('home.titulo', username='Juan')
    """
    partes = clave.split('.')
    valor = _i18n_dict

    for parte in partes:
        valor = valor.get(parte, clave)

    # Interpolación de variables
    if isinstance(valor, str) and kwargs:
        valor = valor.format(**kwargs)

    return valor

def get_idioma():
    """Obtener idioma del session state"""
    if 'idioma' not in st.session_state:
        st.session_state.idioma = 'es'
    return st.session_state.idioma

def set_idioma(idioma):
    """Cambiar idioma"""
    st.session_state.idioma = idioma
    global _i18n_dict
    _i18n_dict = load_i18n(idioma)

# USO EN APP:
# En app.py, importar:
# from utils.i18n import t
# 
# En home.py:
# st.title(t('home.titulo', username=st.session_state.username))
# st.write(t('home.subtitulo'))
# if st.button(t('home.tarjeta_1_btn')):
#     # ...
#
# Selector de idioma en sidebar:
# idioma = st.sidebar.radio('Idioma', ['Español', 'Quechua', 'Aimara'])
# set_idioma({'Español': 'es', 'Quechua': 'que', 'Aimara': 'aim'}[idioma])
