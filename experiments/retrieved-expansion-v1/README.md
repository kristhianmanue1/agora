# Recuperación sin localizador prefijado — ensayo 01

2026-09-28. Desarrollo sobre las dos afirmaciones ya conocidas, no holdout.
Consulta exacta: question + salto de línea + claim. No se añaden palabras clave,
frase inicial del pasaje, respuesta esperada ni localizador al recuperador.
Se mantiene lexical-paragraph-overlap/v0.1 del producto, top_k=3, con presupuestos
4096 y 8192 bytes; ambas condiciones se fijan antes de ejecutar. Sin embeddings,
LLM para consultas, cambios al ranking ni reintentos adaptados al gold.

Se conserva abstract y se añaden los pasajes recuperados literales. La lectura
local consulta todo el documento; los bytes entregados al modelo se miden aparte.
La comprobación del pasaje decisivo utiliza los localizadores previos DESPUÉS de
seleccionar: es medición, no entrada del recuperador. Coincidencia con un párrafo
conocido no demuestra recuperación de todas las excepciones ni exhaustividad.

Evaluación posterior: sólo se fijará gold sobre la evidencia realmente recuperada,
antes de llamar, sin modificar consultas ni presupuesto. Hasta 4 casos por revisor,
8 llamadas máximas; mismas instrucciones v2, 2048 tokens de salida GLM y 90 s por
llamada, cero reintentos. Conservar resultados anteriores, fuente, rangos, consulta,
manifest y revisión. Ninguna revisión implica admisión o promoción del proveedor.
