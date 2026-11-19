# Clase 7 - Máximo diario de la media móvil de 8 horas (ozono, ene-abr 2024)

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

CARPETA = Path(__file__).parent if "__file__" in globals() else Path.cwd()

# 1. Carga
ozono = pd.read_csv(CARPETA / "o3_01_2024_04_2024.csv", parse_dates=["fecha"])
ozono = ozono.dropna(subset=["o3"])

# 2. De minutos a horas
ozono_hora = (
    ozono.groupby(["estacion", pd.Grouper(key="fecha", freq="h")])["o3"]
    .mean()
    .rename("media")
    .reset_index()
    .rename(columns={"fecha": "fecha_hora"})
)

# 3. Grilla horaria completa (si faltan horas la media móvil sería incorrecta)
grilla = pd.date_range(ozono_hora["fecha_hora"].min(), ozono_hora["fecha_hora"].max(), freq="h")
indice = pd.MultiIndex.from_product(
    [sorted(ozono_hora["estacion"].unique()), grilla], names=["estacion", "fecha_hora"]
)
ozono_8h = ozono_hora.set_index(["estacion", "fecha_hora"])[["media"]].reindex(indice).reset_index()
ozono_8h["media_8h"] = ozono_8h.groupby("estacion")["media"].transform(
    lambda s: s.rolling(8, min_periods=8).mean()
)

# 4. Máximo diario
max_8h_dia = (
    ozono_8h.assign(dia=ozono_8h["fecha_hora"].dt.floor("D"))
    .groupby(["estacion", "dia"])["media_8h"]
    .max()
    .reset_index(name="max_8h")
)

# 5. Gráfico
fig, ax = plt.subplots(figsize=(10, 5.5))
for estacion, datos in max_8h_dia.groupby("estacion"):
    ax.plot(datos["dia"], datos["max_8h"], linewidth=1.6, label=estacion)
ax.axhline(100, linestyle="--", color="#555555", linewidth=1)
ax.text(max_8h_dia["dia"].min(), 102, "Guía OMS 2021: 100 µg/m³", fontsize=9, color="#555555")
ax.set_title("Máximo diario de la media móvil de 8 horas\nOzono en Montevideo, enero-abril 2024")
ax.set_xlabel("Fecha")
ax.set_ylabel("O₃ (µg/m³)")
ax.legend(title="Estación", frameon=False)
ax.grid(alpha=0.3)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig(CARPETA / "clase07_ozono_max_8h.png", dpi=200)
plt.show()

print(max_8h_dia.groupby("estacion")["max_8h"].agg(["mean", "max"]).round(1))
