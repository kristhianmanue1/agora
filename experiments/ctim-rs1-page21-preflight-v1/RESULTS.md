# Resultado: Ágora sobre página 21 del borrador CTIM RS1

Fecha local: 2026-10-10. Se ejecutó **una vez** `answer-v2` con la fuente
autorizada de 582 bytes (SHA-256
`ee7ec9b09e6c171dd4e37ed5c1d155366093b2098f38d060a6170f0eefe200c4`),
pregunta y presupuestos del preflight. Llavero suministró la credencial `zai`
con la `ZAI_API_KEY` heredada ausente en ese proceso. No se envió el PDF
completo ni otra página; no hubo reintentos automáticos.

`live-answer-v1/result.json` registra `candidate_reviewed`, cuatro despachos y
`memory_admission=not_performed`. Generación produjo tres afirmaciones y
`finish_reason=stop`: 1718 tokens de salida reportados (1323 de razonamiento).
Respaldo, pertinencia y cobertura terminaron; GLM etiquetó las tres
afirmaciones como `supported`/`relevant` y cobertura como `complete`. Estas
etiquetas son consejos del mismo proveedor, no adjudicación independiente.
Jev y el diagnóstico de omisiones no corrieron.

`package-live-v1/package.json`, esquema
`agora/consultation-package/v2-experimental`, se exportó y reconstruyó offline:
SHA-256 `ebe5f9eff530540055b890d16e03749656ab6e510de4fc9708aa95d45da43aaf`.
Declara `original_integrity=sha256_verified`, tres afirmaciones y 13
localizadores de la página 21 para cada cita. Un intercambio de control con
hash de segmento alterado se rechazó (`segment_sha256_mismatch`). El PDF sólo
se leyó localmente para verificar SHA y localizadores; esos controles no
acreditan fidelidad visual ni verdad institucional.

**Límite material:** el modo de IDs usado por `answer-v2` formó **una sola
unidad de evidencia de 582 bytes**. Por ello, las tres afirmaciones citan el
pasaje completo. El paquete permite localizarlo, pero no demuestra por sí
solo que cada frase esté respaldada por la línea precisa. La referencia a
«Anexo 6» y el nombre «Oficio de autorización del anteproyecto conceptual»
aparecen en el pasaje; su mera mención no verifica la existencia del anexo,
la autoridad final, la aprobación ni la vigencia del borrador.

**Entrega para cotejo:** expertoGobernanza debe contrastar cada afirmación con
el PDF y su análisis directo de esa página, comprobar responsable, acción,
objeto y destinatario, y resolver si las citas son suficientemente precisas.
El paquete conserva `disposition=requires_review` y
`adjudication=not_performed`. No se hizo otra serie ni se incorporó la salida
al contrato consumidor.
