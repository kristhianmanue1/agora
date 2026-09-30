# Comparación pareada con identificadores de evidencia

Ronda completada: [resultados y autorrevisión adversarial](RESULTS.md).

## Pregunta y condición congelada

¿La redistribución experimental del presupuesto mejora la utilidad de las respuestas frente a cuotas iguales cuando ambas rutas usan el contrato existente de afirmaciones con IDs?

Se conservan los 24 contextos de 12 documentos del [ensayo anterior](../retrieval-answer-paired-v1/CONTINUATION.md), con hash de cada sobre y comprobación byte a byte de las unidades contra la fuente. No se vuelve a recuperar ni se corrigen los pasajes. El orden alterna la ruta inicial por documento. IDs neutrales, sin etiqueta de método en el prompt. Son documentos de desarrollo ya conocidos, no casos reservados nuevos.

GLM glm-5.3-flash, temperatura 0, salida máxima 2.048 tokens, timeout 90 s, sin reintentos. Parada ante 401/402/403/429 o tres fallos de transporte. Máximo 24 generaciones y 24 revisiones. Solicitudes fallidas y parciales se conservan. No se cambia el presupuesto tras observar respuestas.

La generación reutiliza build_units, id_system y validate_ids de Ágora, con EvidencePolicy predeterminada y salida en inglés. El contrato por afirmaciones difiere de concise-v1: una diferencia frente al ensayo literal anterior no permite atribuir causalmente la mejora sólo a los identificadores. La comparación entre rutas dentro de este ensayo sí mantiene contrato, modelo y presupuesto comunes. Los IDs garantizan pertenencia y procedencia, nunca implicación semántica.

## Revisión y medida

Sólo candidatos localmente válidos se envían a Jev jev-1.13.0. Revisión con fuente completa, pregunta, afirmaciones, citas resueltas y datos faltantes; sin método, gold, otra respuesta, offsets ni IDs de evidencia. Orden mezclado con semilla fija. Se conservan los criterios de fidelidad y cobertura del ensayo anterior.

Una respuesta se cuenta como útil cuando es válida, declara answered y Jev asigna supported y complete. partial y not_in_passages permanecen separados. Pares con una salida inválida, transporte fallido o revisión ausente son incompletos para comparación semántica; también se reporta el éxito operativo sobre las 12 oportunidades por ruta. No se descartan fallos para calcular esa tasa. Se identifica el contexto idéntico para evitar atribuir diferencias del modelo a recuperación.

Se contabilizan tokens y tiempo de generación y revisión, incluidas respuestas rechazadas. El uso de llamadas agotadas puede ser desconocido. Tiempo de solicitudes no equivale al tiempo total de ingeniería. No hay adjudicación humana ni calibración independiente de Jev; ninguna mayoría basta para promover el método predeterminado.

## Reproducción

prepare.py crea un directorio nuevo y requiere las entradas locales ignoradas del ensayo anterior. generate.py rechaza reutilizar un directorio de salida existente. prepare_review.py valida y prepara una revisión nueva; review.py usa el transporte existente; score.py verifica hashes, entradas efectivamente enviadas y consolida los journals. No volver a ejecutar solicitudes ya reservadas. freeze.json y review-freeze-02.json fijan entradas antes del envío. Los journals completos y documentos permanecen ignorados; se publican metadatos y resultados saneados.

Producto y método predeterminado sin cambios.
