# Reparación candidata explícita — 2026-09-28

Cero llamadas nuevas a modelos. replay.py conserva la respuesta original del
intento GLM v4 y produce una representación distinta: elimina sólo el byte de
backtick posterior al objeto JSON. Los bytes interiores, campos, valores y citas
no se modifican. El recibo registra original, candidato, hashes, política y edición.

La nueva representación pasa v4: estado resolved, fecha 2026-10-21, responsable
Lina. Es resultado local sobre una reparación del host, no una respuesta nueva ni
una revisión admitida. La operación histórica permanece response_ready, sin cambios.
El hash del input reconstruido se contrastó con el request original local: coincide.

404 tests pasan, incluidos diez nuevos. Controles negativos: objetos múltiples,
texto extra, fences, comentarios, JSON truncado, claves duplicadas, números no
finitos, arrays/escalares, tamaño excesivo, Unicode inválido, recibos con cambios
de valores, política o edición. Controles positivos: respuesta histórica, JSON
válido preservado y offsets UTF-8 con acentos/backticks dentro de strings.

## Autorrevisión adversarial

No se usa extracción del primer objeto seguida de descarte arbitrario: el sufijo
no vacío debe ser exactamente un backtick más espacios JSON. No se reserializa
el contenido. Esto limita la transformación al defecto observado; no acredita
que cualquier sufijo pueda ignorarse ni que los valores sean correctos.

Un recibo alterado se rechaza al reconstruir la operación. Cambiar también el
original completo puede producir otro recibo válido: por eso la futura incorporación
requiere ligarlo a la respuesta persistida y request exactos. Los hashes no son firmas.
No hay revisión independiente. La política acotada todavía no mide frecuencia de
fallos del proveedor ni evita errores semánticos.

## Próximo paso propuesto

Incorporación explícita de la reparación como derivado: enlazar respuesta original,
recibo, request y revisión esperada; persistir la nueva revisión de forma atómica y
recuperable, conservando el rechazo histórico. Primero contra una copia experimental
de la operación fallida; cero nuevas llamadas. No tratar repaired como respuesta
original del modelo ni activar reparación automática para otros defectos.
