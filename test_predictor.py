# test_predictor.py
"""
Script de prueba del predictor integrado
"""
from services.predictor import anemia_predictor

# Caso de prueba 1: Niño con anemia (hemoglobina baja)
print("=" * 60)
print("CASO 1: Niño con anemia probable")
print("=" * 60)

datos_caso1 = {
    'hemoglobina': 9.5,          # Baja
    'edad_meses': 18,            # 1.5 años
    'altitud': 3200,             # Puno (alta altitud)
    'tiene_suplemento': False,   # Sin suplemento
    'area_rural': True,
    'asiste_cred': False,
    'departamento': 'PUNO'
}

resultado1 = anemia_predictor.predecir(datos_caso1)

print(f"\n📊 DIAGNÓSTICO CLÍNICO:")
print(f"   Tiene anemia: {resultado1['tiene_anemia']}")
print(f"   Severidad: {resultado1['severidad']}")
print(f"   Hemoglobina ajustada: {resultado1['hemoglobina_ajustada']} g/dL")

if 'ml' in resultado1:
    print(f"\n🤖 PREDICCIÓN ML:")
    print(f"   Probabilidad: {resultado1['ml']['probabilidad']*100:.1f}%")
    print(f"   Categoría: {resultado1['ml']['categoria_riesgo_ml']}")
    print(f"   Confianza: {resultado1['ml']['confianza']}%")

print(f"\n⚠️  RIESGO CLÍNICO:")
print(f"   Categoría: {resultado1['categoria']}")
print(f"   Score: {resultado1['score']}")
print(f"   Probabilidad: {resultado1['probabilidad_anemia']*100:.0f}%")

print(f"\n💊 RECOMENDACIONES:")
for i, rec in enumerate(resultado1['recomendaciones'], 1):
    print(f"   {i}. [{rec['prioridad']}] {rec['mensaje']}")


# Caso de prueba 2: Niño saludable
print("\n\n" + "=" * 60)
print("CASO 2: Niño saludable")
print("=" * 60)

datos_caso2 = {
    'hemoglobina': 12.5,         # Normal
    'edad_meses': 30,
    'altitud': 150,              # Lima (baja altitud)
    'tiene_suplemento': True,
    'area_rural': False,
    'asiste_cred': True,
    'departamento': 'LIMA'
}

resultado2 = anemia_predictor.predecir(datos_caso2)

print(f"\n📊 DIAGNÓSTICO CLÍNICO:")
print(f"   Tiene anemia: {resultado2['tiene_anemia']}")
print(f"   Severidad: {resultado2['severidad']}")
print(f"   Hemoglobina ajustada: {resultado2['hemoglobina_ajustada']} g/dL")

if 'ml' in resultado2:
    print(f"\n🤖 PREDICCIÓN ML:")
    print(f"   Probabilidad: {resultado2['ml']['probabilidad']*100:.1f}%")
    print(f"   Categoría: {resultado2['ml']['categoria_riesgo_ml']}")

print(f"\n✅ RIESGO CLÍNICO:")
print(f"   Categoría: {resultado2['categoria']}")
print(f"   Score: {resultado2['score']}")

print(f"\n{'='*60}")
print("✅ PRUEBA COMPLETADA")
print(f"{'='*60}")
