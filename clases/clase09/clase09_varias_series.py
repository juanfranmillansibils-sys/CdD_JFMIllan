# Clase 9 - Las partes de un gráfico: más de una serie
# Ozono (ene-abr) por estación, y NO2 con PM2.5 (jun-ago) en Curva de Maroñas.

# %%
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

CARPETA = Path(__file__).parent if "__file__" in globals() else Path.cwd()
ESTACION = "Curva de Maroñas"
FRANJAS = ["madrugada", "mañana", "tarde", "noche"]
COLORES = {"madrugada": "#0072B2", "mañana": "#E69F00", "tarde": "#009E73", "noche": "#CC79A7"}
MARCAS_PM = [3, 5, 10, 20, 50, 100, 200, 400]
FUENTE = "Fuente: Intendencia de Montevideo, Catálogo de Datos Abiertos."


def guardar(fig, nombre):
    fig.text(0.01, 0.005, FUENTE, fontsize=8, color="gray")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(CARPETA / f"{nombre}.png", dpi=150)
    plt.show()


def escala_log(ax):
    ax.set_xscale("log")
    ax.set_xticks(MARCAS_PM, [str(m) for m in MARCAS_PM])
    ax.minorticks_off()


# %% Datos
ozono = pd.read_csv(CARPETA / "o3_01_2024_04_2024.csv", parse_dates=["fecha"]).dropna(subset=["o3"])
o3_dia = ozono.groupby(["estacion", pd.Grouper(key="fecha", freq="D")])["o3"].mean().unstack("estacion")
o3_dia = o3_dia.asfreq("D")   # días sin dato = NaN, así la línea se corta


def por_hora(archivo, col):
    d = pd.read_csv(CARPETA / archivo, parse_dates=["fecha"])
    return d[d["estacion"] == ESTACION].set_index("fecha")[col].resample("h").mean()


aire = pd.DataFrame({"no2": por_hora("no2_05_2024_08_2024.csv", "no2"),
                     "pm2_5": por_hora("pm_2_5_05_2024_08_2024.csv", "pm2_5")})
ambos = aire.dropna().copy()
ambos["franja"] = pd.cut(ambos.index.hour, bins=[-1, 5, 11, 17, 23], labels=FRANJAS)
print("Horas con NO2 y PM2.5:", len(ambos))

# %% 1. Un color por grupo
fig, ax = plt.subplots(figsize=(10, 4.5))
for est in o3_dia.columns:
    ax.plot(o3_dia.index, o3_dia[est], label=est)
ax.set_title("Ozono: media diaria por estación, enero a abril de 2024", loc="left")
ax.set_ylabel("O₃ (µg/m³)")
ax.set_ylim(0, None)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
ax.legend(title="Estación", frameon=False)
guardar(fig, "clase09_1_color_por_grupo")

# %% 2. Apilados: dos contaminantes, mismo eje horizontal
diario = aire.resample("D").mean()
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
ax1.plot(diario.index, diario["no2"], color="#7B4B2A")
ax1.set_ylabel("NO₂ (µg/m³)")
ax1.set_title(f"NO₂ y PM2.5: media diaria en {ESTACION}, mayo a agosto de 2024", loc="left")
ax2.plot(diario.index, diario["pm2_5"], color="#D4A373")
ax2.set_ylabel("PM2.5 (µg/m³)")
ax2.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
guardar(fig, "clase09_2_apilados")

# %% 3. Dispersión: escala lineal y logarítmica
r = ambos["no2"].corr(ambos["pm2_5"])
fig, (ax_lin, ax_log) = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
for ax in (ax_lin, ax_log):
    ax.scatter(ambos["pm2_5"], ambos["no2"], s=6, alpha=0.3)
    ax.set_xlabel("PM2.5 (µg/m³)")
ax_lin.set_ylabel("NO₂ (µg/m³)")
ax_lin.set_title("Escala lineal", loc="left")
escala_log(ax_log)
ax_log.set_title("Escala logarítmica", loc="left")
fig.suptitle(f"NO₂ y PM2.5 por hora en {ESTACION}, jun-ago 2024 (r = {r:.2f})")
guardar(fig, "clase09_3_dispersion_y_escala")

# %% 4. Color discreto por franja del día
fig, ax = plt.subplots(figsize=(8, 5.5))
for franja, d in ambos.groupby("franja", observed=True):
    ax.scatter(d["pm2_5"], d["no2"], s=8, alpha=0.5, color=COLORES[franja], label=franja)
escala_log(ax)
ax.set_xlabel("PM2.5 (µg/m³)")
ax.set_ylabel("NO₂ (µg/m³)")
ax.set_title(f"NO₂ y PM2.5 por franja del día, {ESTACION}", loc="left")
ax.legend(title="Franja", frameon=False)
guardar(fig, "clase09_4_color_por_franja")

# %% 5. Paneles: un panel por franja
fig, axes = plt.subplots(2, 2, figsize=(10, 8), sharex=True, sharey=True)
for ax, (franja, d) in zip(axes.flat, ambos.groupby("franja", observed=True)):
    ax.scatter(d["pm2_5"], d["no2"], s=8, alpha=0.4, color=COLORES[franja])
    ax.set_title(f"{franja}  r = {d['no2'].corr(d['pm2_5']):.2f}", loc="left")
escala_log(axes[0, 0])
for ax in axes[1, :]:
    ax.set_xlabel("PM2.5 (µg/m³)")
for ax in axes[:, 0]:
    ax.set_ylabel("NO₂ (µg/m³)")
fig.suptitle(f"NO₂ y PM2.5 por franja del día, {ESTACION}, jun-ago 2024")
guardar(fig, "clase09_5_paneles_por_franja")

# %% 6. Cajas por franja
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
for ax, col, nombre in [(axes[0], "no2", "NO₂"), (axes[1], "pm2_5", "PM2.5")]:
    ax.boxplot([ambos.loc[ambos["franja"] == f, col] for f in FRANJAS], tick_labels=FRANJAS,
               flierprops={"markersize": 2, "alpha": 0.3})
    ax.set_title(nombre, loc="left")
    ax.set_ylabel(f"{nombre} (µg/m³)")
axes[1].set_yscale("log")
fig.suptitle(f"Distribución por franja del día, {ESTACION}, jun-ago 2024")
guardar(fig, "clase09_6_cajas_por_franja")

print(ambos.groupby("franja", observed=True)[["no2", "pm2_5"]].median())

# El PM2.5 es más alto de noche; el NO2 sube de mañana y de noche, como el
# tránsito. Dentro de cada franja la relación entre los dos se mantiene.
