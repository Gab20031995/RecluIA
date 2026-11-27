# database.py
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi

load_dotenv()

def obtener_conexion_mongo():
    """
    Establece y retorna una conexión segura a MongoDB Atlas.
    """
    # URI con el formato +srv para mayor estabilidad
    MONGO_URI = os.getenv("MONGO_URI")  # Defínala en un archivo .env (ver .env.example)
    
    try:
        # Se usa certifi para validar los certificados SSL/TLS
        client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        # Prueba de conexión (Ping)
        client.admin.command('ping')
        return client
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None
