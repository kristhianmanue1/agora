# Selección de lectura: fuente o candidato

Incremento local autorizado2026-09-17, posterior al lote multifuente.
La transformación conserva raw_output sin editar. Se admite JSON puro o un
único bloque completo abierto con ```json y cerrado con ```, con saltos de
línea y sólo espacio alrededor. Se registra output_normalization.operation.
Texto externo, múltiples bloques, JSON concatenado y claves duplicadas se
rechazan. La normalización no repara contenido ni evita validar citas y límites.

Después de validar, se mide el resumen renderizado en bytes UTF8 incluyendo
encabezado, IDs y saltos. compression.status es shorter sólo si es estrictamente
menor que la fuente exacta; igualdad o crecimiento producen not_shorter.
reading_selection elige candidate_summary o original_source respectivamente.
Esta selección usa tamaño, **no certifica fidelidad ni concede autoridad**.
review_status sigue unreviewed y semantic_support not_verified.

En salidas válidas, la CLI escribe:
- source.txt: bytes originales verificados.
- summary.txt: candidato conservado, aunque sea más largo.
- evidence.json: citas del candidato.
- reading.txt: fuente exacta o candidato más breve, según result.json.
- result.json: procedencia, comparación, normalización y estado de revisión.

Las vistas ahora se generan también sin --summary-max-bytes. Con ese argumento,
el exceso absoluto conserva el rechazo sin archivos de lectura, como antes.
El límite no trunca la fuente elegida: limita el candidato. source.txt/reading.txt
no convierten la fuente en confiable. La CLI imprime compression_status y
reading_kind para no confundir salida válida con compresión lograda.

Validación: tests/test_selection.py y tests/test_cli.py; replay sin red de cinco
respuestas breves más un caso largo. No mejora demostrada de generación:
clasifica el ahorro y recupera un envoltorio inequívoco. Las pruebas históricas
conservan sus veredictos. Evidencia en Pinax: docs/design/agora-seleccion-lectura-v1.
No cambia el experimento M1 congelado, no instala ni publica ni admite memoria.
