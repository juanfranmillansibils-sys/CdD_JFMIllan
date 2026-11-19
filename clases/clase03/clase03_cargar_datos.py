# Clase 3 - Crear un dataset y volver a cargarlo

# %%
from pathlib import Path

import numpy as np
import pandas as pd

CARPETA = Path(__file__).parent if "__file__" in globals() else Path.cwd()

# %% Ejercicio 1: tipos
df = pd.DataFrame({
    "objeto_id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "textura": ["suave", "rugoso", "poroso", "suave", "rugoso",
                "suave", "poroso", "rugoso", "suave", "poroso"],
    "rigidez": ["blando", "rígido", "medio", "blando", "rígido",
                "rígido", "blando", "medio", "medio", "blando"],
    "num_aristas": [0, 8, 0, 4, 12, 0, 0, 6, 4, 0],
    "peso_estimado_g": [45.0, 120.5, 15.0, 85.0, 210.0,
                        35.0, 18.5, 95.0, 70.0, 22.0],
    "certeza_observador": [5, 4, 3, 5, 4, 2, 4, 3, 4, 3],
})
print(df.dtypes)

TIPO_RIGIDEZ = pd.CategoricalDtype(["blando", "medio", "rígido"], ordered=True)
TIPO_CERTEZA = pd.CategoricalDtype([1, 2, 3, 4, 5], ordered=True)
df["textura"] = df["textura"].astype("category")
df["rigidez"] = df["rigidez"].astype(TIPO_RIGIDEZ)
df["certeza_observador"] = df["certeza_observador"].astype(TIPO_CERTEZA)
print(df.dtypes)

# %% Ejercicio 2: validar
df_roto = df.copy()
df_roto.loc[0, "peso_estimado_g"] = -12.0
df_roto.loc[3, "num_aristas"] = -1
df_roto.loc[7, "objeto_id"] = 1


def validar(datos):
    problemas = []
    if (datos["peso_estimado_g"] <= 0).any():
        problemas.append("peso no positivo")
    certeza = pd.to_numeric(datos["certeza_observador"].astype("object"))
    if not certeza.between(1, 5).all():
        problemas.append("certeza fuera de 1-5")
    if ((datos["num_aristas"] < 0) | (datos["num_aristas"] % 1 != 0)).any():
        problemas.append("aristas negativas o no enteras")
    if datos["objeto_id"].duplicated().any():
        problemas.append("objeto_id repetido")
    return problemas


print(validar(df))
print(validar(df_roto))

# %% Ejercicio 3: diccionario de variables
diccionario = pd.DataFrame({
    "variable": ["objeto_id", "textura", "rigidez", "num_aristas",
                 "peso_estimado_g", "certeza_observador"],
    "tipo": ["identificador", "nominal", "ordinal", "discreta", "continua", "ordinal"],
    "unidad": ["-", "-", "-", "aristas", "gramos", "-"],
    "rango_valido": ["1 a 10, sin repetidos", "suave, rugoso, poroso",
                     "blando < medio < rígido", "entero >= 0", "> 0", "1 a 5"],
    "faltante": ["no admite", "vacío", "vacío", "vacío (nunca 0)", "vacío", "vacío"],
})
diccionario.to_csv(CARPETA / "diccionario_variables.csv", index=False)
print(diccionario)

# %% Ejercicio 4: ida y vuelta
df.to_csv(CARPETA / "caja_negra_mio.csv")
leido = pd.read_csv(CARPETA / "caja_negra_mio.csv")
print(leido.columns.tolist())   # aparece "Unnamed: 0" (el índice)
print(leido["rigidez"].dtype)   # rigidez vuelve como texto

df.to_csv(CARPETA / "caja_negra_mio.csv", index=False)
leido = pd.read_csv(CARPETA / "caja_negra_mio.csv",
                    dtype={"textura": "category", "rigidez": TIPO_RIGIDEZ,
                           "certeza_observador": TIPO_CERTEZA})
print((leido.dtypes == df.dtypes).all())

df.to_parquet(CARPETA / "caja_negra_mio.parquet")
print(pd.read_parquet(CARPETA / "caja_negra_mio.parquet").dtypes)

# %% Ejercicio 5: el CSV de Excel
try:
    pd.read_csv(CARPETA / "caja_negra_excel.csv")
except Exception as e:
    print(type(e).__name__, e)

excel = pd.read_csv(CARPETA / "caja_negra_excel.csv", sep=";", decimal=",", encoding="latin-1")
print(excel.dtypes)
print(excel["peso_estimado_g"].mean())

# %% Ejercicio 6: rutas
print(Path.cwd())
base = pd.read_csv(CARPETA / "caja_negra.csv")
print(base.shape)

# %% Ejercicio 7: faltantes disfrazados
ingenuo = pd.read_csv(CARPETA / "caja_negra_faltantes.csv")
print(ingenuo.isna().sum())
print("Media ingenua:", ingenuo["peso_estimado_g"].mean())

declarado = pd.read_csv(CARPETA / "caja_negra_faltantes.csv", na_values=["-99", "s/d"])
print(declarado.isna().sum())
print("Media declarada:", declarado["peso_estimado_g"].mean())

# %% Ejercicio 8: archivo del equipo vecino
vecino = pd.read_csv(CARPETA / "equipo_vecino.csv")
print(vecino.dtypes)
print(vecino.head())

vecino = pd.read_csv(CARPETA / "equipo_vecino.csv", thousands=".")
vecino.columns = vecino.columns.str.strip().str.lower().str.replace(" ", "_")
vecino["fecha_operacion"] = pd.to_datetime(vecino["fecha_operacion"], format="%d/%m/%Y")
vecino["sucursal"] = vecino["sucursal"].str.strip().astype("category")
print(vecino.dtypes)
print(vecino.describe())

# %% Desafío: datos experimentales (valores inventados)
experimento = pd.DataFrame({
    "codigo": [f"P{i:02d}" for i in range(1, 11)],
    "rol": ["dictador", "receptor"] * 5,
    "momento": pd.to_datetime(["2026-09-24 10:05"] * 2 + ["2026-09-24 10:12"] * 2
                              + ["2026-09-24 10:20"] * 2 + ["2026-09-24 10:31"] * 2
                              + ["2026-09-24 10:40"] * 2),
    "generosidad": [4, 3, 5, 2, 3, 4, 2, 5, 4, 3],
    "monto_entregado": [40, np.nan, 50, np.nan, 20, np.nan, 10, np.nan, 30, np.nan],
})
experimento["rol"] = experimento["rol"].astype("category")
experimento.to_csv(CARPETA / "experimento_minimo.csv", index=False)

releido = pd.read_csv(CARPETA / "experimento_minimo.csv")
print(releido.dtypes)   # rol y momento vuelven como texto
