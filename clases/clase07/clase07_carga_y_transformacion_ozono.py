# Clase 7 - Carga y transformación: ozono, Montevideo (enero-abril 2024)
# Versión del script de la clase solo con el archivo de ozono.

# %%
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

CARPETA = Path(__file__).parent if "__file__" in globals() else Path.cwd()


def p95(x):
    return x.quantile(0.95)


# %% 1. Carga
ozono = pd.read_csv(CARPETA / "o3_01_2024_04_2024.csv", encoding="utf-8", parse_dates=["fecha"])
ozono_limpio = ozono.copy()   # con los NaN, para la sección 10

# %% 2. Perfilado: identificador, faltantes y duplicados
ozono.info()
print(ozono.head())
print(ozono["estacion"].unique())
print(ozono.isna().sum())

ozono_sinna = ozono.dropna(subset=["o3"]).copy()
print("Filas sin NaN:", len(ozono_sinna))
print("Filas repetidas:", ozono_sinna.duplicated().sum())
print("fecha + estacion repetidas:", ozono_sinna.duplicated(subset=["fecha", "estacion"]).sum())

# %% 3. Variables nuevas
ozono_new = ozono_sinna.assign(
    anio=ozono_sinna["fecha"].dt.year,
    mes=ozono_sinna["fecha"].dt.month,
    hora=ozono_sinna["fecha"].dt.hour,
)
print(ozono_new["mes"].value_counts().sort_index())

# %% 4. Promedio mensual
ozono_mes = (
    ozono_new.groupby("mes")
    .agg(o3_medio_mes=("o3", "mean"), n_registros_mes=("o3", "size"))
    .reset_index()
)
print(ozono_mes)

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(ozono_mes["mes"], ozono_mes["o3_medio_mes"], color="blue", linewidth=2)
ax.scatter(ozono_mes["mes"], ozono_mes["o3_medio_mes"], color="red", s=60, zorder=3)
ax.set(title="Concentración de Ozono en el ambiente, por mes, 2024", xlabel="Mes", ylabel="O3 (µg/m³)")
ax.set_xticks(ozono_mes["mes"])
ax.grid(alpha=0.3)
plt.tight_layout()
plt.show()

# %% 5. Por hora: media, máximo, p95 y cantidad de minutos
ozono_hora = (
    ozono_sinna.groupby(["estacion", pd.Grouper(key="fecha", freq="h")])["o3"]
    .agg(media="mean", maximo="max", p95=p95, n_min="size")
    .reset_index()
    .rename(columns={"fecha": "fecha_hora"})
)
print(ozono_hora.head())

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(ozono_hora["fecha_hora"], ozono_hora["media"], color="blue", linewidth=1)
ax.set(title="Concentración de Ozono en el ambiente, por hora, 2024", xlabel="Fecha", ylabel="O3 (µg/m³)")
ax.grid(alpha=0.3)
plt.tight_layout()
plt.show()

# %% 7. Por día
ozono_dia = (
    ozono_sinna.groupby(["estacion", pd.Grouper(key="fecha", freq="D")])["o3"]
    .agg(media="mean", maximo="max", p95=p95, n_min="size")
    .reset_index()
    .rename(columns={"fecha": "dia"})
)

estaciones = ozono_dia["estacion"].unique()
fig, axes = plt.subplots(len(estaciones), 1, figsize=(9, 3 * len(estaciones)), sharex=True, squeeze=False)
for ax, est in zip(axes[:, 0], estaciones):
    d = ozono_dia[ozono_dia["estacion"] == est]
    for col in ("media", "p95", "maximo"):
        ax.plot(d["dia"], d[col], label=col)
    ax.set_title(est)
    ax.set_ylabel("O3 (µg/m³)")
axes[0, 0].legend()
fig.suptitle("Media, p95 y máximo diario por estación")
plt.tight_layout()
plt.show()

# %% 8. Máximo diario de la media móvil de 8 horas
grilla = pd.date_range(ozono_hora["fecha_hora"].min(), ozono_hora["fecha_hora"].max(), freq="h")
indice = pd.MultiIndex.from_product(
    [sorted(ozono_hora["estacion"].unique()), grilla], names=["estacion", "fecha_hora"]
)
ozono_8h = ozono_hora.set_index(["estacion", "fecha_hora"])[["media"]].reindex(indice).reset_index()
print("Horas con dato:", len(ozono_hora), "| horas de la grilla:", len(ozono_8h))

ozono_8h["media_8h"] = ozono_8h.groupby("estacion")["media"].transform(
    lambda s: s.rolling(8, min_periods=8).mean()
)
max_8h_dia = (
    ozono_8h.assign(dia=ozono_8h["fecha_hora"].dt.floor("D"))
    .groupby(["estacion", "dia"])["media_8h"]
    .agg(max_8h="max", horas_validas="count")
    .reset_index()
)

fig, ax = plt.subplots(figsize=(9, 5))
for est, d in max_8h_dia.groupby("estacion"):
    ax.plot(d["dia"], d["max_8h"], label=est)
ax.axhline(100, linestyle="--", color="black")   # guía OMS 2021
ax.set(title="Máximo diario de la media móvil de 8 h", ylabel="O3 (µg/m³)")
ax.legend()
plt.tight_layout()
plt.show()

# %% 10. Faltantes
print(ozono_limpio.groupby("estacion")["o3"].agg(n_filas="size", n_na=lambda s: s.isna().sum()))

na_dia = (
    ozono_limpio.assign(es_na=ozono_limpio["o3"].isna())
    .groupby(["estacion", pd.Grouper(key="fecha", freq="D")])["es_na"]
    .mean()
    .reset_index()
)
fig, axes = plt.subplots(len(estaciones), 1, figsize=(9, 2.5 * len(estaciones)), sharex=True, squeeze=False)
for ax, est in zip(axes[:, 0], estaciones):
    d = na_dia[na_dia["estacion"] == est]
    ax.bar(d["fecha"], d["es_na"], color="grey", width=1)
    ax.set_title(est)
    ax.set_ylabel("Proporción de NaN")
plt.tight_layout()
plt.show()


# %% Rachas de NaN seguidos
def rachas_na(serie):
    es_na = serie.isna().to_numpy()
    id_racha = np.concatenate([[0], np.cumsum(es_na[1:] != es_na[:-1])])
    return (pd.DataFrame({"faltante": es_na, "id": id_racha})
            .groupby("id")
            .agg(faltante=("faltante", "first"), largo=("faltante", "size")))


partes = []
for est, grupo in ozono_limpio.sort_values(["estacion", "fecha"]).groupby("estacion"):
    r = rachas_na(grupo["o3"])
    r["estacion"] = est
    partes.append(r)
rachas = pd.concat(partes, ignore_index=True)

rachas = rachas[rachas["faltante"]].copy()
rachas["tipo"] = pd.cut(rachas["largo"], bins=[0, 1, 10, 60, 1440, np.inf],
                        labels=["1 min", "2-10 min", "11 min-1 h", "1 h-1 día", "> 1 día"])
print(rachas.groupby(["estacion", "tipo"], observed=True).size())

# %% Minutos que no están en el archivo
inicio = pd.Timestamp("2024-01-01 00:00")
fin = pd.Timestamp("2024-04-30 23:59")
esperados = int((fin - inicio) / pd.Timedelta(minutes=1)) + 1

cobertura = ozono_limpio.groupby("estacion").agg(
    presentes=("fecha", "nunique"), validos=("o3", "count")
)
cobertura["sin_fila"] = esperados - cobertura["presentes"]
cobertura["cobertura_%"] = (100 * cobertura["validos"] / esperados).round(1)
print(cobertura)
