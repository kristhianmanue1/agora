# Piloto conjunto: recorrido correcto con referencias por ID

**Completado, 2026-09-26.** Se conserva intacto el intento literal 01, rechazado
por JSON mal formado. En una ejecución nueva se eligió el modo `ids` ya existente
en Ágora. La reunión, preguntas, modelo y límites no cambiaron. La variante no
repara ni completa JSON: el modelo selecciona identificadores y el código resuelve
citas literales desde unidades verificadas. IDs desconocidos siguen rechazándose.

## Resultado observado

Skopos reabrió el almacén experimental, recuperó revisión 2 y excluyó el lunes de
la búsqueda vigente. Exportó texto y localizadores verificados; Ágora generó un
candidato estructuralmente válido y completó sus revisiones separadas.

| Aspecto | Respuesta observada y contraste con fuente |
|---|---|
| Fecha | Martes 29 de septiembre de 2026, coincide con revisión 2 |
| Cantidad | 40 equipos, coincide |
| Responsable | Nerea, coincide |
| Condición | Completar la prueba de aceptación, conservada |
| Presupuesto | No especificado en los pasajes; no se inventó una cifra |

Dos citas resueltas por ID, dos navegaciones verificadas a segmentos originales:
`delivery` (0–10000 ms) y `owner` (10000–20000 ms), hablante Nerea. La auditoría
verificó huellas, rangos UTF-8, identidad/revisión y correspondencia de citas con
el original. El agente contrastó además los hechos de la tabla; es autorrevisión,
no adjudicación independiente.

Estado de ejecución: complete. Estado del candidato: candidate_partial porque
el presupuesto no está en la fuente. Esa respuesta parcial es correcta para la
información disponible y no representa un fallo técnico. El revisor emite
needs_adjudication, no aprobación. No evalúa omisiones globales ni certifica el
idioma; el contraste explícito del presupuesto ausente se hizo por separado.

Tres solicitudes reales, sin reintentos, a glm-5.3-flash (solicitado y reportado):
1535 + 955 + 1016 = **3506 tokens**; suma de tiempos de transporte **35.681 s**.
Sin consumo desconocido; no se calculó coste monetario. El intento 01 conserva
sus 1744 tokens y su fallo; no se elimina al informar este resultado favorable.

## Reproducción y publicación

Ejecutor: `experiments/meeting-bridge-v1/run.py`, argumentos raíz Skopos,
directorio de salida nuevo y `ids`; omitir el último mantiene literal. Credencial
entregada por Llavero, sin cambios de perfil ni exposición de secretos.

Entrada Skopos probada: commit `5773dbd`, rama `codex/meeting-source-currency`.
Base Ágora: `4364bde`; la modificación del ejecutor y el protocolo están congelados
por hash dentro de la ejecución. Se publican resultados sintéticos por aspecto,
juicios y localizadores en `experiments/meeting-bridge-v1/result-glm-02-ids.json`.
Los artefactos crudos permanecen locales e ignorados en `runs/glm-02-ids/`.

## Límites y decisión propuesta

Un fallo literal y un éxito por IDs no prueban causalidad ni una tasa de fiabilidad.
Cambian la forma de referencia y su prompt; el modelo es no determinista. El modo
por ID puede citar unidades mayores y consumir más bytes de evidencia. Esta prueba
no permite afirmar que evita todos los errores de JSON o las alucinaciones.

El recorrido conjunto queda demostrado para esta reunión sintética acotada. No es
un conector de producción, un despliegue, una fusión de Skopos a main ni admisión
AN-KLA. No se cambian modos predeterminados. Siguiente paso recomendado: repetir
con una exportación de reunión real autorizada y criterios fijados, incluyendo
correcciones, información ausente y navegación. Conservar cualquier rechazo.
