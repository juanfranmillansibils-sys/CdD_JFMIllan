# Clase 2 - Caja negra: bootstrap y datos sintéticos

# %%
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

CARPETA = Path(__file__).parent if "__file__" in globals() else Path.cwd()

# %% Datos de la caja
caja = pd.DataFrame({
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
caja["textura"] = caja["textura"].astype("category")
caja["rigidez"] = pd.Categorical(caja["rigidez"], ["blando", "medio", "rígido"], ordered=True)
caja["certeza_observador"] = pd.Categorical(caja["certeza_observador"], [1, 2, 3, 4, 5], ordered=True)
caja.info()

# %% Bootstrap (N = 100)
bootstrap = caja.sample(n=100, replace=True, random_state=42)
print(bootstrap["objeto_id"].value_counts().sort_index())

# %% Sintético con una normal (N = 500)
rng = np.random.default_rng(42)
pesos = rng.normal(caja["peso_estimado_g"].mean(), caja["peso_estimado_g"].std(), 500)
print("Pesos negativos:", (pesos < 1).sum())
pesos = np.clip(pesos, 1, None)

# %% Peso medio por rigidez
print(caja.groupby("rigidez", observed=True)["peso_estimado_g"].mean())
print(bootstrap.groupby("rigidez", observed=True)["peso_estimado_g"].mean())

# %% Gráfico
fig, axes = plt.subplots(3, 1, figsize=(8, 7), sharex=True)
bins = range(0, 260, 10)
axes[0].hist(caja["peso_estimado_g"], bins=bins, color="#2E86AB")
axes[0].set_title("Caja: 10 objetos medidos", loc="left")
axes[1].hist(bootstrap["peso_estimado_g"], bins=bins, color="#7B4B2A")
axes[1].set_title("Bootstrap: 100 filas remuestreadas", loc="left")
axes[2].hist(pesos, bins=bins, color="#D4A373")
axes[2].set_title("Sintético normal: 500 pesos inventados", loc="left")
axes[2].set_xlabel("Peso estimado (g)")
for ax in axes:
    ax.set_ylabel("Cantidad")
fig.suptitle("Peso estimado de los objetos de la caja negra, según cómo se generó el dato")
plt.tight_layout()
plt.savefig(CARPETA / "clase02_caja_negra_sinteticos.png", dpi=150)
plt.show()

# El bootstrap solo repite pesos reales. La normal inventa pesos negativos,
# que con el clip quedan en 1 g: un objeto que no está en la caja.
