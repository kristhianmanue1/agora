# Evaluación de revisión acotada — 01

## Objetivo y cambio

Revisar las seis afirmaciones de la respuesta QASPER N2/1024 que agotó el límite
de salida cuando se envió completa al revisor v2. La cola realiza una llamada
por afirmación y conserva el vínculo con su posición y hash originales. Una
unidad fallida o no revisada impide declarar completa la revisión conjunta.

El cambio es optativo, mediante API; no activa revisiones implícitas en las CLI
existentes, no cambia generación, no admite memoria y no publica respuestas.
Contrato y uso: `docs/revision-acotada-por-afirmacion.md`.

## Protocolo

`experiments/review-batch-v1/runs/glm-01` congela código, candidato completo,
fuente, transporte, runner y protocolo antes de ejecutar. GLM-5.3-flash,
temperatura 0, máximo seis llamadas, 8192 tokens de salida por llamada y 49152
reservados para toda la tanda. Tope acumulado de prompts: 120000 bytes UTF-8.
Tiempo de tanda: 1200 s; timeout por llamada: 180 s o el tiempo restante si es
menor. El transporte usa timeout HTTP y límite duro del proceso hijo.

Esos límites no son un presupuesto exacto de tokens de entrada+salida ni de
moneda. Los tokens totales reportados se contabilizan aparte. No se devuelven las
reservas de salida tras llamadas baratas. Los prompts contienen únicamente la
pregunta/aspectos y cada afirmación con sus propias citas y faltantes; las
expectativas del protocolo no se envían. Se guarda contenido final y uso, sin
contenido de razonamiento.

Criterios fijados antes de ejecutar:

1. Seis trabajos con dictámenes válidos y cobertura de cola completa.
2. Afirmación original 2: `insufficient` por A1–C1 sin evidencia en sus citas.
3. Afirmación original 5: `extra`, por regresión lineal frente a pregunta de
   clasificadores.

No se reintenta ni se repara JSON. Se conservan cada request/receipt y snapshots
progresivos nuevos. El candidato y sus citas se mantienen intactos; los índices
locales 0 se relacionan con los originales mediante el registro de cada trabajo.

## Autorrevisión adversarial y límites

- Todos los dictámenes se vinculan a una copia inicial; una modificación del
  objeto de entrada durante ejecución no cambia lo que se revisa silenciosamente.
- Un rechazo estructural no borra la unidad: permanece `failed`, incluso si las
  demás terminan. El fallo de transporte o uso desconocido detiene nuevos envíos.
- Una parte sin afirmaciones requiere revisar el idioma de sus `missing`, pero
  esto no valida que falte esa información en la fuente.
- La cobertura completa de la cola no es cobertura semántica del documento.
  El revisor aún puede etiquetar mal detalles y los modelos no son árbitros.
- Se conserva una recomendación provisional, nunca aprobación: como máximo,
  `needs_adjudication`; si hay observaciones, `needs_revision`.
- El proveedor debe respetar el máximo solicitado de salida. El transporte del
  piloto impone tiempo por proceso; la API no puede interrumpir un callback
  Python arbitrario que no devuelve control.
- La muestra es un caso conocido de desarrollo. No es corpus nuevo ni
  adjudicación independiente. No basta para afirmar ahorro, precisión general
  ni estabilidad bajo repetición.

## Pruebas locales

**266 pruebas** pasaron. Cubren presupuestos antes del envío, ausencia de
reintentos, uso desconocido, timeout, rechazo intermedio/final, identidad/índices,
partes sin afirmaciones, snapshots aislados y no promoción a aprobación.
Se prueban también cobertura completa con ejecución incompleta por uso desconocido
o llegada tardía, y mutación del candidato externo durante la revisión.

## Resultado real

**Seis de seis trabajos completos**, sin reintentos ni truncamientos. La cola
terminó con `execution_status: complete`, `review_coverage: complete` y
`recommendation: needs_revision`. No hubo uso desconocido ni motivo de parada.

| Afirmación original (índice 0-based) | Dictamen global | Pertinencia |
|---|---|---|
| 0: clasificadores WEKA | supported | relevant |
| 1: modelos documentales y líneas base | supported | relevant |
| 2: modelos de oración, cinco clases A1–C1 | insufficient | relevant |
| 3: clasificación de dificultad y resultados | supported | relevant |
| 4: selección de regresión logística | supported | relevant |
| 5: regresión lineal | supported | extra |

La afirmación 2 separó otra vez `(niveles A1-C1).` como detalle insuficiente.
El agregado local preservó ese juicio. El contenido sobre regresión lineal quedó
respaldado pero fuera de la pregunta de clasificadores. Estos dos hallazgos cumplen
las expectativas predefinidas; los restantes dictámenes son evaluaciones del modelo,
no adjudicación independiente de todos los detalles.

**Uso total reportado: 18830 tokens.** Reservas de salida: 49152 tokens; prompts:
19999 bytes UTF-8. Las reservas son límites solicitados, no consumo real. Tiempo
sumado de llamadas: 245.316 s; tanda completa: 245.375 s. Preparación, pruebas y
autorrevisión quedan fuera de ese tiempo. No se estima coste monetario.

La revisión conjunta anterior consumió 9813 tokens y terminó sin contenido por
límite de salida. La nueva tanda consumió más y sí produjo los seis dictámenes:
no se afirma ahorro ni equivalencia de condiciones, y el fallo anterior no se borra.
El proveedor reportó `glm-5.3-flash`; ello no es verificación independiente del modelo.

## Auditoría y controles sin red

`experiments/review-batch-v1/audit.py` verificó hashes congelados y código actual,
candidato, citas contra bytes originales, proyecciones, requests/receipts y
reproducción local completa de cada resultado. También reutilizó los receipts
para cuatro simulaciones locales, sin llamadas nuevas:

| Simulación | Revisados | Estado global |
|---|---:|---|
| Tope de dos llamadas | 2/6 | incomplete / call_budget_exhausted |
| Reserva total de salida para una llamada | 1/6 | incomplete / output_budget_exhausted |
| Tercera respuesta marcada truncada | 5/6 | incomplete; trabajo 2 fallido |
| Fallo de transporte en segunda llamada | 1/6 | incomplete; nuevas llamadas detenidas |

En las cuatro simulaciones, `recommendation` permaneció `review_incomplete`.
Los tokens de sus receipts son contabilidad reproducida, no consumo nuevo del API.
Las simulaciones no prueban aislamiento o disponibilidad del proveedor real.

Los snapshots intermedios permanecieron incompletos; sólo el resultado final con
los seis trabajos pasó a cobertura completa. Se conservan errores, proyecciones
y dictámenes individuales para inspección; no hay reanudación automática.

## Cierre y siguiente paso

Incremento implementado y piloto acotado completado. Sin commit, push, publicación,
escritura AN-KLA ni cambio de contexto canónico. El árbol conserva cambios anteriores.
Los datos y ejecuciones del experimento siguen gitignored: los scripts y este
informe no sustituyen conservar el expediente local completo para reproducirlo.

Siguiente paso recomendado: una muestra real nueva, con criterios fijados antes
de ejecutar, para comprobar falsos positivos, falsos rechazos y coste de la cola.
Después podrá decidirse su incorporación explícita al flujo de consulta. La cola
ya puede invocarse mediante API; mantenerla optativa y exigir adjudicación evita
convertir cobertura de trabajos en aprobación semántica automática.
