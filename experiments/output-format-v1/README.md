# Adaptador experimental de formato v1

Política cerrada `single-trailing-backtick/v1`. Admite un objeto JSON estricto o
propone borrar **un único backtick externo posterior** al objeto, sólo si el resto
son espacios JSON. Es la anomalía observada, no un reparador general.

Preserva íntegra la respuesta original y produce otro texto, con estado
repair_candidate, hashes y una edición en offsets UTF-8. Ningún byte dentro del
objeto cambia. JSON válido pasa unchanged sin reserializar. Rechaza objetos
múltiples, comentarios, prefijos, fences, texto extra, claves duplicadas, valores
no finitos, JSON truncado y salidas mayores de 1 MiB. No completa valores.

verify reconstruye la transformación y exige recibo exacto, incluida su política.
Un hash no es autenticación: cambiar original y recibo juntos no prueba origen.
El recibo no es aprobación ni admisión. El caller debe vincularlo al request y a
la respuesta persistida; el transporte sigue rechazando respuestas incompletas.

replay.py produce una reparación candidata de la respuesta GLM histórica y la
valida con v4, sin modificar aquella operación response_ready. Cero llamadas.
La semántica y citas siguen siendo responsabilidad de v4 y de revisión de fidelidad;
que el JSON sea válido no acredita verdad. No se activa reparación automática.
