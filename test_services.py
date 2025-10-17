# test_services.py
"""Test de servicios de negocio"""
from services.predictor import anemia_predictor
from services.menu_generator import menu_generator

print("=" * 60)
print("TEST: Servicios de Negocio")
print("=" * 60)

# ========== TEST 1: PREDICTOR ==========
print("\n1. Test Predictor de Anemia:")

datos_paciente = {
    'hemoglobina': 9.5,
    'edad_meses': 18,
    'altitud': 3200,
    'tiene_suplemento': False,
    'area_rural': True,
    'cuartil_vulnerabilidad': 4
}

resultado = anemia_predictor.predecir(datos_paciente)

print(f"   Hemoglobina observada: {resultado['hemoglobina_observada']} g/dL")
print(f"   Hemoglobina ajustada: {resultado['hemoglobina_ajustada']} g/dL")
print(f"   ¿Tiene anemia?: {resultado['tiene_anemia']}")
print(f"   Severidad: {resultado['severidad']}")
print(f"   Riesgo: {resultado['categoria']} ({resultado['probabilidad_anemia']*100:.0f}% prob.)")
print(f"   Recomendaciones: {len(resultado['recomendaciones'])}")

assert resultado['tiene_anemia'] == True
assert resultado['severidad'] in ['Leve', 'Moderada', 'Severa']
print("   ✅ Predictor funcionando correctamente")

# ========== TEST 2: GENERADOR DE MENÚS ==========
print("\n2. Test Generador de Menús:")

menu = menu_generator.generar_menu(
    edad_meses=18,
    presupuesto_diario=3.0,
    region="Costa"
)

print(f"   Edad: {menu['edad_meses']} meses")
print(f"   Requerimiento: {menu['requerimiento_hierro_mg']} mg/día")
print(f"   Hierro aportado: {menu['hierro_aportado_mg']} mg")
print(f"   Cobertura: {menu['cobertura_pct']:.1f}%")
print(f"   Costo: S/ {menu['costo_total']:.2f}")
print(f"   Alimentos: {len(menu['menu_items'])}")
print(f"   Evaluación: {menu['evaluacion']}")

assert menu['menu_items'], "Debe haber al menos 1 alimento"
assert menu['costo_total'] <= 3.0, "No debe exceder presupuesto"
print("   ✅ Generador de menús funcionando correctamente")

print("\n" + "=" * 60)
print("🎉 TODOS LOS TESTS DE SERVICIOS PASARON!")
print("=" * 60)
