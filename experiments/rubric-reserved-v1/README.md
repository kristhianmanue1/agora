# Caso reservado: revisión de rúbrica antes del candidato

**Resultado: detenido antes de generación por discrepancia de alcance.** Jev
`jev-1.13.0` devolvió `deficient`; no explicó el defecto. No es evidencia suficiente
para adjudicar que la rúbrica sea incorrecta, ni para sustituir las anotaciones.

## Diseño y resultado

- QASPER público, documento `1911.10401`: 34.003 bytes, 4.857 palabras.
- Pregunta original: “What datasets are used for training and testing?”
- Cuatro requisitos extraídos de la primera anotación humana; la segunda también
  enumera los cuatro conjuntos de evaluación. Ambas se entregaron al revisor.
- Selección determinista por SHA-256; exclusión de identificadores observados en
  archivos de experimentos de hasta 2 MB, sin los datasets crudos. Es reserva local
  respecto a ese inventario, no garantía de ausencia de exposición del modelo.
- Rúbrica y solicitud congeladas antes de la llamada. Revisor de otro proveedor,
  con fuente completa y sin candidato. Productor del diseño y prompt: Codex.
- Una llamada Jev, 11.210 tokens de entrada y 47 de salida; 0,534 segundos medidos
  por el cliente. Coste monetario no informado por la respuesta; no se estima.
- Cero generaciones GLM, cero evaluaciones de candidatos, cero reintentos.

La regla previa exigía detenerse si el juicio era `deficient` o `uncertain`.
Se cumplió; no se cambió la rúbrica para obtener un resultado favorable.

## Autorrevisión adversarial

La pregunta permite discutir si se refiere a los cuatro benchmarks del estudio
(SemEval-2018, Riloff, Reddit político y SemEval-2015 Task 11) o también al
preentrenamiento. La fuente menciona Wikipedia y BookCorpus al describir BERT.
Esto plantea una hipótesis de ambigüedad, no demuestra que deban añadirse a la
respuesta de la pregunta original de QASPER.

El prompt del productor destacó explícitamente preentrenamiento frente a evaluación.
Ese énfasis pudo influir en Jev. Su respuesta tipada no identifica qué defecto
observó; no se le atribuye una explicación no devuelta. La separación de proveedor
no elimina el sesgo del diseño ni demuestra independencia de la adjudicación.

**Siguiente paso:** obtener una crítica localizada: requisito cuestionado o aspecto
faltante, pasaje que lo respalda y por qué lo exige la pregunta. Sólo después decidir
si hay defecto de rúbrica, ambigüedad del encargo o exceso del revisor. Una revisión
posterior será otra condición, conservando esta rúbrica y el resultado originales.
No ampliar automáticamente una pregunta del benchmark ni reinterpretar su etiqueta.

## Reproducción y límites

`python3 experiments/rubric-reserved-v1/verify.py` reconstruye los datos públicos
usando el dataset QASPER local fijado por hash y verifica vínculos y offsets, sin red.
`selection.json` conserva exclusiones, tamaño y hash del inventario; el inventario
completo y el journal se conservan localmente en directorios ignorados. `result.json`
publica la respuesta del proveedor y hashes del journal y solicitud. El script
`selection_protocol.py` es histórico: el inventario cambia al publicar esta prueba.
No volver a ejecutar llamadas para reconstruir evidencia perdida.

No hay nuevas conclusiones sobre exactitud de `review-rubric`, ahorro de tokens,
documentos enormes, cierre de pendientes ni admisión de memoria. Esta prueba detectó
un desacuerdo previo que una evaluación basada sólo en la rúbrica habría ocultado.
