# test_utils.py
"""Test de utilidades"""
from utils.data_loader import data_loader
from utils.validators import validate_edad, validate_hemoglobina, validate_altitud

print("=" * 60)
print("TEST: Módulo de Utilidades")
print("=" * 60)

# Test DataLoader
print("\n1. Test DataLoader:")
stats = data_loader.get_stats()
print(f"   Archivos disponibles: {len(stats['archivos_disponibles'])}")
print(f"   Archivos faltantes: {len(stats['archivos_faltantes'])}")

# Test Validadores
print("\n2. Test Validadores:")

# Edad válida
valido, msg = validate_edad(12)
assert valido, "Edad 12 meses debería ser válida"
print(f"   ✅ Edad 12 meses: válida")

# Edad inválida
valido, msg = validate_edad(3)
assert not valido, "Edad 3 meses debería ser inválida"
print(f"   ✅ Edad 3 meses: inválida ({msg})")

# Hemoglobina válida
valido, msg = validate_hemoglobina(11.5)
assert valido, "Hemoglobina 11.5 g/dL debería ser válida"
print(f"   ✅ Hemoglobina 11.5 g/dL: válida")

# Altitud válida
valido, msg = validate_altitud(2500)
assert valido, "Altitud 2500 msnm debería ser válida"
print(f"   ✅ Altitud 2500 msnm: válida")

print("\n" + "=" * 60)
print("🎉 TODOS LOS TESTS DE UTILIDADES PASARON!")
print("=" * 60)
