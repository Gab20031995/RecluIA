import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display, Markdown, HTML

class EDA_RH():
    def __init__(self, dataframe: pd.DataFrame, id_column: str | None = None):
        """
        Clase para realizar el Análisis Exploratorio de Datos (EDA)
        enfocado en los requisitos de limpieza y transformación.
        """
        self._df = dataframe.copy()
        self._id_column = id_column
        
        # 1. Limpieza técnica: eliminamos el _id de MongoDB para el análisis técnico
        if '_id' in self._df.columns:
            self._df = self._df.drop(columns=['_id'])
            
        # 2. Validación de la columna de ID (Ej: Número de cédula)
        if id_column is not None:
            self._check_id_column(id_column)
            
        self._preview_rows = 5
        self._float_precision = 2

    def _check_id_column(self, id_col: str):
        """Detecta problemas de calidad en el identificador único (Requisito ETL)."""
        if id_col not in self._df.columns:
            return

        # Hallazgo: Nulos en el ID
        nulos_id = self._df[id_col].isna().sum()
        if nulos_id > 0:
            display(Markdown(f"> ⚠️ **Hallazgo ETL:** La columna `{id_col}` tiene **{nulos_id}** valores nulos."))

        # Hallazgo: Duplicados (Requisito: limpieza de duplicados)
        if not self._df[id_col].is_unique:
            dups = self._df[id_col].duplicated().sum()
            display(Markdown(f"> ⚠️ **Hallazgo ETL:** Se detectaron **{dups}** registros duplicados en `{id_col}`."))

    def _section(self, title: str, func = None, level: int = 2):
        display(Markdown(f"{'#' * level} {title}\n"))
        if func:
            func()
            display(Markdown("<br>"))

    def _fmt(self, df: pd.DataFrame):
        """
        Formatea la salida. Si falta 'jinja2', usa un fallback simple 
        para evitar el AttributeError.
        """
        try:
            return df.style.format(precision=self._float_precision)
        except Exception:
            # Fallback si jinja2 no está instalado
            return df.round(self._float_precision)

    # --- Métodos de Análisis Requeridos por la Rúbrica ---

    def dimensions(self):
        """Dimensiones del dataset."""
        display(pd.DataFrame({"Filas": [self._df.shape[0]], "Columnas": [self._df.shape[1]]}))

    def preview(self):
        """Vista previa para detectar formatos incorrectos (ej. científico)."""
        display(Markdown("> **Nota:** Revisa si las cédulas o IDs aparecen en formato científico (E+11)."))
        display(self._df.head(self._preview_rows))

    def data_types(self):
        """Análisis de nulos y tipos (Requisito: nulos, tipos, formato)."""
        info = pd.DataFrame({
            "Tipo de Dato": self._df.dtypes.astype(str),
            "No Nulos": self._df.notna().sum(),
            "Nulos": self._df.isna().sum(),
            "% Nulos": (self._df.isna().mean() * 100).round(2)
        })
        display(self._fmt(info))

    def descriptive_stats(self):
        """Estadísticas para columnas numéricas."""
        num = self._df.select_dtypes(include="number")
        if not num.empty:
            display(self._fmt(num.describe().T))
        else:
            display(Markdown("_No se detectaron columnas numéricas. Se requiere ETL para transformar salarios._"))

    def visual_distributions(self):
        """Distribución de variables clave (Evidencia para el reporte)."""
        sns.set_theme(style="whitegrid")
        if 'Puesto' in self._df.columns:
            plt.figure(figsize=(10, 5))
            self._df['Puesto'].value_counts().plot(kind='bar', color='skyblue', edgecolor='black')
            plt.title("Distribución de Candidatos por Puesto")
            plt.xticks(rotation=45, ha='right')
            plt.show()


    def run_full_analysis(self):
        """Ejecución secuencial del pipeline de análisis."""
        sections = [
            ("1. Dimensiones del Dataset", self.dimensions),
            ("2. Vista Previa (Análisis de Formatos)", self.preview),
            ("3. Calidad de Datos (Nulos y Tipos)", self.data_types),
            ("4. Distribución de Candidatos", self.visual_distributions),
        ]

        for title, func in sections:
            self._section(title, func)