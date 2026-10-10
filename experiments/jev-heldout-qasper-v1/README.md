# Jev sobre dos documentos QASPER reservados para esta serie

Esta serie se congeló antes de las llamadas en `freeze.json`: dos preguntas de
documentos distintos del caso 03, seis respuestas preparadas (completa, omisión
y contradicción por documento), expectativas por eje y máximo de seis llamadas.
Las listas de respuesta coinciden entre los anotadores QASPER de cada pregunta.
La selección fue deliberada y el productor redactó las variantes; «reservados»
sólo significa que no se usaron en la prueba Jev anterior. No hay evaluación
humana independiente de las seis respuestas.

Cada petición llevó pregunta, requisitos, respuesta y fuente completa. No llevó
etiquetas esperadas, anotaciones QASPER ni nombre de variante. El transporte
registró un intento antes de cada envío, sin reintentos ni historia compartida.
No se modificó el producto ni se admitió memoria.

## Resultados

| Caso | Esperado respaldo/cobertura | Jev respaldo/cobertura |
| --- | --- | --- |
| Datos, completa | `supported` / `complete` | `supported` / `complete` |
| Datos, omisión | `supported` / `omitted` | `unsupported` / `omitted` |
| Datos, contradicción | `unsupported` / `omitted` | `unsupported` / `omitted` |
| Métodos, omisión | `supported` / `omitted` | `unsupported` / `omitted` |
| Métodos, contradicción | `unsupported` / `omitted` | `unsupported` / `omitted` |
| Métodos, completa | `supported` / `complete` | `supported` / `complete` |

El [auditor offline](audit.py) verificó seis intentos, seis respuestas, hashes de
petición y congelado, etiquetas y modelo reportado `jev-1.13.0`. La cobertura
coincidió en **6/6** y el respaldo en **4/6**; coincidieron ambos ejes en **4/6**.
La API reportó 37.540 tokens de entrada y 472 de salida en total; esto no
acredita coste facturado ni identidad efectiva del ejecutor.

La [autorrevisión](adjudication.json) cotejó los desacuerdos con las fuentes.
Las frases incompletas enumeran elementos verdaderos sin afirmar exclusividad.
Jev detectó que faltaban elementos, pero llamó `unsupported` a esas mismas
frases. Es una confusión entre respaldo de afirmaciones y cobertura de la
pregunta bajo los criterios fijados. No se cambiaron expectativas después del
resultado. El productor de controles también realizó este cotejo; las
anotaciones QASPER son referencia externa de elementos, no juicio ciego sobre
nuestro rubric.

**Decisión técnica propuesta:** conservar Jev como señal experimental de
cobertura en este tipo de listas y no usar esta configuración como puerta de
respaldo o admisión. La serie no prueba fiabilidad general, utilidad en CTIM
ni reparación de la generación B del caso 03. Se necesita adjudicación humana
independiente y una muestra más diversa antes de promoverla.

Reproducción sin red:

```sh
.venv/bin/python experiments/jev-heldout-qasper-v1/run.py --check
.venv/bin/python experiments/jev-heldout-qasper-v1/audit.py
```
