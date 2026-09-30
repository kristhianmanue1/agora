# Derivado explícito y contraste de materialidad

## Resultado del encargo

Se retiró **únicamente el último byte 0x60 (backtick)** de la respuesta conservada del control shared. receipt.json registra hash del resultado original, contenido anterior, contenido derivado, archivo de respuesta derivado y offset de la eliminación. El original sigue rechazado por JSONDecodeError y permanece byte a byte intacto.

La respuesta derivada pasó el parser y el contrato de IDs mediante diagnose-omissions --response. Resultado: dos propuestas, cero HTTP, origin=replay, disposition=requires_review. El estado complete de este replay significa forma validada, no aceptación semántica ni nueva ejecución de GLM. El derivado tiene procedencia local explícita; no se atribuye la corrección al proveedor. review_disagreement=true conserva el desacuerdo con la revisión previa complete.

## Contraste de las dos propuestas

| Propuesta | Fuente | Evaluación del productor |
|---|---|---|
| Múltiples respuestas válidas dificultan evaluación | [14385,15677) | Se solapa con la explicación ya incluida sobre diversidad de respuestas y referencias necesarias para BLEU. Puede enriquecerla; no queda demostrada una omisión material nueva. |
| No hay métrica perfecta; se toman métricas de traducción | [4504,4899) | Añade contexto sobre origen de métricas. Las limitaciones solicitadas ya están explicadas; no se demuestra que agregarlo sea necesario para contestar. |

El candidato shared expresa tres puntos: débil correlación con juicios humanos, muchas referencias para BLEU por diversidad de respuestas y complejidad insuficiente de promedios de embeddings para composicionalidad. Dos anotaciones QASPER dan esos puntos; una tercera incluye la explicación de múltiples respuestas válidas. No se decide por mayoría ni se convierte la unión de anotaciones alternativas en una lista obligatoria. La evaluación considera el contenido ya expresado y la pregunta concreta.

**Conclusión acotada:** ninguna propuesta queda confirmada como omisión material en esta evaluación del productor. No es adjudicación independiente, aprobación del Operador ni prueba de exhaustividad. assessment.json conserva argumentos, contraargumentos e identidad de las referencias. La expectativa histórica no se cambió retrospectivamente. No se modificó el candidato ni se incorporaron esas frases automáticamente.

## Implicación práctica

El problema ya no es aumentar tokens. El diagnóstico confunde potencialmente “hay más información en la fuente” con “falta información necesaria para responder”. La cita válida resuelve localización; no resuelve materialidad.

Siguiente paso recomendado: fijar una rúbrica explícita de requisitos de respuesta y distinguir **requisito ausente**, **información ya cubierta con otras palabras** y **ampliación opcional**. Validarla con controles nuevos que incluyan paráfrasis suficientes y fuentes con detalles irrelevantes. Mantener en paralelo la evidencia de omisiones claras del candidato equal. No implementar una reparación genérica que recorte salida de modelos silenciosamente, ni promover por este caso conocido.

## Verificación y límites

verify.py comprueba modificación exacta de un byte, hashes de todos los originales y derivados, offsets UTF-8 de evidencia y replay sin red. La reparación se diseñó para esta respuesta concreta y no está instalada como comportamiento del producto. derive.py reserva un directorio nuevo y falla si ya existe; no se debe repetir sobre este lote. Se verificaron los enlaces de documentación; no cambió código de producto ni se repitió su suite de 483 pruebas.

La reparación de formato y el contraste solicitado están completados. La validación general del detector de omisiones sigue pendiente: falta distinguir materialidad de ampliación y realizar revisión independiente. Ningún desacuerdo fue borrado para declarar éxito.
