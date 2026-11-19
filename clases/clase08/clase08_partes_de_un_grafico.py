# Clase 8 - Las partes de un gráfico: el de partida y el corregido

# %%
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

CARPETA = Path(__file__).parent if "__file__" in globals() else Path.cwd()

ozono = pd.read_csv(CARPETA / "o3_01_2024_04_2024.csv", parse_dates=["fecha"]).dropna(subset=["o3"])
ozono_mes = (ozono.assign(mes=ozono["fecha"].dt.month)
             .groupby("mes")["o3"].agg(o3_medio_mes="mean", n_registros="size")
             .reset_index())
print(ozono_mes.round(1))

# %% Gráfico de partida (el de la clase 7)
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(ozono_mes["mes"], ozono_mes["o3_medio_mes"], color="blue", linewidth=2)
ax.scatter(ozono_mes["mes"], ozono_mes["o3_medio_mes"], color="red", s=60, zorder=3)
ax.set(title="Concentración de Ozono en el ambiente, por mes, 2024", xlabel="Fecha", ylabel="Valores")
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(CARPETA / "clase08_partida.png", dpi=150)
plt.show()

# Problemas: "Valores" sin unidad, marcas 1.5 / 2.5 / 3.5, eje que no empieza
# en 0, dos colores que no significan nada y sin fuente.

# %% Gráfico corregido
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(ozono_mes["mes"], ozono_mes["o3_medio_mes"], color="#2E86AB", linewidth=2, marker="o")
for mes, valor in zip(ozono_mes["mes"], ozono_mes["o3_medio_mes"]):
    ax.annotate(f"{valor:.1f}", (mes, valor), xytext=(0, 9), textcoords="offset points", ha="center")
ax.set_xticks([1, 2, 3, 4], ["Enero", "Febrero", "Marzo", "Abril"])
ax.set_ylim(0, 40)
ax.set_title("Ozono en Montevideo: media mensual, enero a abril de 2024", loc="left")
ax.set_xlabel("Mes (2024)")
ax.set_ylabel("Ozono, O₃ (µg/m³)")
ax.grid(axis="y", alpha=0.3)
ax.spines[["top", "right"]].set_visible(False)
fig.text(0.01, 0.01, "Fuente: Intendencia de Montevideo. Promedio de las estaciones Colón y Curva de Maroñas.",
         fontsize=8, color="gray")
plt.tight_layout(rect=(0, 0.04, 1, 1))
plt.savefig(CARPETA / "clase08_corregida.png", dpi=150)
plt.show()
