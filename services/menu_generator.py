# services/menu_generator.py
"""
Generador de menús personalizados ricos en hierro
Basado en Notebook 5: Motor Alimentario
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import logging
from utils.data_loader import data_loader

logger = logging.getLogger(__name__)


class MenuGenerator:
    """Generador de menús personalizados para combatir anemia"""
    
    def __init__(self):
        """Inicializa el generador"""
        self.alimentos_df = None
        self._cargar_base_alimentos()
    
    def _cargar_base_alimentos(self):
        """Carga base de datos de alimentos"""
        self.alimentos_df = data_loader.load_alimentos_hierro()
        if self.alimentos_df is None:
            logger.warning("Base de alimentos no disponible, usando datos por defecto")
            self.alimentos_df = self._crear_base_default()
    
    def _crear_base_default(self) -> pd.DataFrame:
        """Crea base de alimentos por defecto"""
        return pd.DataFrame({
            'nombre': [
                'Sangrecita de pollo', 'Bazo de res', 'Hígado de pollo',
                'Lentejas', 'Quinua', 'Espinaca', 'Huevo'
            ],
            'categoria': [
                'visceras', 'visceras', 'visceras',
                'menestras', 'cereales', 'verduras', 'proteinas'
            ],
            'hierro_mg_100g': [29.5, 25.3, 8.5, 7.6, 4.6, 2.7, 2.5],
            'precio_porcion': [0.35, 0.40, 0.50, 0.60, 0.80, 0.40, 0.50],
            'tipo': ['hemo', 'hemo', 'hemo', 'no_hemo', 'no_hemo', 'no_hemo', 'hemo']
        })
    
    def calcular_requerimiento_hierro(self, edad_meses: int) -> float:
        """
        Calcula requerimiento diario de hierro según edad (OMS/FAO 2024)
        
        Args:
            edad_meses: Edad del niño en meses
            
        Returns:
            Requerimiento en mg/día
        """
        if edad_meses < 6:
            return 6.0
        elif edad_meses < 12:
            return 11.0
        elif edad_meses < 36:
            return 7.0
        else:  # 36-59 meses
            return 10.0
    
    def generar_menu(
        self,
        edad_meses: int,
        presupuesto_diario: float = 5.0,
        region: str = "Costa",
        preferencias: Optional[List[str]] = None,
        excluir: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Genera un menú personalizado
        
        Args:
            edad_meses: Edad del niño
            presupuesto_diario: Presupuesto disponible en soles
            region: Costa, Sierra o Selva
            preferencias: Lista de alimentos preferidos
            excluir: Lista de alimentos a excluir
            
        Returns:
            Diccionario con menú completo
        """
        # 1. Calcular requerimiento
        req_hierro = self.calcular_requerimiento_hierro(edad_meses)
        
        # 2. Filtrar alimentos disponibles
        alimentos = self.alimentos_df.copy()
        
        if excluir:
            alimentos = alimentos[~alimentos['nombre'].isin(excluir)]
        
        # 3. Priorizar hierro hemo (mejor absorción)
        alimentos = alimentos.sort_values(
            ['tipo', 'hierro_mg_100g'],
            ascending=[False, False]  # Hemo primero, luego más hierro
        )
        
        # 4. Seleccionar alimentos dentro del presupuesto
        menu_items = []
        hierro_total = 0
        costo_total = 0
        
        # Prioridad 1: Al menos 1 fuente de hierro hemo
        hemo_foods = alimentos[alimentos['tipo'] == 'hemo']
        if not hemo_foods.empty and costo_total < presupuesto_diario:
            mejor_hemo = hemo_foods.iloc[0]
            menu_items.append({
                'alimento': mejor_hemo['nombre'],
                'categoria': mejor_hemo['categoria'],
                'hierro_mg': mejor_hemo['hierro_mg_100g'],
                'precio': mejor_hemo['precio_porcion'],
                'porcion': '100g',
                'tipo': 'hemo'
            })
            hierro_total += mejor_hemo['hierro_mg_100g']
            costo_total += mejor_hemo['precio_porcion']
        
        # Prioridad 2: Complementar con fuentes no-hemo
        presupuesto_restante = presupuesto_diario - costo_total
        no_hemo_foods = alimentos[alimentos['tipo'] == 'no_hemo']
        
        for _, alimento in no_hemo_foods.iterrows():
            if costo_total + alimento['precio_porcion'] <= presupuesto_diario:
                if hierro_total < req_hierro * 1.5:  # 150% para asegurar cobertura
                    menu_items.append({
                        'alimento': alimento['nombre'],
                        'categoria': alimento['categoria'],
                        'hierro_mg': alimento['hierro_mg_100g'],
                        'precio': alimento['precio_porcion'],
                        'porcion': '100g',
                        'tipo': 'no_hemo'
                    })
                    hierro_total += alimento['hierro_mg_100g']
                    costo_total += alimento['precio_porcion']
            
            if len(menu_items) >= 4:  # Máximo 4 alimentos por día
                break
        
        # 5. Calcular cobertura
        cobertura_pct = (hierro_total / req_hierro) * 100
        
        # 6. Generar preparaciones sugeridas
        preparaciones = self._generar_preparaciones(menu_items, edad_meses)
        
        # 7. Resultado
        resultado = {
            "edad_meses": edad_meses,
            "requerimiento_hierro_mg": round(req_hierro, 1),
            "hierro_aportado_mg": round(hierro_total, 1),
            "cobertura_pct": round(cobertura_pct, 1),
            "costo_total": round(costo_total, 2),
            "presupuesto": presupuesto_diario,
            "menu_items": menu_items,
            "preparaciones": preparaciones,
            "cumple_requerimiento": cobertura_pct >= 100,
            "evaluacion": self._evaluar_menu(cobertura_pct, costo_total, presupuesto_diario)
        }
        
        logger.info(f"Menú generado: {len(menu_items)} alimentos, {cobertura_pct:.1f}% cobertura, S/ {costo_total:.2f}")
        return resultado
    
    def _generar_preparaciones(self, menu_items: List[Dict], edad_meses: int) -> List[str]:
        """Genera sugerencias de preparación según edad"""
        preparaciones = []
        
        for item in menu_items:
            if item['categoria'] == 'visceras':
                if edad_meses < 12:
                    preparaciones.append(f"🍽️ {item['alimento']}: Papilla suave (bien cocido y triturado)")
                else:
                    preparaciones.append(f"🍽️ {item['alimento']}: Guiso con verduras o en segundo")
            
            elif item['categoria'] == 'menestras':
                preparaciones.append(f"🍽️ {item['alimento']}: Puré o sopa (combinar con vitamina C)")
            
            elif item['categoria'] == 'verduras':
                preparaciones.append(f"🍽️ {item['alimento']}: Al vapor o en puré")
        
        return preparaciones
    
    def _evaluar_menu(self, cobertura: float, costo: float, presupuesto: float) -> str:
        """Evalúa la calidad del menú generado"""
        if cobertura >= 150:
            return "⭐⭐⭐ EXCELENTE: Cubre ampliamente el requerimiento"
        elif cobertura >= 100:
            return "⭐⭐ MUY BUENO: Cubre el requerimiento"
        elif cobertura >= 75:
            return "⭐ BUENO: Cubre parcialmente, complementar con suplemento"
        else:
            return "⚠️ INSUFICIENTE: Requiere suplementación obligatoria"


# Instancia global del generador
menu_generator = MenuGenerator()
