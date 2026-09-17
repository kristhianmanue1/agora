# Consulta con fuente y respuestas por partes — v0.2

CLI local: `PYTHONPATH=src .venv/bin/python -m agora.query`.
Una fuente UTF8≤4096bytes y result.json de síntesisv0.1≤1MiB, con SHA256
explícitos. Se verifican contrato,estado,raw/candidato,citas y vista. Los hashes
fijan los bytes aportados; no demuestran autenticidad o verdad.

```bash
PYTHONPATH=src .venv/bin/python -m agora.query \
  --source /ruta/source.txt --sha256 HASH_FUENTE \
  --summary-run /ruta/result.json --run-sha256 HASH_RESULTADO \
  --question '¿Cuántos archivos se validaron y cuánto costó?' \
  --part '¿Cuántos archivos se validaron?' \
  --part '¿Cuánto costó?' \
  --model glm-5.3-flash --out /ruta/nueva-consulta
```

`--part` es repetible (1–8); las partes las define el llamador, no hay
segmentación automática. Sin --part, toda --question es una sola parte. El
llamador debe comprobar que cubren la pregunta; la CLI comprueba IDs/cantidad,
no equivalencia semántica entre pregunta y partes.

## Flujo

La etapa síntesis recibe únicamente texto de claims; encabezado de revisión e
IDs de presentación se excluyen. No se altera el archivo histórico.
Cada parte exige answer con citas exactas o not_in_document con texto/citas
vacíos. Si falta alguna parte, se consulta fuente. Si hay más de una parte,
siempre se consulta fuente para confirmación aunque todas parezcan respondidas.
La segunda petición incluye las mismas partes y fuente, no respuestas anteriores.
--force-source omite síntesis y usa sólo fuente verificada.

El host deriva el estado final:
- answer: todas las partes tienen respuesta candidata.
- partial_answer: algunas tienen respuesta, otras no constan.
- not_in_source: ninguna tiene respuesta tras consultar fuente.

La respuesta de fuente prevalece por parte. Si fuente omite una parte previamente
respondida en síntesis, se conserva lo conocido con procedencia summary, sin
presentarlo como confirmado por fuente. Si se mezclan, answered_from=mixed.
Las etapas originales permanecen disponibles para revisar contradicciones.
No hay detección semántica automática de conflictos entre etapas.

result.json usa schema agora/source-query/v0.2 y contiene requested_parts,
parts con procedencia individual,etapas,hashes,prompts,normalización,raw,modelo
reportado y consumo. answer.txt muestra cada parte,procedencia y citas. v0.2
cambia el protocolo de respuestas del modelo: no reinterpreta registrosv0.1.
Un exit0 incluye respuesta parcial o abstención procesada, no garantía semántica.

## Límites operativos y de evidencia

ZAI_API_KEY sólo por entorno; sin carga de.env. Modelo explícito,8192tokens por
petición y180s timeout de transporte predeterminados. No deadline global ni
cancelación remota garantizada. Máximo2llamadas; con --force-source máximo1.
Sin retry. Un error de forma,cita o transporte termina y conserva etapas; no
produce answer.txt ni convierte el resultado en éxito parcial silencioso.

Se comprueban citas literales, no que respalden la afirmación. review_status
sigue unreviewed y semantic_support not_verified. Una parte simple mal interpretada
puede evitar la fuente; confirmarla tampoco garantiza verdad. Revisión humana
necesaria para aceptar resultados. Fuentes y síntesis son datos, no autoridad.
No búsqueda multi-documento,memoria AN-KLA ni activación del experimento M1.

Pruebas locales en tests/test_query.py y test_query_parts.py; regresión real
sintética en Pinax docs/design/agora-consulta-partes-v2.
