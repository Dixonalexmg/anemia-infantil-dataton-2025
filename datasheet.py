"""
GENERADOR DE MODEL CARD - CORREGIDO
Proyecto: NutriSenseIA - Datatón 3.0
"""

from datetime import datetime
from pathlib import Path

OUTPUT_DIR = "outputs/"
Path(OUTPUT_DIR).mkdir(exist_ok=True)

print("="*80)
print("📋 GENERANDO MODEL CARD (DATASHEET)")
print("="*80)

# Generar contenido sin f-string complejo
fecha_actual = datetime.now().strftime('%d de %B de %Y')
fecha_actualizacion = datetime.now().strftime('%d/%m/%Y')

model_card_content = """# Model Card: NutriSenseIA
## Sistema de Predicción Adaptativa de Anemia Infantil

**Versión:** 3.0 (Híbrida Calibrada)  
**Fecha:** """ + fecha_actual + """  
**Desarrollado por:** Equipo NutriSenseIA - Datatón 3.0 MINSA Perú  
**Contacto:** nutrisenseia@minsa.gob.pe

---

## 1. DESCRIPCIÓN DEL MODELO

### 1.1 Propósito
Sistema de machine learning para predecir el riesgo de anemia en niños menores de 5 años en Perú, optimizando la asignación de recursos de salud pública mediante predicciones calibradas y explicables.

### 1.2 Casos de Uso Previstos
- **Primario**: Priorización de screening con HemoCue en centros de salud
- **Secundario**: Planificación de intervenciones nutricionales preventivas
- **Terciario**: Monitoreo epidemiológico y asignación de recursos regionales

### 1.3 Casos de Uso NO Previstos
- ❌ Diagnóstico clínico definitivo de anemia
- ❌ Sustitución de evaluación médica profesional
- ❌ Uso en poblaciones fuera de Perú sin reentrenamiento
- ❌ Aplicación en niños >5 años o adultos

---

## 2. ARQUITECTURA DEL MODELO

### 2.1 Tipo de Modelo
**Ensemble híbrido calibrado** con tres componentes:
1. **Modelo ML**: CalibratedClassifierCV con calibración isotónica
2. **Componente clínico**: Reglas basadas en umbrales OMS
3. **Fusión**: Promedio ponderado (70% ML + 30% reglas clínicas)

### 2.2 Features de Entrada (n=35)

Incluye variables demográficas, clínicas, geográficas y de intervención.

---

## 3. MÉTRICAS DE DESEMPEÑO

### 3.1 Clasificación (Test Set, n=50,000)
- **AUC-ROC**: 0.9815 (Excelente)
- **Accuracy**: 87.7%
- **Precision**: 98.9%
- **Recall**: 7.3% (Conservador)
- **Specificity**: 99.99%

### 3.2 Calibración
- **Brier Score**: 0.1079 (Bueno)
- **ECE**: 0.1130 (Aceptable)
- **MCE**: 0.3230 (Mejorable)

---

## 4. LIMITACIONES

1. **Sensibilidad baja** con threshold 0.80 (solo 7.3%)
2. **Sobreconfianza** en probabilidades medias (0.3-0.5)
3. **Dependencia de HemoCue** para medición de Hb
4. **Generalización** solo validada en Perú

---

## 5. PROTOCOLO DE CONSENTIMIENTO

### Texto para Padres/Tutores:

**¿Qué es NutriSenseIA?**
Es un sistema de computadora que ayuda a identificar qué niños tienen más riesgo de anemia.

**¿Cómo funciona?**
Usa la información del control CRED (edad, peso, talla, análisis) para priorizar atención.

**¿Qué pasa con los datos?**
- Se guardan de forma segura en MINSA
- No se comparten con privados
- Se usan solo para mejorar salud
- Puede pedir borrado en cualquier momento

**¿Puedo rechazar?**
Sí. Su hijo/a recibirá atención normal de todas formas.

Acepto uso de NutriSenseIA: [ ] SÍ  [ ] NO

Firma: _____________ Fecha: _________

---

## 6. CONTACTO

**Equipo:** NutriSenseIA - Datatón 3.0  
**Institución:** MINSA Perú  
**Última actualización:** """ + fecha_actualizacion + """

---

*Model Card siguiendo estándares de transparencia en IA (Mitchell et al., 2019)*
"""

# Guardar
md_path = f"{OUTPUT_DIR}model_card_nutrisenseia.md"
with open(md_path, 'w', encoding='utf-8') as f:
    f.write(model_card_content)

print(f"\n✅ Model Card guardado en: {md_path}")

print("\n" + "="*80)
print("✅ MODEL CARD COMPLETADO")
print("="*80)
