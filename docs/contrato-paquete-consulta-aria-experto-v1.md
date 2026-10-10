---
id: contrato-paquete-consulta-aria-experto-v1
autor: Codex
fecha: 2026-10-10
proyectos: [agora, expertoGobernanza, skopos]
estado: borrador
derivado_de: []
---

# Paquete de consulta Ágora → ARIA → expertoGobernanza v1

**Estado:** contrato productor implementado en Ágora; adopción por ARIA y
expertoGobernanza pendiente. No sustituye el contrato de recuperación de
Skopos ni el gate de citas del consumidor.

## Frontera funcional

Ágora puede recibir **una fuente UTF-8 fijada por SHA-256**, generar un
candidato con GLM, revisar respaldo/pertinencia/cobertura y, si se solicita,
pedir un consejo adicional a Jev sobre cada afirmación y sus citas. La entrada
`scripts/agora.py` expone `answer`, `answer-v2`, `jev-review` y `export-answer`. Estas
operaciones funcionan sin AN-KLA y no requieren un runtime central de ARIA.

`export-answer` produce `agora/consultation-package/v1-experimental` para citas
de un solo segmento y respuestas sin faltantes; el esquema v2 experimental
representa varios segmentos contiguos y conserva los faltantes declarados y
el posible conflicto con la revisión de cobertura. El
consumidor obtiene pregunta y requisitos, afirmaciones, citas literales y
rangos UTF-8, etiquetas GLM/Jev separadas, cobertura, diagnóstico y hashes
del recorrido. Puede reconstruir y verificar el paquete con
`--verify-package` usando los mismos artefactos. La salida conserva
`requires_review`; ningún resultado de modelos admite memoria, cita jurídica
o interpretación institucional.

La integración en ARIA consiste en consumir este contrato **sin mover la
custodia de fuentes a Ágora**: Skopos entrega original y derivado verificables;
Ágora transforma y revisa candidatos; expertoGobernanza decide si una cita
sirve a su pregunta y gate. No se exige que EKTEL, AN-KLA o un proveedor de IA
se conviertan en dependencias exclusivas del paquete.

## Condición para citas institucionales

Un paquete producido sobre texto manual, como el [caso CTIM 18–22](../experiments/answer-entry-ctim-v1/README.md),
tiene `original_integrity=not_established`. Es útil para estudiar la pregunta,
pero **no** habilita citar el PDF original como si Ágora hubiese verificado
la transcripción o su localizador.

Para que expertoGobernanza evalúe una cita de PDF/HTML, el productor debe
entregar un `agora/source-evidence-exchange/v1` validado con el original local:
SHA del original y derivado, segmentos y localizador físico o de bytes por
segmento. `export-answer --exchange ... --original ...` acepta una cita que
cruce segmentos **contiguos** si representa cada rango y localizador por
separado; rechaza huecos como `[omitted]` y citas no literales. El paquete
entonces indica `original_integrity=sha256_verified` y lleva página,
`item_id`/`bbox` o rango HTML **declarados por el productor**. El consumidor
aún coteja visualmente la relación actor–actividad, vigencia y pertinencia.

El puente `skopos-page-v02` acepta `read_pdf_page` de Skopos CTIM v0.2,
solicitud y respuesta guardadas, SHA esperado del manifiesto fijado en la
política del productor, manifiesto y PDF original local. Comprueba
hash de solicitud, manifiesto y original, identidad, geometría y líneas contra el
manifiesto; selecciona `item_id` explícitos y emite `derived.txt` y
`exchange.json`. No consulta Skopos ni decide orden visual o responsables.
Los controles positivos y las mutaciones de texto, `bbox`, página, geometría,
solicitud y SHA pasan en fixtures. El [ensayo CTIM de la página 15](../experiments/ctim-v02-bilateral-v1/README.md)
también consumió una respuesta real v0.2 y comprobó el PDF local. El recorrido
real produjo un candidato parcial: la cita global cruza `[omitted]` y no puede
exportarse con atribución PDF; el control offline con 41 segmentos contiguos sí
verificó la estructura. La consistencia de estos archivos no acredita por sí
sola la custodia remota de Skopos ni la semántica de la respuesta.

```sh
.venv/bin/python scripts/agora.py run skopos-page-v02 \
  --request request.json --response response.json \
  --producer-manifest manifest.json --manifest-sha256 SHA_FIJADO \
  --original original.pdf \
  --item-id ITEM_ID --out-dir page-exchange
```

## DoD bilateral antes de consumo por expertoGobernanza

1. El productor Skopos entrega la misma página y original bajo el contrato
   v0.2, con manifiesto y recibo fijados; Ágora ejecuta `skopos-page-v02`
   sobre esos bytes sin reinterpretar el orden visual.
2. Ágora responde y exporta el paquete desde ese **mismo derivado**; todos los
   bytes citados caen en uno o varios segmentos contiguos con localizadores y
   el paquete se verifica offline. Ninguna cita atraviesa `[omitted]`.
3. expertoGobernanza compara la respuesta con su línea base léxica sobre la
   misma pregunta, mismos pasajes y presupuesto. Registra omisiones,
   atribuciones, falsas alarmas, citas, tiempo y llamadas.
4. Un revisor coteja el PDF y decide si cada afirmación y cita sirven al gate
   del consumidor. Los juicios GLM y Jev se muestran por separado, con
   desacuerdos intactos. Jev no veta una afirmación sólo por etiquetar
   `unsupported`: ya confundió dos listas verdaderas pero incompletas.
5. La decisión del consumidor sobre N1–N5 y la activación institucional se
   registran aparte. El preflight `repair` histórico no se convierte en
   aceptación por el ensayo posterior.

Este DoD describe el siguiente incremento, no declara que ya se superó.
En el repositorio de expertoGobernanza hay trabajo local ajeno sin seguimiento;
esta entrega no lo modifica ni atribuye su contenido a Ágora.
