# Revisión acotada por afirmación

## Alcance

`agora.review_batch.review_candidate(candidate, provider, budget=ReviewBudget())`
planifica y ejecuta revisiones v2 de una afirmación por llamada. Produce
`agora/bounded-evidence-review/v1`. No cambia generación ni activa revisiones
implícitas en la CLI existente. No aprueba candidatos, publica ni escribe memoria.

La respuesta original se copia al comenzar y se identifica por SHA-256. Cada
trabajo conserva `part_id`, `claim_index` original y hash de su proyección. El
revisor recibe una afirmación con índice local 0, su texto/citas intactos, la
pregunta/aspectos originales y los elementos `missing` de esa parte. La proyección
es una vista para revisión, no una respuesta nueva ni evidencia adicional. No se
utiliza evidencia de otras afirmaciones para rellenar la seleccionada.

Una parte sin afirmaciones pero con `missing` crea un trabajo de idioma; no
certifica que el dato falte realmente en la fuente. Cada parte debe tener ID
único. El llamador conserva la responsabilidad de verificar integridad de fuentes;
la cola recibe candidatos estructuralmente aceptados y no reabre los documentos.

## Presupuesto

Los valores predeterminados son:

| Límite | Valor |
|---|---:|
| Llamadas máximas | 6 |
| Tokens máximos de salida por llamada | 8192 |
| Tokens de salida reservados para toda la tanda | 49152 |
| Bytes UTF-8 de contenido de prompts acumulados | 120000 |
| Tiempo de la tanda | 1200 s |
| Timeout máximo solicitado por llamada | 180 s |

Antes de llamar, se reserva el máximo completo de salida; no se devuelve la
reserva si el modelo usa menos. Se suman los bytes UTF-8 de system+user, excluyendo
envoltura HTTP. Los tokens totales reportados por el proveedor se contabilizan
aparte. No hay conversión supuesta bytes→tokens ni presupuesto monetario exacto.
El límite de salida se solicita al proveedor, cuya aplicación depende del
transporte y servicio. El transporte recibe los límites explícitamente y debe
respetarlos. El piloto agrega un timeout duro del proceso hijo, además del HTTP.
Un callback Python que no devuelve control no puede ser interrumpido por la cola.

Se comprueban los límites antes de cada llamada y el plazo al regresar. Si falta
contabilidad de uso o falla el transporte, se detienen nuevas llamadas. Un rechazo
estructural con uso conocido queda como fallo y permite revisar las siguientes
unidades. No se reintenta, se repara salida ni se reanuda automáticamente.

## Cobertura y resultado

Cada trabajo queda `reviewed`, `failed` o `not_reviewed`. `review_coverage` sólo
es `complete` si todos tienen un dictamen válido. Si existe algún trabajo faltante,
fallido, un plazo incumplido o contabilidad desconocida, `execution_status` queda
`incomplete` y la recomendación es `review_incomplete`.

Cuando todos se revisan sin problema de control:

- Algún dictamen pide corrección → `needs_revision`.
- Todos favorables → `needs_adjudication`, nunca aprobación.

Si todos se revisaron pero falta uso reportado, puede haber cobertura completa y
ejecución incompleta: son propiedades distintas. `semantic_coverage` permanece
`not_verified`: la cobertura de la cola no prueba exhaustividad de la respuesta
ni calidad del juicio semántico. `findings` conserva observaciones útiles incluso
cuando el conjunto es incompleto.

`on_result` recibe una copia separada tras cada unidad y al terminar. El piloto
guarda snapshots nuevos y cada request/receipt; no sobrescribe intentos anteriores.
Un snapshot parcial sirve para inspección, no autoriza repetir llamadas cuyo
resultado se desconoce. La reanudación gobernada no está implementada.

## Verificación

Pruebas: límites antes del despacho, cero llamadas cuando no cabe el prompt,
reserva sin devolución, interrupción por uso desconocido/timeout, fallo intermedio
y final, índices originales, partes sin afirmaciones, aislamiento de snapshots y
no aprobación. Experimento: `experiments/review-batch-v1/` sobre la respuesta real
conocida de seis afirmaciones. Su auditoría reproduce los dictámenes guardados y
simula fallos sin nuevas llamadas. Resultados en `docs/evaluacion-revision-acotada-01.md`.
