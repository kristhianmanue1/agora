# Contraste de candidatos con referencias QASPER

## Resultado y alcance

Contraste completado de los **20 candidatos válidos** del [ensayo con IDs](../retrieval-answer-ids-v1/RESULTS.md), sin nuevas llamadas a GLM o Jev. Se conservan las cuatro respuestas rechazadas fuera de este análisis semántico y dentro del resultado operativo original de 24 intentos.

El productor comparó cada respuesta con todas las anotaciones de su pregunta, las evidencias citadas y los pasajes entregados. La evaluación es una **autorrevisión con referencias externas**, no adjudicación independiente ni puntuación oficial QASPER. Las etiquetas semánticas están explícitas en annotations.json; audit.py reproduce hashes y comprobaciones literales, no automatiza ni demuestra esos juicios.

| Cobertura del contenido solicitado según este contraste | Cuotas iguales | Redistribución |
|---|---:|---:|
| Adecuada frente a referencias | 4 | 6 |
| Incompleta frente a referencias | 6 | 4 |
| Candidatos examinados | 10 | 10 |

Adecuada significa que el contenido central coincide con una respuesta de referencia respaldada por la fuente. No certifica cada afirmación adicional ni exhaustividad universal. Las referencias alternativas no se suman mecánicamente como requisitos obligatorios. Sobre los 12 intentos originales por ruta siguen existiendo dos rechazos en cada una: estas cifras no los borran.

Jev había asignado complete a 11 candidatos. Uno de esos 11 no responde a la intención reflejada en las anotaciones; este contraste encuentra diez respuestas adecuadas. No convertimos 10/11 en precisión general: corpus de desarrollo, etiquetas del productor, una muestra por ruta y falta de adjudicación independiente. Los resultados de Jev permanecen intactos.

## Hallazgos y causas

- **1803.08419, métricas de diálogo:** cuotas iguales omite limitaciones de BLEU y embeddings cuyo pasaje falta en su contexto. Redistribución lo incorpora y responde. Dos anotaciones coinciden con el contenido de esa respuesta; otra varía en detalle.
- **1707.06875, lista de métricas:** ambas rutas omiten grupos de métricas cuyos párrafos definitorios faltan. Redistribución también omite como respuesta el parsing score, que sí aparece en el contexto. Coexisten hueco de recuperación y omisión del generador; no se atribuye todo a una sola capa.
- **1909.11706, SVM/Random Forest:** cuotas iguales se abstiene porque faltan las cifras en sus pasajes; la fuente completa sí responde. Redistribución aporta las cifras y responde SVM, como ambas referencias.
- **1909.13466, tamaños de entrenamiento:** faltan los tamaños en ambos contextos. La fuente los contiene. Además, una referencia libre dice 291k, mientras la anotación extractiva y el párrafo fuente indican 219.777. No usar la respuesta libre como autoridad para corregir una respuesta futura.
- **1909.02322, identidad del modelo:** ambos candidatos responden cómo se entrenó. Las dos referencias apuntan a la arquitectura Condense-Abstract / BiLSTM / LSTM. El nombre del framework aparece en ambos contextos, aunque sólo como encabezados en cuotas iguales; faltan los detalles arquitectónicos. Hay ambigüedad de pregunta, omisión y recuperación parcial. La etiqueta complete de Jev en cuotas iguales es discrepante con la intención del benchmark; no se reemplaza silenciosamente.
- **2004.02214, idiomas:** ambos candidatos reconocen dos idiomas sin nombrarlos; Chinese y English están en la fuente pero no en sus pasajes.
- **1911.01940, 1802.03052, 2003.11531 y 1909.04251:** ambas rutas cubren el contenido central de referencia: todas las capas, palabras compartidas, modelo SAT y evaluación humana, respectivamente.

## Frontera de evidencia del revisor

Jev recibió la fuente completa y el candidato, pero no el inventario exacto de pasajes que vio GLM. En tres abstenciones (SVM de cuotas iguales y tamaños de entrenamiento de ambas rutas) marcó unsupported aunque el candidato circunscribe su ausencia a los pasajes. La inspección comprueba que esos datos no están en los pasajes y sí en la fuente completa.

Esto es un riesgo de alcance del criterio: la respuesta puede estar incompleta respecto de la tarea global y, a la vez, describir correctamente sus límites de lectura. No basta con la fuente completa para adjudicar una afirmación de ausencia en el subconjunto entregado. No se invalidan automáticamente todas las etiquetas unsupported ni se confunde una abstención honesta con una respuesta útil. Las otras dos etiquetas unsupported, en la lista de métricas, requieren examen de cada afirmación y sus matices; quedan sin adjudicar.

## Decisión propuesta

Mantener la redistribución experimental. La revisión del productor encuentra dos mejoras localizadas y ningún triunfo de cuotas iguales frente a las referencias, pero esto no constituye superioridad general ni habilita promoción.

**Próximo incremento recomendado:** probar una revisión con dos alcances explícitos: (1) pasajes efectivamente entregados para juzgar afirmaciones sobre lo leído y (2) fuente completa para juzgar suficiencia global. Usar los candidatos conservados, incluir los tres casos de abstención, el caso de pregunta ambigua y controles positivos ya adecuados. Conservar la revisión anterior, congelar criterios antes del ensayo y mantener las referencias QASPER fuera del generador y de la revisión ciega. Las referencias se usan después para contrastar, incluyendo sus discrepancias.

Después, decidir si conviene ampliar recuperación, ajustar generación o recalibrar revisión. Aumentar tokens por sí solo no corrige una pregunta mal interpretada ni una frontera de evidencia mal definida.

## Verificación y límites

- Hash del dataset cotejado contra el protocolo original de selección.
- Hashes de sobres cotejados contra el congelado; fuentes cotejadas contra sus revisiones originales.
- Referencias, IDs de anotación y comprobaciones de pertenencia literal en result.json. La ausencia de un párrafo literal completo no prueba por sí sola que su contenido falte; los diagnósticos anteriores incluyen inspección de los pasajes y búsqueda de los datos concretos.
- Integridad AN-KLA verificada; memoria histórica no usada como estado actual ni modificada.
- Sin cambios de producto, reparación de candidatos, nuevas llamadas ni modificación de etiquetas originales.
- No se evalúan aquí de nuevo todas las afirmaciones adicionales, ni se obtiene una revisión humana/independiente. Causas son atribuciones razonadas del productor y pueden coexistir.

Reproducción local: `python3 experiments/retrieval-reference-audit-v1/audit.py`. Requiere los insumos ignorados de los ensayos anteriores; no llama a proveedores.
