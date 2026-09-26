# Fallback acotado v1 — protocolo previo

Cinco casos nuevos sintéticos, conocidos por productor; no holdout.
N1sinónimos recuperables, N2coincidenciairrelevante, N3datoausente,
N4fuente sobrepresupuesto, N5coincidencia útil. Criterios en cases.json.
Dos rutas: retrieve existente; retrieve con fallback_source_budget8192bytes.
Mismo prompt/contentbudget256/promptbudget65536/top_k3. Máximo10solicitudes,
una por ruta, sin retries. Sin candidatos puede causar0solicitudes.
GLM solicitado glm-5.3-flash,2048tokens,temperatura0,timeoutsocket90s,
deadline proceso110s. Credencialpreexistente del laboratorio inyectada sólo proceso.

El fallback sólo responde a cero coincidencias, no al vacío por presupuesto,
ni a respuesta insuficiente después de consultar, ni a candidatos irrelevantes.
No cambios de prompt/buscador tras observar resultados. Congelar fuente, criterios,
código y protocolo. Conservar todos los fallos y detener tras dos fallos proveedor
consecutivos o deadline. Un rechazoestructural queda como resultado, no reintentar.

Medir respuestas/citas contra fuente, solicitudes, tokensreportados y tiempo.
Recuperar una tarea antesfallida puede aumentar coste: no exigir ahorrocomoéxito.
Quitar norespuesta del denominador sería engañoso. Una limitación reconocidaN2
no equivale a resolver la tarea informativa. N4debe informar presupuestoagotado.
No admisión en memoria ni integración Typesafe ni datos reales en este piloto.
