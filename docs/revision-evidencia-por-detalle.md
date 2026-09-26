# Revisión de evidencia por detalle — v2 experimental

## Problema y alcance

En el piloto anterior el revisor llamó `supported` a una afirmación sobre cinco
clases A1–C1, aunque su propio motivo reconocía que las citas no mencionaban A1–C1.
El contrato v1 comprobaba forma, pero no podía evitar esa contradicción semántica.

La API `review_evidence(candidate, provider, review_version="v2")` incorpora
`agora/evidence-review/v2`. El valor predeterminado sigue siendo `v1`; los
consumidores deben optar explícitamente por v2. Los artefactos anteriores no se
reinterpretan ni modifican. El contrato v2 sólo modifica la revisión, no las
fuentes, sus IDs, el generador, la memoria ni la publicación.

## Qué aporta el modelo y qué calcula el código

El modelo devuelve idioma y una fila por afirmación con `part_id`, `claim_index`,
`relevance` y `details`. Cada detalle contiene:

- `text`: porción literal de la afirmación, sin paráfrasis.
- `support`: `supported`, `insufficient` o `contradicted`.
- `quote_indices`: índices de sus citas originales, no de otras afirmaciones.
- `reason`: motivo del juicio.

El modelo debe separar las proposiciones y sus calificativos materiales: sujeto,
población, fecha, cantidad, rango, condiciones, negación y certeza. Las porciones
van en orden y cubren el texto completo, incluida la puntuación. Sólo se permiten
huecos de espacio en blanco. Se admiten entre 1 y 32 detalles; una afirmación
simple no necesita una descomposición artificial.

El validador rechaza texto cambiado, huecos, reordenamientos, citas inexistentes,
filas faltantes y una etiqueta global `support` enviada por el modelo. Comprueba
que detalles `supported` y `contradicted` tengan al menos una referencia.

La etiqueta global se **calcula localmente**:

1. Algún detalle `contradicted` → afirmación `contradicted`.
2. Sin contradicción y algún detalle `insufficient` → `insufficient`.
3. Todos `supported` → `supported`.

La salida enriquecida conserva los detalles y añade `unsupported_details`
(índices de detalles insuficientes o contradichos), `detail_text_coverage`,
`aggregation`, `support` y la unión de referencias. El motivo global indica que
la etiqueta es derivada localmente. El `response.content` conserva la salida
original del proveedor, separada del resultado validado y enriquecido.

Un detalle no respaldado obliga a `needs_revision`. Todos respaldados siguen
produciendo, como máximo, `needs_adjudication`. Nada aprueba o modifica el
candidato ni lo admite en memoria.

## Lo que esto no demuestra

Cubrir todos los caracteres **no prueba** que se hayan separado todos los hechos,
ni que se hayan interpretado bien las citas. Un modelo puede agrupar demasiados
hechos, etiquetar mal un detalle o contradecirse dentro de su motivo. El código
no interpreta ese motivo ni demuestra entailment. También puede omitir una
condición relevante de la fuente al revisar una afirmación demasiado amplia.

Los detalles se leen en el contexto de la afirmación completa: un número o rango
que aparezca en una cita no acredita por sí solo sujeto, fecha o población.
`detail_text_coverage: complete` es cobertura del texto de la afirmación, nunca
cobertura del documento o ausencia de omisiones en la respuesta.

Se mantiene revisión probabilística y consultiva, con hash del candidato exacto,
sin reintentos, extracción desde Markdown, adjudicación independiente ni aprobación
automática. El llamador conserva la responsabilidad de verificar la fuente.

## Evaluación acotada

`experiments/evidence-details-v2/` congela código, entradas y cuatro casos antes
de ejecutar: regresión real conocida N2/1024 y tres controles sintéticos nuevos
(población, negación, condición). Cada control sintético contiene una afirmación
correcta y una incorrecta. Los resultados esperados quedan fuera del prompt.

No es una batería nueva de documentos reales ni una revisión independiente. El
productor del cambio también redacta las fixtures y realiza la autorrevisión.
Los resultados se registran en `docs/evaluacion-revision-detalles-01.md`.

## Ejecución acotada de varias afirmaciones

`docs/revision-acotada-por-afirmacion.md` documenta una API optativa que planifica
una revisión v2 por afirmación, reserva presupuesto y conserva faltantes/fallos.
El piloto conocido de seis afirmaciones y sus controles locales se registran en
`docs/evaluacion-revision-acotada-01.md`. La versión del revisor por detalles no
cambia y sus límites semánticos siguen vigentes.
