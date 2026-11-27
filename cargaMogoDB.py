import os
import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient
import datetime
import certifi

load_dotenv()

# --- CONFIGURACIÓN (Requisito: Conexión Real) ---
MONGO_URI = os.getenv("MONGO_URI")  # Defínala en un archivo .env (ver .env.example)
DB_NAME = "RH"
COLLECTION_NAME = "RH"


def create_mongo_client(uri):
    return MongoClient(
        uri,
        tls=True,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=20000,
        socketTimeoutMS=20000,
        connectTimeoutMS=20000,
    )

def ingesta_excel_a_mongodb(ruta_excel):
    print(f"[{datetime.datetime.now()}] >>> INICIANDO: Fase de Ingesta de Datos Raw")
    
    try:
        # 1. Lectura del Excel (Requisito: Fuente de datos real)
        # Nota: read_excel detecta automáticamente las columnas de tu archivo
        print(f"[{datetime.datetime.now()}] >>> Leyendo archivo: {ruta_excel}")
        df = pd.read_excel(ruta_excel) 
        
        # 2. Conexión a MongoDB
        client = create_mongo_client(MONGO_URI)
        db = client[DB_NAME]
        coleccion = db[COLLECTION_NAME]
        
        # 3. Preparación de datos (JSON/Diccionario)
        # MongoDB almacena documentos, por lo que convertimos las filas del Excel
        datos_dict = df.to_dict(orient='records')
        
        # 4. Inserción masiva en la colección 'raw'
        # Esto asegura que los datos existan en una base real antes del ETL
        print(f"[{datetime.datetime.now()}] >>> Insertando {len(datos_dict)} registros en MongoDB...")
        resultado = coleccion.insert_many(datos_dict)
        
        print(f"[{datetime.datetime.now()}] >>> PROCESO COMPLETADO EXITOSAMENTE")
        print(f"[{datetime.datetime.now()}] >>> IDs insertados: {len(resultado.inserted_ids)}")
        
    except Exception as e:
        print(f"[{datetime.datetime.now()}] >>> ERROR DURANTE LA CARGA: {e}")
    finally:
        client.close()

# Ejecución del script maestro de ingesta
if __name__ == "__main__":
    # Cambia el nombre por el de tu archivo real
    archivo_usuario = r"C:\Users\Gabo\Desktop\ULEAD\ADMIN BD\Entrega final\BD RRHH CANDIDATOS.xlsx"
    ingesta_excel_a_mongodb(archivo_usuario)
