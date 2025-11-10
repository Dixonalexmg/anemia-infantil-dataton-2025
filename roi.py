"""
CALCULADORA DE ROI Y ANÁLISIS DE SENSIBILIDAD - CORREGIDO
Proyecto: NutriSenseIA - Datatón 3.0
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

OUTPUT_DIR = "outputs/"
Path(OUTPUT_DIR).mkdir(exist_ok=True)

print("="*80)
print("💰 ANÁLISIS DE ROI Y SENSIBILIDAD")
print("="*80)

# =====================================================
# SUPUESTOS DEL MODELO
# =====================================================

supuestos = {
    'Población objetivo (niños < 5 años)': 3_500_000,
    'Prevalencia de anemia': 0.40,
    'Cobertura CRED actual': 0.75,
    'Casos esperados de anemia': 1_050_000,
    'Casos detectables con cobertura': 787_500,
    'Costo HemoCue universal (S/ por niño)': 25,
    'Costo tratamiento anemia (S/ por caso)': 180,
    'Costo seguimiento anemia (S/ por caso/mes)': 45,
    'Duración promedio tratamiento (meses)': 6,
    'Costo predicción NutriSenseIA (S/ por niño)': 2,
    'Costo HemoCue focalizado (S/ por niño alto riesgo)': 25,
    'Reducción en HemoCue innecesarios': 0.70,
    'Mejora en adherencia por detección temprana': 0.25,
    'Reducción en casos severos': 0.30,
}

print("\n📊 SUPUESTOS DEL MODELO:")
for key, value in supuestos.items():
    if isinstance(value, float) and value < 1:
        print(f"   • {key}: {value:.1%}")
    elif isinstance(value, int) and value > 1000:
        print(f"   • {key}: {value:,}")
    else:
        print(f"   • {key}: {value}")

# =====================================================
# CÁLCULO DE ROI
# =====================================================

print("\n" + "="*80)
print("💵 CÁLCULO DE ROI - ESCENARIO BASE")
print("="*80)

poblacion = supuestos['Población objetivo (niños < 5 años)']
cobertura = supuestos['Cobertura CRED actual']
poblacion_cubierta = int(poblacion * cobertura)

# Método tradicional
costo_hemocue_universal = poblacion_cubierta * supuestos['Costo HemoCue universal (S/ por niño)']
casos_anemia_detectados = supuestos['Casos detectables con cobertura']
costo_tratamiento_tradicional = casos_anemia_detectados * (
    supuestos['Costo tratamiento anemia (S/ por caso)'] +
    supuestos['Costo seguimiento anemia (S/ por caso/mes)'] * supuestos['Duración promedio tratamiento (meses)']
)

costo_total_tradicional = costo_hemocue_universal + costo_tratamiento_tradicional

print(f"\n🔴 MÉTODO TRADICIONAL (Sin NutriSenseIA):")
print(f"   • Costo screening universal (HemoCue): S/ {costo_hemocue_universal:,.0f}")
print(f"   • Costo tratamiento casos detectados: S/ {costo_tratamiento_tradicional:,.0f}")
print(f"   • COSTO TOTAL: S/ {costo_total_tradicional:,.0f}")

# Con NutriSenseIA
costo_prediccion_total = poblacion_cubierta * supuestos['Costo predicción NutriSenseIA (S/ por niño)']
poblacion_alto_riesgo = poblacion_cubierta * (1 - supuestos['Reducción en HemoCue innecesarios'])
costo_hemocue_focalizado = poblacion_alto_riesgo * supuestos['Costo HemoCue focalizado (S/ por niño alto riesgo)']

reduccion_severidad = supuestos['Reducción en casos severos']
costo_tratamiento_nutrisense = casos_anemia_detectados * (
    supuestos['Costo tratamiento anemia (S/ por caso)'] * (1 - reduccion_severidad * 0.4) +
    supuestos['Costo seguimiento anemia (S/ por caso/mes)'] * supuestos['Duración promedio tratamiento (meses)'] * (1 - reduccion_severidad * 0.3)
)

costo_total_nutrisense = costo_prediccion_total + costo_hemocue_focalizado + costo_tratamiento_nutrisense

print(f"\n🟢 CON NUTRISENSEIA:")
print(f"   • Costo predicción (población cubierta): S/ {costo_prediccion_total:,.0f}")
print(f"   • Costo HemoCue focalizado (30% de población): S/ {costo_hemocue_focalizado:,.0f}")
print(f"   • Costo tratamiento optimizado: S/ {costo_tratamiento_nutrisense:,.0f}")
print(f"   • COSTO TOTAL: S/ {costo_total_nutrisense:,.0f}")

# ROI
ahorro_total = costo_total_tradicional - costo_total_nutrisense
inversion_nutrisense = 5_000_000
roi = (ahorro_total - inversion_nutrisense) / inversion_nutrisense * 100
payback_meses = inversion_nutrisense / (ahorro_total / 12)

print(f"\n" + "="*80)
print(f"📈 RETORNO DE INVERSIÓN (ROI)")
print(f"="*80)
print(f"   💰 Ahorro anual: S/ {ahorro_total:,.0f}")
print(f"   📊 Inversión inicial: S/ {inversion_nutrisense:,.0f}")
print(f"   🎯 ROI: {roi:.1f}%")
print(f"   ⏱️  Periodo de recuperación (Payback): {payback_meses:.1f} meses")

# =====================================================
# ANÁLISIS DE SENSIBILIDAD - CORREGIDO
# =====================================================

print(f"\n" + "="*80)
print(f"📊 ANÁLISIS DE SENSIBILIDAD")
print(f"="*80)

# Variables con NOMBRES CORRECTOS
variables_sensibilidad = {
    'Reducción en HemoCue innecesarios': np.arange(0.5, 0.9, 0.1),
    'Reducción en casos severos': np.arange(0.1, 0.5, 0.1),
    'Prevalencia de anemia': np.arange(0.30, 0.50, 0.05),
    'Cobertura CRED actual': np.arange(0.60, 0.90, 0.05)  # ← CORREGIDO
}

resultados_sensibilidad = {}

for variable, valores in variables_sensibilidad.items():
    rois = []
    for valor in valores:
        # Recalcular simplificado
        if variable == 'Reducción en HemoCue innecesarios':
            ahorro_hemocue = costo_hemocue_universal * valor
            ahorro_temp = ahorro_hemocue - costo_prediccion_total
        elif variable == 'Reducción en casos severos':
            ahorro_tratamiento = costo_tratamiento_tradicional * valor * 0.3
            ahorro_temp = ahorro_total + ahorro_tratamiento - ahorro_total
        elif variable == 'Cobertura CRED actual':  # ← CORREGIDO
            factor = valor / supuestos['Cobertura CRED actual']
            ahorro_temp = ahorro_total * factor
        else:
            factor = valor / supuestos[variable]
            ahorro_temp = ahorro_total * factor
        
        roi_temp = (ahorro_temp - inversion_nutrisense) / inversion_nutrisense * 100
        rois.append(roi_temp)
    
    resultados_sensibilidad[variable] = (valores, rois)

# VISUALIZACIÓN
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
axes = axes.flatten()

for idx, (variable, (valores, rois)) in enumerate(resultados_sensibilidad.items()):
    ax = axes[idx]
    
    if all(v < 1 for v in valores):
        valores_plot = valores * 100
        xlabel = f"{variable} (%)"
    else:
        valores_plot = valores
        xlabel = variable
    
    ax.plot(valores_plot, rois, marker='o', linewidth=3, markersize=10, color='#667eea')
    ax.axhline(y=0, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Break-even')
    ax.fill_between(valores_plot, 0, rois, alpha=0.2, color='#667eea')
    
    ax.set_xlabel(xlabel, fontsize=12, fontweight='bold')
    ax.set_ylabel('ROI (%)', fontsize=12, fontweight='bold')
    ax.set_title(f'Sensibilidad: {variable}', fontsize=13, fontweight='bold', pad=10)
    ax.grid(True, alpha=0.3)
    ax.legend()

plt.tight_layout()
img_path = f"{OUTPUT_DIR}analisis_sensibilidad_roi.png"
plt.savefig(img_path, dpi=300, bbox_inches='tight', facecolor='white')
print(f"\n✅ Gráfico de sensibilidad guardado en: {img_path}")

plt.show()

# Guardar Excel
try:
    df_roi = pd.DataFrame({
        'Concepto': [
            'Población objetivo',
            'Cobertura CRED',
            'COSTO TRADICIONAL',
            'COSTO NUTRISENSEIA',
            'Ahorro anual',
            'ROI (%)',
            'Payback (meses)'
        ],
        'Valor': [
            f'{poblacion:,}',
            f'{cobertura:.1%}',
            f'S/ {costo_total_tradicional:,.0f}',
            f'S/ {costo_total_nutrisense:,.0f}',
            f'S/ {ahorro_total:,.0f}',
            f'{roi:.1f}%',
            f'{payback_meses:.1f}'
        ]
    })
    
    excel_path = f"{OUTPUT_DIR}analisis_roi_completo.xlsx"
    df_roi.to_excel(excel_path, index=False, engine='xlsxwriter')
    print(f"✅ Excel guardado en: {excel_path}")
except ImportError:
    csv_path = f"{OUTPUT_DIR}analisis_roi_completo.csv"
    df_roi.to_csv(csv_path, index=False)
    print(f"✅ CSV guardado en: {csv_path}")

print("\n" + "="*80)
print("✅ ANÁLISIS DE ROI COMPLETADO")
print("="*80)
