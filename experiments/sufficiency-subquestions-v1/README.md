# Subpreguntas y redistribución de presupuesto: contraste local

## Resultado

Las subpreguntas genéricas con `paragraphs-equal` no recuperaron el párrafo de evaluación que faltaba. Una ampliación experimental por vecinos con presupuesto compartido sí lo recuperó. Ninguna llamada a modelos en este lote: la brecha de recuperación era observable localmente.

| Documento | Consulta anterior | Subpreguntas con cuotas iguales | Redistribución experimental | Tope |
|---|---:|---:|---:|---:|
| 1610.00479 | 3.786 bytes | 6.011 bytes | 7.882 bytes | 8.000 |
| 1902.08830 | 5.254 bytes | 6.549 bytes | 7.698 bytes | 8.000 |

En el primero, la redistribución añade íntegro el párrafo de 929 bytes sobre la construcción de contextos para denoising; se verifica el intervalo UTF-8 [21639,22568) sobre la misma revisión de fuente. Conserva el pasaje de evaluación de entidades y entrenamiento. En el segundo, conserva la lista de cinco idiomas. Los indicadores por palabras son auxiliares: no son una certificación de completitud.

## Causa observada

Cada una de las dos subpreguntas tenía cuota de 4.000 bytes. A la segunda le quedaban 137, insuficientes para el vecino de 929 bytes. Tras deduplicar, el conjunto tenía 1.989 bytes sin usar. El párrafo también ocupaba posiciones bajas en ranking lexical (29 y 16), por lo que no fue semilla. `paragraphs-equal` conserva deliberadamente cuotas sin redistribución; no es una regresión del contrato existente.

El experimento conserva la unión inicial, propone vecinos inmediatos de las semillas, los ordena por coincidencia de términos con la subpregunta y orden documental, y añade los que caben en el presupuesto común. Una sola expansión; no recibe gold, anotaciones ni nombres de evaluaciones faltantes. Código en shared_frontier.py, regla en shared-protocol.json y evidencia en shared-result.json.

## Qué se comparó

Fuentes y hashes iguales al piloto de recuperación real; preguntas generales redactadas por el agente antes de seleccionar. Son una descomposición manual basada en la pregunta, no una capacidad autónoma de generación de subpreguntas. Las subpreguntas no incluyen denoising, FACC ni la lista de idiomas. Sin embargo, el agente conocía los fallos previos: es desarrollo posterior al diagnóstico, no evaluación ciega ni reservada.

Presupuesto fijado antes de ejecutar: 8.000 bytes, top_k=3 por subpregunta y estrategia existente paragraphs-equal. La variante compartida se diseñó después de observar su fallo y se registra separada, sin sustituir el resultado negativo. Mantiene todas las referencias previas y respeta el límite; también incorpora texto de relevancia débil y no demuestra optimalidad.

## Verificaciones

AN-KLA verify correcto. Hashes de fuentes cotejados con el piloto previo. Subcadenas UTF-8 exactas, conservación de rangos anteriores, límite de bytes y presencia completa del párrafo ausente comprobados con asserts. No se ejecutó la suite de producto: no se cambió src/agora. Cero llamadas a proveedores y cero coste API nuevo.

Una primera solicitud de ejecución no llegó a iniciarse por timeout de revisión automática; el reintento encontró que el script temporal aún no existía. Se creó después y la ejecución local autorizada terminó correctamente. No hubo rechazo sustantivo de seguridad ni ejecución duplicada de proveedores.

## Decisión y siguiente paso

Conservar esta ampliación como candidata experimental. Antes de incorporarla: probar casos nuevos con etiquetas de cobertura fijadas sin ver la selección, y controles de no pérdida, deduplicación y presupuesto, incluyendo textos UTF-8 y ausencia de espacio. Si esos resultados sostienen la mejora, añadir una estrategia optativa y retrocompatible; no cambiar silenciosamente paragraphs-equal. La integración de juicios de suficiencia como decisiones de CLI sigue pendiente y es un cambio distinto.

No se afirma ahorro adicional: la mejora consume más bytes dentro del mismo techo. Tampoco se demuestra cobertura de todas las evaluaciones ni fidelidad de una síntesis nueva. Lo comprobado es recuperar un pasaje antes omitido, con referencias exactas y sin retirar lo que ya se había encontrado.

## Reproducción

prepare.py prepara el contraste y rechaza una carpeta existente; requiere inputs del piloto anterior. shared_frontier.py ejecuta la ampliación local, sin proveedor. Los envelopes y entradas quedan ignorados en inputs/. No ejecutar run.py para repetir revisiones sin un lote y presupuesto explícitos.
