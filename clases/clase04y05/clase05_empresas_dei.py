# Clase 5 - Carga de datos: Directorio de Empresas Industriales

# %%
from pathlib import Path

import pandas as pd

CARPETA = Path(__file__).parent if "__file__" in globals() else Path.cwd()

df = pd.read_csv(CARPETA / "empresasdei_20230330.csv")
df.info()
print(df.head())

# %% Identificador, faltantes y duplicados
print("Dimensiones:", df.shape)
print("RUT distintos:", df["RUT"].nunique(), "de", len(df))
print(df.isna().sum())
print("Celdas con S/D:", (df == "S/D").sum().sum())
print("Filas duplicadas:", df.duplicated().sum())

# %% Limpieza: caracteres invisibles y S/D
print("Departamentos antes:", df["Departamento Estab. Principal"].nunique())

for col in df.select_dtypes(include=["object", "string"]).columns:
    df[col] = df[col].str.replace(r"[\x00-\x1f\x7f-\x9f]", "", regex=True).str.strip()
df = df.replace("S/D", pd.NA)

print("Departamentos después:", df["Departamento Estab. Principal"].nunique())

# %% Empresas por departamento y actividad
print(df["Departamento Estab. Principal"].value_counts(dropna=False))
print(df["Descripción Código CIIU principal"].value_counts().head(10))
