# utils/data_loader.py
"""
Módulo para cargar datos procesados de los notebooks
"""
import pandas as pd
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rutas base
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"


class DataLoader:
    """Clase para cargar y gestionar datos procesados"""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Inicializa el cargador de datos
        
        Args:
            data_dir: Ruta al directorio de datos (opcional)
        """
        self.data_dir = data_dir or DATA_DIR
        self._cache = {}
        
    def load_csv(self, filename: str, use_cache: bool = True) -> Optional[pd.DataFrame]:
        """
        Carga un archivo CSV
        
        Args:
            filename: Nombre del archivo (sin ruta)
            use_cache: Si usar caché (default True)
            
        Returns:
            DataFrame o None si no existe
        """
        if use_cache and filename in self._cache:
            logger.info(f"📦 Cargando desde caché: {filename}")
            return self._cache[filename]
        
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            logger.warning(f"⚠️ Archivo no encontrado: {filepath}")
            return None
        
        try:
            df = pd.read_csv(filepath)
            logger.info(f"✅ Cargado: {filename} ({len(df):,} registros)")
            
            if use_cache:
                self._cache[filename] = df
            
            return df
        except Exception as e:
            logger.error(f"❌ Error al cargar {filename}: {e}")
            return None
    
    def load_json(self, filename: str, use_cache: bool = True) -> Optional[Dict[Any, Any]]:
        """
        Carga un archivo JSON
        
        Args:
            filename: Nombre del archivo (sin ruta)
            use_cache: Si usar caché (default True)
            
        Returns:
            Diccionario o None si no existe
        """
        if use_cache and filename in self._cache:
            logger.info(f"📦 Cargando desde caché: {filename}")
            return self._cache[filename]
        
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            logger.warning(f"⚠️ Archivo no encontrado: {filepath}")
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"✅ Cargado: {filename}")
            
            if use_cache:
                self._cache[filename] = data
            
            return data
        except Exception as e:
            logger.error(f"❌ Error al cargar {filename}: {e}")
            return None
    
    def clear_cache(self):
        """Limpia la caché de datos"""
        self._cache.clear()
        logger.info("🗑️ Caché limpiada")
    
    # === MÉTODOS ESPECÍFICOS POR NOTEBOOK ===
    
    def load_sien_nacional(self) -> Optional[pd.DataFrame]:
        """Carga dataset SIEN nacional procesado (Notebook 1)"""
        return self.load_csv("sien_nacional_procesado.csv")
    
    def load_alimentos_hierro(self) -> Optional[pd.DataFrame]:
        """Carga base de alimentos ricos en hierro (Notebook 5)"""
        return self.load_csv("base_alimentos_hierro.csv")
    
    def load_brechas_departamento(self) -> Optional[pd.DataFrame]:
        """Carga brechas de equidad por departamento (Notebook 4)"""
        return self.load_csv("brechas_departamento.csv")
    
    def load_tendencias_departamento(self) -> Optional[pd.DataFrame]:
        """Carga tendencias temporales por departamento (Notebook 6)"""
        return self.load_csv("tendencias_departamento.csv")
    
    def load_proyecciones(self) -> Optional[pd.DataFrame]:
        """Carga proyecciones a 3 meses (Notebook 6)"""
        return self.load_csv("proyecciones_3_meses.csv")
    
    def load_reporte_temporal(self) -> Optional[Dict]:
        """Carga reporte temporal en JSON (Notebook 6)"""
        return self.load_json("reporte_temporal.json")
    
    def load_reporte_equidad(self) -> Optional[Dict]:
        """Carga reporte de equidad en JSON (Notebook 4)"""
        return self.load_json("reporte_equidad.json")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de datos disponibles
        
        Returns:
            Diccionario con estadísticas
        """
        stats = {
            "archivos_disponibles": [],
            "archivos_faltantes": [],
            "total_registros": 0
        }
        
        archivos_esperados = [
            "sien_nacional_procesado.csv",
            "base_alimentos_hierro.csv",
            "brechas_departamento.csv",
            "tendencias_departamento.csv",
            "proyecciones_3_meses.csv",
            "reporte_temporal.json",
            "reporte_equidad.json"
        ]
        
        for archivo in archivos_esperados:
            filepath = self.data_dir / archivo
            if filepath.exists():
                stats["archivos_disponibles"].append(archivo)
                
                # Contar registros si es CSV
                if archivo.endswith('.csv'):
                    try:
                        df = pd.read_csv(filepath)
                        stats["total_registros"] += len(df)
                    except:
                        pass
            else:
                stats["archivos_faltantes"].append(archivo)
        
        return stats


# Instancia global del cargador
data_loader = DataLoader()

def load_modelo_ml(self) -> Optional[Dict]:
    """Carga modelo ML de predicción de anemia"""
    try:
        model_path = Path("models/predictor_anemia_ml.pkl")
        if not model_path.exists():
            return None
        
        import pickle
        with open(model_path, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        logger.error(f"Error cargando modelo: {e}")
        return None
