# RecluIA: pipeline de datos e IA para priorizar candidatos en reclutamiento retail

Pipeline ETL de extremo a extremo y modelo de clasificación que ayuda a un equipo de reclutamiento masivo a enfocarse primero en los candidatos que cumplen los requisitos del puesto.

**Curso:** Administración de Bases de Datos · **Profesor:** Alejandro Zamora
**Equipo:** Gabriel Corrales, Jafet Rojas, Luis Rojas

## El problema

En reclutamiento masivo de retail llegan miles de aplicaciones con datos sucios: duplicados, formatos inconsistentes y cédulas guardadas en notación científica. Filtrarlas a mano consume la mayor parte del tiempo del reclutador.

## Resultados

- **Limpieza:** de más de 41.000 registros crudos se eliminó un 68 % de duplicados y ruido, lo que reduce en esa proporción el volumen que el reclutador debe revisar.
- **Priorización:** un modelo Random Forest clasifica a cada candidato según su compatibilidad con el puesto usando 4 variables: puesto, escolaridad, aspiración salarial y estatus laboral (preaviso).
- **Herramienta:** una app en Streamlit donde el reclutador consulta la prioridad de los candidatos.

> **Nota sobre la precisión (~98 %).** Las etiquetas de entrenamiento se construyeron a partir de las mismas reglas de negocio que usa el ETL. Por eso la precisión alta indica que el modelo **replica fielmente esas reglas de priorización**, no que prediga el desempeño futuro del candidato. Un siguiente paso sería entrenarlo con resultados reales de contratación (por ejemplo, permanencia a 3 meses).

## Arquitectura (Medallion)

1. **Bronce (extracción):** carga de los registros crudos desde MongoDB Atlas e identificación de datos sucios.
2. **Plata (transformación):** la clase `ETL_RH` elimina duplicados, normaliza identificaciones y aplica las reglas de negocio. Los datos limpios se guardan en la colección `RH_curada`.
3. **Oro (IA y aplicación):** entrenamiento del modelo y despliegue en Streamlit.

## Reglas de negocio aplicadas

- **Validación salarial:** topes de aspiración salarial según escolaridad.
- **Filtros críticos:** manipulación de alimentos obligatoria y bachillerato como mínimo para puestos administrativos.
- **Disponibilidad:** identificación de candidatos que trabajan actualmente, para estimar el preaviso.

## Tecnologías

Python 3.10+ · MongoDB Atlas · pandas · pymongo · scikit-learn (Random Forest) · joblib · Streamlit · Matplotlib · Seaborn

## Estructura

```
├── database.py        # Conexión a MongoDB (lee MONGO_URI del archivo .env)
├── cargaMogoDB.py     # Ingesta del Excel crudo a MongoDB (capa bronce)
├── EDA.py             # Clase para análisis exploratorio
├── ETL.py             # Clase para transformación y reglas de negocio
├── ia_model.py        # Entrenamiento y exportación del modelo
├── main.py            # Orquestador del pipeline completo
├── app.py             # Interfaz en Streamlit
├── eda_etl_RH.ipynb   # Notebook de exploración
└── requirements.txt
```

## Cómo ejecutarlo

1. Instale las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

2. Cree un archivo `.env` en la raíz del proyecto (está excluido de Git) con su propia conexión:

   ```
   MONGO_URI=mongodb+srv://USUARIO:CONTRASEÑA@SU-CLUSTER.mongodb.net/
   ```

3. Ejecute el pipeline completo (limpieza, carga y entrenamiento):

   ```bash
   python main.py
   ```

4. Inicie la aplicación:

   ```bash
   streamlit run app.py
   ```

## Próximos pasos

- Entrenar con resultados reales de contratación en lugar de etiquetas derivadas de reglas.
- Agregar métricas por clase (precisión y recall) y una comparación contra un filtro por reglas simple.
- Agregar un dashboard con indicadores del embudo de reclutamiento.
