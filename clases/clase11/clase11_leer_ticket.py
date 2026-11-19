# Clase 11 - Leer un ticket con IA (Gemini)
# La clave va en clave_gemini.txt, en esta carpeta (no se sube a GitHub).

# %%
import base64
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

CARPETA = Path(__file__).parent if "__file__" in globals() else Path.cwd()
FOTO = CARPETA / "ticket.jpg"
MODELO = "gemini-3.5-flash-lite"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO}:generateContent"

INSTRUCCION = """Transcribí los ítems de este ticket de compra.
Respondé solo con una tabla CSV con dos columnas: descripcion,monto
- monto con punto decimal y sin separador de miles
- no incluyas SUBTOTAL, IVA, TOTAL, EFECTIVO, CAMBIO ni TARJETA"""

# %% Foto a base64
imagen = base64.b64encode(FOTO.read_bytes()).decode("ascii")
print(len(FOTO.read_bytes()), "bytes ->", len(imagen), "caracteres en base64")

cuerpo = {
    "contents": [{"parts": [
        {"text": INSTRUCCION},
        {"inline_data": {"mime_type": "image/jpeg", "data": imagen}},
    ]}],
    "generationConfig": {"temperature": 0},
}

# %% Enviar
clave = (CARPETA / "clave_gemini.txt").read_text().strip()
respuesta = requests.post(URL, headers={"x-goog-api-key": clave}, json=cuerpo, timeout=120)
print(respuesta.status_code)

# %% Leer la respuesta
datos = respuesta.json()
texto = datos["candidates"][0]["content"]["parts"][0]["text"]
texto = texto.replace("```csv", "").replace("```", "").strip()
print(texto)
print("Tokens:", datos["usageMetadata"]["promptTokenCount"], "+",
      datos["usageMetadata"]["candidatesTokenCount"])

tabla = pd.read_csv(StringIO(texto))
tabla.to_csv(CARPETA / "ticket_gemini.csv", index=False)
print(tabla)

# %% Control: la suma tiene que dar el TOTAL del ticket ($ 50,00)
print("Suma:", tabla["monto"].sum())
