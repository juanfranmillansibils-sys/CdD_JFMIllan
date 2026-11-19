# Clase 6 - Diseño de encuestas

## De la tabla al cuestionario (cafetería de la facultad)

**Encuesta a clientes de la cafetería**

Estamos estudiando cómo se usa la cafetería para proponer mejoras. Son 7
preguntas, unos 2 minutos. Es anónima y voluntaria; podés dejar preguntas sin
responder. Marcá una opción, salvo donde diga «todas las que correspondan».

**P1.** En los últimos 30 días, ¿cuántas veces compraste en la cafetería?
☐ Nunca ☐ 1 a 3 veces ☐ 4 a 8 veces ☐ Más de 8 veces
→ Si marcaste «Nunca», pasá a la P5.

**P2.** En los últimos 30 días, ¿qué compraste? *(todas las que correspondan)*
☐ Café u otra bebida caliente ☐ Comida ☐ Bebidas frías ☐ Otros

**P3.** En los últimos 30 días, ¿cómo calificarías la atención?
1 = Muy mala ☐ 2 ☐ 3 ☐ 4 ☐ 5 = Muy buena

**P4.** En los últimos 30 días, ¿cómo pagaste? *(todas las que correspondan)*
☐ Efectivo ☐ Tarjeta ☐ Transferencia

**P5.** ¿Sos estudiante de esta facultad este semestre? ☐ Sí ☐ No

**P6.** ¿Qué mejorarías de la cafetería? ________

**P7.** ¿Cuántos años cumplidos tenés? ____

Gracias por responder.

| Pregunta | Columnas | Cantidad |
|---|---|---|
| — | `id` | 1 |
| P1 | `frecuencia` | 1 |
| P2 | `prod_cafe`, `prod_comida`, `prod_frias`, `prod_otros` | 4 |
| P3 | `atencion` | 1 |
| P4 | `pago_efectivo`, `pago_tarjeta`, `pago_transferencia` | 3 |
| P5 | `estudiante` | 1 |
| P6 | `mejora` | 1 |
| P7 | `edad` | 1 |
| | **Total** | **13** |

Quien responde «Nunca» en P1 saltea P2 a P4: esas columnas quedan vacías por
diseño, no porque no quiso responder.

## Seis preguntas con problemas

| Pregunta | Problema | Reescrita | Columnas |
|---|---|---|---|
| ¿Está conforme con lo que gasta en comida y en transporte? | Pregunta dos cosas a la vez; sin período | Dos preguntas: «En los últimos 30 días, ¿qué tan conforme está con lo que gastó en comida?» (1 a 5) y lo mismo para transporte | 2 |
| ¿No le parece que gasta demasiado en salidas? | Induce la respuesta y está en negativo | «¿Cuánto gastó en salidas en los últimos 30 días?» $ ____ | 1 |
| ¿Cuánto gastó últimamente en ropa? | «Últimamente» no es un período | «¿Cuánto gastó en ropa en los últimos 30 días?» $ ____ | 1 |
| Gasto en transporte: $0-1.000 / $1.000-3.000 / $3.000-6.000 | Tramos que se superponen y no cubren todo | Nada / hasta $1.000 / $1.001-3.000 / $3.001-6.000 / más de $6.000, en los últimos 30 días | 1 |
| ¿Cómo paga? Efectivo / Tarjeta / Ambos / Transferencia | «Ambos» no dice cuáles; es selección múltiple | «¿Con qué medios pagó en los últimos 30 días?» (todas las que correspondan) | 3 |
| (Primera pregunta) ¿Cuál es el ingreso mensual exacto de su hogar? | Sensible, al principio y pide un monto exacto | Al final, por tramos y con «Prefiero no responder» | 1 |
