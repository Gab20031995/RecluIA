# database.py
from pymongo import MongoClient
import certifi

def obtener_conexion_mongo():
    """
    Establece y retorna una conexión segura a MongoDB Atlas.
    """
    # URI con el formato +srv para mayor estabilidad
    MONGO_URI = "mongodb+srv://luizclzm_db_user:Z6ondingMP7UWGfQ@cluster0.qlmcjle.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    
    try:
        # Se usa certifi para validar los certificados SSL/TLS
        client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        # Prueba de conexión (Ping)
        client.admin.command('ping')
        return client
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None