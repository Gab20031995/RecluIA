import streamlit as st
import pandas as pd
import joblib
import numpy as np

# Configuración de la página
st.set_page_config(page_title="FIFCO Retail - Predictor de Reclutamiento", layout="centered")

# 1. CARGA DE ACTIVOS
@st.cache_resource
def cargar_activos():
    modelo = joblib.load('modelo_rh.pkl')
    le_puesto = joblib.load('le_puesto.pkl')
    le_escolaridad = joblib.load('le_escolaridad.pkl')
    return modelo, le_puesto, le_escolaridad

try:
    modelo, le_puesto, le_escolaridad = cargar_activos()
except:
    st.error("❌ No se encontraron los archivos del modelo. Ejecuta primero el entrenamiento de la IA.")
    st.stop()

# --- INTERFAZ DE USUARIO ---
st.title("🎯 Clasificador de Prioridad - FIFCO")
st.sidebar.header("Datos del Candidato")

# Entradas del usuario
puesto_sel = st.sidebar.selectbox("Puesto de interés", le_puesto.classes_)
escolaridad_sel = st.sidebar.selectbox("Nivel de Escolaridad", le_escolaridad.classes_)
salario_input = st.sidebar.number_input("Expectativa Salarial (Colones)", min_value=0, value=450000)

# NUEVO: Input para la 4ta variable (Preaviso/Laborando)
laborando_sel = st.sidebar.radio("¿Se encuentra laborando actualmente?", ["Si", "No"])
# Mapeo simple: Si -> 1, No -> 0 (Igual que en el ETL)
preaviso_val = 1 if laborando_sel == "Si" else 0

# --- PROCESO DE INFERENCIA ---
if st.sidebar.button("Analizar Candidato"):
    try:
        # 1. Transformar entradas
        puesto_enc = le_puesto.transform([puesto_sel])[0]
        escolaridad_enc = le_escolaridad.transform([escolaridad_sel])[0]
        
        # 2. Crear el vector de entrada con las 4 VARIABLES
        # [Puesto, Escolaridad, Salario, Preaviso]
        X_nuevo = np.array([[puesto_enc, escolaridad_enc, salario_input, preaviso_val]])
        
        # 3. Predicción
        prediccion = modelo.predict(X_nuevo)[0]
        probabilidad = modelo.predict_proba(X_nuevo)[0][1]

        # --- MOSTRAR RESULTADOS ---
        st.subheader("Resultado del Análisis")
        if prediccion == 1:
            st.success(f"✅ CANDIDATO APTO (Prioridad Alta)")
            st.write(f"Probabilidad de éxito: **{probabilidad*100:.1f}%**")
            st.write("El perfil cumple con los rangos salariales y requisitos de FIFCO.")
        else:
            st.warning(f"⚠️ REVISIÓN MANUAL (Prioridad Media/Baja)")
            st.write(f"Probabilidad de éxito: **{probabilidad*100:.1f}%**")
            st.write("El perfil podría estar fuera de rango salarial o no cumplir con la escolaridad mínima para el puesto.")

    except Exception as e:
        st.error(f"Error en la predicción: {e}")

else:
    st.info("👈 Ingresa los datos del candidato y presiona 'Analizar'.")