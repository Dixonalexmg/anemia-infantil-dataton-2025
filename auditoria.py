#!/usr/bin/env python3
"""
🔍 SCRIPT DE AUDITORÍA OPTIMIZADO - NutriSenseIA
Ejecutar: python3 audit_optimizado.py > reporte_auditoria.txt
Corregido para Windows + grandes volúmenes de archivos
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from collections import defaultdict

print("="*100)
print("🔍 AUDITORÍA TÉCNICA OPTIMIZADA - SISTEMA ANEMIA INFANTIL")
print("="*100)
print(f"Fecha: {datetime.now().isoformat()}")
print(f"Ubicación: {os.getcwd()}")
print()

# ============================================================================
# 1. ESTRUCTURA DE DIRECTORIOS (PRIMEROS NIVELES)
# ============================================================================
print("\n" + "="*100)
print("📁 1. ESTRUCTURA PRINCIPAL (PRIMEROS 3 NIVELES)")
print("="*100)

def print_tree(path, prefix="", max_depth=3, current_depth=0, max_items=15):
    """Print tree structure optimizado"""
    if current_depth >= max_depth:
        return

    try:
        items = sorted([x for x in Path(path).iterdir() if not x.name.startswith('.')], 
                      key=lambda x: (not x.is_dir(), x.name))

        dirs = [x for x in items if x.is_dir()][:max_items]
        files = [x for x in items if x.is_file()][:5]

        for d in dirs:
            print(f"{prefix}├── {d.name}/")
            print_tree(str(d), prefix + "│   ", max_depth, current_depth + 1, max_items)

        for f in files:
            print(f"{prefix}├── {f.name}")
    except Exception as e:
        pass

print_tree(".")

# ============================================================================
# 2. CONTEO Y DISTRIBUCIÓN DE ARCHIVOS
# ============================================================================
print("\n" + "="*100)
print("📊 2. ANÁLISIS DE ARCHIVOS")
print("="*100)

print("\n⏳ Escaneando archivos (esto puede tardar)...\n")

extensions = defaultdict(int)
directories = defaultdict(int)
total_size = 0
py_files_count = 0

for root, dirs, files in os.walk("."):
    # Ignorar directorios especiales
    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', 'env', 'node_modules']]

    for file in files:
        if file.startswith('.'):
            continue

        # Contar por extensión
        ext = Path(file).suffix.lower() if Path(file).suffix else 'no_ext'
        extensions[ext] += 1

        # Contar por directorio padre
        rel_dir = os.path.relpath(root, ".")
        directories[rel_dir[:20]] += 1

        # Tamaño total
        try:
            filepath = os.path.join(root, file)
            total_size += os.path.getsize(filepath)
        except:
            pass

        if ext == '.py':
            py_files_count += 1

print(f"✅ Escaneo completado\n")
print(f"Total de archivos Python (.py): {py_files_count:,}")
print(f"Total de archivos (todos): {sum(extensions.values()):,}")
print(f"Tamaño total del proyecto: {total_size / 1024 / 1024 / 1024:.2f} GB")

# ============================================================================
# 3. TOP EXTENSIONES
# ============================================================================
print("\n" + "-"*100)
print("Top 10 tipos de archivo:")
print("-"*100)

sorted_ext = sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:10]
for ext, count in sorted_ext:
    print(f"  {ext:<15} {count:>8,} archivos")

# ============================================================================
# 4. DIRECTORIOS PRINCIPALES
# ============================================================================
print("\n" + "-"*100)
print("Top 15 directorios con más archivos:")
print("-"*100)

sorted_dirs = sorted(directories.items(), key=lambda x: x[1], reverse=True)[:15]
for dir_path, count in sorted_dirs:
    print(f"  {dir_path:<40} {count:>6,} archivos")

# ============================================================================
# 5. ARCHIVOS CLAVE
# ============================================================================
print("\n" + "="*100)
print("📄 3. ARCHIVOS CLAVE")
print("="*100)

critical_files = [
    "app.py", "main.py",
    "requirements.txt", "setup.py", "pyproject.toml",
    "config.py", "settings.py",
    "README.md", ".env", ".env.example",
    "docker-compose.yml", "Dockerfile",
    ".streamlit/config.toml"
]

print()
for cf in critical_files:
    found = False
    for root, dirs, files in os.walk("."):
        if cf in files or cf.replace('/', os.sep) in root:
            print(f"  ✅ {cf}")
            found = True
            break
    if not found:
        print(f"  ❌ {cf}")

# ============================================================================
# 6. MODELOS ML
# ============================================================================
print("\n" + "="*100)
print("🤖 4. MODELOS ML")
print("="*100)

model_extensions = ['.pkl', '.joblib', '.h5', '.pt', '.pth', '.onnx']
models_found = []

for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', 'env']]

    for file in files:
        if any(file.endswith(ext) for ext in model_extensions):
            filepath = os.path.join(root, file)
            try:
                size_mb = os.path.getsize(filepath) / 1024 / 1024
                models_found.append((filepath, size_mb))
            except:
                pass

if models_found:
    print(f"\n✅ Encontrados {len(models_found)} modelos ML:\n")
    for model, size in sorted(models_found, key=lambda x: x[1], reverse=True):
        print(f"  {model:<60} ({size:>8.2f} MB)")
else:
    print("\n⚠️  No se encontraron modelos (.pkl, .joblib, .h5, etc)")

# ============================================================================
# 7. DATOS
# ============================================================================
print("\n" + "="*100)
print("📊 5. DATOS")
print("="*100)

data_extensions = ['.csv', '.xlsx', '.xls', '.json', '.parquet', '.feather']
data_found = []

for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', 'env']]

    for file in files:
        if any(file.lower().endswith(ext) for ext in data_extensions):
            filepath = os.path.join(root, file)
            try:
                size_kb = os.path.getsize(filepath) / 1024
                data_found.append((filepath, size_kb))
            except:
                pass

if data_found:
    print(f"\n✅ Encontrados {len(data_found)} archivos de datos:\n")
    for data, size in sorted(data_found, key=lambda x: x[1], reverse=True)[:30]:
        if size > 1024:
            print(f"  {data:<60} ({size/1024:>8.2f} MB)")
        else:
            print(f"  {data:<60} ({size:>8.2f} KB)")
    if len(data_found) > 30:
        print(f"\n  ... y {len(data_found) - 30} archivos más")
else:
    print("\n⚠️  No se encontraron archivos de datos")

# ============================================================================
# 8. NOTEBOOKS
# ============================================================================
print("\n" + "="*100)
print("📓 6. NOTEBOOKS JUPYTER")
print("="*100)

notebooks = []
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith('.ipynb'):
            notebooks.append(os.path.join(root, file))

if notebooks:
    print(f"\n✅ Encontrados {len(notebooks)} notebooks:\n")
    for nb in sorted(notebooks)[:20]:
        print(f"  {nb}")
    if len(notebooks) > 20:
        print(f"\n  ... y {len(notebooks) - 20} notebooks más")
else:
    print("\n⚠️  No se encontraron notebooks")

# ============================================================================
# 9. ESTADÍSTICAS DE CÓDIGO PYTHON
# ============================================================================
print("\n" + "="*100)
print("📈 7. ESTADÍSTICAS DE CÓDIGO PYTHON")
print("="*100)

print("\n⏳ Analizando archivos Python (esto puede tardar)...\n")

total_lines = 0
total_classes = 0
total_functions = 0
files_analyzed = 0

for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', 'env']]

    for file in files:
        if file.endswith('.py'):
            try:
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = len(content.split('\n'))
                    total_lines += lines
                    total_classes += content.count('class ')
                    total_functions += content.count('def ')
                    files_analyzed += 1
            except:
                pass

print(f"Total archivos Python analizados: {files_analyzed:,}")
print(f"Total líneas de código Python: {total_lines:,}")
print(f"Total clases definidas: {total_classes:,}")
print(f"Total funciones definidas: {total_functions:,}")
print(f"Promedio líneas por archivo: {total_lines // max(files_analyzed, 1):,}")

# ============================================================================
# 10. GIT INFO
# ============================================================================
print("\n" + "="*100)
print("🔗 8. INFORMACIÓN GIT")
print("="*100)

if os.path.isdir(".git"):
    print("\n✅ Es un repositorio Git\n")

    try:
        result = subprocess.run(["git", "log", "--oneline", "-5"], 
                              capture_output=True, text=True, timeout=5)
        if result.stdout:
            print("Últimos commits:")
            for line in result.stdout.strip().split('\n'):
                print(f"  {line}")
    except Exception as e:
        print(f"  ⚠️  No se pudo obtener commits: {e}")

    try:
        result = subprocess.run(["git", "remote", "-v"], 
                              capture_output=True, text=True, timeout=5)
        if result.stdout:
            print("\nRemotes:")
            for line in result.stdout.strip().split('\n'):
                print(f"  {line}")
    except:
        pass
else:
    print("\n❌ No es un repositorio Git")

# ============================================================================
# 11. APP.PY
# ============================================================================
print("\n" + "="*100)
print("📄 9. CONTENIDO APP.PY (PRIMERAS 150 LÍNEAS)")
print("="*100)

app_files = []
for root, dirs, files in os.walk("."):
    for file in files:
        if file in ['app.py', 'main.py']:
            app_files.append(os.path.join(root, file))

if app_files:
    app_path = app_files[0]
    print(f"\n✅ Encontrado: {app_path}\n")
    try:
        with open(app_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            for i, line in enumerate(lines[:150], 1):
                print(f"{i:3d}: {line.rstrip()}")
            if len(lines) > 150:
                print(f"\n... {len(lines) - 150} líneas más")
    except Exception as e:
        print(f"Error leyendo archivo: {e}")
else:
    print("\n❌ No se encontró app.py o main.py")

# ============================================================================
# 12. REQUIREMENTS.TXT
# ============================================================================
print("\n" + "="*100)
print("📚 10. DEPENDENCIAS (requirements.txt)")
print("="*100)

req_files = []
for root, dirs, files in os.walk("."):
    for file in files:
        if file == 'requirements.txt':
            req_files.append(os.path.join(root, file))

if req_files:
    req_path = req_files[0]
    print(f"\n✅ Encontrado: {req_path}\n")
    try:
        with open(req_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines[:50]:
                print(f"  {line.rstrip()}")
            if len(lines) > 50:
                print(f"\n  ... y {len(lines) - 50} dependencias más")
    except Exception as e:
        print(f"Error leyendo archivo: {e}")
else:
    print("\n❌ No se encontró requirements.txt")

# ============================================================================
# RESUMEN FINAL
# ============================================================================
print("\n" + "="*100)
print("✅ RESUMEN FINAL DE AUDITORÍA")
print("="*100)

print(f"""
Archivos Python: {py_files_count:,}
Líneas de código Python: {total_lines:,}
Clases definidas: {total_classes:,}
Funciones definidas: {total_functions:,}

Modelos ML encontrados: {len(models_found)}
Archivos de datos encontrados: {len(data_found)}
Notebooks encontrados: {len(notebooks)}

Tamaño total del proyecto: {total_size / 1024 / 1024 / 1024:.2f} GB
""")

print("="*100)
print("✅ FIN DE LA AUDITORÍA")
print("="*100)
