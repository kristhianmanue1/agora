# Integración CLI de suficiencia

Candidato GLM real conservado de QASPER 2003.11531, variante equal del ensayo retrieval-answer-ids-v1. prepare.py materializa el resultado mediante replay del contrato de evidencia por IDs; no regenera ni llama al productor. provenance.json identifica origen y hashes. El artículo es público.

Ejecuciones desde scripts/agora_issues.py: workspace nuevo, review-coverage con respuesta guardada válida (exit 0 y cero HTTP), etiqueta inválida (exit 2 y cero HTTP), y --live (una llamada, coverage=complete, disposition=requires_review). El candidato y fuente no se modificaron. result.json contiene uso, modelo y hashes del caso real; requests y respuestas completas permanecen ignorados.

Diez pruebas específicas cubren hash alterado, cita no literal, parte inexistente, JSON estricto/duplicado, truncamiento, timeout sin retry, reserva antes del envío, replay sin red y coincidencia exacta de prompt congelado. Suite completa: 470 pruebas aprobadas. Autorrevisión del diff: defaults de generate-plan conservados; no hay llamada automática ni escritura en almacén de memoria.

Tras la llamada real se añadió sólo source_completeness=not_established al informe; el código final se verifica de nuevo offline. No se repitió la llamada por un cambio de metadatos. Limitaciones: almacenamiento separado en archivos, sin recuperación transaccional general; preguntas ambiguas pendientes de revisión humana; complete no admite el candidato. Uso: [guía CLI](../../docs/revision-suficiencia-cli.md).
