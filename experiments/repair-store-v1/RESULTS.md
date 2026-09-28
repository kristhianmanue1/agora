# Derivado recuperable de respuesta real — 2026-09-28

La base histórica del intento GLM se abrió en modo sólo lectura para crear una
copia con SQLite backup. Se capturó de la copia la operación live-v4-001 y su
revisión esperada. Se persistió un derivado en un tercer archivo separado.

El hijo confirmó la transacción y terminó con código 7 sin devolver resultado.
El padre recuperó el registro y repitió la misma incorporación: un solo derivado,
resultado idéntico. Otro proceso volvió a leerlo, comprobando identidad externa y
reconstrucción exacta sin necesitar la base fuente. Cero llamadas a modelos.

La evaluación derivada queda resolved con la fecha y responsable ya comprobados;
la operación fuente permanece response_ready. Los bytes tanto del original como
de su copia quedaron idénticos antes/después. La diferencia de hash entre original
y copia no implica cambios de contenido: SQLite backup no garantiza copia binaria.

415 tests pasan, incluidos once nuevos: lectura/repetición, recibo de otra respuesta,
cambio de valores, cabeza obsoleta, request alterado con hash recalculado, respuesta
incompleta, rollback, conflicto de identidad, digest externo incorrecto, base
incompatible sin modificaciones y manipulación del registro guardado.

## Autorrevisión adversarial

- Almacenar sólo el texto reparado ocultaría la procedencia: se conserva el original
  y se declara host_format_repair, nunca modelo original ni admisión.
- Un recibo válido pero de otra respuesta se rechaza al compararlo con la operación.
- Un paquete con hashes recalculados no basta: se reconstruye desde la revisión base.
- Una confirmación perdida no exige repetir efectos: identidad estable y transacción
  retornan el registro guardado. No garantiza deduplicación si se inventa otro ID.
- El resultado es histórico respecto al snapshot. Una nueva fuente posterior puede
  requerir otra evaluación; no se promete actualidad permanente o atomicidad entre bases.
- No hay revisor independiente, autenticación criptográfica, prueba de energía ni
  incorporación al historial principal. El resultado pertenece al almacén de derivados.

## Próximo paso

Consolidar una entrada CLI que permita preparar, inspeccionar e incorporar estos
resultados con IDs y cabezas explícitos. Debe mostrar original y derivado sin
confundir reparación con respuesta del proveedor, y permitir retomar sin repetir
llamadas. No hace falta otra ronda equivalente de pilotos ni otra llamada GLM para
esa consolidación local.
