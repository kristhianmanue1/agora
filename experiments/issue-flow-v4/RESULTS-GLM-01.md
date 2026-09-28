# GLM v4 real: rechazo de formato conservado — 2026-09-28

**La prueba de extremo a extremo no pasó.** Una llamada, cero reintentos:
glm-5.3-flash solicitado y reportado, finish_reason=stop, 6407 tokens y 94,994 s.
El proveedor devolvió un objeto JSON seguido de una comilla invertida (`).
json.loads rechazó el contenido con JSONDecodeError: Extra data.

Los valores visibles son la fecha esperada (2026-10-21) y Lina, con referencias
literales, pero eso no convierte la respuesta inválida en candidata aceptada.
No se recortó el carácter, no se cambió el prompt ni se aumentó el presupuesto.
El request usó response_format=json_object; en esta ejecución ese parámetro no
bastó para obtener un documento JSON íntegramente válido. No se infiere una causa
interna ni un fallo general del proveedor a partir de un caso.

## Conservación y recuperación

La operación quedó response_ready y la respuesta original se conservó exacta.
No se creó la segunda revisión. inspect_live_failure.py abrió la base en un
proceso nuevo e intentó finalizar con un proveedor que fallaría si se invocase.
Se reprodujo el rechazo, sin llamada, sin modificar operación y con una sola
revisión (la original). result-failure-recovery.json registra esa comprobación.

394 tests pasan, incluida regresión con la respuesta real inválida. Este conteo
acredita los controles locales, no éxito del ensayo real. Las entradas y código
congelados permanecieron sin cambios durante la llamada. La respuesta conservada
está en result-glm-01.json; sus datos son sintéticos.

## Autorrevisión y siguiente paso

El rechazo estricto evita que una reparación implícita se atribuya al modelo.
La recuperación evita repetir una llamada ya respondida. Ninguno demuestra
calidad semántica general ni flujo GLM completo satisfactorio. Revisión del
productor, sin revisor independiente; cero admisión o despliegue.

Prioridad: definir y probar localmente un adaptador de salida versionado que
preserve la respuesta original, distinga explícitamente cualquier reparación
candidata y rechace contenido ambiguo (varios objetos, texto adicional o cambios
de valores). Mantener el parser estricto para la respuesta original. Sólo después
considerar una nueva llamada acotada; no reiterar ni aumentar tokens a ciegas.
La consolidación CLI continúa pendiente del tratamiento de esta frontera.
