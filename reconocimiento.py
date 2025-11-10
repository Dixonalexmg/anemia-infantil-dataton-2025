"""
SCRIPT DE BÚSQUEDA DE DATOS CON GROUND TRUTH
Busca archivos que contengan etiquetas verdaderas de anemia
"""

import pandas as pd
import os
from pathlib import Path

print("="*80)
print("🔍 BÚSQUEDA EXHAUSTIVA DE DATOS CON GROUND TRUTH")
print("="*80)

# =====================================================
# 1. ESCANEAR TODAS LAS CARPETAS DE DATOS
# =====================================================
carpetas_a_buscar = [
    'data/processed/',
    'data/raw/',
    'data/historial/',
    'data/feedback/',
    './'  # Raíz del proyecto
]

archivos_encontrados = []

print("\n[1] Escaneando carpetas...")
for carpeta in carpetas_a_buscar:
    if os.path.exists(carpeta):
        archivos = [f for f in os.listdir(carpeta) if f.endswith(('.csv', '.xlsx', '.xls'))]
        print(f"\n📁 {carpeta}")
        print(f"   Archivos encontrados: {len(archivos)}")
        for archivo in archivos:
            archivos_encontrados.append(os.path.join(carpeta, archivo))
            print(f"   - {archivo}")

print(f"\n✅ Total de archivos a analizar: {len(archivos_encontrados)}")

# =====================================================
# 2. ANALIZAR CADA ARCHIVO
# =====================================================
print("\n" + "="*80)
print("[2] ANALIZANDO CONTENIDO DE CADA ARCHIVO")
print("="*80)

candidatos_ground_truth = []

for archivo in archivos_encontrados:
    print(f"\n📊 Analizando: {archivo}")
    try:
        # Leer archivo
        if archivo.endswith('.csv'):
            df = pd.read_csv(archivo, nrows=1000)  # Leer solo primeras 1000 filas para velocidad
        else:
            df = pd.read_excel(archivo, nrows=1000)
        
        print(f"   Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
        
        # Buscar columnas relacionadas con anemia (GROUND TRUTH)
        columnas_anemia_gt = []
        keywords_gt = [
            'anemia', 'diagnostico', 'resultado', 'hemoglobina', 'hb', 'hemo',
            'estado', 'clasificacion', 'categoria', 'nivel_anemia', 'tiene_anemia',
            'anemic', 'diagnosis', 'status', 'label', 'target', 'outcome'
        ]
        
        for col in df.columns:
            col_lower = col.lower()
            for keyword in keywords_gt:
                if keyword in col_lower:
                    # Verificar que no sea probabilidad
                    if 'prob' not in col_lower and 'riesgo' not in col_lower and 'score' not in col_lower:
                        columnas_anemia_gt.append(col)
                        break
        
        if columnas_anemia_gt:
            print(f"   ✅ COLUMNAS DE GROUND TRUTH ENCONTRADAS: {columnas_anemia_gt}")
            
            # Analizar cada columna candidata
            for col in columnas_anemia_gt:
                valores_unicos = df[col].dropna().unique()
                n_unicos = len(valores_unicos)
                
                print(f"\n   📌 Columna: '{col}'")
                print(f"      Tipo: {df[col].dtype}")
                print(f"      Valores únicos: {n_unicos}")
                print(f"      Ejemplos: {valores_unicos[:10]}")
                
                # Verificar si parece una columna de diagnóstico válida
                if n_unicos <= 10:  # Columnas categóricas con pocos valores
                    candidatos_ground_truth.append({
                        'archivo': archivo,
                        'columna_gt': col,
                        'tipo': df[col].dtype,
                        'n_unicos': n_unicos,
                        'valores': valores_unicos.tolist()[:5],
                        'n_muestras': len(df)
                    })
        else:
            print(f"   ⚠️ No se encontraron columnas de ground truth evidentes")
        
        # Buscar también columnas de hemoglobina (para calcular ground truth)
        columnas_hb = [col for col in df.columns if 
                       any(k in col.lower() for k in ['hb', 'hemoglobina', 'hemoglobin'])]
        
        if columnas_hb:
            print(f"   ℹ️ Columnas de hemoglobina encontradas: {columnas_hb}")
            
            for col in columnas_hb:
                if pd.api.types.is_numeric_dtype(df[col]):
                    valores_hb = df[col].dropna()
                    print(f"      - {col}: rango [{valores_hb.min():.1f}, {valores_hb.max():.1f}] g/dL")
                    
                    # Si hay HB, podemos calcular ground truth
                    candidatos_ground_truth.append({
                        'archivo': archivo,
                        'columna_gt': col + ' (calcular desde HB)',
                        'tipo': 'numeric',
                        'n_unicos': 'continuo',
                        'valores': 'HB continua - requiere umbral',
                        'n_muestras': len(df)
                    })
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

# =====================================================
# 3. REPORTE DE CANDIDATOS
# =====================================================
print("\n" + "="*80)
print("[3] RESUMEN DE CANDIDATOS CON GROUND TRUTH")
print("="*80)

if candidatos_ground_truth:
    print(f"\n✅ Se encontraron {len(candidatos_ground_truth)} candidatos:")
    
    for i, candidato in enumerate(candidatos_ground_truth, 1):
        print(f"\n{i}. Archivo: {candidato['archivo']}")
        print(f"   Columna GT: {candidato['columna_gt']}")
        print(f"   Tipo: {candidato['tipo']}")
        print(f"   Valores únicos: {candidato['n_unicos']}")
        print(f"   Ejemplos: {candidato['valores']}")
        print(f"   Muestras: {candidato['n_muestras']}")
else:
    print("\n❌ NO SE ENCONTRARON ARCHIVOS CON GROUND TRUTH DIRECTO")
    print("\n⚠️ OPCIONES:")
    print("   1. Buscar el dataset original de entrenamiento (antes de predecir)")
    print("   2. Usar datos de SIEN con hemoglobina real para calcular ground truth")
    print("   3. Verificar carpeta data/raw/ si tiene archivos originales")

# =====================================================
# 4. BUSCAR ARCHIVO SIEN ORIGINAL
# =====================================================
print("\n" + "="*80)
print("[4] BÚSQUEDA ESPECÍFICA: ARCHIVO SIEN ORIGINAL")
print("="*80)

archivos_sien = [f for f in archivos_encontrados if 'sien' in f.lower()]

if archivos_sien:
    print(f"\n✅ Archivos SIEN encontrados: {len(archivos_sien)}")
    for archivo_sien in archivos_sien:
        print(f"\n📊 {archivo_sien}")
        try:
            if archivo_sien.endswith('.csv'):
                df_sien = pd.read_csv(archivo_sien, nrows=5)
            else:
                df_sien = pd.read_excel(archivo_sien, nrows=5)
            
            print(f"   Columnas ({len(df_sien.columns)}):")
            for col in df_sien.columns:
                print(f"      - {col}")
            
            print(f"\n   Primeras 2 filas:")
            print(df_sien.head(2).to_string())
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
else:
    print("⚠️ No se encontraron archivos SIEN")

# =====================================================
# 5. RECOMENDACIÓN FINAL
# =====================================================
print("\n" + "="*80)
print("[5] RECOMENDACIÓN")
print("="*80)

print("\n💡 Para generar la curva de calibración necesitamos:")
print("   1. Un archivo con ETIQUETAS VERDADERAS (ground truth)")
print("   2. Un archivo con PROBABILIDADES PREDICHAS por el modelo")
print("\n   Opciones:")
print("   A) Usar dataset de entrenamiento/test split original")
print("   B) Usar datos SIEN con HB real + calcular anemia con umbrales OMS")
print("   C) Generar predicciones sobre dataset con ground truth conocido")

print("\n" + "="*80)
print("✅ BÚSQUEDA FINALIZADA")
print("="*80)
