# Revisión separada: fidelidad mejora, suficiencia falla

## Ensayo completado

Mismos diez candidatos del [ensayo con ámbitos explícitos](../reviewer-scopes-v1/README.md). Veinticinco solicitudes Jev jev-1.13.0: cinco de claridad por pregunta única antes de candidatos, diez de fidelidad con sólo los pasajes entregados y diez de cobertura con la fuente completa. Sin nueva generación, reintentos, reparación de respuestas ni cambios de producto.

**Resultado: no adoptar el conjunto de revisiones como criterio de aceptación.** La separación resolvió en esta muestra las tres discrepancias de fidelidad de abstenciones, pero produjo tres falsos completos frente a las expectativas de suficiencia. Las etiquetas originales y las nuevas se conservan por separado.

## Protocolo y comprobaciones

freeze.json fija entradas, presupuesto máximo de 25 llamadas, modelo, timeout de 90 s y regla de agregación antes del envío. Claridad se ejecutó primero; el runner requiere esas cinco respuestas completas antes de enviar las revisiones. Las llamadas son independientes y sin historial compartido. El transporte existente registra cada intento y se detiene por errores de acceso/saldo/límite o tres fallos.

- Claridad recibe únicamente task, sin candidato ni fuente.
- Fidelidad recibe task, answer y delivered_passages; no recibe fuente completa.
- Cobertura recibe task, answer y full_source; no recibe el subconjunto de pasajes.
- No se envían método de recuperación, grupo de control, referencia QASPER, expectativas, etiquetas anteriores ni otra respuesta.
- Las citas del candidato permanecen como parte de answer. La separación impide añadir la fuente completa a fidelidad, no elimina conocimientos previos del modelo.
- score.py compara cada request real completo con el constructor y verifica hashes de entradas y del resultado anterior. Los datos recuperados son evidencia, no instrucciones.

La misma decisión de claridad se aplica a todos los candidatos de una pregunta. Si no es clear, la agregación produce requires_clarification; conserva las etiquetas crudas y no admite nada automáticamente. Esa regla no convierte una detección de ambigüedad en verdad.

## Resultados observados

| Grupo | Fidelidad sobre pasajes | Suficiencia frente a fuente |
|---|---|---|
| Tres abstenciones honestas | supported en 3/3, esperado | complete en 3/3, contrario a omitted esperado |
| Tres controles positivos | supported en 3/3 | complete en 3/3 |
| Dos controles negativos | unsupported en 2/2 | omitted en 2/2 |
| Dos candidatos de pregunta ambigua | supported en 2/2 | complete en 2/2; no es admisión y discrepa con la intención QASPER |

En los ocho controles con expectativas del productor: fidelidad 8/8, cobertura 5/8 y par completo 5/8. Los dos candidatos ambiguos se reportan aparte. No son tasas de precisión general ni adjudicación independiente. La revisión anterior obtuvo 6/8 pares: el nuevo diseño no mejoró el resultado conjunto en estos controles, aunque mejoró fidelidad. No es una comparación causal controlada: cambian instrucciones, estructura de solicitudes, orden y momento, sin repetición simultánea.

Claridad: cuatro preguntas marcadas ambiguous y sólo la definición de lexical overlap marcada clear. Esto deja **nueve de diez candidatos** con requires_clarification. La pregunta sobre identidad del modelo recibe ahora una sola etiqueta, estable por construcción para sus dos candidatos. Sin embargo, retirar toda fuente deja sin referente preguntas como “they”: marcar ambigüedad puede reflejar una carencia introducida por el diseño. No se atribuye automáticamente al modelo toda esta sobrederivación; no se había fijado una expectativa para las otras cuatro preguntas.

Las 25 llamadas terminaron. Uso reportado: **99.237 tokens** (98.057 entrada y 1.180 salida), 7,950 segundos acumulados de solicitudes. No es coste monetario ni tiempo total de ingeniería. El lote anterior tuvo 93.961 tokens y diez llamadas, pero esa comparación también cambia criterios y entradas; no demuestra ahorro de producto.

## Autorrevisión adversarial

- **No basta con aceptar abstenciones como fieles.** Una afirmación honesta sobre lo no leído no contesta por sí misma la tarea. Los tres complete son resultados adversos preservados, no aciertos por una redefinición posterior.
- **Control positivo y negativo presentes.** La fidelidad aislada rechaza tanto la ausencia falsa en pasajes con cifras como el nombre de modelo inventado y acepta tres respuestas adecuadas. Esto respalda utilidad acotada, no fiabilidad general.
- **Ambigüedad antes del candidato requiere contexto documental.** Pregunta sola garantiza separación, pero elimina información necesaria para resolver referentes. La alternativa a probar es pregunta y contexto documental fijado, sin candidato ni etiquetas de referencia. No corregir automáticamente la intención del usuario.
- **La regla de derivación puede esconder errores si sólo se mira el resultado final.** Nueve requires_clarification evitan aceptación, pero no corrigen los complete erróneos. Por eso se reportan ambos niveles.
- **No se conoce el motivo interno de las salidas.** Se verificó que cada petición llevaba el campo de evidencia previsto y que la API respondió; no se infiere cómo razonó Jev ni se presenta el modelo como incapaz universalmente.
- **Muestra conocida y juicios del productor.** Los controles negativos son sintéticos; los casos se seleccionaron por fallos previos. No hay adjudicación independiente ni generalización a fuentes reservadas.

## Decisión y próximo paso

Mantener el producto y revisor predeterminados sin cambios; conservar la fidelidad aislada sólo como candidato experimental. No seguir variando prompts y promover por el mejor lote.

El siguiente paso recomendado es **contrastar la suficiencia con otro revisor, conservando estos candidatos y expectativas congeladas**, y revisar sus desacuerdos contra las fuentes. GLM puede servir como comparador, declarando que pertenece a la misma familia que produjo candidatos y no constituye adjudicación independiente. Los juicios del productor y referencias externas quedan como una capa separada. Priorizar los tres falsos completos, controles adecuados y negativos; no gastar otra vez en generación.

Antes de integrar en CLI, exigir que honestidad local y suficiencia global permanezcan distintas y que una discrepancia conduzca a revisión explícita. Si se vuelve a probar claridad, aportar contexto documental sin candidato y medir derivaciones innecesarias. No se implementó ni ejecutó esa siguiente propuesta en este lote.

## Reproducción

prepare.py prepara directorio nuevo desde entradas locales ignoradas anteriores. run.py clarity y run.py review despachan llamadas: no repetir sobre este lote. score.py recompone sin API. Los journals y textos completos quedan ignorados; se publican claves neutrales, configuración, métricas y límites. Pruebas de reproducción y documentación realizadas; no se repitió suite del producto porque no cambió código de producto.
