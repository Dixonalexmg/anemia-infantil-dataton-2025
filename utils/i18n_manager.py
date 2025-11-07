# utils/i18n_manager.py
"""
Gestor de internacionalización (i18n) para NutriSenseIA
Soporta: Español (ES), Quechua (QUE), Aimara (AIM)
"""

import json
import streamlit as st
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class I18nManager:
    """Gestor centralizado de traducciones multiidioma"""

    IDIOMAS_DISPONIBLES = {
        'ES': {'nombre': 'Español', 'emoji': '🇪🇸', 'codigo': 'ES'},
        'QUE': {'nombre': 'Qhichwa (Quechua)', 'emoji': '🏔️', 'codigo': 'QUE'},
        'AIM': {'nombre': 'Aymar Aru (Aimara)', 'emoji': '🌿', 'codigo': 'AIM'}
    }

    def __init__(self, i18n_path: str = "data/i18n.json"):
        """Inicializa el gestor de traducciones"""
        self.i18n_path = Path(i18n_path)
        self.translations = {}
        self._load_translations()

        # Inicializar idioma en session_state si no existe
        if 'language' not in st.session_state:
            st.session_state.language = 'ES'

    def _load_translations(self):
        """Carga el archivo JSON de traducciones"""
        try:
            with open(self.i18n_path, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
            logger.info(f"✅ Traducciones cargadas: {list(self.translations.keys())}")
        except FileNotFoundError:
            logger.error(f"❌ Archivo i18n no encontrado: {self.i18n_path}")
            self.translations = {'ES': {}}
        except json.JSONDecodeError as e:
            logger.error(f"❌ Error parseando i18n.json: {e}")
            self.translations = {'ES': {}}

    def get(self, key: str, **kwargs) -> str:
        """
        Obtiene texto traducido por clave

        Args:
            key: Clave en formato 'modulo.subclave' ej: 'common.save'
            **kwargs: Variables para interpolación {name}, {value}, etc.

        Returns:
            Texto traducido en el idioma actual

        Ejemplo:
            i18n.get('landing.greeting_morning')  → "Buenos días"
            i18n.get('risk.name')  → "Nombre del niño/a"
        """
        language = st.session_state.get('language', 'ES')

        try:
            # Navegar por el diccionario usando la clave
            keys = key.split('.')
            value = self.translations[language]

            for k in keys:
                value = value[k]

            # Interpolar variables si existen
            if kwargs:
                value = value.format(**kwargs)

            return value

        except (KeyError, TypeError) as e:
            logger.warning(f"⚠️ Clave no encontrada: {key} en idioma {language}")
            # Fallback a español
            try:
                value = self.translations['ES']
                for k in keys:
                    value = value[k]
                return value
            except:
                return f"[{key}]"

    def change_language(self, language_code: str):
        """
        Cambia el idioma actual

        Args:
            language_code: Código del idioma ('ES', 'QUE', 'AIM')
        """
        if language_code in self.IDIOMAS_DISPONIBLES:
            st.session_state.language = language_code
            logger.info(f"✅ Idioma cambiado a: {language_code}")
            st.rerun()
        else:
            logger.error(f"❌ Idioma no soportado: {language_code}")

    def get_current_language(self) -> str:
        """Devuelve el código del idioma actual"""
        return st.session_state.get('language', 'ES')

    def get_current_language_name(self) -> str:
        """Devuelve el nombre del idioma actual"""
        lang = self.get_current_language()
        return self.IDIOMAS_DISPONIBLES[lang]['nombre']

    def render_language_selector(self, key_suffix: str = ""):
        """
        Renderiza un selector de idioma en la interfaz

        Args:
            key_suffix: Sufijo único para evitar colisión de keys
        """
        current_lang = self.get_current_language()

        col1, col2 = st.columns([5, 1])

        with col2:
            # Selector de idioma como selectbox
            idiomas_options = [
                f"{info['emoji']} {info['nombre']}" 
                for info in self.IDIOMAS_DISPONIBLES.values()
            ]

            # Índice actual
            idiomas_codigos = list(self.IDIOMAS_DISPONIBLES.keys())
            current_index = idiomas_codigos.index(current_lang)

            selected = st.selectbox(
                "🌐",
                options=idiomas_options,
                index=current_index,
                key=f"lang_selector_{key_suffix}",
                label_visibility="collapsed"
            )

            # Detectar cambio
            selected_code = idiomas_codigos[idiomas_options.index(selected)]

            if selected_code != current_lang:
                self.change_language(selected_code)


# Instancia global del gestor (singleton)
_i18n_instance = None

def get_i18n() -> I18nManager:
    """
    Devuelve la instancia global del gestor i18n (singleton)

    Uso:
        from utils.i18n_manager import get_i18n
        i18n = get_i18n()
        texto = i18n.get('common.save')
    """
    global _i18n_instance
    if _i18n_instance is None:
        _i18n_instance = I18nManager()
    return _i18n_instance