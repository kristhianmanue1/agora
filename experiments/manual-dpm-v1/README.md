# Manual DPM: prueba documental local (2026-09-28)

**Actualización:** la fase real autorizada ya se ejecutó; véase [LIVE.md](LIVE.md). El resto de este archivo conserva el protocolo y los hallazgos de la fase local previa. Las menciones al bloqueo y a cero llamadas describen esa fase histórica.

**Incremento posterior:** [recuperación por subpreguntas](../../docs/subpreguntas.md), con resultados locales en `subquestions-results.json`.

**Generación conectada:** [evaluación y rechazo conservado](../../docs/generacion-desde-plan.md), `generation-result.json`.

## Resultado y alcance

El PDF `2000-002-001.pdf`, Manual de Organización de la Dirección de Prestaciones Médicas, sirve como caso de documento largo: **188 páginas, 391.299 bytes de texto UTF-8 y aproximadamente 54.658 palabras**. El conteo incluye encabezados, pies y marcadores; no es un conteo de tokens. No demuestra escalabilidad a corpus mayores ni vigencia jurídica del documento.

La interfaz pública pudo preparar, inspeccionar, crear una revisión derivada y recuperarla para cuatro casos. Las respuestas utilizadas son **simuladas**: verifican persistencia y trazabilidad, no capacidad de GLM ni Jev. En los cuatro casos el hash del padre permaneció idéntico y la recuperación devolvió el mismo hash derivado. No hubo llamadas a proveedores ni respuesta global generada.

La ejecución externa quedó bloqueada por revisión automática: solicita autorización explícita para transmitir fragmentos de este documento a Z.AI/GLM y Typesafe/Jev. No se intentó otra vía. El presupuesto propuesto es ocho revisiones (cuatro por proveedor) y una generación global con GLM, sin reintentos. No se consumieron tokens de estos proveedores en este experimento.

## Método fijado

- Código base: `8fe65603ee4bf8416c424ef76abc7f39af854ad1`.
- Texto extraído con pypdf, sin OCR, preservando orden y marcadores `[PDF page N]`.
- Identidad del PDF, texto y mapa de offsets: `extraction.json`.
- Recuperación léxica: presupuesto 12.000 bytes, `top_k=3`, pregunta y afirmación para las revisiones; pregunta sola para la consulta global.
- Criterios preparados antes de cualquier llamada real. Casos diseñados por el productor; no son benchmark reservado ni adjudicación independiente.
- Los originales importados contienen solamente identificación del manual y una respuesta simulada `insufficient`; no se presentan como fallos previos de un modelo.
- Las páginas fueron revisadas selectivamente (portada, organigrama y secciones relevantes); no hubo cotejo visual exhaustivo de las 188 páginas.

## Hallazgos

| Caso | Evidencia documental | Recuperación observada | Resultado esperado sobre fragmentos |
|---|---|---|---|
| Normas | Página 170 | Texto de 122, 170, 177; 7.639 bytes | supported |
| Exclusión de cocina/comedor | Página 177 contradice la exclusión | Texto de 171, 177, 178; 7.645 bytes | contradicted |
| Dos responsabilidades | Requiere 170 y 177 | Texto de 146, 171, 177; 8.315 bytes; falta 170 | insufficient |
| Fecha de sello | Visible en portada, sin texto extraído | Texto de 7, 8, 9; 10.340 bytes; sin sello | insufficient |

`selected_pages` cuenta solapamientos, incluidos marcadores sin cuerpo de página. `selected_content_pages` distingue el contenido sustantivo. Contar un marcador como evidencia de toda la página sería un error de evaluación.

La portada no produjo texto. El organigrama de la página 18 conservó encabezados pero perdió nodos y conexiones. Que una página produzca algún texto **no demuestra extracción completa**. La fecha visible en el sello no se incorporó silenciosamente a la fuente textual.

La consulta global seleccionó texto de las páginas **6, 152 y 186**, con 6.513 bytes, sin recuperar las páginas de responsabilidades fijadas como referencia (25, 87, 109, 146, 182 y 184). Cobertura de esas seis secciones: **0/6**. Esto no equivale a evaluar una respuesta inexistente ni a afirmar que ningún dato útil esté en los pasajes seleccionados; demuestra una selección insuficiente para el criterio global fijado.

Los fragmentos de revisión representan aproximadamente 2–3% del texto completo, pero el buscador escaneó localmente los 391.299 bytes. **No se midieron ahorro de tokens de inferencia, latencia de proveedores ni coste monetario**. Seleccionar menos bytes sin cobertura suficiente no constituye éxito.

## Reproducción local

El PDF, texto extraído, planes con pasajes y bases SQLite permanecen locales e ignorados por Git (`inputs/`, `runs/`). Se publican métricas, rangos, hashes y resultados de interfaz.

1. Con pypdf disponible: `python3 extract.py /ruta/2000-002-001.pdf` (exige la identidad esperada; no sobrescribe inputs).
2. `python3 prepare.py` (requiere workspace nuevo; no llama proveedores).
3. `python3 check_offline.py` (una ejecución por workspace; rechaza revisiones duplicadas).

Estos scripts se ejecutan desde esta carpeta. `prepare.py` usa `scripts/agora_issues.py` para el recorrido; la preparación de la consulta global usa la función pública del consumidor de pasajes. La inspección de referencia humana fijada en los JSON no reemplaza una adjudicación independiente.

## Continuación recomendada

1. Autorizar explícitamente el envío acotado si se desea comparar GLM/Jev con estos fragmentos; sus juicios se medirán contra lo recibido, no contra páginas que nunca recibieron.
2. Detectar extracción parcial y añadir OCR/lectura visual con procedencia propia para portada y diagramas, sin alterar el original.
3. Ensayar recuperación por subpreguntas y cobertura por sección; repetir estos casos como regresión y después usar casos nuevos reservados. No corregir el fallo aumentando contexto sin medir cobertura, coste y omisiones.

No se modificó código de producto ni se promocionó Jev como revisor predeterminado. Esta entrega es parcial respecto de las pruebas reales con proveedores.
