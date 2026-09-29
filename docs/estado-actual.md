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
- Generación conectada: devuelve seis áreas con responsabilidades y alcance parcial, pero se rechaza porque seis citas no son literales. El ensayo posterior con IDs sí produjo un candidato parcial válido, sin certificar exhaustividad. Evidencia y límites: [generación](generacion-desde-plan.md).
- Última regresión de código: 460 pruebas aprobadas. Es una fotografía de esta revisión, no un contador contractual ni validación semántica general.

## Fronteras y pendientes

Skopos conserva fuentes; hay pilotos mediante contratos/exportaciones explícitas, sin escritura directa entre almacenes ni dependencia obligatoria. AN-KLA conserva continuidad y registros gobernados; no hay admisión automática de resultados de Ágora. Los componentes mantienen independencia y ciclos propios.

No están resueltos: motor completo de transformación y consolidación de memoria, consolidación general, OCR fiable, extracción automática de estructura, descomposición autónoma de preguntas, adjudicación independiente general, catálogo de artefactos y verificación de sus front-matter. Tampoco watcher ni corrección automática de documentos.

**Incremento disponible:** `generate-plan --citation-mode ids` reutiliza las referencias por identificador existentes. Validación local y una ejecución real completadas: seis afirmaciones, doce referencias exactas y candidato parcial; sin ahorro demostrado. Revisión posterior Jev: 6/6 afirmaciones del manual respaldadas y 4/6 concordancias con etiquetas AttrScore reservadas; dos desacuerdos pendientes de adjudicación. Controles negativos completados: tres alteraciones rechazadas y cuatro controles respaldados aceptados; etiquetas exactas 6/7, con confusión entre contradicción e insuficiencia en la ampliación de alcance. [Informe](../experiments/plan-ids-negative-v1/RESULTS.md). Distinción contrastada contra código y dos respuestas conservadas: respaldo de afirmaciones no demuestra suficiencia del resumen; el módulo de suficiencia actual evalúa pasajes. [Piloto de dos resúmenes preparado](../experiments/summary-task-sufficiency-v1/README.md), sin nuevas llamadas, pendiente de autorización del envío concreto. Aumentar tiempo o contexto no basta para corregir omisiones.

La integración explícita de [referencias por ID](referencias-evidencia-por-id.md) mantiene el modo literal anterior y usa un formato de salida por afirmaciones distinto; véase [generación desde plan](generacion-desde-plan.md).

## Aclaración sobre L0…Ln

La decisión de identidad del 7 de septiembre proponía representaciones por niveles L0…Ln, con semántica todavía pendiente. Esa referencia es un antecedente de diseño, no un contrato implementado ni un requisito operativo de este prototipo. Presentarla en este estado como “motor completo L0→LN pendiente” fue una extrapolación incorrecta.

El trabajo actual se describe por **fuentes versionadas, evidencia recuperada, representaciones derivadas, afirmaciones, cuestiones abiertas y revisiones**, vinculadas por procedencia. Las transformaciones pueden tener dependencias o distinta granularidad sin formar una escalera fija de niveles. Esto conserva el propósito de memoria para agentes y la independencia frente a Skopos y AN-KLA.

La aclaración solicitada por el Operador corrige la descripción operativa; no declara implementado un grafo completo ni sustituye silenciosamente todos los contratos experimentales de septiembre. Adoptar en el futuro una jerarquía de niveles requeriría definición y decisión explícitas.
