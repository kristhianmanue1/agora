# Resultado: omisión relevante según la tarea

## Resultado observado

Cuatro llamadas completadas. Coincidencia con etiquetas congeladas del productor: **4/4 juicios de suficiencia y 8/8 clasificaciones de unidades**. Criterio principal cumplido. Cero inconsistencias según el chequeo local de suficiencia frente a missing_required.

| Tarea | Resumen | Jev: suficiencia | Fragmento de autorización e2 |
|---|---|---|---|
| Describir procedimiento | Completo | sufficient | covered |
| Describir procedimiento | Breve | insufficient | missing_required |
| Identificar unidad | Completo | sufficient | covered |
| Identificar unidad | Breve | sufficient | not_required |

La tarea operativa no nombra autorización, autoridad ni momento. El modelo diferencia qué exige esa tarea de lo necesario para identificar la unidad. La fuente y el resumen breve son iguales entre las dos tareas: la diferencia observada corresponde al contexto de la tarea.

## Evidencia de la omisión

En operational-brief, Jev seleccionó e2 como missing_required. Su texto se resuelve de forma exacta contra los offsets del fragmento local. El reporte saneado guarda ID, hash y offsets; la cita se conserva en los inputs privados. No son offsets del PDF original ni una explicación libre generada por Jev. El contenido de e2 es el sometimiento de políticas y programas a autorización de la persona titular de la Dirección de Prestaciones Médicas antes de instrumentarlos.

Selección de evidencia y vinculación literal son comprobaciones diferentes: la segunda pasó localmente; la primera coincide con el criterio del productor, sin adjudicación independiente.

## Ejecución y verificación

Modelo reportado: jev-1.13.0. Cuatro llamadas, cero errores y cero reintentos; timeout individual 90 s. Tokens: 3.842 entrada + 586 salida = 4.428; suma de tiempos de petición 1,409 s, sin incluir preparación ni representar coste monetario.

Hashes de casos y gold verificados contra el freeze previo. State coincide exactamente con task/evidence/summary/units; gold excluido. Cada unidad coincide con su subcadena. Respuestas saneadas en [result.json](result.json); fragmentos y journals completos no publicados. No se modificaron etiquetas, defaults, código de producto ni candidatos previos.

## Autorrevisión adversarial y límites

Cuatro casos dependientes, una fuente, una corrida y etiquetas del mismo productor. No son cuatro observaciones independientes ni un benchmark reservado. Las unidades fueron separadas manualmente; la propia selección hace visible la condición relevante. Por ello no demuestra descubrir automáticamente requisitos en documentos grandes. No hubo comparación GLM pareada ni prueba de estabilidad ante repeticiones/paráfrasis.

El chequeo de consistencia detecta algunas contradicciones internas, no todas ni la corrección semántica. Las probabilidades no se toman como confianza calibrada. Un sufficient es un juicio experimental, nunca autorización para actuar ni garantía de suficiencia clínica u operativa.

## Próximo paso recomendado

Preparar una batería de transferencia con otras condiciones: excepciones, responsables, plazos y cifras. Fijar requisitos antes de generar resúmenes, conservar controles donde omitir un dato sí es admisible y reservar casos fuera del desarrollo. Comparar Jev y GLM con los mismos casos antes de integrar el eje answer_sufficiency en la CLI. No seguir afinando solamente sobre este fragmento.

El Operador autorizó todos los envíos de esta serie a Typesafe/Jev; la autorización se registra para evitar repetir preguntas por cada lote del mismo alcance. Cada nuevo lote conservará su límite de llamadas y cero reintentos salvo decisión distinta. Esta declaración no amplía proveedor, fuentes sensibles ajenas al encargo ni publicación de contenido privado.
