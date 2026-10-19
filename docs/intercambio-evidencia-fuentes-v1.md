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
  referencias opcionales, no attestations. El derivado puede declarar además
  `transformations`: una cadena ordenada de hasta ocho pasos
  `{operation, version}` que describen cómo se produjo (extracción, OCR,
  alineación, normalización). Es metadato declarado por el llamador, no
  atestiguado; su ausencia significa «no declarado», no «sin transformaciones».
  Cada segmento liga un rango UTF-8
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
incluye texto **literal del derivado**, hash del fragmento, rango, modalidad,
localizador original declarado y la cadena `transformations` del derivado
(lista vacía cuando no fue declarada). El texto de la afirmación permanece aparte con
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

### Extensión compatible de perfiles tipados

El mismo esquema v1 admite un perfil ampliado sin cambiar las formas anteriores:

- `source.temporal`, si existe, es exactamente
  `{"document_date": <fecha declarada o null>, "status": "not_assessed"}`.
  Conserva un dato temporal declarado; no admite ni produce `vigente`,
  `derogado`, prioridad, jerarquía o una conclusión jurídica.
- `derivative.normalization`, si existe, es independiente del literal:
  `{"status": "not_applied" | "applied", "description": <null o texto>}`.
  La salida conserva por separado el literal del derivado, el SHA del literal y
  esa declaración de normalización. Una normalización declarada no prueba que
  sea reversible ni fiel al original.
- En el perfil ampliado, los únicos medios fuente admitidos son `application/pdf`, `text/plain;
  charset=utf-8`, `text/markdown; charset=utf-8`, `text/html; charset=utf-8`
  y `text/html; charset=iso-8859-1`. El HTML DOF 2021 conserva su codificación
  original; el derivado entregado a Ágora sigue siendo UTF-8.
  El contrato sigue validando un derivado UTF-8 fijado por hash; no extrae PDF ni
  HTML, no hace OCR y no comprueba que el derivado transcriba visualmente al
  original.
- En ese perfil, los localizadores admitidos son `pdf_page` (requiere `page`), `text_range`
  (requiere rango UTF-8) y `html_fragment` (requiere `selector` o rango de bytes
  del original; puede conservar ambos e `item_id`). Ágora valida la forma del
  rango; el consumidor coteja offsets y hash contra el HTML original. Los
  anclajes `section`, `activity` y `article` son tipados como entero no negativo
  o texto no vacío. `function` y `bbox` quedan restringidos a `pdf_page`;
  `item_id` también se admite en `html_fragment` cuando lo produce Skopos.
  Un localizador de conversación o de DOCX se rechaza cerrado en este perfil.
  La forma heredada conserva la aceptación genérica anterior para no romper
  consumidores v1, pero no acredita soporte de extracción, localización tipada
  ni validación de esos formatos.

Un `bundle` puede añadir a cada relación candidata un objeto `relation` con
`kind`, `temporal_status`, `identity_status` y `normalization`. Los cuatro tipos
admitidos son `cross_source_candidate`, `temporal_conflict_candidate`,
`identity_unresolved_candidate` y `version_relation_candidate`; ambos estatus
sólo aceptan `not_assessed`. Este último añade `version_relation` con `amends`,
`amended_by`, `supersedes` o `superseded_by`. Es una relación declarada por el
candidato: no adjudica vigencia, ni se infiere desde una URL, fecha o nombre de
archivo.
Un candidato temporal exige al menos dos fechas documentales declaradas y
distintas. Eso comprueba forma y evita convertir una diferencia de fechas en
vigencia. La identidad institucional tampoco se deduce: `identity_unresolved`
conserva precisamente la ausencia de adjudicación.

## Escenario IMSS declarado: cinco fixtures y siete originales registrados

El contrato se probó localmente con cinco **fixtures declarados**, no con
transcripciones ni PDFs reales. Conservan los SHA-256 suministrados para el
Manual DPM `2000-002-001` y el manual IMSS `0500-002-001` ya presentes en el
intercambio anterior, más los tres nuevos identificadores:

| Fuente declarada | Medio | SHA-256 declarado | Fecha declarada de fixture | Localizador ejercitado |
|---|---|---|---|---|
| DPM `2000-002-001` | PDF | `719d6da341bff3733750f05357de50ca09fabc7c31c4354186dae8a7a3a70323` | 2025 | página, sección, actividad |
| IMSS `0500-002-001` | PDF | `ce665959759f74331464471c71dc9cff107e061de09b8be5419a7cf1302e48b7` | 2022 | página, sección, actividad |
| DA `1000-002-001` | PDF | `2578bc3df7bafaefd250e971e0087f1b28dc5e9878ed343e8159a23e22d8de49` | 2025 | página, sección, actividad |
| Procedimiento `2900` | PDF | `141d9b090efa4d70799ee1368350a5167347b4e8cd5f99912fb192ce6c704faa` | 2021 | página, actividad |
| DOF HTML `5625913` | HTML ISO-8859-1 | `e088234e624a6172a7e85eb0aed5c338b55c84e399b6ea086cd326f85ddc580e` | 2021 | selector HTML, artículo |

La prueba crea un `temporal_conflict_candidate` para contrastar 2021 y 2025,
pero su salida conserva `temporal_status=not_assessed`,
`semantic_support=not_verified` y `admitted=false`. Por tanto, **no prueba**
que haya conflicto jurídico, cuál texto sea vigente o qué fuente prevalece.

Una segunda relación usa `identity_unresolved_candidate` entre DPM y DA. La
información recibida para diseño indica que el manual DA nombra a la División de
Equipo Médico de la Coordinación Técnica de Planeación de Infraestructura Médica,
mientras DPM nombra a CPIM y a la Coordinación Técnica de Infraestructura Médica.
Esa declaración no demuestra identidad institucional; el contrato la conserva
como cuestión sin adjudicar y no transforma las denominaciones en equivalencia.

Después de elaborar esos cinco fixtures, expertoGobernanza registró dos
originales más en `main` (`d681288`): el PDF POBALINES `1000-001-029`
aprobado en 2022 (`aae49eb2ed265e6379777287afff2f97b42a754aa20ea83acce642adde207843`)
y el acuerdo DOF publicado en 2023
(`7818f222365e5ef02d1a20a85a0604568b3983e53be6ea8e14b6bee0a7a06532`).
El transitorio tercero del acuerdo declara sin efectos la versión de 2021;
el registro y el análisis del consumidor documentan esa relación. Estos dos
originales no se ejercitan en los fixtures de esta suite. Si el consumidor
aporta sus literales y localizadores verificados, puede formular una relación
`version_relation_candidate` con `version_relation: supersedes`; Ágora sólo
validará estructura y hashes, sin adjudicar por sí misma vigencia jurídica.

Los fixtures siguen siendo declaraciones y su `original_integrity` permanece
`not_checked`: no son una exportación ni una transcripción de esas fuentes. Sin
embargo, en esta revisión se recalcularon localmente los SHA-256 de los cinco
originales en expertoGobernanza, en el commit externo `7e2c45e`, y coincidieron
con la tabla. Eso acredita únicamente identidad de bytes de esas copias locales,
no los literales de fixture, su localización, cobertura, vigencia o jerarquía.
Para una evidencia utilizable, el consumidor debe suministrar el archivo local
original a `--original`, obtener `sha256_verified` y cotejar el pasaje visual o
textual.

## Capacidad actual y hueco futuro

**Implementado y probado localmente:** asociación de un original PDF, texto o
HTML por SHA-256 con derivados UTF-8; literales por rango; perfiles de
localizador anteriores; declaración temporal sin inferencia; candidatos de
relación temporal, identidad no resuelta o versión declarada; rechazo cerrado
en el perfil tipado de medios y localizadores no soportados. Todo funciona sin Skopos, corpus, memoria,
proveedor, vector o red.

**No implementado:** extracción PDF/HTML, OCR, verificación visual de página,
parsing de DOCX, modelo de conversaciones, mapeo de una conversación a turnos,
validación semántica, detección de conflictos, vigencia, jerarquía normativa,
identidad institucional, corpus o admisión en memoria. DOCX y conversaciones
son extensiones futuras posibles mediante nuevos perfiles de `media_type` y
`locator`, con versión, extractor y pruebas propias; no se aceptan por el mero
hecho de que el contrato sea extensible.

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
