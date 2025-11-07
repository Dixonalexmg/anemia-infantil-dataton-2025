# utils/menu_recommender.py
"""
Recomendador inteligente de menús basado en:
- Valor nutricional (hierro)
- Costo económico
- Accesibilidad regional
"""

import json
import numpy as np
from typing import List, Dict, Tuple
from pathlib import Path

class MenuRecommender:
    """Recomendador multi-criterio para menús nutricionales"""

    def __init__(self, catalogo_path: str = "data/catalogo_ingredientes_costo.json"):
        """Carga catálogo de ingredientes"""
        with open(catalogo_path, 'r', encoding='utf-8') as f:
            self.catalogo = json.load(f)['ingredientes']

        # Crear índice por ID
        self.catalogo_dict = {ing['id']: ing for ing in self.catalogo}

    def calcular_costo_menu(self, ingredientes: List[Dict]) -> float:
        """
        Calcula costo total del menú

        Args:
            ingredientes: [{"id": "higado_res", "cantidad_g": 100}, ...]

        Returns:
            Costo en soles
        """
        costo_total = 0.0

        for ing in ingredientes:
            info_ing = self.catalogo_dict.get(ing['id'])
            if info_ing:
                costo_kg = info_ing['costo_s_kg']
                cantidad_kg = ing['cantidad_g'] / 1000
                costo_total += costo_kg * cantidad_kg

        return round(costo_total, 2)

    def calcular_hierro_total(self, ingredientes: List[Dict]) -> float:
        """Calcula hierro total del menú en mg"""
        hierro_total = 0.0

        for ing in ingredientes:
            info_ing = self.catalogo_dict.get(ing['id'])
            if info_ing:
                hierro_100g = info_ing['hierro_mg_100g']
                cantidad_g = ing['cantidad_g']
                hierro_total += (hierro_100g * cantidad_g) / 100

        return round(hierro_total, 1)

    def calcular_score_accesibilidad(self, ingredientes: List[Dict], 
                                     departamento: str) -> float:
        """
        Score de accesibilidad regional (0-100)

        100 = todos los ingredientes disponibles localmente
        0 = ninguno disponible
        """
        if not ingredientes:
            return 0.0

        n_disponibles = 0

        for ing in ingredientes:
            info_ing = self.catalogo_dict.get(ing['id'])
            if info_ing:
                disponibilidad = info_ing.get('disponibilidad_regiones', [])

                # "todas" significa disponible en cualquier región
                if disponibilidad == "todas" or departamento in disponibilidad:
                    n_disponibles += 1

        score = (n_disponibles / len(ingredientes)) * 100
        return round(score, 1)

    def calcular_score_menu(self, menu: Dict, contexto: Dict) -> Tuple[float, Dict]:
        """
        Calcula score compuesto del menú

        Args:
            menu: {
                "nombre": "Desayuno andino",
                "ingredientes": [{"id": "quinua", "cantidad_g": 100}, ...],
                "preparacion": "..."
            }
            contexto: {
                "departamento": "CUSCO",
                "edad_meses": 18,
                "presupuesto_diario_s": 15.0
            }

        Returns:
            (score_final, desglose)
        """
        # 1. Calcular métricas base
        costo = self.calcular_costo_menu(menu['ingredientes'])
        hierro = self.calcular_hierro_total(menu['ingredientes'])
        accesibilidad = self.calcular_score_accesibilidad(
            menu['ingredientes'], 
            contexto['departamento']
        )

        # 2. Calcular score nutricional (0-100)
        hierro_necesario = 7 if contexto['edad_meses'] < 12 else 10  # mg/día
        score_nutri = min(100, (hierro / hierro_necesario) * 100)

        # 3. Calcular score costo (0-100, invertido: más barato = mejor)
        presupuesto_comida = contexto.get('presupuesto_diario_s', 15.0) / 3  # Por comida

        if costo <= presupuesto_comida * 0.5:
            score_costo = 100  # Muy barato
        elif costo <= presupuesto_comida:
            score_costo = 75  # Dentro de presupuesto
        elif costo <= presupuesto_comida * 1.5:
            score_costo = 50  # Ligeramente caro
        else:
            score_costo = max(0, 100 - ((costo / presupuesto_comida) * 30))

        # 4. Score final ponderado
        score_final = (
            0.40 * score_nutri +      # Nutrición es lo más importante
            0.35 * score_costo +       # Costo es crítico
            0.25 * accesibilidad       # Accesibilidad regional
        )

        desglose = {
            'costo_s': costo,
            'hierro_mg': hierro,
            'score_nutri': round(score_nutri, 1),
            'score_costo': round(score_costo, 1),
            'score_accesibilidad': round(accesibilidad, 1),
            'score_final': round(score_final, 1)
        }

        return round(score_final, 1), desglose

    def recomendar_top3(self, menus: List[Dict], contexto: Dict) -> List[Dict]:
        """
        Devuelve top 3 menús rankeados por score

        Args:
            menus: Lista de menús con estructura estándar
            contexto: Contexto del paciente

        Returns:
            Top 3 menús con scores agregados
        """
        menus_con_score = []

        for menu in menus:
            score, desglose = self.calcular_score_menu(menu, contexto)

            menu_scored = menu.copy()
            menu_scored['score'] = score
            menu_scored['desglose'] = desglose

            menus_con_score.append(menu_scored)

        # Ordenar por score descendente
        menus_rankeados = sorted(menus_con_score, key=lambda x: x['score'], reverse=True)

        return menus_rankeados[:3]