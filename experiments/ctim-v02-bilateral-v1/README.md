# CTIM: prueba bilateral Skopos v0.2 → Ágora `answer-v2`

Fecha: 2026-10-10. Ensayo local sobre la página 15 del PDF IMSS
`2900-003-001.pdf` (SHA-256
`141d9b090efa4d70799ee1368350a5167347b4e8cd5f99912fb192ce6c704faa`).
Skopos devolvió 41 líneas nativas en `response.json`, a partir de
`request.json`; `exchange-v2/` conserva la página textual completa y
`exchange-focused/` selecciona roles y actividades 18–22. La selección y los
saltos están en `selection-focused.json`. La inspección visual local del PDF
asignó la actividad 18 a CPIM y 19–22 a CTIM; esa asignación **no queda
codificada** en el texto de `exchange-focused/derived.txt`.

Los intentos `01`–`05` documentan: credencial heredada rechazada con HTTP 401;
tres generaciones agotadas con 4096 tokens; y una petición nominal GLM-4.7
que recibió `reported_model=glm-5.3-flash` y fue rechazada por discordancia.
No se atribuye esa respuesta a GLM-4.7. Los intentos `06` y `07` usaron el
recorrido v2; `06` terminó en respaldo por el presupuesto inicial de 4096,
y `07` recibió JSON seguido de `</br>` en generación. La prueba
`offline-normalization-probe/` mostró que retirar exclusivamente ese sufijo
permite validar aquel candidato; no constituye una revisión completa en vivo.

`flow-2026-10-10-08-normalized-v2/` es la ejecución posterior en vivo con
GLM-5.3-Flash solicitado y también reportado por el proveedor. Terminó con
`candidate_reviewed`, cinco despachos y etapas de generación, respaldo,
pertinencia, cobertura y omisiones completas. Los límites solicitados fueron
16 384, 16 384, 8 192, 4 096 y 8 192 tokens, respectivamente. La generación
consumió 7802 tokens de salida (6790 de razonamiento). El candidato contiene
ocho afirmaciones, pero marca como faltante la asignación CPIM/CTIM: el texto
no conserva las columnas visuales. `candidate_reviewed` sólo significa que
terminó el recorrido, no que la respuesta sea suficiente para el Operador.

`package-2026-10-10-08-text-only/` exporta y verifica offline las ocho
afirmaciones, sin afirmar vínculo de cada cita con un localizador PDF. El
intento de exportar con `exchange-focused/exchange.json` falló con
`citation_unmapped_to_exchange`: la unidad de evidencia generada abarca el
pasaje entero y cruza varios segmentos, incluido un salto `[omitted]`. No se
relajó el validador para atribuir una cita global a una línea PDF concreta.
La salida textual es una candidata para revisión, no una respuesta CTIM
aceptada ni una integración activada en expertoGobernanza.

## Corrección de exportación y control offline

La exportación v2 representa una cita que ocupa segmentos contiguos mediante
`segment_refs` con rangos y localizadores individuales. El control
`offline-full-page-control-v2/` usa `exchange-v2/derived.txt` sin saltos y un
proveedor **sintético local** identificado como `offline-fixture`: no hubo
llamadas de modelo ni se adjudicó su afirmación.
`package-offline-full-page-control-v2/` se exportó y verificó con el
PDF original, `original_integrity=sha256_verified` y 41 referencias contiguas
a líneas de la página 15. Esto comprueba el vínculo estructural, no la
fidelidad semántica ni la revisión visual de cada línea.

El recorrido real `flow-2026-10-10-08-normalized-v2/` continúa fallando al
exportar **con** `exchange-focused/`: su cita global cruza `[omitted]`, que no
es evidencia de Skopos. `package-2026-10-10-08-text-only-v2/` exporta el mismo
recorrido **sin** atribución PDF. Expone `candidate_answer_status=candidate_partial`,
los seis faltantes declarados, `coverage_advice=complete` y
`candidate_coverage_conflict=true`, con `disposition=requires_review`. El
paquete textual v1 anterior permanece como recibo histórico; no representa
este conflicto nuevo.

La ejecución de Skopos requirió el almacén local; el primer intento sin él
quedó en `response-store-unavailable.json`. El recibo
`runtime-receipt.jsonl` corresponde a un arranque fallido del supervisor;
la respuesta final se obtuvo tras arrancar directamente el controlador de
custodia y el host CTIM y se detuvieron ambos al terminar. Los recibos de
modelo registran lo solicitado y lo reportado, no prueban identidad efectiva
independiente ni facturación.
