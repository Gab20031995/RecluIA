import os
import time
from dotenv import load_dotenv
from datetime import datetime
from database import obtener_conexion_mongo
from EDA import EDA_RH
from ETL import ETL_RH
import pandas as pd

load_dotenv()

class OrquestadorPipeline:
    def __init__(self):
        self.start_time = None
        self.uri = os.getenv("MONGO_URI")  # Defínala en un archivo .env
        self.db_name = "RH"

    def log(self, mensaje):
        """Genera logs con timestamp para evidencia del reporte."""
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{ahora}] [ORQUESTADOR] {mensaje}")

    def ejecutar_pipeline(self):
        self.start_time = time.time()
        self.log("=== INICIANDO EJECUCIÓN DEL PIPELINE AUTOMATIZADO ===")

        try:
            # PASO 1: EXTRACCIÓN Y EDA (Diagnóstico)
            self.log("PASO 1: Iniciando Extracción y Análisis Exploratorio (EDA)...")
            client = obtener_conexion_mongo()
            df_raw = pd.DataFrame(list(client[self.db_name]["RH"].find()))
            client.close()

            analisis = EDA_RH(df_raw, id_column="Número de cedula")
            # En el orquestador podemos correr una versión resumida o completa
            self.log(f"Extracción exitosa: {len(df_raw)} registros encontrados.")

            # PASO 2: ETL (Transformación y Carga a Capa Curada)
            self.log("PASO 2: Iniciando Transformación y Carga (ETL)...")
            etl = ETL_RH(
                uri=self.uri,
                db_name=self.db_name,
                raw_coll="RH",
                curated_coll="RH_curada"
            )
            # El método run_pipeline ya tiene sus propios logs internos
            etl.run_pipeline()

            # PASO 3: VALIDACIÓN FINAL
            self.log("PASO 3: Validando consistencia en Capa Curada...")
            client = obtener_conexion_mongo()
            count_curada = client[self.db_name]["RH_curada"].count_documents({})
            client.close()
            
            self.log(f"Validación completada: {count_curada} documentos en 'RH_curada'.")

            total_time = round(time.time() - self.start_time, 2)
            self.log(f"=== PIPELINE FINALIZADO EXITOSAMENTE EN {total_time} SEG ===\n")

        except Exception as e:
            self.log(f"❌ ERROR CRÍTICO EN EL PIPELINE: {e}")

if __name__ == "__main__":
    pipeline = OrquestadorPipeline()
    pipeline.ejecutar_pipeline()
