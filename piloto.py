import os
import pandas as pd
import json

# Ruta principal de datos (ajusta si es necesario)
main_data_folder = "./data"

# Listar todas las subcarpetas relevantes dentro de data
for subfolder in ["raw", "processed", "geojson"]:
    folder_path = os.path.join(main_data_folder, subfolder)
    print(f"\nArchivos en: {folder_path}")
    for file in os.listdir(folder_path):
        print("  -", file)

        # Exploración resumida según tipo de archivo
        file_path = os.path.join(folder_path, file)
        if file.endswith('.csv'):
            try:
                df = pd.read_csv(file_path, nrows=500)
                print(f"    Columnas: {list(df.columns)}")
                print(f"    Primeras filas:\n{df.head(2)}")
            except Exception as e:
                print(f"    Error leyendo CSV: {e}")
        elif file.endswith('.xlsx'):
            try:
                xls = pd.ExcelFile(file_path)
                print("    Hojas:", xls.sheet_names)
                for hoja in xls.sheet_names:
                    df = xls.parse(hoja, nrows=2)
                    print(f"    Hoja '{hoja}', columnas: {list(df.columns)}")
            except Exception as e:
                print(f"    Error leyendo Excel: {e}")
        elif file.endswith('.json') or file.endswith('.geojson'):
            try:
                with open(file_path, encoding='utf8') as f:
                    data = json.load(f)
                print(f"    Tipo: {'dict' if isinstance(data,dict) else 'list'}")
                # Muestra estructura principal
                if isinstance(data, dict):
                    print(f"    Claves principales: {list(data.keys())[:4]}")
                elif isinstance(data, list) and len(data) > 0:
                    print("    Primer elemento de lista:")
                    print(data[0])
            except Exception as e:
                print(f"    Error leyendo JSON: {e}")
        else:
            print("    Formato no soportado para exploración rápida.")

print("\nExploración completada. Copia aquí las columnas/estructura de archivos clave.")
