# Resultado: suficiencia del resumen para la tarea

## Resultado observado

Dos llamadas completadas sin errores ni reintentos. Jev (modelo reportado jev-1.13.0) coincide con las dos etiquetas fijadas por el productor antes de ejecutar:

| Resumen | Respaldo observado anteriormente | Suficiencia observada ahora |
|---|---|---|
| Conserva autorización, autoridad y momento | supported | sufficient |
| Sólo afirma que la Unidad define las políticas | supported | insufficient |

El criterio principal congelado se cumple (2/2). El segundo resumen contiene una afirmación respaldada, pero omite información necesaria para la tarea explícita. La etiqueta de insuficiencia no lo convierte en una afirmación falsa.

## Qué acredita y qué no

Demuestra una ejecución en la que una pregunta separada sobre suficiencia distingue este par. No acredita sensibilidad general a omisiones, descubrimiento autónomo de requisitos, suficiencia para operar ni vigencia externa del documento. No promueve a Jev como revisor predeterminado ni incorpora este eje al producto.

Las etiquetas son del productor, sin adjudicación independiente. Dos casos de desarrollo, una fuente, una corrida; sin comparación pareada con GLM. La tarea pregunta explícitamente por autorización y momento: no equivale a una tarea abierta. Las respuestas sólo contienen una elección; no acreditan que el proveedor haya identificado por separado cada dato omitido. No se interpretan probabilidades como confianza calibrada.

La comparación de respaldo reutiliza respuestas previas, comprobadas contra sus requests originales; no es una comparación simultánea controlada entre prompts. No se afirma que el módulo existente de suficiencia de pasajes detecte esta omisión: el piloto envía también el resumen candidato.

## Verificación

Hashes de casos y gold coinciden con el freeze original. Se comprobó que cada state contiene exactamente task, evidence y summary; etiquetas no enviadas. Dos llamadas autorizadas, timeout individual 90 s, sin reintentos. Consumo reportado: 1.230 tokens de entrada + 104 de salida = 1.334. Suma de tiempos de petición: 0,904 s; no mide preparación ni coste monetario.

Respuestas saneadas en [result.json](result.json). Inputs y journals completos quedan fuera de Git. No se modificaron código de producto, candidatos previos, etiquetas ni configuración predeterminada.

## Recomendación

Conservar tres comprobaciones separadas: evidencia disponible, respaldo de lo afirmado y suficiencia del resumen para la tarea. Siguiente prueba acotada: tarea menos dirigida, con criterios críticos fijados antes de observar respuestas y un control donde la misma omisión no sea necesaria para responder. Exigir explicación y referencias para los faltantes antes de plantear integración; una etiqueta sola no basta para reparar el resumen. No añadir todavía automatización ni cierre de cuestiones por este resultado.
