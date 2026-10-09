---
id: intercambio-evidencia-fuentes-v1
autor: Codex
fecha: 2026-10-08
proyectos: [agora, expertoGobernanza, skopos]
estado: borrador
derivado_de: []
---

# Intercambio local de evidencia entre fuentes v1

**Estado:** incremento experimental de Ágora, 2026-10-08. No instala una
integración con Skopos ni admite memoria o corpus. Funciona sin proveedor,
Mongo ni red. Entrada y salida JSON; la CLI sólo imprime a stdout.

## Contratos

- `agora/source-evidence-exchange/v1`: un original identificado por `id`,
  `sha256`, `media_type`, `revision` declarada y `uri` opcional; un derivado UTF-8
  identificado por SHA-256, `coverage` declarada y productor. `producer.system`
  puede ser `skopos` u otro productor; `manifest_sha256` y `derivation_id` son
  referencias opcionales, no attestations. Cada segmento liga un rango UTF-8
  `[start_byte,end_byte)`, su hash, localizador, modalidad y estado de
  extracción declarado. Los huecos entre segmentos pueden contener marcadores
  editoriales; no se pueden citar como evidencia.
- `agora/source-evidence-candidate/v1`: una interpretación o relación candidata
  sobre **una** fuente. Fija el hash del manifiesto y los hashes de original y
  derivado; sus referencias deben quedar dentro de segmentos validados.
- `agora/source-evidence-bundle-candidate/v1`: relación candidata entre 2–8
  fuentes independientes. Fija cada manifiesto y exige al menos dos fuentes
  distintas por relación. No mezcla offsets ni localizadores entre fuentes.

`resolve` devuelve `agora/source-evidence-resolution/v1` y `resolve-bundle`
devuelve `agora/source-evidence-bundle-resolution/v1`. Cada evidencia resuelta
incluye texto **literal del derivado**, hash del fragmento, rango, modalidad y
localizador original declarado. El texto de la afirmación permanece aparte con
`semantic_support=not_verified`; la respuesta conserva `admitted=false` y
`provider_calls=0`. Ninguna de estas comprobaciones demuestra que la
transcripción corresponda a la imagen del PDF, que una arista visual sea una
jerarquía jurídica o que la norma esté vigente.

`--original` comprueba el SHA-256 de los bytes originales locales y devuelve
`original_integrity=sha256_verified`; sin él devuelve `not_checked`. Incluso
con ese hash verificado, página, función, modalidad y estado de extracción
siguen siendo datos del productor o del llamante. La URL no se consulta ni
acredita disponibilidad futura. El consumidor debe cotejar contra el PDF la
cita concreta que vaya a usar. Todo candidato mal formado se rechaza completo
con código 2; no se entrega un subconjunto validado.

## Ejemplo reproducible desde expertoGobernanza

Las rutas siguientes se refieren a los dos PDF custodiados por ese consumidor.
Los textos derivados y manifiestos en `examples/source-evidence-exchange-v1/`
son fixtures locales **declarados**, no exportaciones de Skopos. En el manual
`0500-002-001` se usan §8.1.3 y función 2, p45; en `2000-002-001`, §7.1.4.4.1
y función 1, p172. Ambos archivos originales fueron cotejados por SHA-256 el
2026-10-08. El candidato de relación entre manuales es una inferencia pendiente
de revisión, no una frase literal de ninguno.

```sh
cd /Users/krisnova/www/expertoGobernanza
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/krisnova/www/aria/agora/src \
  /Users/krisnova/www/aria/agora/.venv/bin/python -m agora.source_evidence_exchange resolve-bundle \
  --derived /Users/krisnova/www/aria/agora/examples/source-evidence-exchange-v1/imss-0500-derived.txt \
  --manifest /Users/krisnova/www/aria/agora/examples/source-evidence-exchange-v1/imss-0500-manifest.json \
  --original docs/fuentes/imss/0500-002-001_3.pdf \
  --derived /Users/krisnova/www/aria/agora/examples/source-evidence-exchange-v1/imss-2000-derived.txt \
  --manifest /Users/krisnova/www/aria/agora/examples/source-evidence-exchange-v1/imss-2000-manifest.json \
  --original docs/fuentes/imss/2000-002-001.pdf \
  --candidate /Users/krisnova/www/aria/agora/examples/source-evidence-exchange-v1/imss-cross-manual-candidate.json
```

Esperado: `status=candidate_unreviewed`, dos
`original_integrity=sha256_verified`, dos `source_sha256` distintos, páginas
45 y 172, modalidad `native_text`, `semantic_support=not_verified`,
`admitted=false`, `provider_calls=0`. El marcador `[omitted]` del derivado no
forma parte de ningún segmento citable.

Para comprobar independencia de Skopos, desde la raíz de Ágora:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python \
  -m agora.source_evidence_exchange resolve \
  --derived examples/source-evidence-exchange-v1/skevi-derived.txt \
  --manifest examples/source-evidence-exchange-v1/skevi-manifest.json \
  --original examples/source-evidence-exchange-v1/skevi-source.txt \
  --candidate examples/source-evidence-exchange-v1/skevi-candidate.json
```

Ese segundo fixture es **sintético**, ajeno a IMSS; demuestra la forma neutral
del contrato y la comprobación de un original de texto. No afirma que SKEVI
haya producido o aceptado ese contenido.

## Puente opcional desde una respuesta local real de Skopos

`agora.skopos_page_bridge` acepta la salida JSON de `scripts.skopos_imss page`
del consumidor y el manifiesto nativo exacto de Skopos. Antes de construir el
derivado comprueba el SHA del manifiesto, `derivation_id`, identidad del padre,
página, modalidad y que todas las líneas de la respuesta coincidan con la
página del manifiesto. Para cada `item_id` elegido produce `derived.txt` y
`exchange.json` en un directorio **nuevo**. Conserva página física, `item_id`,
`bbox`, modalidad, SHA de fuente, derivación y manifiesto. El texto permanece
`unreviewed`. El puente no inicia Skopos ni llama a un modelo.

Una vez que el controlador Skopos esté libre, el consumidor puede capturar una
respuesta operativa nueva siguiendo su contrato local y ejecutar:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/krisnova/www/aria/agora/src \
  /Users/krisnova/www/aria/agora/.venv/bin/python -m agora.skopos_page_bridge \
  --response /ruta/segura/page-172-response.json \
  --producer-manifest /Users/krisnova/www/aria/skopos/runs/pdf-document-imss-pilot-v1/derived/372fdaef7fb1171ec8dce708b79ef1e32b38e43dfb1b079e6b27ae070d8f7587/manifest.json \
  --item-id 6a7a856c86bf4790f1ddf067c6d72bf2b79c2d435f2c2f9b1ee32c78abcaff6d \
  --out-dir /ruta/nueva/agora-skopos-page172
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/krisnova/www/aria/agora/src \
  /Users/krisnova/www/aria/agora/.venv/bin/python -m agora.source_evidence_exchange validate \
  --derived /ruta/nueva/agora-skopos-page172/derived.txt \
  --manifest /ruta/nueva/agora-skopos-page172/exchange.json \
  --original /Users/krisnova/www/expertoGobernanza/docs/fuentes/imss/2000-002-001.pdf
```

La captura operativa debe respetar el bloqueo, política y apagado del contrato
Skopos del consumidor; estos comandos posteriores sólo leen la respuesta y el
manifiesto. Una respuesta autocontenida falsa que se haga coincidir con un
manifiesto controlado por el mismo actor no acredita una ejecución real ni
autenticidad del productor. Para probar bilateralidad hay que conservar la
procedencia de la respuesta operativa y su ejecución identificable.

## Límites de esta versión

El validador fija integridad local de bytes, esquema, rangos UTF-8 y asociación
de candidatos con manifiestos. No verifica semántica, localizadores dentro de
un PDF, fidelidad visual, autoría del productor, vigencia, permisos de
transmisión ni la cobertura declarada. La fuente derivada está limitada por
`FileSourceAdapter` a 16 MiB; manifiesto y candidato a 1 MiB cada uno; un
original opcional a 64 MiB. Los localizadores de PDF conservan página y campos
de contexto. El consumidor conservó un intercambio bilateral real de p45
del manual 0500 y p172 del manual 2000, con `bbox` e `item_id`, en
`/Users/krisnova/www/expertoGobernanza/docs/evidencia/imss-0500-bilateral-2026-10-08/`.
Ese paquete acredita compatibilidad local observada; no demuestra fidelidad
semántica ni independencia del productor. La validación después de reinicio
consiste en releer los mismos archivos y hashes; no hay almacén ni servicio nuevo.
