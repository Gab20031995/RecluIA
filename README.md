# 🎯 Recruitment Predictive Pipeline - FIFCO Retail Case
**Curso:** Administración de Bases de Datos  
**Profesor:** Alejandro Zamora  
**Desarrollado por:** Gabriel Corrales / Jafet Rojas / Luis Rojas  

---

## 📌 Descripción del Proyecto
Este proyecto implementa un pipeline de datos (ETL) de extremo a extremo y un modelo de Inteligencia Artificial para la automatización y priorización del reclutamiento masivo en el sector Retail. El flujo está diseñado para transformar datos crudos de aplicaciones laborales en una herramienta predictiva que asiste a los reclutadores en la toma de decisiones basada en reglas de negocio reales.

## 🏗️ Arquitectura del Pipeline
El sistema se divide en tres fases principales siguiendo una arquitectura de capas (Medallion Architecture):

1.  **Extract & Raw (Capa Bronce):** Extracción de más de 41,000 registros desde **MongoDB Atlas**. En esta fase se identifica la data "sucia", incluyendo duplicados masivos y errores de formato (como cédulas en notación científica).
2.  **Transform & Curated (Capa Plata):** Procesamiento mediante la clase `ETL_RH`. Se eliminan duplicados (-68% de ruido), se normalizan los IDs y se inyectan **Reglas de Negocio** (salarios por escolaridad, requisitos de puesto y certificaciones). Los datos limpios se cargan en la colección `RH_curada`.
3.  **IA & Application (Capa Oro):** Entrenamiento de un modelo de clasificación **Random Forest** que predice la idoneidad del candidato. El resultado se despliega en una interfaz interactiva con **Streamlit**.

---

## 🛠️ Reglas de Negocio Implementadas
Para garantizar que la IA sea predictiva, el ETL normaliza la data bajo los siguientes criterios de FIFCO:
* **Validación Salarial:** Topes máximos según escolaridad (ej. Primaria ₡400k, Universidad ₡700k).
* **Filtros Críticos:** Manipulación de alimentos obligatoria y nivel académico mínimo (Bachillerato) para puestos administrativos.
* **Gestión de Disponibilidad:** Análisis de candidatos laborando actualmente para cálculo de preaviso.

## 🛠️ Tecnologías Utilizadas
* **Lenguaje:** Python 3.10+
* **Base de Datos:** MongoDB Atlas (NoSQL)
* **IA / Machine Learning:** Scikit-Learn (Random Forest), Joblib
* **Visualización & App:** Streamlit, Matplotlib, Seaborn
* **Librerías Clave:** `pandas`, `pymongo`, `certifi`, `re` (Regex).

---

## 🚀 Configuración del Entorno

### 1. Variables de Entorno
Cree un archivo `.env` o configure las variables en su script `database.py`:
```env
MONGO_URI="mongodb+srv://luizclzm_db_user:Z6ondingMP7UWGfQ@cluster0.qlmcjle.mongodb.net/"
DB_NAME="RH"
RAW_COLLECTION="RH"
CURATED_COLLECTION="RH_curada"