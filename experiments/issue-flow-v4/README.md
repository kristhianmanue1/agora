# Fuente nueva → evaluación v4 → revisión recuperable

Flujo experimental explícito, sin watcher ni admisión. Base propia con
application_id 0x41474935 y user_version 5: almacena revisiones v4 y operaciones.
Rechaza bases anteriores, incluida issue-store-v2; no realiza migraciones.

1. prepare exige cabeza esperada, conserva historial y añade una fuente cuya
   identidad, hash y fecha de corte se comprueban. Rechaza duplicados exactos.
2. reserve persiste ID de operación y request completo (prompt de sistema,
   mensajes, modelo solicitado y parámetros) antes de invocar el proveedor.
3. La respuesta se conserva como response_ready, incluso si después es inválida.
4. finalize valida/adapta a v4 y guarda revisión + operación committed en una
   única transacción. Una escritura concurrente impide sobrescribir historial.
5. Mismo ID y request devuelve lo guardado sin volver a invocar al proveedor.
   attempted sin respuesta conservada significa provider_outcome_unknown: no
   reenvía. response_ready permite finalizar sin una nueva llamada.

El proveedor recibe una copia del request persistido. Esto verifica lo entregado
al adaptador, no que un servicio externo respete todos sus parámetros. Cambiar
prompt/configuración y reutilizar el mismo ID produce conflicto de request.
Caller debe conservar ID estable; elegir otro ID no garantiza deduplicación remota.

run.py usa un evaluador simulado: el hijo confirma la transacción y sale con código
7 sin devolver resultado. El padre reabre y recupera sin otra llamada, conservando
la revisión original y alcance ampliado. Cero llamadas LLM. Las clasificaciones
semánticas de este fixture no constituyen evidencia del comportamiento de GLM.

Conserva v3, v4 y consumidores publicados anteriormente. No comparte tablas con
Skopos ni escribe AN-KLA. Requiere código/validador compatible. Hashes no son firmas;
no se probó pérdida de energía, proveedor real ni exactly-once distribuido.
