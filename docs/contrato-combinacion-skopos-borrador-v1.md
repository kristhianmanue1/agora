# Contrato de combinación Skopos ↔ Ágora: entrada de evidencia (borrador v1)

**Estado:** borrador aceptado por el Operador, 2026-10-19. La decisión está
registrada; la vigencia espera sus dos puertas restantes: la verificación
bilateral sobre salidas reales (Skopos confirma respuesta y manifiesto;
Ágora confirma derivado, segmentos y localizadores contra el original) y un
caso reservado no usado por el desarrollo del puente. Nada de este documento
cambia los contratos existentes ni activa integración alguna.

## Dirección y objeto

Skopos conserva fuentes; Ágora transforma y consulta. El contrato cubre **una
sola dirección**: evidencia que entra de Skopos a Ágora. Ningún comando de
Ágora escribe en Skopos, ni en sus almacenes ni en sus colas.

Cruzan la frontera, todos fijados por hash antes de usarse:

- la solicitud Skopos (`request.json`) y su respuesta — hoy sólo respuesta
  CTIM **v0.2**;
- el manifiesto Skopos con el SHA-256 esperado del original;
- el original local (p. ej. el PDF IMSS del piloto);
- los item IDs seleccionados.

## Contratos que lo componen, sin crear otros nuevos

La combinación no inventa un esquema propio: versiona la composición de los
que ya existen:

1. `agora/source-evidence-exchange/v1` — el derivado declara
   `producer.system = skopos`, cobertura y, desde el incremento del
   2026-10-19, su cadena `transformations` versionada.
2. `skopos-page-v02` — la herramienta que construye `derived.txt` y
   `exchange.json` desde la respuesta v0.2.
3. `agora/claim-evidence-query/v2` con `citation_mode = ids` — el consumo del
   intercambio por la consulta.

## Puertas de validación (fallan cerrado)

- Verificación del hash del original y del derivado; segmentos validados por
  rango y hash; huecos no citables.
- Localizadores de página: toda cita debe mapear a un segmento con
  localizador. El rechazo `citation_unmapped_to_exchange` observado en el
  [ensayo bilateral](../experiments/ctim-v02-bilateral-v1/README.md) es el comportamiento
  correcto y sigue siéndolo: una unidad de evidencia que abarque un salto sin
  segmento no se exporta como si tuviera vínculo con el original.
- Control negativo: fuente alterada tras fijar su revisión se rechaza antes
  de despachar (escenario S6 de la batería de calidad).
- La inspección de texto extraído sin revisión visual conserva
  `extraction_status = unreviewed`; nunca se promociona solo por cruzar la
  frontera.

## Política de versiones

- Cambiar la versión de respuesta aceptada (v0.2 → otra) exige una puerta
  nueva y un ensayo bilateral propio; no es un cambio compatible hacia atrás.
- El intercambio v1 evoluciona de forma aditiva y retrocompatible
  (`transformations` es el precedente); un cambio que rompa manifiestos
  existentes exige v2 y decisión explícita.

## Criterios para pasar de borrador a vigente

1. Verificación bilateral sobre salidas reales: Skopos confirma que la
   respuesta y el manifiesto son los suyos; Ágora confirma derivado,
   segmentos y localizadores contra el original.
2. Un caso reservado no usado por el desarrollo del puente.
3. Decisión escrita del Operador; el contrato se publica entonces en el
   manifiesto del proyecto.

## No-objetivos

OCR automático, ingesta universal de formatos, escritura en Skopos,
vigilancia de cambios del original o admisión automática de candidatos.
