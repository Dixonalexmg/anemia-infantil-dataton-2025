"""
GENERADOR DE TABLA DE UMBRALES DE DECISIÓN - CORREGIDO
Proyecto: NutriSenseIA - Datatón 3.0
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

OUTPUT_DIR = "outputs/"
Path(OUTPUT_DIR).mkdir(exist_ok=True)

print("="*80)
print("📊 GENERANDO TABLA DE UMBRALES DE DECISIÓN")
print("="*80)

# =====================================================
# DEFINICIÓN DE UMBRALES Y ACCIONES
# =====================================================

umbrales_decision = {
    'Rango de Probabilidad': [
        '[0.00 - 0.20)',
        '[0.20 - 0.40)',
        '[0.40 - 0.60)',
        '[0.60 - 0.80)',
        '[0.80 - 1.00]'
    ],
    'Nivel de Riesgo': [
        'Muy Bajo',
        'Bajo',
        'Moderado',
        'Alto',
        'Muy Alto'
    ],
    'Color Semáforo': [
        'Verde',
        'Amarillo',
        'Naranja',
        'Rojo',
        'Rojo Crítico'
    ],
    'Protocolo de Intervención': [
        'Seguimiento de rutina (CRED mensual)',
        'Monitoreo reforzado + consejería nutricional',
        'Evaluación HemoCue + suplementación preventiva',
        'Intervención intensiva + seguimiento semanal',
        'Acción inmediata + derivación a especialista'
    ],
    'Recursos Necesarios': [
        'Personal: Técnico de enfermería | Tiempo: 15 min | Insumos: Ninguno adicional',
        'Personal: Nutricionista | Tiempo: 30 min | Insumos: Material educativo',
        'Personal: Enfermera + Nutricionista | Tiempo: 45 min | Insumos: HemoCue, suplementos',
        'Personal: Médico + Nutricionista | Tiempo: 60 min | Insumos: HemoCue, suplementos, recetas',
        'Personal: Equipo multidisciplinario | Tiempo: 90 min | Insumos: Análisis completo, derivación'
    ],
    'Frecuencia de Seguimiento': [
        'Cada 3 meses',
        'Cada 2 meses',
        'Mensual',
        'Quincenal',
        'Semanal'
    ],
    'Prevalencia Estimada': [
        '65-70%',
        '15-20%',
        '5-8%',
        '3-5%',
        '2-3%'
    ],
    'Costo por Caso (S/)': [
        10,
        35,
        85,
        150,
        280
    ]
}

# Crear DataFrame
df_umbrales = pd.DataFrame(umbrales_decision)

# =====================================================
# GUARDAR EN CSV
# =====================================================
csv_path = f"{OUTPUT_DIR}tabla_umbrales_decision.csv"
df_umbrales.to_csv(csv_path, index=False, encoding='utf-8-sig')
print(f"\n✅ Tabla CSV guardada en: {csv_path}")

# =====================================================
# GUARDAR EN EXCEL (SIN openpyxl - usar xlsxwriter si está disponible)
# =====================================================
try:
    excel_path = f"{OUTPUT_DIR}tabla_umbrales_decision.xlsx"
    df_umbrales.to_excel(excel_path, index=False, engine='xlsxwriter')
    print(f"✅ Tabla Excel guardada en: {excel_path}")
except ImportError:
    print(f"ℹ️  Para Excel, instala: pip install openpyxl")
    print(f"   Continuando sin Excel...")

# =====================================================
# VISUALIZACIÓN GRÁFICA
# =====================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# GRÁFICO 1: Distribución de recursos por nivel de riesgo
niveles = df_umbrales['Nivel de Riesgo']
costos = df_umbrales['Costo por Caso (S/)']
prevalencia = [float(p.split('-')[0]) for p in df_umbrales['Prevalencia Estimada']]

colores = ['#27ae60', '#f39c12', '#e67e22', '#e74c3c', '#c0392b']

ax1.bar(niveles, costos, color=colores, edgecolor='black', linewidth=1.5, alpha=0.8)
ax1.set_xlabel('Nivel de Riesgo', fontsize=12, fontweight='bold')
ax1.set_ylabel('Costo por Caso (S/)', fontsize=12, fontweight='bold')
ax1.set_title('Costo de Intervención por Nivel de Riesgo', fontsize=14, fontweight='bold', pad=15)
ax1.grid(axis='y', alpha=0.3)

# Añadir valores sobre barras
for i, (nivel, costo) in enumerate(zip(niveles, costos)):
    ax1.text(i, costo + 10, f'S/ {costo}', ha='center', fontweight='bold', fontsize=10)

ax1.tick_params(axis='x', rotation=45)

# GRÁFICO 2: Prevalencia estimada
ax2.pie(prevalencia, labels=niveles, colors=colores, autopct='%1.1f%%',
        startangle=90, textprops={'fontsize': 10, 'fontweight': 'bold'},
        wedgeprops={'edgecolor': 'black', 'linewidth': 1.5})
ax2.set_title('Distribución Estimada de Casos por Nivel de Riesgo', 
              fontsize=14, fontweight='bold', pad=15)

plt.tight_layout()
img_path = f"{OUTPUT_DIR}umbrales_decision_grafico.png"
plt.savefig(img_path, dpi=300, bbox_inches='tight', facecolor='white')
print(f"✅ Gráfico guardado en: {img_path}")

plt.show()

# =====================================================
# GENERAR MARKDOWN
# =====================================================
markdown_content = """# Tabla de Umbrales de Decisión - NutriSenseIA

## Protocolo de Actuación Basado en Probabilidad de Riesgo

| Probabilidad | Nivel | Semáforo | Protocolo | Frecuencia | Costo |
|-------------|-------|----------|-----------|------------|-------|
"""

for _, row in df_umbrales.iterrows():
    protocolo_corto = row['Protocolo de Intervención'][:50] + "..."
    markdown_content += f"| {row['Rango de Probabilidad']} | **{row['Nivel de Riesgo']}** | {row['Color Semáforo']} | {protocolo_corto} | {row['Frecuencia de Seguimiento']} | S/ {row['Costo por Caso (S/)']} |\n"

markdown_content += """
## Criterios de Escalamiento

- **Muy Bajo (0-20%)**: Seguimiento rutinario según cronograma CRED
- **Bajo (20-40%)**: Refuerzo educativo y consejería nutricional familiar
- **Moderado (40-60%)**: **UMBRAL DE ACCIÓN** - Medición HemoCue obligatoria + suplementación preventiva
- **Alto (60-80%)**: Intervención intensiva con seguimiento quincenal y evaluación médica
- **Muy Alto (80-100%)**: **ALERTA CRÍTICA** - Acción inmediata, equipo multidisciplinario, derivación

---
*Generado por NutriSenseIA - Datatón 3.0 MINSA*
"""

md_path = f"{OUTPUT_DIR}umbrales_decision.md"
with open(md_path, 'w', encoding='utf-8') as f:
    f.write(markdown_content)

print(f"✅ Documentación Markdown guardada en: {md_path}")

print("\n" + "="*80)
print("✅ TABLA DE UMBRALES COMPLETADA")
print("="*80)
