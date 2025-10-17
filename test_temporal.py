# test_temporal.py
from services.predictor import anemia_predictor
from services.temporal_predictor import get_temporal_predictor

# Caso de prueba
datos_test = {
    'edad_meses': 18,
    'hemoglobina': 10.2,
    'altitud': 3500,
    'recibe_suplemento': False,
    'asiste_cred': True,
    'area_rural': True,
    'departamento': 'PUNO',
    'tiene_juntos': False,
    'tiene_sis': True
}

# Obtener predictor
predictor_temporal = get_temporal_predictor(anemia_predictor)

# Proyección a 3 meses
resultado_3m = predictor_temporal.predecir_futuro(datos_test, meses=3)

print("🔮 PROYECCIÓN A 3 MESES")
print(f"Hb actual: {resultado_3m['hemoglobina_actual']} g/dL")
print(f"Hb proyectada: {resultado_3m['hemoglobina_proyectada']} g/dL")
print(f"Probabilidad actual: {resultado_3m['probabilidad_actual']*100:.1f}%")
print(f"Probabilidad futura: {resultado_3m['probabilidad_futura']*100:.1f}%")
print(f"Tendencia: {resultado_3m['tendencia']} {resultado_3m['tendencia_emoji']}")
print(f"\nFactores de riesgo:")
for f in resultado_3m['factores_deterioro']:
    print(f"  - {f}")
