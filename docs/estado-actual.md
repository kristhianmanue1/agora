# Estado actual de Ágora

Observación: 2026-09-29. Prototipo experimental independiente. Este documento resume capacidades actuales; las decisiones arquitectónicas conservan su autoridad y los informes fechados conservan sus resultados originales.

## Qué funciona y dónde entrar

| Necesidad | Capacidad comprobada | Guía |
|---|---|---|
| Leer y volver a la fuente | UTF-8 fijado por SHA, offsets y presupuestos | [Proveedor local](proveedor-archivos.md) |
| Leer partes de un documento largo | Pasajes, recorridos, recuperación por subpreguntas; estrategia optativa por funciones | [Subpreguntas](subpreguntas.md) |
| Generar sobre un plan | Reproduce el plan, verifica fuente, una llamada GLM; conserva rechazo y alcance parcial | [Generación](generacion-desde-plan.md) |
| Mantener cuestiones y revisarlas | Preparación, evaluación, inspección, recuperación, reparación explícita | [CLI de pendientes](pendientes-cli.md) |
| Ampliar evidencia de una revisión | Original inmutable y revisión derivada por GLM/Jev | [CLI de ampliación](ampliacion-cli.md) |
| Revisar afirmaciones | Revisores experimentales y criterios separados de admisión | [Revisión](revision-acotada-por-afirmacion.md) |
| Evaluar métodos | QASPER, AttrScore, controles y documentos de desarrollo | [Corpus](evaluacion-corpus-publicos.md) |

La entrada `python3 scripts/agora_issues.py --help` reúne pendientes, ampliación y planes. Otras familias mantienen sus CLI específicas. No existe todavía una única interfaz que cubra toda la biblioteca. Con Llavero, usar ruta absoluta del intérprete y del script; `PYTHONPATH` puede no propagarse.

## Evidencia reciente que cambia la prioridad

- Manual DPM: 188 páginas, unas 54.658 palabras extraídas. La portada y el organigrama muestran pérdidas de extracción; OCR/lectura visual automática sigue pendiente.
- GLM/Jev: ambos coinciden con cuatro etiquetas del productor; sin base para sustituir al revisor predeterminado.
- Funciones: 439 bytes para los dos pasajes del caso compuesto; 2.152 bytes para una función de cada una de seis áreas. Cobertura global no establecida y referencias de páginas completas todavía parciales.
- Generación conectada: devuelve seis áreas con responsabilidades y alcance parcial, pero se rechaza porque seis citas no son literales. No hay síntesis aceptada de este ensayo. Evidencia y límites: [generación](generacion-desde-plan.md).
- Última regresión de código: 458 pruebas aprobadas. Es una fotografía de esta revisión, no un contador contractual ni validación semántica general.

## Fronteras y pendientes

Skopos conserva fuentes; hay pilotos mediante contratos/exportaciones explícitas, sin escritura directa entre almacenes ni dependencia obligatoria. AN-KLA conserva continuidad y registros gobernados; no hay admisión automática de resultados de Ágora. Los componentes mantienen independencia y ciclos propios.

No están resueltos: motor completo L0→LN, consolidación general, OCR fiable, extracción automática de estructura, descomposición autónoma de preguntas, adjudicación independiente general, catálogo de artefactos y verificación de sus front-matter. Tampoco watcher ni corrección automática de documentos.

**Próxima prioridad:** reutilizar referencias por identificador para que el generador no tenga que volver a copiar citas; contrastar respuesta, cobertura y evidencia sin relajar silenciosamente literalidad. Después, casos nuevos reservados. Aumentar tiempo o contexto no basta para corregir omisiones.

Los prototipos ya existentes de [referencias por ID](referencias-evidencia-por-id.md) son una base de implementación, no prueba de compatibilidad automática con `generate-plan`.
