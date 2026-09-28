# Skopos -> cuestión recuperable: paquete sintético

28 de septiembre de 2026. Se ejecutó el exportador experimental real de Skopos
(commit 5773dbd) sobre un archivo sintético creado en la corrida de Ágora.
MeetingStore fue efímero; no se modificaron archivos ni Mongo de Skopos.

El consumidor comprueba hash de contenido, rangos UTF-8, reconstrucción exacta
del texto y cada localizador contra fetch de Skopos. La identidad local incluye
el hash del paquete completo. El recibo conserva fuente/revisión/hash originales,
localizadores y declaraciones de completitud. Citas vuelven al segmento nativo.

Resultado local-01: dos citas navegables, dos revisiones de cuestión, operación
recuperada después de reabrir conexión, una llamada simulada, cero llamadas LLM.
Se mantuvieron capture_complete_declared=false y selection_complete=not_established.
347 tests pasan; tres nuevos cubren rangos, contenido, localizadores alterados,
origen no disponible y citas sin segmento. Es prueba de integración contractual,
no evaluación nueva de capacidad semántica del modelo.

## Límites relevantes

- Contrato experimental skopos/meeting-evidence-packet/v0, no conector productivo.
- Paquete y recibo se conservan junto a SQLite, ligados por hash en source_id.
  El historial por sí solo no contiene toda la procedencia nativa ni las etiquetas
  de completitud; tampoco se suministran estas etiquetas al proveedor del flujo
  v1. Este puente NO demuestra razonamiento consciente de completitud.
- Antes de una integración real se requiere conservación conjunta, recuperación
  por hash y exposición explícita de esos metadatos al consumidor.
- El evaluador es un doble determinista; no sustituye una prueba GLM sobre paquete.
- fetch verifica bytes frente a su índice; no autentica origen ni autor.
- El lector requiere una revisión por paquete y citas dentro de un segmento.
  No resuelve citas que cruzan segmentos ni búsqueda semántica.
- Skopos permanece independiente; no hay escritura cruzada, vigilancia ni AN-KLA.

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python experiments/skopos-issue-bridge-v1/run.py /ruta/skopos experiments/skopos-issue-bridge-v1/runs/NOMBRE_NUEVO
```

result-local-01.json es sintético y publicable. runs/ mantiene base y paquete
locales ignorados. Los hashes de los dos archivos ejecutados de Skopos figuran
como evidencia; el puente no modifica ni publica el trabajo pendiente de Skopos.
