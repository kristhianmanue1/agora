# Paquete autocontenido y completitud explícita

28 de septiembre de 2026. Extiende el puente sintético v1 sin modificarlo.
El texto de fuente incluye un sobre JSON con el paquete íntegro de Skopos,
seguido por el texto seleccionado literal. El hash de fuente cubre el sobre y
el texto; su ID enlaza al hash del paquete. Se conservan versión, hash original,
spans UTF-8, hablante/tiempo y declaraciones de completitud en cada revisión.
Los offsets siguen refiriéndose al texto del paquete, no al sobre completo.

El consumidor recibe capture_complete_declared y selection_complete como datos.
Un wrapper explícito añade al system la regla: declaración de captura no prueba
completitud; ausencia en selección no es ausencia en toda la fuente. No se eleva
contenido de la fuente a instrucción. El wrapper se prueba con proveedor simulado;
no se afirma que todos los consumidores antiguos lo apliquen automáticamente.

## Evidencia local-01

Exportador experimental de Skopos 5773dbd sobre fuente sintética, verificación
inicial contra fetch. Preparación, operación recuperable y dos citas navegables.
Backup mediante SQLite backup API. Un proceso nuevo lee sólo el archivo SQLite
restaurado para recuperar dos revisiones, operación committed y el paquete exacto,
sin abrir packet.json, receipt.json ni el archivo fuente de reunión.

capture_complete_declared=false y selection_complete=not_established permanecen
iguales. El doble de proveedor comprueba metadatos en user y política en system.
Una llamada simulada; cero llamadas a GLM. 351 tests pasan; cuatro nuevos cubren
roundtrip Unicode/comillas/saltos, alteraciones de identidad/contenido, cambio de
completitud con hash exterior recalculado e instrucciones del wrapper.

## Límites y autorrevisión

- Recuperación del paquete es evidencia histórica, no nueva verificación del
  audio, de la fuente original ni de completitud material.
- Hashes no autentican al emisor ni resisten reescritura coherente por un atacante.
- El respaldo contiene la información de origen, pero necesita código compatible
  y el validador fijado para interpretarse. No es un formato universal de archivo.
- El sobre duplica el texto para permitir citas literales: coste de contexto mayor,
  no optimización de tokens. No se evaluó escala ni compresión de estos metadatos.
- No se evaluó semántica de GLM ante fuentes parciales; que la política llegue
  al proveedor no demuestra que se cumpla. No existe guardia semántica universal.
- Las respuestas mantienen admission=not_admitted; no hay watcher ni escritura
  en Skopos o AN-KLA. Datos sintéticos, dependencias experimentales locales.
- Se prueba una copia de SQLite y reapertura normal, no corte eléctrico, backups
  incrementales, ataques o recuperación multihost. Política ejecutada por wrapper;
  la configuración persistida de operación aún no identifica todos sus detalles.

## Siguiente comprobación propuesta

Una prueba GLM acotada de fuente parcial: preguntar por un dato ausente en la
selección pero presente en un segmento no exportado. Debe conservar el pendiente
sin convertirlo en negación global; después ampliar explícitamente la selección
para resolverlo. Conservar ambos paquetes y sus versiones. Antes de reusar una
operación entre políticas, ligar también la versión/hash de política a su identidad.

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python experiments/skopos-issue-bridge-v2/run.py /ruta/skopos experiments/skopos-issue-bridge-v2/runs/NOMBRE_NUEVO
```

Corridas y base en runs/ ignoradas. result-local-01.json contiene sólo evidencia
sintética publicable. src/agora y AGENTS.md permanecen sin cambios.
