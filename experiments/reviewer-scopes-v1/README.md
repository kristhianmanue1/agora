# Revisor con dos ámbitos explícitos — resultado parcial

## Qué se probó

Diez revisiones nuevas con Jev jev-1.13.0, sin regenerar respuestas: tres abstenciones relativas a pasajes, ambos candidatos de una pregunta ambigua, tres candidatos adecuados como controles positivos y dos controles negativos derivados (ausencia falsa y nombre de modelo falso). Selección intencional sobre fallos conocidos, no muestra reservada. Las expectativas son del productor, apoyadas en el [contraste externo](../retrieval-reference-audit-v1/README.md), sin adjudicación independiente.

Cada petición incluye task, full_source, delivered_passages y answer. Jev no recibe método, grupo, referencia QASPER, expectativas, etiquetas anteriores ni respuesta hermana. Orden mezclado e identificadores neutrales. Los negativos son copias alteradas explícitamente para el control; los candidatos originales no se modifican.

Tres ejes: fidelity, coverage e interpretation. Las afirmaciones de ausencia en pasajes se juzgan sobre delivered_passages; suficiencia global se juzga sobre full_source. Se añade detección de ambigüedad. El contrato y las entradas se prepararon antes de enviar; freeze.json conserva el hash de entradas y result.json verifica que los requests reales coincidan con run.py. Diez llamadas máximas, 90 segundos, sin reintentos; transporte existente con parada por acceso/saldo/límite o tres errores. No se repite el prompt anterior: la comparación histórica no aísla cambios de prompt, campos y variación del modelo.

## Resultado

Las diez peticiones terminaron. Modelo reportado: jev-1.13.0. Consumo: **93.961 tokens** (92.622 entrada y 1.339 salida); 3,680 segundos acumulados de solicitudes, no tiempo total de trabajo. Sin coste monetario verificado.

| Grupo | Resultado |
|---|---|
| Abstención SVM, contexto de cuotas iguales | supported + omitted: reconoce el límite de lectura y conserva insuficiencia global |
| Abstenciones sobre tamaños, ambas rutas | unsupported + omitted: persiste el desacuerdo sobre fidelidad al ámbito |
| Tres controles positivos | supported + complete en los tres |
| Ausencia falsa en contexto que sí contiene cifras | unsupported + omitted |
| Nombre de modelo alterado | unsupported + omitted |
| Pregunta ambigua, cuotas iguales | supported + omitted + ambiguous |
| Misma pregunta, redistribución | unsupported + omitted + clear |

Se cumplen las dos etiquetas esperadas en **6 de 8 controles con expectativa fijada**. Los dos candidatos ambiguos no tienen una etiqueta semántica total prefijada y se reportan aparte; no se suman como aciertos. De las tres abstenciones problemáticas, sólo una pasa de unsupported a supported manteniendo omitted. Las dos restantes conservan el problema. No extrapolar una tasa de precisión a producción.

## Autorrevisión adversarial

1. **El control negativo funciona en este lote.** Jev no acepta indiscriminadamente una afirmación de ausencia: rechaza la ausencia falsa cuando el contexto sí incluye las cifras. Tampoco acepta el modelo inventado. Esto acota, pero no elimina, el problema del ámbito.
2. **Entregar ambas fuentes no basta.** Las dos abstenciones de tamaños siguen rechazadas pese a que sus afirmaciones se circunscriben a pasajes sin esas cifras. No se conoce la razón interna: es una salida discrepante, no prueba de un mecanismo de razonamiento particular. El informe previo conserva el cotejo contra fuente y pasajes.
3. **Ambigüedad dependiente del candidato.** La misma pregunta obtiene ambiguous en un caso y clear en otro. Los contextos y respuestas difieren, por lo que no es una repetición idéntica; sí muestra que este diseño no estabiliza la interpretación de la tarea antes de calificar respuestas.
4. **Ejes poco coherentes.** Para el caso marcado ambiguous, el criterio de coverage ofrecía uncertain ante interpretaciones materialmente distintas, pero Jev devolvió omitted. No se corrige la salida ni se cuenta automáticamente como evaluación satisfactoria. Los ejes requieren comprobación conjunta y manejo explícito de discrepancias.
5. **No atribución causal ni independencia.** Cambian criterios y datos enviados, se seleccionaron fallos ya observados y no existe una repetición simultánea del revisor previo. Las expectativas y esta revisión son del productor; no hay segunda adjudicación independiente. No se promociona modelo ni configuración.

## Decisión y siguiente incremento recomendado

El ensayo autorizado está terminado; su hipótesis de corregir de forma consistente el problema de ámbito **no queda respaldada**. Mantener el producto y el revisor predeterminado sin cambios.

El próximo ensayo debe separar físicamente las tareas de revisión:

1. Evaluar fidelidad de afirmaciones sobre lectura con **sólo los pasajes entregados**. Así el revisor no puede usar la fuente completa como si el generador la hubiera leído.
2. Evaluar suficiencia global en otra llamada con la fuente completa. Mantener los resultados separados: una respuesta puede ser honesta e insuficiente.
3. Evaluar la claridad de la pregunta una vez antes de mostrar candidatos. Si es ambigua, registrar la necesidad de aclaración o interpretaciones alternativas; no inventar una intención humana ni reescribir la pregunta original.

Antes de integrar, probar los controles conservados y definir el tratamiento de ejes incompatibles. Este diseño sigue siendo propuesta: no se implementó en la CLI ni se ejecutaron esas llamadas separadas. Una nueva ronda debe congelar presupuesto y criterios; no repetir generación. Evitar ampliar corpus mientras no se resuelva la medición.

## Reproducción y preservación

prepare.py crea entradas nuevas a partir de los artefactos locales anteriores. run.py hace solicitudes y no debe repetirse sobre este lote. score.py recompone resultados, verifica las entradas, comprueba el request completo contra el protocolo y el hash del resultado original. Los documentos, candidatos completos y journals se mantienen ignorados. Los artefactos publicados contienen metadatos, criterios, resultados y límites. No cambió código del producto ni memoria canónica.
