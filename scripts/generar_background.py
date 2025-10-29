# Script para generar background dummy: scripts/generar_background.py

import pandas as pd
import numpy as np
import os

# Crear directorio si no existe
os.makedirs('data/processed', exist_ok=True)

# Generar datos sintéticos representativos
np.random.seed(42)

n_samples = 100

data = {
    'hemoglobina_g_dl': np.random.normal(11.5, 1.5, n_samples),
    'edad_meses': np.random.randint(6, 59, n_samples),
    'peso_kg': np.random.normal(12, 3, n_samples),
    'talla_cm': np.random.normal(85, 10, n_samples),
    'recibe_suplemento_hierro': np.random.choice([0, 1], n_samples),
    'frecuencia_carne_semanal': np.random.randint(0, 7, n_samples),
    'altitud_msnm': np.random.choice([0, 500, 1500, 3000], n_samples),
    'anemia': np.random.choice([0, 1], n_samples, p=[0.6, 0.4])
}

df_background = pd.DataFrame(data)

# Guardar
df_background.to_csv('data/processed/sien_nacional_procesado.csv', index=False)

print("✅ Archivo background generado en: data/processed/sien_nacional_procesado.csv")
print(f"📊 Dimensiones: {df_background.shape}")
