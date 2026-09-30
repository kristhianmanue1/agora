# CLI de suficiencia: contraste de omisiones en una fuente de 6.474 palabras

## Resultado

Dos candidatos GLM reales conservados de QASPER 1803.08419, materializados por replay del contrato de evidencia; no se regeneraron. Fuente completa suministrada: **41.578 bytes y 6.474 palabras**. Es la mayor fuente entre los candidatos utilizables de este lote, no un ensayo a escala del manual de 188 páginas.

La CLI review-coverage ejecutó una llamada por candidato con la configuración congelada. Cuotas iguales obtuvo omitted; redistribución obtuvo complete. Ambas coinciden con las expectativas fijadas antes de estas llamadas y conservan disposition=requires_review. No hay aceptación ni admisión automática.

## Contraste con la fuente

La pregunta pide limitaciones de las métricas cuantitativas para evaluar diálogo. La primera respuesta explica la débil correlación con juicios humanos, pero omite dos limitaciones que aparecen cerca del final del documento:

- BLEU necesita muchas respuestas de referencia para cubrir la diversidad de respuestas válidas: fragmento localizable en bytes 39.500–39.577.
- Promedios de embeddings resultan insuficientes para representar la composicionalidad de una oración: fragmento localizable en bytes 39.829–39.896.

Esos textos no estaban en los pasajes entregados a cuotas iguales, ni aparecen en sus afirmaciones. Sí aparecen en los pasajes y afirmaciones de redistribución. audit.py verifica rangos, pertenencia, fuente completa efectivamente enviada y hashes del candidato. La interpretación semántica es del productor; la búsqueda literal por sí sola no certifica exhaustividad.

La causa observada en este par es recuperación insuficiente para el primer candidato. La etiqueta omitted no distingue esa causa automáticamente: el diagnóstico procede del cotejo externo de pasajes y fuente. La CLI actual devuelve una clasificación, no una lista automática de omisiones con sus localizadores.

## Consumo y procedencia

| Candidato | Contexto original de generación | Resultado CLI | Tokens revisión |
|---|---:|---|---:|
| Cuotas iguales | 3.711 bytes | omitted | 9.876 |
| Redistribución | 5.679 bytes | complete | 9.193 |

Total: **19.069 tokens** reportados, modelo glm-5.3-flash, dos llamadas sin reintentos. Ambos revisores leyeron los 41.578 bytes de la fuente completa, más candidato e instrucciones. No se presenta ahorro total de tokens ni coste monetario verificado. La generación original y el trabajo de auditoría no están incluidos en esos consumos.

freeze.json identifica fuente, candidatos, expectativas y commit de código. result.json conserva uso, decisiones y localizadores. Los textos y journals completos permanecen ignorados. Fuente y candidatos no cambiaron; sus hashes se cotejan antes y después.

## Límites y siguiente paso

Caso conocido de desarrollo, seleccionado por su omisión ya documentada. No es nueva evidencia reservada ni revisión independiente, y una ejecución por candidato no prueba estabilidad. El éxito valida el recorrido de la CLI en este par, no fidelidad general ni completitud de la extracción.

La CLI admite hasta 160.000 bytes de fuente y rechaza excedentes; no se probó aquí una fuente de ese tamaño ni se resolvió el tratamiento de documentos mayores. Fraccionar una fuente sin definir cobertura global no produciría una revisión equivalente.

Siguiente paso recomendado: convertir una etiqueta omitted en un diagnóstico comprobable con información faltante y localizadores de evidencia, manteniéndolo como derivado propuesto y separado del candidato original. Usar este par como control de desarrollo y validar después con casos nuevos. No automatizar ampliación de lectura o reparación a partir de la etiqueta sola. No se implementó ese diagnóstico en esta tarea.

Reproducción sin red: `python3 experiments/coverage-cli-long-v1/audit.py`. prepare.py y run.py requieren directorios nuevos; run.py envía solicitudes y no debe repetirse sobre este lote. No cambió código de producto; se comprobó reproducción del contraste y enlaces documentales, sin repetir la regresión de 470 pruebas del commit anterior.
