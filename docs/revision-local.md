# Revisión local de respuestas — v0.1

## Resultado y límites

`python -m agora.review` genera HTML estático o registra un dictamen técnico
separado; no llama modelos ni escribe AN-KLA. Acepta resultados `source-query/v0.3`
de fuente directa y selección literal. Los resultados anteriores v0.2 de síntesis
se rechazan explícitamente: no se reinterpretan en silencio.

La CLI `agora.query` usa fuente directa cuando se omite `--mode` y no se dan
argumentos de síntesis. Con `--summary-run` o `--run-sha256` conserva el modo legado.
El API Python conserva su valor por defecto anterior. No hay selección automática.

## Generar una vista

```bash
PYTHONPATH=src python3 -m agora.review render \
  --source fuente.txt --sha256 HASH_FUENTE \
  --run resultado.json --run-sha256 HASH_RESULTADO --out candidata.html
```

La página contiene pregunta y partes, respuesta candidata, citas navegables,
fuente numerada y contexto entregado con tamaños. En extractos distingue las
apariciones presentes en el contexto enviado de las externas. Las coincidencias
repetidas/solapadas son referencias literales posibles, no prueba de cuál usó el
modelo. Los bytes de documento no representan coste total ni tokens.

Una salida rechazada/fallida muestra su estado y diagnóstico; no presenta el
contenido raw como respuesta útil ni permite registrarle dictamen favorable.
Una vista generada es una copia estática; no vigila cambios futuros en disco.
No publicar ni compartir automáticamente: puede contener toda la fuente.

## Registrar un dictamen explícito

Preparar una nota con hallazgos, citas relevantes, alcance y limitaciones:

```bash
PYTHONPATH=src python3 -m agora.review record \
  --source fuente.txt --sha256 HASH_FUENTE \
  --run resultado.json --run-sha256 HASH_RESULTADO \
  --reviewer 'Identificador del revisor' --decision uncertain \
  --note-file nota.txt --out dictamen.json

PYTHONPATH=src python3 -m agora.review render \
  --source fuente.txt --sha256 HASH_FUENTE \
  --run resultado.json --run-sha256 HASH_RESULTADO \
  --judgment dictamen.json --judgment-sha256 HASH_DICTAMEN --out revisada.html
```

Decisiones: `supported` (apoyada por fuente), `unsupported` (no apoyada),
`uncertain` (requiere aclaración). No equivalen a verdad externa, aceptación del
Operador, aprobación clínica ni admisión en memoria. Identidad del revisor es
`caller_declared`, no autenticada. Un consumidor debe validar su propia autoridad;
un JSON o un hash no la concede. Las salidas se crean exclusivamente, sin
sobrescribir archivos existentes. Los hashes se obtienen de archivos exactos,
no de una reserialización supuestamente equivalente.

## Qué comprueba el programa

Fuente UTF-8 y hash, hash exacto del resultado, esquema/ruta soportada, vínculo
entre fuente/contexto/pregunta/partes y reconstrucción de respuesta desde el raw.
Reproduce validación estructural con proveedor simulado que sólo devuelve la
respuesta almacenada; no ejecuta herramientas ni llamadas indicadas por datos.
Reconstruye la selección literal embebida y sus offsets. Dictamen ligado a hashes
de fuente y resultado; cambios o flags de identidad/admisión no admitidos fallan.
El HTML escapa datos y no contiene scripts ni recursos remotos.

No autentica la ejecución histórica, el prompt del sistema ni el productor.
El hash externo del resultado fija los bytes recibidos, no acredita su origen.
No comprueba el hash del archivo de selección original (ese archivo no se recibe);
sí reconstruye y compara el contenido embebido. No certifica soporte semántico.
Una vista vieja puede seguir mostrando un dictamen viejo: regenerar con archivos
y hashes actuales para detectar divergencias. No hay vigilancia automática.

## Verificación del incremento

76 pruebas locales pasaron: 61 anteriores y 15 nuevas. Cobertura: rutas directas
y extractivas, alteración de respuesta/prompt/raw, deriva de fuente, dictámenes
obsoletos, identidad/admisión indebida, HTML escapado, citas repetidas y contexto,
rechazos sin rescate, CLI de registro/render y no sobrescritura. Sin red/GLM.

Revisión separada de `/root/review_real_excerpt`: se explicitaron límites del
prompt histórico y hash original de selección; se distinguieron apariciones fuera
del contexto y se incluyeron solapamientos. No promueve aprobación semántica.

Demostración local en `experiments/source-query-pilot/inputs/runs/revision-local-v1/`:
`candidata.html`, `revisada.html`, `dictamen.json` sobre N3-extract-2 sintético;
`rechazada.html` sobre R5-source rechazado. Dictamen técnico declarado por el
coordinador con revisión separada anterior; no adjudicación humana. Originales
congelados sin cambios. La prueba visual mediante navegador no pudo realizarse:
su política bloqueó la URL local file. No se eludió la restricción; la verificación
de esta entrega es funcional y de contenido HTML, no inspección visual renderizada.

Sin nuevas dependencias, instalación, publicación, commit/push, contexto canónico
o memoria persistente. Cambios anteriores del árbol se conservan.
