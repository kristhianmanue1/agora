# Piloto reservado local de documentos largos

Dos artículos QASPER test-v0.3: 1610.00479 (7.689 palabras, 51.806 bytes) y 1902.08830 (9.555 palabras, 64.369 bytes). Hash del dataset comprobado contra procedencia local. Selección determinista por hash, 33 IDs locales excluidos y primer ejemplo elegible por documento. Véase selection.json: exclusión por referencias en JSON locales, no prueba de ausencia en entrenamiento ni en actividad no registrada. Tras este lote ya no son reservados para evaluar futuras afinaciones.

Dos variantes de respuesta (extractiva original y reducción del productor), cada una con documento completo o pasajes anotados: ocho casos/proveedor, GLM y Jev, 16 llamadas, 90 s cada una, cero reintentos. Un solo intento; no se ajustan gold ni respuestas. Gold original derivado de QASPER se conserva; las etiquetas de suficiencia y las variantes NO son etiquetas oficiales del corpus. Estado congelado en freeze.json.

El contexto corto usa evidencia anotada del benchmark: oracle retrieval. No evalúa la recuperación de Ágora, generación nueva, lectura global ni pipeline end-to-end. Respaldo de afirmaciones contrastado cualitativamente por revisor separado, no una tasa automática validada de fidelidad. Respuestas y fragmentos privados excluidos de Git.

Véanse [resultados](RESULTS.md), [revisión separada](independent-review.json), [metadatos](documents.json) y [datos saneados](result.json).
