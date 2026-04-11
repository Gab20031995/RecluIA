import pandas as pd
from pymongo import MongoClient
import certifi
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import joblib

def entrenar_modelo_ia():
    print(">>> [IA] Iniciando fase de entrenamiento con Reglas de Negocio...")
    
    # 1. Carga de datos desde Capa Curada
    # IMPORTANTE: Ahora usamos la data que ya pasó por las reglas del ETL
    client = MongoClient("mongodb+srv://luizclzm_db_user:Z6ondingMP7UWGfQ@cluster0.qlmcjle.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0", tlsCAFile=certifi.where())
    df = pd.DataFrame(list(client["RH"]["RH_curada"].find()))
    client.close()

    if df.empty:
        print("❌ Error: La colección 'RH_curada' está vacía. Corre el ETL primero.")
        return

    # 2. Preprocesamiento (Encoding)
    # Necesitamos convertir el texto a números para que la IA entienda
    le_puesto = LabelEncoder()
    le_escolaridad = LabelEncoder()
    
    # Ajustamos los encoders con toda la data disponible
    df['Puesto_Enc'] = le_puesto.fit_transform(df['Puesto'].astype(str))
    df['Escolaridad_Enc'] = le_escolaridad.fit_transform(df['Escolaridad'].astype(str))

    # 3. Selección de Variables (Features y Target)
    # Agregamos 'Requiere_Preaviso' como una nueva variable que la IA debe analizar
    X = df[['Puesto_Enc', 'Escolaridad_Enc', 'Salario_Numerico', 'Requiere_Preaviso']]
    
    # Nuestro TARGET ahora es 'Apto_IA', que ya trae los filtros de:
    # - Manipulación de alimentos
    # - Rangos salariales reales de FIFCO
    # - Nivel académico para administradores
    y = df['Apto_IA']

    # 4. Entrenamiento
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Usamos Random Forest: excelente para reglas de clasificación
    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)

    # 5. Evaluación (Requisito ULEAD)
    preds = modelo.predict(X_test)
    accuracy = accuracy_score(y_test, preds)
    print(f"\n✅ Precisión del modelo: {accuracy:.2f}")
    print("\n--- Reporte de Clasificación ---")
    print(classification_report(y_test, preds))

    # 6. Guardar Activos
    joblib.dump(modelo, 'modelo_rh.pkl')
    joblib.dump(le_puesto, 'le_puesto.pkl')
    joblib.dump(le_escolaridad, 'le_escolaridad.pkl')
    print("\n>>> [IA] Modelo y encoders actualizados y guardados.")

if __name__ == "__main__":
    entrenar_modelo_ia()