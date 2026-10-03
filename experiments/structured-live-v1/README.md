# Generación real con plan estructurado — 2026-10-03

## Resultado

Una llamada GLM 5.3 Flash produjo una candidata parcial con ocho afirmaciones,
once referencias exactas y tres faltantes explícitos. La inspección del productor
acepta el resultado **para este caso conocido**: recogida humana y predictor se
mantienen separados; la escala 1–5, clase negativa 1 y exclusión de 2 se conservan;
el conjunto positivo sigue desconocido por `INLINEFORM0`, sin deducción por descarte.
Los umbrales y fórmulas ausentes se mantienen en `missing` y la vista los muestra.

`execution_status: complete` significa que pasó el contrato estructural.
`answer_status: candidate_requires_expansion` y `semantic_support: not_verified`
permanecen intactos. La evaluación del productor no es adjudicación independiente,
aceptación del sistema, admisión a memoria ni prueba de completitud documental.

## Presupuesto y evidencia

- Una llamada, sin reintentos; modelo solicitado y reportado: `glm-5.3-flash`.
- 11.990 bytes entregados de 45.571, presupuesto de lectura 12.000.
- Máximo de salida: 8.192 tokens; timeout 90 segundos.
- Uso reportado: 3.767 tokens de entrada + 4.828 de salida = **8.595**.
- De la salida, 3.964 tokens se reportaron como razonamiento; no se conserva su texto.
- Duración observada: **87,30 segundos**, poco margen respecto del timeout.
- 8.876 bytes de citas contando repeticiones, dentro del presupuesto del contrato.

No es ahorro neto demostrado: hubo preparación y ensayos anteriores, y sólo una
medición de tiempo. No se midieron dólares ni se comparó de nuevo contra MemOS.
No se modificó código del producto en esta ronda.

La selección se hizo con la pregunta inglesa fijada en el plan; la generación
recibió la pregunta española explícita de la reparación anterior. Ambas están en
freeze.json. El plan estructurado preserva la selección léxica y agrega estructura;
no equivale al selector estructural aislado de ~6 KB. El contrato de generación
es `claim-evidence-query/v2`, con máximo de 16 afirmaciones por aspecto: no debe
atribuirse a este recorrido el máximo de seis del consumidor passage v0.4.

## Verificación

Se comprobaron el hash del plan y de la fuente, offsets UTF-8 de todas las citas,
conservación de alcance parcial, diagnóstico vacío y hashes de implementación sin
cambios durante la ejecución. La inspección semántica contrastó las ocho afirmaciones
con sus pasajes, incluida la separación entre entrenamiento y despliegue.
No se llamó a Jev ni a un segundo revisor.

- `freeze.json`: parámetros y criterios fijados antes de ejecutar.
- `receipt.json`: respuesta original, modelo/usage, citas, estados y hashes.
- `view.json`: presentación de afirmaciones y faltantes.
- `execution.json`: resultado del comando y tiempo observado.
- `assessment.json`: evaluación del productor, separada del estado del producto.

Se omiten fuente íntegra y prompt duplicado; el plan se reconstruye con el ejecutor
`../structured-handoff-v1/run.py` y dataset fijado por hash. El receipt conserva hash
del prompt. Los rechazos y costes anteriores permanecen en sus expedientes.

## Cierre y continuación

Queda demostrado el recorrido de este caso: selección estructurada reproducible,
entrega por IDs, generación real y faltantes visibles. No exige más iteraciones
sobre la misma pregunta para afirmar ese resultado acotado. Antes de generalizar,
retomar el fallo reservado streaming/texto completo de section-comparison-v1 y
someter resultados a revisión separada. Conservar casos con etiquetas discrepantes
y tablas ausentes como estratos distintos; no usarlos para aparentar una mejora.
