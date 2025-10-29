# utils/adherencia.py
"""
Sistema de tracking de adherencia a menús
Métrica clave: % de menús que las madres realmente preparan
Objetivo: +15pp vs baseline (ENDES 2023)
"""

import csv
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


BASELINE_ADHERENCIA = 57.3  # ENDES 2023 (ejemplo - ajustar con datos reales)


def registrar_adherencia(caso_id: str, 
                        menu_id: str, 
                        menu_tipo: str,
                        preparado: bool,
                        comentario: str = ""):
    """
    Registra si la madre preparó el menú
    
    Args:
        caso_id: ID único del caso
        menu_id: ID del menú (ej: "desayuno_andino")
        menu_tipo: "desayuno" | "almuerzo" | "cena"
        preparado: True si lo preparó
        comentario: Feedback opcional de la madre
    """
    log_file = Path('data/logs/adherencia_menus.csv')
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Crear archivo si no existe
    if not log_file.exists():
        with open(log_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp', 'caso_id', 'menu_id', 'menu_tipo', 
                'preparado', 'comentario'
            ])
    
    # Agregar registro
    with open(log_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            caso_id,
            menu_id,
            menu_tipo,
            1 if preparado else 0,
            comentario
        ])


def calcular_adherencia_global() -> Dict:
    """
    Calcula métricas de adherencia global
    
    Returns:
        {
            'adherencia_pct': 72.5,
            'n_preparados': 145,
            'n_totales': 200,
            'mejora_vs_baseline': +15.2,
            'objetivo_cumplido': True,
            'por_tipo_menu': {...}
        }
    """
    log_file = Path('data/logs/adherencia_menus.csv')
    
    if not log_file.exists():
        return {
            'adherencia_pct': 0.0,
            'n_preparados': 0,
            'n_totales': 0,
            'mejora_vs_baseline': -BASELINE_ADHERENCIA,
            'objetivo_cumplido': False,
            'por_tipo_menu': {}
        }
    
    df = pd.read_csv(log_file)
    
    if len(df) == 0:
        return {
            'adherencia_pct': 0.0,
            'n_preparados': 0,
            'n_totales': 0,
            'mejora_vs_baseline': -BASELINE_ADHERENCIA,
            'objetivo_cumplido': False,
            'por_tipo_menu': {}
        }
    
    n_preparados = df['preparado'].sum()
    n_totales = len(df)
    
    adherencia_pct = (n_preparados / n_totales) * 100
    mejora = adherencia_pct - BASELINE_ADHERENCIA
    objetivo_cumplido = mejora >= 15.0
    
    # Adherencia por tipo de menú
    por_tipo = {}
    for tipo in ['desayuno', 'almuerzo', 'cena']:
        df_tipo = df[df['menu_tipo'] == tipo]
        if len(df_tipo) > 0:
            prep_tipo = df_tipo['preparado'].sum()
            pct_tipo = (prep_tipo / len(df_tipo)) * 100
            por_tipo[tipo] = {
                'adherencia_pct': round(pct_tipo, 1),
                'n_preparados': int(prep_tipo),
                'n_totales': len(df_tipo)
            }
    
    return {
        'adherencia_pct': round(adherencia_pct, 1),
        'n_preparados': int(n_preparados),
        'n_totales': int(n_totales),
        'mejora_vs_baseline': round(mejora, 1),
        'objetivo_cumplido': objetivo_cumplido,
        'baseline': BASELINE_ADHERENCIA,
        'por_tipo_menu': por_tipo
    }


def calcular_adherencia_por_paciente(caso_id: str) -> Dict:
    """Calcula adherencia individual de un paciente"""
    log_file = Path('data/logs/adherencia_menus.csv')
    
    if not log_file.exists():
        return {'adherencia_pct': 0, 'n_preparados': 0, 'n_totales': 0}
    
    df = pd.read_csv(log_file)
    df_paciente = df[df['caso_id'] == caso_id]
    
    if len(df_paciente) == 0:
        return {'adherencia_pct': 0, 'n_preparados': 0, 'n_totales': 0}
    
    n_prep = df_paciente['preparado'].sum()
    n_tot = len(df_paciente)
    pct = (n_prep / n_tot) * 100
    
    return {
        'adherencia_pct': round(pct, 1),
        'n_preparados': int(n_prep),
        'n_totales': int(n_tot)
    }


def exportar_reporte_adherencia(output_path: str = "data/reports/adherencia_menus.csv"):
    """Exporta reporte detallado de adherencia"""
    log_file = Path('data/logs/adherencia_menus.csv')
    
    if not log_file.exists():
        return None
    
    df = pd.read_csv(log_file)
    
    # Agregar columnas calculadas
    df['fecha'] = pd.to_datetime(df['timestamp']).dt.date
    df['hora'] = pd.to_datetime(df['timestamp']).dt.hour
    
    # Agrupar por fecha
    df_resumen = df.groupby('fecha').agg({
        'preparado': ['sum', 'count', 'mean']
    }).reset_index()
    
    df_resumen.columns = ['fecha', 'n_preparados', 'n_totales', 'adherencia_pct']
    df_resumen['adherencia_pct'] = df_resumen['adherencia_pct'] * 100
    
    # Guardar
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df_resumen.to_csv(output_file, index=False)
    
    return output_file
