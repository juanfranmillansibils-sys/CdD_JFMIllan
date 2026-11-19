# Clase 5 - Del seudocódigo al código: filtrar temperaturas mayores a 20

# 1. Crear el vector
temperaturas = [18, 22, 15, 25, 30]

# 2. Filtrar, siguiendo el seudocódigo paso a paso
vector_filtrado = []
for temp in temperaturas:
    if temp > 20:
        vector_filtrado.append(temp)
print(vector_filtrado)

# Lo mismo en una línea
print([temp for temp in temperaturas if temp > 20])
