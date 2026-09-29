# Prueba real GLM/Jev — Manual DPM

Observación UTC: 2026-09-29T01:52:46.934652+00:00. Código de partida: `166afa7a8d2c970ab20ed45f842a4b76b5b67c52`.

## Resultado

El Operador autorizó explícitamente el envío de fragmentos del PDF a Z.AI/GLM y Typesafe/Jev. Se ejecutaron las **nueve solicitudes presupuestadas, sin reintentos de proveedor**: ocho revisiones completadas y una generación global con timeout.

| Caso | Esperado sobre evidencia recibida | GLM | Jev |
|---|---|---|---|
| Normas | supported | supported | supported |
| Exclusión de cocina/comedor | contradicted | contradicted | contradicted |
| Dos responsabilidades | insufficient | insufficient | insufficient |
| Fecha de sello | insufficient | insufficient | insufficient |

Los modelos reportados por las respuestas fueron `glm-5.3-flash` y `jev-1.13.0`. Los ocho resultados tienen origen `live_provider`; se verificó que los originales conservaron su hash y que la recuperación local devolvió exactamente el hash derivado, sin llamadas adicionales. Ninguna revisión se admitió automáticamente en memoria.

**4/4 por proveedor sólo describe estos cuatro casos**, cuyas etiquetas fueron fijadas por el productor. No demuestra superioridad, equivalencia general ni adjudicación independiente. El documento completo respalda la afirmación compuesta, pero el paquete recuperado omite la página necesaria: ambos revisores hicieron bien en declararlo insuficiente. La misma distinción aplica a la fecha visible en portada y ausente del texto.

## Tiempo y uso reportado

| Revisor | Coincidencia con criterio | Tiempo acumulado de cuatro invocaciones | Tokens entrada | Tokens salida |
|---|---|---|---|---|
| glm | 4/4 | 51.276 s | 10386 | 2040 |
| jev | 4/4 | 2.260 s | 11961 | 185 |

Los tiempos incluyen CLI, Llavero, red y proveedor; son una sola pasada, no un benchmark de latencia. Los tokens dependen del tokenizer y contrato de cada servicio. En GLM la salida incluye tokens de razonamiento reportados. Jev fue más rápido en esta muestra, sin que eso establezca una ventaja general.

No se calculó precio monetario ni ahorro contra una ejecución de contexto completo. La consulta global no devolvió métricas de uso: el timeout **no demuestra cancelación en el servidor ni coste cero**.

## Consulta global

La CLI realizó una solicitud con `glm-5.3-flash`, máximo 8.192 tokens de salida, timeout de 90 segundos y contexto seleccionado de 6.513 bytes. Terminó en **90,373 segundos**, `execution_status=failed`, `diagnostic=timeout`. No hay respuesta ni citas que evaluar. La implementación permaneció inalterada durante esa ejecución.

Independientemente del timeout, la recuperación ya había omitido las seis secciones de responsabilidad fijadas en el protocolo. Aumentar tiempo por sí solo no corrige esa falta de cobertura.

## Incidencia local y controles

Antes del envío, ocho invocaciones fallaron en Llavero por usar `python3` sin ruta absoluta. El consumidor no se ejecutó y no hubo solicitudes al proveedor en esos intentos. Se corrigió la invocación a `/usr/bin/python3`; no se modificó Llavero ni se repitió ninguna solicitud de resultado incierto.

AN-KLA verificó correctamente; persiste el aviso preexistente sobre cambios fuera del bloque administrado. No se escribió memoria. La prueba usa las CLI existentes y una adaptación temporal de arranque para el consumidor global, que traduce la variable de credencial del perfil Z.AI sin exponerla. Los resultados completos con pasajes y la base local permanecen excluidos de Git.

Evidencia publicable: `live-results.json` (juicios, modelos, uso, tiempos, hashes y controles) y `global-live-result.json` (fallo, configuración y procedencia). El manifiesto original de casos y sus criterios permanecieron sin modificaciones durante esta fase.

## Decisión recomendada

Conservar GLM como generador y Jev como candidato a revisor. Priorizar detección de extracción incompleta, recuperación por subpreguntas y cobertura de secciones antes de ampliar comparativas de modelos. Usar este documento como regresión y reservar otros casos para medir generalización. Cualquier nueva generación global constituye una nueva ejecución, no recuperación de la que agotó tiempo.

El bloque experimental quedó ejecutado; el objetivo de obtener una respuesta global sigue sin cumplirse. No se cambió código de producto.
