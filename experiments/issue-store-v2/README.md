# Consumidor SQLite de candidatos v4 — experimental

Store independiente: application_id 0x41474934, user_version 4 y registro
agora/issue-revision/experimental-v4. No abre bases legacy, no migra ni las altera.
Los anteriores Store/recovery y sus contratos permanecen intactos.

append recibe por separado entrada, respuesta original, candidato v4 y procedencia.
Comprueba que el host sólo añadió schema y reviewed_scope: fields/reason deben
coincidir con la respuesta original. Conserva ambos textos con sus hashes, input
completo, citas, alcance, estado calculado y manifiesto del validador/dependencias.
La procedencia es declaración; el registro se guarda como not_admitted.

La escritura usa transacción SQLite y comparación de cabeza esperada. Dos escritores
con la misma cabeza no pueden producir ambas revisiones: el segundo debe releer.
Leer recalcula hashes, adaptación y validación. Cambios de validador bloquean lectura
hasta una migración explícita, que este incremento no implementa.

run.py RUTA_NUEVA reproduce las dos respuestas sintéticas conservadas, respalda
SQLite y compara recuperación exacta en un proceso nuevo. El proceso hijo sólo
lee la base, código compatible y cabezas externas; no lee fixtures ni archivos
laterales. No hay llamadas LLM, watcher ni admisión automática.

Límites: no añade operaciones recuperables ni garantías de reenvío al proveedor;
recovery-v1 sigue siendo v3. Un timeout no autoriza repetir append: primero leer
historial. No es auditoría autenticada; sustituir toda la base y cabezas externas
puede eludir hashes. La cabeza externa detecta pérdida de cola; sin ella no.
No se probó pérdida de energía ni corrupción física. Requiere código compatible.
