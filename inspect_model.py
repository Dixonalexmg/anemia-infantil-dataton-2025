# inspect_model.py
import pickle
from pathlib import Path

# Cargar modelo
model_path = Path("models/predictor_anemia_ml.pkl")

if model_path.exists():
    with open(model_path, 'rb') as f:
        model_package = pickle.load(f)
    
    print("=" * 60)
    print("📊 INFORMACIÓN DEL MODELO ML")
    print("=" * 60)
    print(f"\n🤖 Tipo de modelo: {type(model_package['model']).__name__}")
    print(f"🎯 Threshold optimizado: {model_package['threshold']}")
    print(f"📈 Número de features: {len(model_package['features'])}")
    print(f"\n📝 Features utilizados:")
    for i, feat in enumerate(model_package['features'], 1):
        print(f"  {i:2d}. {feat}")
    
    # Si hay métricas guardadas
    if 'metrics' in model_package:
        print(f"\n📊 Métricas del modelo:")
        for metric, value in model_package['metrics'].items():
            print(f"  - {metric}: {value}")
    
else:
    print(f"❌ Modelo no encontrado en: {model_path}")
    print("\n📁 Archivos .pkl disponibles:")
    for pkl in Path(".").rglob("*.pkl"):
        print(f"  - {pkl}")
