# Agrupación de hechos con evidencia compartida

**Resultado: candidato original válido sin reparación y cuatro requisitos cubiertos.**
Una ejecución favorable de desarrollo; no demuestra fiabilidad general.

## Qué cambió

Mismo documento QASPER `1911.10401`, pregunta, rúbrica y lectura completa de 34.003
bytes. Se conservó el tamaño original de unidad (hasta 4.096 bytes) y los límites:
12 usos de citas, 12.000 bytes por parte, generación de hasta 4.096 tokens, revisión
con 2.048, timeout 90 segundos y sin reintentos.

Se añadió al prompt de generación una instrucción: agrupar hechos relacionados
cuando comparten respaldo y elegir el conjunto suficiente más pequeño de IDs,
sin omitir información requerida ni matices materiales. No se mostró la rúbrica
al generador. El texto exacto queda congelado en `freeze.json`; el request efectivo
se guarda y fija por hash. El campo `prompt` del candidato conserva la base de
`query_evidence`; `prompt_addendum` y `effective_request_sha256` identifican la
instrucción adicional realmente enviada. No se modificó código de producto.

## Resultado observado

- Cuatro afirmaciones, cinco usos de referencias: **6.824 bytes** resueltos.
- Cuatro unidades únicas: 5.097 bytes. El límite sigue contando cada uso.
- Candidato original `execution_status: complete`; ninguna referencia retirada.
- CLI `review-rubric`: R1–R4 `covered`, coincidentes con la expectativa previa.
- Se conservan `requires_review` y completitud de rúbrica no establecida.

El modelo mantiene su respuesta como `partial` por no establecer divisiones entre
entrenamiento/prueba. Esto no contradice cubrir los cuatro requisitos: la rúbrica
pide identificar datasets, no adjudica esa declaración de ausencia. Tampoco se
realizó una evaluación independiente de fidelidad de cada afirmación.

La referencia anterior sin instrucción de agrupación produjo 15.062 bytes y quedó
rechazada. La diferencia descriptiva es favorable, pero una sola ejecución por
condición no estima causalidad, estabilidad ni tasa de éxito. No se mezclan el
candidato reparado anterior y este candidato intacto.

## Verificación y coste

`python3 experiments/citation-grouping-v1/verify.py` reproduce exactamente el
candidato a partir de la respuesta guardada, verifica el prompt efectivo, hashes,
41 unidades y los resultados de la revisión, sin red. La auditoría documental no
encontró enlaces o módulos faltantes. Sin cambios de producto; suite general no
repetida.

Esta condición: dos llamadas, 14.233 tokens, 26,425 segundos acumulados de cliente.
Incluyendo el [intento de unidades pequeñas](../citation-units-1000-v1/README.md):
tres llamadas, 27.660 tokens y 90,521 segundos. Coste monetario no informado.
Se leyó toda la fuente: no se afirma ahorro de lectura. Fuente conocida y mismo
proveedor para generación/revisión; expectativas del productor, no adjudicación
independiente. No se cambian los defaults ni se admite memoria.

## Próximo paso

Contrastar esta instrucción en dos documentos reservados antes de promoverla a
opción de producto. Congelar casos y expectativas; medir validez sin reparación,
omisiones y respaldo de afirmaciones, además de tokens y tiempo. Si mantiene esa
calidad, usarla en la comparación de lectura selectiva frente a completa. No
repetir este caso hasta obtener una tasa favorable ni eliminar el intento fallido.
