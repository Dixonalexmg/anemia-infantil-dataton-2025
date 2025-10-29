# utils/menu_substitutions.py
"""
Motor de sustituciones inteligentes de ingredientes
"""

import json
from typing import List, Dict, Optional
from pathlib import Path


class MenuSubstitutionEngine:
    """Motor de sustituciones nutricionales inteligentes"""
    
    def __init__(self, 
                 catalogo_sust_path: str = "data/catalogo_sustituciones.json",
                 catalogo_ing_path: str = "data/catalogo_ingredientes_costo.json"):
        """Carga catálogos de sustituciones e ingredientes"""
        
        with open(catalogo_sust_path, 'r', encoding='utf-8') as f:
            self.catalogo_sust = json.load(f)
        
        with open(catalogo_ing_path, 'r', encoding='utf-8') as f:
            catalogo_ing = json.load(f)
            self.catalogo_ing = {ing['id']: ing for ing in catalogo_ing['ingredientes']}
    
    def sugerir_sustituto(self, 
                          ingrediente_faltante: str, 
                          departamento: str = None,
                          presupuesto_max: float = None,
                          prioridad: str = "costo") -> List[Dict]:
        """
        Sugiere sustitutos inteligentes para un ingrediente
        """
        if ingrediente_faltante not in self.catalogo_sust:
            return []
        
        sustitutos = self.catalogo_sust[ingrediente_faltante]['sustitutos'].copy()
        
        # Filtrar por presupuesto (CORRECCIÓN CLAVE)
        if presupuesto_max is not None:
            sustitutos_filtrados = []
            for s in sustitutos:
                try:
                    costo = float(s['costo_s'])  # ← ACCESO DIRECTO AL VALOR
                    if costo <= presupuesto_max:
                        sustitutos_filtrados.append(s)
                except (ValueError, KeyError, TypeError):
                    # Si falla la conversión, omitir este sustituto
                    continue
            sustitutos = sustitutos_filtrados
        
        # Filtrar por disponibilidad regional
        if departamento:
            sustitutos_disponibles = []
            for sust in sustitutos:
                info_ing = self.catalogo_ing.get(sust['id'])
                if info_ing:
                    disponibilidad = info_ing.get('disponibilidad_regiones', [])
                    if disponibilidad == "todas" or departamento in disponibilidad:
                        sustitutos_disponibles.append(sust)
            sustitutos = sustitutos_disponibles
        
        # Ordenar según prioridad
        if prioridad == "costo":
            sustitutos.sort(key=lambda x: float(x['costo_s']))
        elif prioridad == "hierro":
            sustitutos.sort(key=lambda x: float(x['hierro_mg']), reverse=True)
        
        return sustitutos[:3]
    
    def generar_mensaje_sustitucion(self, 
                                    ingrediente_original: str, 
                                    sustituto: Dict,
                                    contexto: str = "simple") -> str:
        """
        Genera mensaje educativo de sustitución
        """
        if ingrediente_original not in self.catalogo_sust:
            return f"ℹ️ No hay información de sustitución para {ingrediente_original}"
        
        original = self.catalogo_sust[ingrediente_original]
        
        # Convertir a float de forma segura
        try:
            costo_orig = float(original['costo_s'])
            hierro_orig = float(original['hierro_mg'])
            costo_sust = float(sustituto['costo_s'])
            hierro_sust = float(sustituto['hierro_mg'])
        except (ValueError, KeyError):
            return "⚠️ Error en datos de sustitución"
        
        if contexto == "simple":
            msg = f"💡 **En lugar de {ingrediente_original}:**\n"
            msg += f"✅ Usa **{sustituto['nombre']}** (S/ {costo_sust:.2f})\n"
            msg += f"🍳 {sustituto.get('preparacion', 'Preparar al gusto')}\n\n"
            msg += f"✨ {sustituto.get('ventaja', 'Buena alternativa')}"
            
        elif contexto == "detallado":
            msg = f"### 💡 Sustitución inteligente\n\n"
            msg += f"❌ **No hay:** {ingrediente_original} (S/ {costo_orig:.2f} - {hierro_orig:.1f} mg hierro)\n\n"
            msg += f"✅ **Usa:** {sustituto['nombre']} (S/ {costo_sust:.2f} - {hierro_sust:.1f} mg hierro)\n\n"
            
            ahorro = costo_orig - costo_sust
            ahorro_pct = (ahorro / costo_orig * 100) if costo_orig > 0 else 0
            
            msg += f"📊 **Comparación:**\n"
            msg += f"- Ahorro: S/ {ahorro:.2f} ({ahorro_pct:.0f}%)\n"
            msg += f"- Hierro: {hierro_sust:.1f} mg vs {hierro_orig:.1f} mg\n\n"
            msg += f"🍳 **Preparación:** {sustituto.get('preparacion', 'Preparar al gusto')}\n\n"
            msg += f"✨ **Ventaja:** {sustituto.get('ventaja', 'Buena opción')}\n"
            
            if sustituto.get('requiere_citrico'):
                msg += f"\n⚠️ **Importante:** {sustituto.get('nota_citrico', 'Agregar cítrico para mejor absorción')}"
        
        else:  # profesional
            msg = f"**Sustitución nutricional:**\n"
            msg += f"{sustituto['nombre']} (factor {sustituto.get('factor_conversion', 1.0)})\n"
            msg += f"Hierro: {hierro_sust:.1f}mg | Costo: S/{costo_sust:.2f}\n"
        
        return msg


def crear_alerta_citrico(ingrediente_id: str, catalogo_ing: Dict) -> Optional[str]:
    """
    Genera alerta si el ingrediente requiere cítrico
    """
    info_ing = catalogo_ing.get(ingrediente_id)
    
    if info_ing and info_ing.get('requiere_citrico'):
        return (
            f"⚠️ **{info_ing['nombre']}** contiene hierro no hemo. "
            f"Agregar jugo de limón o naranja para mejorar absorción en 3-4x."
        )
    
    return None
