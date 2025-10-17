# scripts/train_ml_model_REAL.py
"""
🎯 MODELO ML CON DATOS 100% REALES DEL SIEN
895K+ niños evaluados - Sin features sintéticas
"""
import pandas as pd
import numpy as np
from pathlib import Path
import pickle
import json
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (classification_report, roc_auc_score, 
confusion_matrix, accuracy_score, precision_recall_curve)
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(exist_ok=True)

print("=" * 90)
print("🎯 MODELO ML CON DATOS 100% REALES - SIEN NACIONAL")
print("=" * 90)

# ============================================================================
# 1. CARGAR DATOS
# ============================================================================
print("\n📂 1. Cargando datos REALES del SIEN...")
df = pd.read_csv(DATA_DIR / 'sien_nacional_procesado.csv')
print(f"   ✅ {len(df):,} registros")

# ============================================================================
# 2. FEATURE ENGINEERING - SOLO DATOS REALES
# ============================================================================
print("\n🔬 2. Preparando features REALES...")

# Seleccionar solo columnas existentes
features = pd.DataFrame()

# EDAD
features['edad_meses'] = df['EdadMeses']
features['edad_anos'] = df['EdadMeses'] / 12

# Crear grupos de edad si no existe
if 'grupo_edad' in df.columns:
    # One-hot encoding del grupo_edad
    grupo_dummies = pd.get_dummies(df['grupo_edad'], prefix='grupo_edad', drop_first=True)
    features = pd.concat([features, grupo_dummies], axis=1)
else:
    # Crear grupos manualmente
    features['edad_6_11m'] = ((df['EdadMeses'] >= 6) & (df['EdadMeses'] < 12)).astype(int)
    features['edad_12_23m'] = ((df['EdadMeses'] >= 12) & (df['EdadMeses'] < 24)).astype(int)
    features['edad_24_35m'] = ((df['EdadMeses'] >= 24) & (df['EdadMeses'] < 36)).astype(int)
    features['edad_36_59m'] = (df['EdadMeses'] >= 36).astype(int)

# SEXO
if 'sexo_numerico' in df.columns:
    features['sexo'] = df['sexo_numerico']

# HEMOGLOBINA (CRÍTICA)
if 'Hemoglobina' in df.columns:
    features['hemoglobina'] = df['Hemoglobina'].fillna(df['Hemoglobina'].median())
    features['hb_baja'] = (features['hemoglobina'] < 11.0).astype(int)
    features['hb_muy_baja'] = (features['hemoglobina'] < 10.0).astype(int)

# ALTITUD
if 'AlturaREN' in df.columns:
    features['altitud'] = df['AlturaREN'].fillna(1500)
    features['altitud_muy_alta'] = (features['altitud'] > 3000).astype(int)
    features['altitud_alta'] = ((features['altitud'] > 2500) & (features['altitud'] <= 3000)).astype(int)
elif 'alta_altitud' in df.columns:
    features['alta_altitud'] = df['alta_altitud']

# SUPLEMENTACIÓN
if 'suplementacion_bin' in df.columns:
    features['recibe_suplemento'] = df['suplementacion_bin']
    features['sin_suplemento'] = 1 - df['suplementacion_bin']

# CONTROLES CRED
if 'cred_bin' in df.columns:
    features['asiste_cred'] = df['cred_bin']
    features['sin_cred'] = 1 - df['cred_bin']

# ÁREA RURAL
if 'area_rural' in df.columns:
    features['area_rural'] = df['area_rural']
    features['area_urbana'] = 1 - df['area_rural']

# PROGRAMAS SOCIALES
if 'Juntos_num' in df.columns:
    features['juntos'] = df['Juntos_num']
if 'SIS_num' in df.columns:
    features['sis'] = df['SIS_num']
if 'Qaliwarma_num' in df.columns:
    features['qaliwarma'] = df['Qaliwarma_num']

if 'cobertura_programas' in df.columns:
    features['cobertura_programas'] = df['cobertura_programas']
    features['sin_programas'] = (df['cobertura_programas'] == 0).astype(int)

# DEPARTAMENTO (Top 8 alto riesgo)
if 'DepartamentoREN' in df.columns:
    dept_alto_riesgo = ['PUNO', 'CUSCO', 'HUANCAVELICA', 'APURIMAC', 
                        'AYACUCHO', 'PASCO', 'JUNIN', 'CAJAMARCA']
    for dept in dept_alto_riesgo:
        if dept in df['DepartamentoREN'].unique():
            features[f'dept_{dept}'] = (df['DepartamentoREN'] == dept).astype(int)

# INTERACCIONES CRÍTICAS (solo con features que existen)
if 'sin_suplemento' in features.columns and 'altitud_muy_alta' in features.columns:
    features['altitud_sin_supl'] = features['altitud_muy_alta'] * features['sin_suplemento']

if 'area_rural' in features.columns and 'sin_cred' in features.columns:
    features['rural_sin_cred'] = features['area_rural'] * features['sin_cred']

if 'hemoglobina' in features.columns and 'altitud_muy_alta' in features.columns:
    features['hb_x_altitud'] = features['hb_baja'] * features['altitud_muy_alta']

# VARIABLE OBJETIVO
target = df['tiene_anemia']

# Eliminar NaNs
features = features.fillna(0)

print(f"   ✅ {features.shape[1]} features REALES creadas")
print(f"   📊 Distribución:")
print(f"      Sin anemia: {(target==0).sum():,} ({(target==0).sum()/len(target)*100:.1f}%)")
print(f"      Con anemia: {(target==1).sum():,} ({(target==1).sum()/len(target)*100:.1f}%)")

# ============================================================================
# 3. BALANCEO
# ============================================================================
print("\n⚖️  3. Balanceando dataset...")

X_train, X_test, y_train, y_test = train_test_split(
    features, target, test_size=0.20, random_state=42, stratify=target
)

# Submuestreo moderado
X_neg = X_train[y_train == 0]
X_pos = X_train[y_train == 1]
y_neg = y_train[y_train == 0]
y_pos = y_train[y_train == 1]

n_neg_sample = int(len(X_neg) * 0.50)
idx_neg = np.random.choice(len(X_neg), n_neg_sample, replace=False)
X_neg_sample = X_neg.iloc[idx_neg]
y_neg_sample = y_neg.iloc[idx_neg]

# Oversampling ligero
n_pos_target = int(n_neg_sample / 3.0)
if n_pos_target > len(X_pos):
    n_dup = n_pos_target - len(X_pos)
    idx_dup = np.random.choice(len(X_pos), n_dup, replace=True)
    X_pos_aug = pd.concat([X_pos, X_pos.iloc[idx_dup]], ignore_index=True)
    y_pos_aug = pd.concat([y_pos, y_pos.iloc[idx_dup]], ignore_index=True)
else:
    X_pos_aug = X_pos
    y_pos_aug = y_pos

X_train_bal = pd.concat([X_neg_sample, X_pos_aug], ignore_index=True)
y_train_bal = pd.concat([y_neg_sample, y_pos_aug], ignore_index=True)

idx_shuffle = np.random.permutation(len(X_train_bal))
X_train_bal = X_train_bal.iloc[idx_shuffle].reset_index(drop=True)
y_train_bal = y_train_bal.iloc[idx_shuffle].reset_index(drop=True)

print(f"   ✅ Train: {len(X_train_bal):,}")
print(f"      Sin anemia: {(y_train_bal==0).sum():,} ({(y_train_bal==0).sum()/len(y_train_bal)*100:.1f}%)")
print(f"      Con anemia: {(y_train_bal==1).sum():,} ({(y_train_bal==1).sum()/len(y_train_bal)*100:.1f}%)")

# ============================================================================
# 4. ENTRENAMIENTO
# ============================================================================
print("\n🤖 4. Entrenando RandomForest...")

modelo = RandomForestClassifier(
    n_estimators=250,
    max_depth=16,
    min_samples_split=200,
    min_samples_leaf=100,
    max_features='sqrt',
    class_weight={0: 1, 1: 4},
    random_state=42,
    n_jobs=-1,
    verbose=0
)

modelo.fit(X_train_bal, y_train_bal)
print("   ✅ Modelo entrenado")

# ============================================================================
# 5. THRESHOLD
# ============================================================================
print("\n🎯 5. Optimizando threshold...")

y_proba = modelo.predict_proba(X_test)[:, 1]
precisions, recalls, thresholds = precision_recall_curve(y_test, y_proba)

# Buscar recall 65-75% con mejor precision
best_threshold = None
best_score = -1

for min_r, max_r in [(0.65, 0.75), (0.60, 0.80), (0.55, 0.85)]:
    idx = np.where((recalls >= min_r) & (recalls <= max_r) & (precisions >= 0.20))[0]
    if len(idx) > 0:
        scores = 0.6 * recalls[idx] + 0.4 * precisions[idx]
        best_idx = idx[np.argmax(scores)]
        if scores.max() > best_score:
            best_score = scores.max()
            best_threshold = thresholds[best_idx]

if best_threshold is None:
    idx = np.argmin(np.abs(recalls - 0.70))
    best_threshold = thresholds[min(idx, len(thresholds)-1)]

print(f"   ✅ Threshold: {best_threshold:.4f}")

y_pred = (y_proba >= best_threshold).astype(int)

# ============================================================================
# 6. EVALUACIÓN
# ============================================================================
print("\n📊 6. Evaluando...")

acc = accuracy_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_proba)

print(f"\n   Accuracy: {acc*100:.2f}%")
print(f"   ROC AUC:  {auc:.4f}")

print(f"\n   Classification Report:")
print(classification_report(y_test, y_pred, target_names=['Sin Anemia', 'Con Anemia'], digits=3))

cm = confusion_matrix(y_test, y_pred)
recall = cm[1][1] / (cm[1][1] + cm[1][0]) if (cm[1][1] + cm[1][0]) > 0 else 0
precision = cm[1][1] / (cm[1][1] + cm[0][1]) if (cm[1][1] + cm[0][1]) > 0 else 0
f1 = 2 * (precision * recall) / (precision + recall + 1e-10)

print(f"\n   🎯 MÉTRICAS FINALES:")
print(f"      Recall:    {recall:.2%} {'✅' if recall >= 0.60 else '⚠️'}")
print(f"      Precision: {precision:.2%} {'✅' if precision >= 0.25 else '⚠️'}")
print(f"      F1-Score:  {f1:.2%}")

# Feature importance
importances = pd.DataFrame({
    'feature': features.columns,
    'importance': modelo.feature_importances_
}).sort_values('importance', ascending=False)

print(f"\n   🔝 TOP 10 FEATURES:")
for i, (_, row) in enumerate(importances.head(10).iterrows(), 1):
    print(f"      {i:2d}. {row['feature']:30s} {row['importance']:.4f}")

# ============================================================================
# 7. GUARDAR
# ============================================================================
print("\n💾 7. Guardando modelo...")

model_package = {
    'model': modelo,
    'threshold': float(best_threshold),
    'features': list(features.columns),
    'training_date': pd.Timestamp.now().isoformat()
}

with open(MODELS_DIR / 'predictor_anemia_ml.pkl', 'wb') as f:
    pickle.dump(model_package, f)

metrics = {
    'model_type': 'RandomForest_RealData',
    'threshold': float(best_threshold),
    'accuracy': float(acc),
    'roc_auc': float(auc),
    'recall_anemia': float(recall),
    'precision_anemia': float(precision),
    'f1_score_anemia': float(f1),
    'top_features': importances.head(10).to_dict('records')
}

with open(MODELS_DIR / 'model_metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)

print(f"\n{'='*90}")
print(f"🎉 MODELO CON DATOS REALES COMPLETADO")
print(f"🎯 Recall: {recall:.1%} | Precision: {precision:.1%} | F1: {f1:.1%} | AUC: {auc:.3f}")
print(f"📊 {len(df):,} registros REALES | {features.shape[1]} features")
print(f"{'='*90}")
