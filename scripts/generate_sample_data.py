# scripts/generate_sample_data.py
"""
Genera datos de ejemplo para desarrollo
"""
import pandas as pd
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
DATA_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("GENERANDO DATOS DE EJEMPLO PARA DATATÓN 2025")
print("=" * 70)

# 1. SIEN Nacional
print("\n1. Generando SIEN Nacional...")
df_sien = pd.DataFrame({
    'sw': range(1000),
    'EdadEnMeses': [12, 24, 36, 18, 30] * 200,
    'Hemoglobina': [10.5, 11.2, 9.8, 12.1, 10.9] * 200,
    'tiene_anemia': [1, 0, 1, 0, 1] * 200,
    'DepartamentoREN': ['LIMA', 'PIURA', 'CUSCO', 'AREQUIPA', 'JUNIN'] * 200
})
df_sien.to_csv(DATA_DIR / 'sien_nacional_procesado.csv', index=False)
print(f"   ✅ sien_nacional_procesado.csv ({len(df_sien):,} registros)")

# 2. Alimentos
print("\n2. Generando Base de Alimentos...")
df_alimentos = pd.DataFrame({
    'nombre': ['Sangrecita de pollo', 'Hígado de res', 'Lentejas', 'Espinaca', 'Quinua'],
    'categoria': ['visceras', 'visceras', 'menestras', 'verduras', 'cereales'],
    'hierro_mg_100g': [29.5, 6.5, 7.6, 2.7, 4.6],
    'precio_porcion': [0.35, 0.80, 0.60, 0.40, 0.70],
    'tipo': ['hemo', 'hemo', 'no_hemo', 'no_hemo', 'no_hemo']
})
df_alimentos.to_csv(DATA_DIR / 'base_alimentos_hierro.csv', index=False)
print(f"   ✅ base_alimentos_hierro.csv ({len(df_alimentos)} alimentos)")

# 3. Brechas por Departamento
print("\n3. Generando Brechas por Departamento...")
departamentos = ['LIMA', 'PIURA', 'CUSCO', 'AREQUIPA', 'JUNIN', 'PUNO', 'LORETO', 
                 'LA LIBERTAD', 'CAJAMARCA', 'AYACUCHO', 'HUANCAVELICA', 'APURIMAC',
                 'ANCASH', 'ICA', 'LAMBAYEQUE', 'UCAYALI', 'MADRE DE DIOS', 'TACNA',
                 'MOQUEGUA', 'TUMBES', 'SAN MARTIN', 'PASCO', 'AMAZONAS', 'HUANUCO']

df_brechas = pd.DataFrame({
    'departamento': departamentos,
    'prevalencia_pct': [10.5, 15.2, 18.7, 9.8, 12.3, 19.1, 16.8, 
                        13.4, 17.2, 18.9, 20.5, 19.7,
                        14.1, 8.9, 11.7, 15.9, 12.8, 6.5,
                        7.2, 10.1, 14.5, 16.3, 17.8, 16.9],
    'brecha_q4_q1_pp': [5.2, 8.1, 12.3, 4.5, 7.8, 13.2, 10.5,
                         6.9, 11.8, 12.9, 14.1, 13.5,
                         7.3, 3.8, 6.2, 9.7, 7.1, 2.9,
                         3.1, 5.4, 8.8, 10.2, 11.5, 10.8],
    'indice_concentracion': [-0.05, -0.08, -0.12, -0.03, -0.07, -0.13, -0.10,
                              -0.06, -0.11, -0.12, -0.14, -0.13,
                              -0.07, -0.03, -0.06, -0.09, -0.07, -0.02,
                              -0.03, -0.05, -0.08, -0.10, -0.11, -0.10]
})
df_brechas.to_csv(DATA_DIR / 'brechas_departamento.csv', index=False)
print(f"   ✅ brechas_departamento.csv ({len(df_brechas)} departamentos)")

# 4. Tendencias
print("\n4. Generando Tendencias por Departamento...")
df_tendencias = pd.DataFrame({
    'departamento': departamentos,
    'tendencia_pp_mes': [0.5, 1.2, 2.1, -0.3, 0.8, 2.3, 1.8,
                         0.9, 1.9, 2.2, 2.5, 2.4,
                         1.1, -0.2, 0.6, 1.6, 0.9, -0.9,
                         -0.5, 0.4, 1.3, 1.7, 2.0, 1.8],
    'prevalencia_actual_pct': [10.5, 15.2, 18.7, 9.8, 12.3, 19.1, 16.8,
                               13.4, 17.2, 18.9, 20.5, 19.7,
                               14.1, 8.9, 11.7, 15.9, 12.8, 6.5,
                               7.2, 10.1, 14.5, 16.3, 17.8, 16.9],
    'r_cuadrado': [0.45, 0.62, 0.78, 0.35, 0.51, 0.81, 0.72,
                   0.58, 0.74, 0.79, 0.85, 0.82,
                   0.59, 0.32, 0.48, 0.68, 0.54, 0.76,
                   0.71, 0.42, 0.61, 0.69, 0.75, 0.70]
})
df_tendencias.to_csv(DATA_DIR / 'tendencias_departamento.csv', index=False)
print(f"   ✅ tendencias_departamento.csv ({len(df_tendencias)} departamentos)")

# 5. Proyecciones
print("\n5. Generando Proyecciones Temporales...")
df_proy = pd.DataFrame({
    'periodo': ['2025-07', '2025-08', '2025-09'],
    'SES': [13.7, 13.9, 14.1],
    'Holt_Winters': [14.6, 15.3, 16.1],
    'Lineal': [14.2, 14.7, 15.2],
    'Ensamble': [14.3, 14.8, 15.3]
})
df_proy.to_csv(DATA_DIR / 'proyecciones_3_meses.csv', index=False)
print(f"   ✅ proyecciones_3_meses.csv ({len(df_proy)} periodos)")

# 6. Reporte Temporal (JSON)
print("\n6. Generando Reporte Temporal...")
reporte_temporal = {
    "fecha_generacion": "2025-10-10",
    "estadisticas_serie": {
        "prevalencia_promedio_pct": 11.91,
        "variacion_relativa_pct": 48.84,
        "desviacion_estandar_pp": 2.22,
        "variacion_absoluta_pp": 5.35,
        "prevalencia_minima_pct": 9.99,
        "prevalencia_maxima_pct": 16.30
    },
    "tendencia_nacional": {
        "pendiente_pp_mes": 2.20,
        "r_cuadrado": 0.78
    },
    "proyecciones_3_meses": {
        "ensamble_pct": [14.3, 14.8, 15.3]
    },
    "alertas": [
        {
            "tipo": "CRÍTICO",
            "mensaje": "Incremento de 48.8% en el periodo analizado (enero-junio 2025)"
        },
        {
            "tipo": "ADVERTENCIA",
            "mensaje": "5 departamentos con tendencia creciente >1.2 pp/mes"
        },
        {
            "tipo": "INFORMATIVO",
            "mensaje": "TACNA muestra declive sostenido: -0.9 pp/mes"
        }
    ]
}
with open(DATA_DIR / 'reporte_temporal.json', 'w', encoding='utf-8') as f:
    json.dump(reporte_temporal, f, indent=2, ensure_ascii=False)
print("   ✅ reporte_temporal.json")

# 7. Reporte Equidad (JSON)
print("\n7. Generando Reporte de Equidad...")
reporte_equidad = {
    "fecha_generacion": "2025-10-10",
    "indice_concentracion": -0.0773,
    "descomposicion_oaxaca_blinder": {
        "brecha_total_pp": 5.64,
        "explicada_pp": -1.84,
        "no_explicada_pp": 7.48,
        "no_explicada_pct": 132.62
    }
}
with open(DATA_DIR / 'reporte_equidad.json', 'w', encoding='utf-8') as f:
    json.dump(reporte_equidad, f, indent=2, ensure_ascii=False)
print("   ✅ reporte_equidad.json")

# Resumen
print("\n" + "=" * 70)
print("🎉 DATOS GENERADOS EXITOSAMENTE")
print("=" * 70)
print(f"\n📁 Ubicación: {DATA_DIR}")
print("\n📊 Archivos creados:")
print("   1. sien_nacional_procesado.csv     (1,000 registros)")
print("   2. base_alimentos_hierro.csv       (5 alimentos)")
print("   3. brechas_departamento.csv        (24 departamentos)")
print("   4. tendencias_departamento.csv     (24 departamentos)")
print("   5. proyecciones_3_meses.csv        (3 periodos)")
print("   6. reporte_temporal.json")
print("   7. reporte_equidad.json")
print("\n✅ Listo para usar en la aplicación Streamlit")
print("=" * 70)
