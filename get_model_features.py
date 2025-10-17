# Script: get_model_features.py
import pickle
import pandas as pd

# Cargar el modelo
with open('models/predictor_anemia_ml.pkl', 'rb') as f:
    modelo = pickle.load(f)

# Obtener nombres de features
if hasattr(modelo, 'feature_names_in_'):
    features = list(modelo.feature_names_in_)
elif hasattr(modelo, 'feature_name_'):
    features = list(modelo.feature_name_)
else:
    # Cargar 5 filas del CSV para ver columnas
    df = pd.read_csv('data/processed/sien_nacional_procesado.csv', nrows=5)
    features = [col for col in df.columns if col not in ['tiene_anemia', 'ID', 'anemia']]

print("="*60)
print(f"TOTAL DE FEATURES: {len(features)}")
print("="*60)
for i, feat in enumerate(features, 1):
    print(f"{i:2d}. {feat}")
print("="*60)
