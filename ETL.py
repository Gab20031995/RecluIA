import pandas as pd
import re
from pymongo import MongoClient
import certifi
from IPython.display import display, Markdown

class ETL_RH():
    def __init__(self, uri: str, db_name: str, raw_coll: str, curated_coll: str):
        self._uri = uri
        self._db_name = db_name
        self._raw_coll = raw_coll
        self._curated_coll = curated_coll
        self._df = pd.DataFrame()

    def _get_connection(self):
        return MongoClient(self._uri, tlsCAFile=certifi.where())

    def extract(self):
        display(Markdown("### 📥 Fase 1: Extracción"))
        client = self._get_connection()
        db = client[self._db_name]
        datos = list(db[self._raw_coll].find())
        self._df = pd.DataFrame(datos)
        client.close()
        print(f"[LOG] Registros extraídos: {len(self._df)}")

    def transform(self):
        display(Markdown("### ⚙️ Fase 2: Transformación con Reglas de Negocio"))
        df = self._df.copy()

        # 1. Limpieza básica y Formatos
        if '_id' in df.columns: df = df.drop(columns=['_id'])
        for col in ['ID', 'Número de cedula']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int).astype(str)
        
        df = df.drop_duplicates(subset=['Número de cedula'], keep='first')

        # 2. Normalización de Salario Numérico (Promedio)
        def _parse_salary(texto):
            numeros = re.findall(r'\d+', str(texto).replace(' ', ''))
            if len(numeros) >= 2: return (int(numeros[0]) + int(numeros[1])) / 2
            elif len(numeros) == 1: return int(numeros[0])
            return 0
        df['Salario_Numerico'] = df['Expectativa salarial'].apply(_parse_salary)

        # 3. Diccionario de Rangos Salariales FIFCO (Regla de Negocio)
        # Usamos el límite superior para validar si el candidato "se sale" del presupuesto
        presupuesto_max = {
            'Bachiller en educación media': 600000,
            'Diplomado/Tecnico completo': 700000,
            'Diplomado/Tecnico incompleto': 600000,
            'Primaria completa': 400000,
            'Secundaria completa': 500000,
            'Secundaria Incompleta': 500000,
            'Universidad completa': 700000,
            'Universidad incompleta': 700000,
            'No indica': 0
        }

        # 4. APLICACIÓN DE REGLAS PARA IA (Target Labeling)
        def validar_aptitud(row):
            escolaridad = str(row.get('Escolaridad', 'No indica')).strip()
            puesto = str(row.get('Puesto', '')).lower()
            salario = row.get('Salario_Numerico', 0)
            manipulacion = str(row.get('Cuenta con título de manipulación de alimentos?', 'No')).strip()
            laborando = str(row.get('Se encuentra laborando actualmente?', 'No')).strip()

            # REGLA A: Manipulación de alimentos obligatoria para todos
            if manipulacion != 'Si': return 0
            
            # REGLA B: Presupuesto salarial por escolaridad
            max_pago = presupuesto_max.get(escolaridad, 9999999)
            if salario > max_pago: return 0

            # REGLA C: Administradores (Bachiller en media en adelante)
            niveles_bajos = ['Primaria completa', 'Secundaria completa', 'Secundaria Incompleta']
            if 'administrador' in puesto and escolaridad in niveles_bajos:
                return 0

            # REGLA D: Validación de Preaviso (Si labora, marcar para revisión)
            # (Si labora, le damos un peso menor o lo marcamos como 'Revisión')
            return 1 # Si pasa todo, es un candidato APTO

        df['Apto_IA'] = df.apply(validar_aptitud, axis=1)

        # 5. Feature Engineering: Columna de Preaviso
        # Esto le enseña a la IA que el tiempo de contratación podría variar
        df['Requiere_Preaviso'] = df['Se encuentra laborando actualmente?'].apply(lambda x: 1 if x == 'Si' else 0)

        self._df = df
        print(f"[LOG] Transformación finalizada. Candidatos aptos detectados: {df['Apto_IA'].sum()}")

    def load(self):
        display(Markdown("### 📤 Fase 3: Carga a Capa Curada"))
        client = self._get_connection()
        db = client[self._db_name]
        try:
            db[self._curated_coll].drop()
            db[self._curated_coll].insert_many(self._df.to_dict(orient='records'))
            print(f"[LOG] Éxito: {len(self._df)} registros en '{self._curated_coll}'.")
        finally:
            client.close()

    def run_pipeline(self):
        self.extract()
        self.transform()
        self.load()
        return self._df.head(3)