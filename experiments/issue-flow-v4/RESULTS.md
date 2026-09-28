# Flujo incremental y recuperación v4 — 2026-09-28

local-02 ejecutado con código final de fixtures. Un proveedor simulado, cero
llamadas reales. El proceso hijo creó una segunda revisión y terminó con código
7 sin respuesta al padre; este recuperó la operación committed sin repetir llamada.

- Revisión inicial partial preservada exactamente.
- Nueva revisión resolved, con fecha del fixture y responsable conservada.
- Alcance suministrado ampliado de una a dos fuentes.
- Respuesta original, candidato y request completo conservados.
- Dos revisiones, una operación, una llamada simulada.

393 tests pasan, incluidos 12 nuevos: replay sin llamada, timeout incierto sin
reenvío, response_ready retomable, respuesta inválida retenida, paquete obsoleto,
escritor concurrente, rollback conjunto, conflicto de ID/request, manipulación de
paquete con hash recalculado, copia de request aislada del proveedor, uso desconocido
y rechazo de base v4 previa sin migración.

## Autorrevisión adversarial

La confirmación de revisión sin confirmar operación generaría duplicación al
retomar: se prueban ambas mutaciones en una sola transacción con un trigger que
falla en la actualización final. No queda revisión huérfana.

El resultado incierto se distingue del resultado fallido: un timeout deja attempted;
no se fuerza reenvío. Una respuesta conservada pero inválida permanece response_ready.
Si otro escritor avanzó, se conserva respuesta pero no se acepta contra cabeza vieja.

La identidad incluye el request completo; una versión de prompt distinta no se
considera la misma petición. Esto no acredita parámetros efectivos del proveedor.
No hubo revisión independiente. El ensayo no demuestra calidad semántica de GLM,
resistencia a pérdida de energía, vigilancia ni ejecución exactamente una vez en red.

## Próximo paso propuesto

Una prueba acotada con GLM y fuentes sintéticas sobre este flujo exacto: evaluar
una aclaración, revisar citas y alcance y recuperar la operación tras reiniciar.
Una llamada máxima, sin reintentos automáticos. Si pasa, consolidar una entrada
CLI reutilizable en vez de seguir duplicando pilotos. No migrar bases existentes.
