# Suficiencia GLM: controles sobre seis documentos nuevos

## Alcance y congelado

Catorce controles semánticos redactados por el productor a partir de seis artículos públicos QASPER. No son salidas nuevas del generador ni un ensayo completo de recuperación. Se mide si el revisor diferencia respuesta suficiente, omisión, respuesta alterada y abstención justificada. Las etiquetas esperadas se fijaron antes de ejecutar GLM; no hay adjudicación independiente.

Se reutilizan sin cambios el payload, criterios e instrucciones de [GLM cobertura](../reviewer-coverage-glm-v1/README.md). freeze.json fija hashes de la configuración y de su fuente de criterios, entradas, modelo glm-5.3-flash, temperatura 0, máximo 2.048 tokens de salida, 90 s, 14 llamadas y cero reintentos. Una predicción complete en cualquier negativo bloquea promoción. Incluso 14/14 es condición necesaria del lote, no validación general.

## Selección y significado de reservado

selection.json conserva el inventario local y los IDs excluidos antes de preparar controles. Se buscaron identificadores de artículos en nombres y contenido de archivos experimentales .json, .jsonl, .md, .py y .txt de hasta 2 MB; se excluyeron los archivos de dataset test/train/dev y validation.jsonl. Se ordenaron candidatos por SHA-256 de semilla coverage-heldout-v1, documento y pregunta; una pregunta por documento. Texto renderizado entre 20.000 y 65.000 bytes; anotaciones concordantes en respondibilidad y evidencia textual localizable para preguntas respondibles.

Se eligieron los primeros cuatro documentos respondibles con respuesta libre o varios spans, y dos no respondibles. Los seis IDs están fuera del conjunto excluido guardado. **Reservado significa nuevo respecto de ese inventario acotado**, no ausencia garantizada en todo el historial, otras máquinas o entrenamiento de modelos. Las referencias fueron inspeccionadas por el productor antes de redactar candidatos; nunca se enviaron como etiquetas al revisor. Tras este ensayo, estos documentos dejan de ser reservados para futuros ajustes.

selection_protocol.py conserva el procedimiento histórico: repetirlo después de crear nuevos artefactos cambia el inventario y no reproduce la selección original. prepare.py usa la selección guardada; no vuelve a seleccionar.

## Controles

| Documento | Pregunta/tema | Variantes |
|---|---|---|
| 1606.07947 | Poda de pesos | Adecuada, valores mayores en lugar de menores, abstención |
| 1908.10149 | Tamaño del test | 3.084 correcto, 30.840 alterado, abstención |
| 1805.09960 | Datasets de traducción | Lista con conjuntos y usos, sólo NIST 2003, abstención |
| 1909.07158 | Representaciones de texto | Lista completa cotejada con fuente, sólo Word2Vec, abstención |
| 1706.02427 | Extracción de tablas HTML | Abstención; ambas anotaciones no respondibles |
| 2002.04745 | Definición de mean field theory | Abstención; ambas anotaciones no respondibles |

Las referencias de representaciones de texto nombran Word2Vec y ELMo; el artículo también describe TF-IDF y Universal Sentence Encoder. El control adecuado incluye los cuatro y conserva esa diferencia con la referencia abreviada. Las preguntas se consideraron evaluables en contexto documental mediante inspección del productor; no se inventó un estrato de ambigüedad que esta selección no contiene.

Los candidatos son mínimos, usan claims/missing y no contienen citas: quotes vacío. Esto es deliberado para probar semántica de suficiencia sin ayuda de citas, **no** aprobación por el validador de candidatos del producto. Hace que la representatividad respecto del flujo real sea limitada. Dentro del lote todas las variantes comparten ese formato.

## Evidencia y límites

Los controles de un documento están correlacionados: n=14 no significa 14 fuentes independientes. Un cambio de cifra o una poda invertida es un negativo sencillo; acertarlo no demuestra detección de omisiones sutiles. Preguntas no respondibles se apoyan en anotaciones externas y examen del texto, no en una garantía de ausencia universal. No se valida fidelidad adicional ni se activa admisión de memoria.

Un fallo de arranque por colisión del nombre select.py con la biblioteca estándar ocurrió antes de crear journals o hacer solicitudes. Se renombró a selection_protocol.py; entradas y prompt congelados no cambiaron. No hubo repetición de llamadas.

Reproducción: score.py verifica requests e integridad y recompone resultados sin API. run.py hace solicitudes y no debe repetirse sobre el lote. Los textos completos, solicitudes y respuestas crudas quedan ignorados; se publican metadatos y resultados saneados.

## Resultado y decisión

**14/14 etiquetas coinciden con las expectativas fijadas, sin falsos complete.** Todas las llamadas terminaron. Grupos: cuatro adecuadas → complete; dos parciales y dos alteradas → omitted; cuatro abstenciones ante fuentes respondibles → omitted; dos abstenciones ante preguntas no respondibles → justified_abstention.

Uso reportado: 85.393 tokens de entrada y 4.647 de salida, **90.040 en total**; 101,320 segundos acumulados de solicitudes. Modelo reportado glm-5.3-flash. No hay coste monetario verificado ni medición del pipeline completo.

El lote cumple el umbral previamente fijado, pero no autoriza promoción general: controles mínimos del productor, seis documentos, sin evaluación independiente, sin casos ambiguos nuevos y sin candidatos reales generados en este lote. El error previo sobre identidad del modelo permanece abierto. Las ausencias de fallos no borran esos límites.

**Siguiente paso recomendado:** integrar la configuración congelada como opción experimental explícita en la CLI, conservando original, versión del revisor, evidencia utilizada y resultado. Su salida debe ser consejo de suficiencia, separado de fidelidad y admisión de memoria; mantener predeterminado y contratos existentes. Verificar el recorrido primero con respuestas conservadas y fallos simulados; después una ejecución acotada sobre un candidato real. No se implementó esa integración en este ensayo.

La autorrevisión contrastó umbral, selección, denominadores y afirmaciones de alcance: no se presenta 14/14 como precisión general, la muestra queda consumida para futuros ajustes y se conserva la discrepancia entre anotación abreviada y fuente completa. No participó revisor independiente.
