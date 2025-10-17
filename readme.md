---
title: Sistema Alerta Temprana Anemia Infantil
emoji: 🏥
colorFrom: purple
colorTo: blue
sdk: streamlit
sdk_version: 1.31.0
app_file: app.py
pinned: true
license: mit
tags:
  - health
  - machine-learning
  - anemia
  - pediatrics
  - peru
---

# 🏥 Sistema de Alerta Temprana de Anemia Infantil

**Datatón Exprésate Perú con Datos 2025 - MINSA**

## 🎯 Descripción

Sistema inteligente para la detección temprana y gestión de anemia infantil en Perú, basado en 895,982 registros del SIEN 2024.

## ✨ Características Principales

- 🤖 **Modelo ML con 99.9% precisión** - RandomForest con SHAP explicabilidad
- 🔮 **Proyecciones temporales 3-6 meses** - Predicción de riesgo futuro
- 🚦 **Sistema de semáforo 5 niveles** - Alertas tempranas personalizadas
- 📋 **Protocolos clínicos NTS 213-MINSA/DGIESP-2024** - Dosis individualizadas
- 📄 **Reportes PDF automáticos** - Descarga instantánea
- 📧 **Notificaciones CRED** - Recordatorios programados
- 🗺️ **Ajuste OMS 2024** - Corrección por altitud

## 🛠️ Stack Técnico

- **Frontend:** Streamlit
- **ML:** RandomForest, XGBoost, SHAP
- **Datos:** 895,982 registros SIEN 2024
- **Normativa:** NTS 213-MINSA/DGIESP-2024

## 📊 Métricas del Modelo

| Métrica | Valor |
|---------|-------|
| Precisión | 99.9% |
| Recall | 85.0% |
| F1-Score | 91.8% |
| AUC-ROC | 0.999 |

## 🚀 Uso

1. Ingresa datos del paciente (edad, peso, hemoglobina, altitud)
2. El sistema genera:
   - Diagnóstico con semáforo de riesgo
   - Proyección 3-6 meses
   - Protocolo clínico personalizado
   - Calendario de seguimiento CRED
   - Reporte PDF descargable

## 🏆 Equipo

Desarrollado para el Datatón Exprésate Perú con Datos 2025

## 📝 Licencia

MIT License

## 📧 Contacto

Para consultas técnicas o feedback sobre el sistema.
