# utils/explainer.py
"""
Motor de explicabilidad con SHAP para modelo de anemia infantil
VERSIÓN CORREGIDA Y COMPLETA
"""
import streamlit as st
import shap
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from typing import Dict, Any
from sklearn.calibration import CalibratedClassifierCV
import logging

logger = logging.getLogger(__name__)


# =====================================================
# CLASE PRINCIPAL - ModelExplainer
# =====================================================
class ModelExplainer:
    """Explicador de modelos ML usando SHAP"""
    
    def __init__(self, model, X_background: pd.DataFrame):
        """Inicializa el explicador SHAP - EXTRAE MODELO BASE SI ES CALIBRADO"""
        self.model_original = model
        self.X_background = X_background
        
        # ✨ EXTRACCIÓN DEL MODELO BASE
        if isinstance(model, CalibratedClassifierCV):
            logger.info("🔄 CalibratedClassifierCV detectado, extrayendo modelo base...")
            
            if hasattr(model, 'calibrated_classifiers_') and len(model.calibrated_classifiers_) > 0:
                self.model_base = model.calibrated_classifiers_[0].estimator
                logger.info(f"✅ Modelo base extraído: {type(self.model_base).__name__}")
            else:
                logger.error("❌ No se pudo extraer modelo base")
                self.model_base = model
        else:
            self.model_base = model
        
        try:
            self.explainer = shap.TreeExplainer(
                self.model_base,  # ← USA MODELO BASE
                data=X_background,
                feature_perturbation="interventional"
            )
            logger.info(f"✅ Explainer SHAP inicializado con {len(X_background)} muestras")
        except Exception as e:
            logger.error(f"❌ Error creando TreeExplainer: {e}")
            self.explainer = None
    
    def explain_individual(self, X_sample: pd.DataFrame, feature_names: list = None) -> Dict[str, Any]:
        """Genera explicación SHAP para una predicción individual"""
        if self.explainer is None:
            logger.warning("⚠️  Explainer no disponible")
            return None
        
        try:
            if not isinstance(X_sample, pd.DataFrame):
                logger.error("❌ X_sample debe ser un DataFrame")
                return None
            
            if X_sample.shape[0] != 1:
                logger.error(f"❌ X_sample debe tener 1 fila, tiene {X_sample.shape[0]}")
                return None
            
            # Limpiar arrays anidados
            for col in X_sample.columns:
                val = X_sample[col].iloc[0]
                if isinstance(val, (list, np.ndarray)):
                    logger.error(f"❌ Columna '{col}' contiene array: {type(val)}")
                    return None
            
            if feature_names is None:
                feature_names = list(X_sample.columns)
            
            X_array = X_sample.values.astype(np.float64)
            
            if X_array.ndim != 2 or X_array.shape[0] != 1:
                logger.error(f"❌ X_array dimensiones incorrectas: {X_array.shape}")
                return None
            
            logger.info(f"✅ X_array validado: shape={X_array.shape}")
            
            # Calcular SHAP values
            shap_values = self.explainer.shap_values(X_array)
            
            # Para clasificación binaria, tomar clase positiva
            if isinstance(shap_values, list):
                shap_values_class1 = shap_values[1]
            else:
                shap_values_class1 = shap_values
            
            # Aplanar
            if shap_values_class1.ndim > 1:
                shap_values_1d = shap_values_class1.flatten()
            else:
                shap_values_1d = shap_values_class1
            
            feature_values_1d = X_array.flatten()
            
            n_features = len(feature_names)
            
            # Ajustar tamaños si no coinciden
            if len(shap_values_1d) != n_features:
                logger.warning(f"⚠️  Ajustando SHAP: {len(shap_values_1d)} → {n_features}")
                shap_values_1d = shap_values_1d[:n_features]
            
            if len(feature_values_1d) != n_features:
                logger.warning(f"⚠️  Ajustando features: {len(feature_values_1d)} → {n_features}")
                feature_values_1d = feature_values_1d[:n_features]
            
            # Crear DataFrame
            shap_df = pd.DataFrame({
                'feature': feature_names,
                'shap_value': shap_values_1d.tolist(),
                'feature_value': feature_values_1d.tolist(),
                'abs_shap': np.abs(shap_values_1d).tolist()
            }).sort_values('abs_shap', ascending=False)
            
            top_10 = shap_df.head(10)
            
            # Generar explicaciones
            fig_waterfall = self._create_waterfall_plot(shap_values_1d, feature_values_1d, feature_names)
            fig_bar = self._create_bar_plot(top_10)
            texto_explicacion = self._generate_explanation_text(top_10)
            
            logger.info("✅ Explicación SHAP generada")
            
            return {
                'shap_values': shap_values_1d,
                'shap_df': shap_df,
                'top_10': top_10,
                'fig_waterfall': fig_waterfall,
                'fig_bar': fig_bar,
                'texto_explicacion': texto_explicacion,
                'base_value': self.explainer.expected_value[1] if isinstance(self.explainer.expected_value, list) 
                            else self.explainer.expected_value
            }
            
        except Exception as e:
            logger.error(f"❌ Error generando explicación SHAP: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _create_waterfall_plot(self, shap_values: np.ndarray, feature_values: np.ndarray, 
                                feature_names: list) -> plt.Figure:
        """Crea gráfico waterfall de SHAP"""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            if isinstance(self.explainer.expected_value, list):
                base_val = float(self.explainer.expected_value[1])
            elif isinstance(self.explainer.expected_value, np.ndarray):
                base_val = float(self.explainer.expected_value.flat[0])
            else:
                base_val = float(self.explainer.expected_value)
            
            explanation = shap.Explanation(
                values=shap_values,
                base_values=base_val,
                data=feature_values,
                feature_names=feature_names
            )
            
            shap.plots.waterfall(explanation, max_display=10, show=False)
            plt.tight_layout()
            
            return plt.gcf()
            
        except Exception as e:
            logger.error(f"Error creando waterfall plot: {e}")
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'Gráfico Waterfall no disponible', 
                    ha='center', va='center', fontsize=14, color='gray')
            ax.axis('off')
            return fig
    
    def _create_bar_plot(self, top_features: pd.DataFrame) -> plt.Figure:
        """Crea gráfico de barras con top features"""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            top_sorted = top_features.sort_values('abs_shap', ascending=True)
            
            colors = ['#ff6b6b' if x > 0 else '#4dabf7' for x in top_sorted['shap_value']]
            
            ax.barh(range(len(top_sorted)), top_sorted['shap_value'], color=colors)
            ax.set_yticks(range(len(top_sorted)))
            ax.set_yticklabels(top_sorted['feature'], fontsize=10)
            ax.set_xlabel('Contribución SHAP', fontsize=11, fontweight='bold')
            ax.set_title('Top 10 Factores de Influencia', fontsize=13, fontweight='bold', pad=15)
            ax.axvline(x=0, color='black', linestyle='--', linewidth=0.8, alpha=0.7)
            ax.grid(axis='x', alpha=0.3)
            
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor='#ff6b6b', label='Aumenta riesgo'),
                Patch(facecolor='#4dabf7', label='Reduce riesgo')
            ]
            ax.legend(handles=legend_elements, loc='lower right')
            
            plt.tight_layout()
            return fig
            
        except Exception as e:
            logger.error(f"Error creando bar plot: {e}")
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'Error generando gráfico', ha='center', va='center')
            ax.axis('off')
            return fig
    
    def _generate_explanation_text(self, top_features: pd.DataFrame) -> str:
        """Genera texto explicativo en lenguaje natural"""
        texto = "### 🔍 ¿Por qué este resultado?\n\n"
        texto += "El modelo analiza múltiples factores. Los **más importantes** para este caso:\n\n"
        
        # ✨ FEATURE MAPPING COMPLETO
        feature_mapping = {
            'hemoglobina': 'Nivel de hemoglobina en sangre',
            'edad_meses': 'Edad del niño en meses',
            'altitud': 'Altitud de residencia',
            'peso_kg': 'Peso del niño',
            'hb_baja': 'Hemoglobina baja (<11 g/dL)',
            'sin_suplemento': 'NO recibe suplemento de hierro',
            'recibe_suplemento': 'Recibe suplemento de hierro',
            'asiste_cred': 'Asiste a controles CRED',
            'sin_cred': 'NO asiste a controles CRED',
            'area_rural': 'Vive en área rural',
            'altitud_muy_alta': 'Altitud muy alta (>3000m)',
            'edad_6_11m': 'Edad 6-11 meses (grupo crítico)',
            'edad_12_23m': 'Edad 12-23 meses',
            'hb_x_altitud': 'Hb baja + Altitud (riesgo multiplicado)',
        }
        
        for idx, row in top_features.head(5).iterrows():
            feat = row['feature']
            shap_val = row['shap_value']
            feat_val = row['feature_value']
            
            feat_name = feature_mapping.get(feat, feat.replace('_', ' ').title())
            
            emoji = "🔴" if shap_val > 0 else "🟢"
            direccion = "**AUMENTA**" if shap_val > 0 else "**REDUCE**"
            
            if isinstance(feat_val, (int, np.integer)):
                feat_val_str = f"{int(feat_val)}"
            elif isinstance(feat_val, (float, np.floating)):
                feat_val_str = f"{feat_val:.2f}"
            else:
                feat_val_str = str(feat_val)
            
            texto += f"{emoji} **{feat_name}** (valor: {feat_val_str}): {direccion} el riesgo en {abs(shap_val):.3f}\n\n"
        
        texto += "\n💡 **Nota:** Valores SHAP positivos = mayor riesgo, negativos = protección."
        
        return texto


# =====================================================
# FUNCIÓN AUXILIAR - load_background_data
# =====================================================
@st.cache_data(show_spinner=False, ttl=3600)
def load_background_data(csv_path: str, features_list: list, n_samples: int = 50) -> pd.DataFrame:
    """Carga muestra de datos de fondo para SHAP"""
    try:
        df = pd.read_csv(csv_path)
        
        missing = [f for f in features_list if f not in df.columns]
        
        if missing:
            logger.warning(f"⚠️  Features faltantes: {missing[:5]}...")
            for feat in missing:
                df[feat] = 0
        
        df_features = df[features_list]
        
        if len(df_features) > n_samples:
            df_sample = df_features.sample(n=n_samples, random_state=42)
        else:
            df_sample = df_features
        
        logger.info(f"✅ Background data: {len(df_sample)} muestras, {df_sample.shape[1]} features")
        return df_sample
        
    except Exception as e:
        logger.error(f"❌ Error cargando background: {e}")
        return None
