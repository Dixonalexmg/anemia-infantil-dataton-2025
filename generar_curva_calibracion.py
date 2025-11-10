"""
CURVA DE CALIBRACIÓN - VERSIÓN FINAL SIN SOBREPOSICIONES
NutriWawa Perú - Datatón 3.0
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.calibration import calibration_curve
from sklearn.metrics import brier_score_loss, roc_auc_score
import joblib
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# CONFIGURACIÓN
MODELO_PATH = "models/predictor_anemia_ml_hibrido_v3.pkl"
DATOS_GT_PATH = "data/processed/sien_modelo_limpio.csv"
OUTPUT_DIR = "outputs/"
USE_ALL_DATA = True

Path(OUTPUT_DIR).mkdir(exist_ok=True)

print("="*80)
print("📊 CURVA DE CALIBRACIÓN - NutriWawa (SIN SOBREPOSICIONES)")
print("="*80)

# 1. CARGAR MODELO
print("\n[1] Cargando modelo...")
with open(MODELO_PATH, 'rb') as f:
    modelo_package = joblib.load(f)

modelo = modelo_package['model']
features_list = modelo_package['features']
threshold = modelo_package.get('threshold', 0.5)
metodo_calibracion = getattr(modelo, 'method', 'Unknown')

print(f"✅ Modelo: {type(modelo).__name__}")
print(f"   Método: {metodo_calibracion}")

# 2. CARGAR Y PREPARAR DATOS (mismo código de antes)
print("\n[2] Cargando datos...")
df_raw = pd.read_csv(DATOS_GT_PATH)
y_true = df_raw['tiene_anemia'].values
print(f"✅ Dataset: {df_raw.shape}")

# 3. FEATURE ENGINEERING (mismo código)
print("\n[3] Feature engineering...")
df = df_raw.copy()

mapeo_columnas = {
    'EdadMeses': 'edad_meses', 'sexo_numerico': 'sexo',
    'Hemoglobina_OMS2024': 'hemoglobina', 'AlturaREN': 'altitud',
    'suplementacion_bin': 'recibe_suplemento', 'cred_bin': 'asiste_cred',
    'area_rural': 'area_urbana', 'Juntos_num': 'juntos',
    'SIS_num': 'sis', 'Qaliwarma_num': 'qaliwarma',
    'DepartamentoREN': 'departamento'
}

for col_original, col_nueva in mapeo_columnas.items():
    if col_original in df.columns:
        df[col_nueva] = df[col_original]

if 'edad_meses' in df.columns:
    df['edad_anos'] = df['edad_meses'] / 12

if 'grupo_edad' in df.columns:
    grupos_edad = pd.get_dummies(df['grupo_edad'], prefix='grupo_edad')
    df = pd.concat([df, grupos_edad], axis=1)

if 'hemoglobina' in df.columns:
    df['hb_baja'] = (df['hemoglobina'] < 11.0).astype(int)
    df['hb_muy_baja'] = (df['hemoglobina'] < 9.0).astype(int)

if 'altitud' in df.columns:
    df['altitud_alta'] = (df['altitud'] >= 2500).astype(int)
    df['altitud_muy_alta'] = (df['altitud'] >= 3500).astype(int)

if 'area_urbana' in df.columns:
    df['area_urbana'] = 1 - df['area_urbana']

if 'recibe_suplemento' in df.columns:
    df['sin_suplemento'] = 1 - df['recibe_suplemento']
if 'asiste_cred' in df.columns:
    df['sin_cred'] = 1 - df['asiste_cred']

if all(col in df.columns for col in ['juntos', 'sis', 'qaliwarma']):
    df['sin_programas'] = ((df['juntos'] == 0) & (df['sis'] == 0) & (df['qaliwarma'] == 0)).astype(int)

departamentos_alto_riesgo = ['PUNO', 'CUSCO', 'HUANCAVELICA', 'APURIMAC', 'AYACUCHO', 'PASCO', 'JUNIN', 'CAJAMARCA']
if 'DepartamentoREN' in df.columns:
    for dept in departamentos_alto_riesgo:
        df[f'dept_{dept}'] = (df['DepartamentoREN'] == dept).astype(int)

if 'altitud' in df.columns and 'recibe_suplemento' in df.columns:
    df['altitud_sin_supl'] = df['altitud'] * df['sin_suplemento']

if 'area_urbana' in df.columns and 'asiste_cred' in df.columns:
    df['rural_sin_cred'] = (1 - df['area_urbana']) * df['sin_cred']

if 'hemoglobina' in df.columns and 'altitud' in df.columns:
    df['hb_x_altitud'] = df['hemoglobina'] * (df['altitud'] / 1000)

for feature in features_list:
    if feature not in df.columns:
        df[feature] = 0

# 4. PREPARAR DATOS
print("\n[4] Preparando datos...")
X = df[features_list].copy()
mask_validos = ~X.isnull().any(axis=1)
X_clean = X[mask_validos]
y_true_clean = y_true[mask_validos]

if not USE_ALL_DATA and len(X_clean) > 100000:
    np.random.seed(42)
    indices = np.random.choice(len(X_clean), 100000, replace=False)
    X_clean = X_clean.iloc[indices]
    y_true_clean = y_true_clean[indices]

print(f"✅ Dataset final: {len(X_clean):,} casos")

# 5. PREDICCIONES
print("\n[5] Generando predicciones...")
y_prob = modelo.predict_proba(X_clean)[:, 1]
print(f"✅ Predicciones generadas")

# 6. MÉTRICAS
print("\n[6] Calculando métricas...")
brier = brier_score_loss(y_true_clean, y_prob)
auc = roc_auc_score(y_true_clean, y_prob)
prob_true, prob_pred = calibration_curve(y_true_clean, y_prob, n_bins=10, strategy='uniform')
ece = np.abs(prob_true - prob_pred).mean()
mce = np.abs(prob_true - prob_pred).max()

print(f"\n📊 MÉTRICAS:")
print(f"   Brier: {brier:.4f}")
print(f"   ECE: {ece:.4f}")
print(f"   AUC: {auc:.4f}")

# Guardar métricas
metricas = {
    'brier_score': float(brier), 'ece': float(ece), 'mce': float(mce),
    'auc_roc': float(auc), 'n_samples': int(len(y_true_clean)),
    'prevalencia': float(y_true_clean.mean()),
    'metodo_calibracion': str(metodo_calibracion),
    'threshold': float(threshold)
}

json_path = f"{OUTPUT_DIR}metricas_calibracion.json"
with open(json_path, 'w') as f:
    json.dump(metricas, f, indent=2)

# 7. GRÁFICO CORREGIDO
print("\n[7] Generando gráfico (sin sobreposiciones)...")

plt.style.use('default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 12

fig, ax = plt.subplots(figsize=(12, 9), facecolor='white')

ax.plot(prob_pred, prob_true, marker='o', linewidth=3.5, markersize=12, 
        color='#2E86AB', markeredgecolor='white', markeredgewidth=2,
        label=f'NutriWawa (ECE={ece:.3f})', zorder=3)

ax.plot([0, 1], [0, 1], linestyle='--', linewidth=2.5, 
        color='#7f8c8d', alpha=0.7, label='Calibración Perfecta', zorder=2)

ax.fill_between(prob_pred, prob_pred, prob_true, alpha=0.25, color='#2E86AB', zorder=1)

ax.set_xlabel('Probabilidad Predicha (Confianza del Modelo)', 
              fontsize=14, fontweight='bold', labelpad=12)
ax.set_ylabel('Fracción Real de Casos Positivos', 
              fontsize=14, fontweight='bold', labelpad=12)

titulo = f'Curva de Calibración - NutriWawa Perú'
if metodo_calibracion != 'Unknown':
    titulo += f'\nMétodo: {metodo_calibracion.capitalize()}'
ax.set_title(titulo, fontsize=16, fontweight='bold', pad=20)

# LEYENDA - Superior derecha
ax.legend(loc='upper right', fontsize=12, frameon=True, 
          shadow=True, fancybox=True, framealpha=0.98,
          edgecolor='#2E86AB', facecolor='white')

ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.8)
ax.set_xlim(-0.02, 1.02)
ax.set_ylim(-0.02, 1.02)
ax.tick_params(labelsize=11)

# MÉTRICAS - Inferior derecha
textstr = f'Brier: {brier:.4f}\nECE: {ece:.4f}\nMCE: {mce:.4f}\nAUC: {auc:.4f}\nn = {len(y_true_clean):,}'
props = dict(boxstyle='round,pad=0.7', facecolor='#FFF9E6', alpha=0.98,
             edgecolor='#2E86AB', linewidth=2.5)

ax.text(0.98, 0.02, textstr, transform=ax.transAxes, fontsize=11,
        verticalalignment='bottom', horizontalalignment='right',
        bbox=props, family='monospace', fontweight='bold')

plt.tight_layout(pad=1.5)

output_png = f"{OUTPUT_DIR}curva_calibracion_NutriWawa.png"
plt.savefig(output_png, dpi=300, bbox_inches='tight', facecolor='white')
print(f"\n✅ Gráfico guardado: {output_png}")

plt.savefig(f"{OUTPUT_DIR}curva_calibracion_NutriWawa.pdf", format='pdf', bbox_inches='tight')
plt.show()

print("\n" + "="*80)
print("✅ CURVA GENERADA SIN SOBREPOSICIONES")
print("="*80)
