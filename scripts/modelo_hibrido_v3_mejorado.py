"""
scripts/modelo_hibrido_v3_mejorado.py
Modelo híbrido con 3 mejoras basadas en testing exhaustivo
"""

import pickle
import numpy as np

def aplicar_reglas_clinicas_mejoradas(prob_base, hb_ajustada, edad_meses, tiene_factores_riesgo, altitud):
    """
    Reglas clínicas mejoradas v3
    
    Mejoras:
    1. Regla específica para alta altitud
    2. Gradientes suaves en Hb 10.0-11.0
    3. Protección para casos severos (Hb <7.0)
    """
    
    prob_ajustada = prob_base
    
    # ✨ MEJORA 3: Casos críticos (Hb <7.0) → mínimo 90%
    if hb_ajustada < 7.0:
        prob_ajustada = max(prob_ajustada, 0.90)
        return np.clip(prob_ajustada, 0, 1)  # Retornar directo
    
    # ✨ MEJORA 2: Gradientes suaves en zona crítica
    if hb_ajustada < 9.0:
        prob_ajustada = max(prob_ajustada, 0.70)
    elif hb_ajustada < 10.0:
        prob_ajustada = max(prob_ajustada, 0.40)
    elif hb_ajustada < 10.5:
        # Gradiente: 40% → 25%
        prob_minima = 0.40 - (hb_ajustada - 10.0) * 0.30
        prob_ajustada = max(prob_ajustada, prob_minima)
    elif hb_ajustada < 11.0:
        # Gradiente: 25% → 15%
        prob_minima = 0.25 - (hb_ajustada - 10.5) * 0.20
        prob_ajustada = max(prob_ajustada, prob_minima)
    elif hb_ajustada < 11.5 and (tiene_factores_riesgo or 6 <= edad_meses <= 12):
        prob_ajustada = max(prob_ajustada, 0.10)
    
    # Casos sanos
    if hb_ajustada > 12.5:
        prob_ajustada = min(prob_ajustada, 0.10)
    
    # ✨ MEJORA 1: Alta altitud con Hb borderline
    if altitud > 3000 and 10.0 <= hb_ajustada <= 11.5 and tiene_factores_riesgo:
        prob_ajustada = max(prob_ajustada, 0.30)
    
    return np.clip(prob_ajustada, 0, 1)

def crear_modelo_mejorado():
    print("="*80)
    print("MODELO HÍBRIDO v3 - CON 3 MEJORAS")
    print("="*80)
    
    # Cargar modelo base
    with open('models/predictor_anemia_ml_calibrado_suave.pkl', 'rb') as f:
        model_package = pickle.load(f)
    
    # Agregar metadata
    model_package['usa_reglas_clinicas'] = True
    model_package['version'] = '3.0_mejorado'
    model_package['mejoras'] = [
        'Gradientes suaves Hb 10-11',
        'Regla altitud >3000m',
        'Protección casos severos Hb <7'
    ]
    
    # Guardar
    with open('models/predictor_anemia_ml_hibrido_v3.pkl', 'wb') as f:
        pickle.dump(model_package, f)
    
    print("\n✅ Modelo v3 guardado: models/predictor_anemia_ml_hibrido_v3.pkl")
    
    # Testing de mejoras
    print("\n" + "="*80)
    print("TESTING DE MEJORAS")
    print("="*80)
    
    from services.predictor import anemia_predictor
    modelo = model_package['model']
    
    casos_criticos = [
        {'nombre': 'Anemia severa (Hb 6.5)', 'hb': 6.5, 'edad': 12, 'alt': 150, 'riesgo': True},
        {'nombre': 'Pasco altitud (Hb 11.2)', 'hb': 11.2, 'edad': 24, 'alt': 4350, 'riesgo': True},
        {'nombre': 'Borderline (Hb 10.5)', 'hb': 10.5, 'edad': 18, 'alt': 150, 'riesgo': False},
        {'nombre': 'Borderline (Hb 10.7)', 'hb': 10.7, 'edad': 18, 'alt': 150, 'riesgo': False},
        {'nombre': 'Borderline (Hb 10.9)', 'hb': 10.9, 'edad': 18, 'alt': 150, 'riesgo': False},
    ]
    
    print(f"\n{'Caso':<30} {'Hb':<6} {'V2':<10} {'V3':<10} {'Mejora':<10}")
    print("-" * 66)
    
    for caso in casos_criticos:
        datos = {
            'hemoglobina': caso['hb'],
            'edad_meses': caso['edad'],
            'peso_kg': 12.0,
            'altitud': caso['alt'],
            'departamento': 'LIMA',
            'area_rural': caso['riesgo'],
            'recibe_suplemento': not caso['riesgo'],
            'asiste_cred': True,
            'es_bajo_peso': False,
            'es_prematuro': False
        }
        
        X = anemia_predictor._preparar_features_ml(datos)
        prob_base = modelo.predict_proba(X)[:, 1][0]
        
        # V2 (reglas anteriores - sin mejoras)
        prob_v2 = prob_base
        if caso['hb'] < 11.0:
            prob_v2 = max(prob_v2, 0.15)
        if caso['hb'] < 10.0:
            prob_v2 = max(prob_v2, 0.40)
        if caso['hb'] < 9.0:
            prob_v2 = max(prob_v2, 0.70)
        
        # V3 (con mejoras)
        prob_v3 = aplicar_reglas_clinicas_mejoradas(
            prob_base, caso['hb'], caso['edad'], caso['riesgo'], caso['alt']
        )
        
        mejora = prob_v3 - prob_v2
        
        print(f"{caso['nombre']:<30} {caso['hb']:<6.1f} {prob_v2*100:>8.1f}% {prob_v3*100:>8.1f}% {mejora*100:>9.1f}%")
    
    print("\n" + "="*80)
    print("RESUMEN DE MEJORAS")
    print("="*80)
    print("""
1. ✅ Gradientes suaves evitan saltos bruscos
2. ✅ Alta altitud detecta casos de riesgo
3. ✅ Casos severos protegidos (>90%)

PRÓXIMO PASO:
- Ejecutar testing exhaustivo con modelo v3
- Comparar resultados con v2
""")

if __name__ == "__main__":
    crear_modelo_mejorado()
