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

**Incremento disponible:** `generate-plan --citation-mode ids` reutiliza las referencias por identificador existentes. Validación local y una ejecución real completadas: seis afirmaciones, doce referencias exactas y candidato parcial; sin ahorro demostrado. Revisión posterior Jev: 6/6 afirmaciones del manual respaldadas y 4/6 concordancias con etiquetas AttrScore reservadas; dos desacuerdos pendientes de adjudicación. Controles negativos completados: tres alteraciones rechazadas y cuatro controles respaldados aceptados; etiquetas exactas 6/7, con confusión entre contradicción e insuficiencia en la ampliación de alcance. [Informe](../experiments/plan-ids-negative-v1/RESULTS.md). Distinción contrastada contra código y dos respuestas conservadas: respaldo de afirmaciones no demuestra suficiencia del resumen; el módulo de suficiencia actual evalúa pasajes. [Piloto de dos resúmenes ejecutado](../experiments/summary-task-sufficiency-v1/RESULTS.md): Jev distingue sufficient/insufficient en los dos casos previstos, con tarea explícita y etiquetas del productor; no demuestra generalización ni integración de producto. [Prueba contextual posterior](../experiments/summary-task-sufficiency-v2/RESULTS.md): 4/4 decisiones y 8/8 clasificaciones de fragmentos coinciden con etiquetas del productor; una misma omisión se juzga según la tarea. Sigue limitada a una fuente y unidades manuales. Aumentar tiempo o contexto no basta para corregir omisiones.

La integración explícita de [referencias por ID](referencias-evidencia-por-id.md) mantiene el modo literal anterior y usa un formato de salida por afirmaciones distinto; véase [generación desde plan](generacion-desde-plan.md).

## Aclaración sobre L0…Ln

La decisión de identidad del 7 de septiembre proponía representaciones por niveles L0…Ln, con semántica todavía pendiente. Esa referencia es un antecedente de diseño, no un contrato implementado ni un requisito operativo de este prototipo. Presentarla en este estado como “motor completo L0→LN pendiente” fue una extrapolación incorrecta.

El trabajo actual se describe por **fuentes versionadas, evidencia recuperada, representaciones derivadas, afirmaciones, cuestiones abiertas y revisiones**, vinculadas por procedencia. Las transformaciones pueden tener dependencias o distinta granularidad sin formar una escalera fija de niveles. Esto conserva el propósito de memoria para agentes y la independencia frente a Skopos y AN-KLA.

La aclaración solicitada por el Operador corrige la descripción operativa; no declara implementado un grafo completo ni sustituye silenciosamente todos los contratos experimentales de septiembre. Adoptar en el futuro una jerarquía de niveles requeriría definición y decisión explícitas.

## Último contraste de suficiencia

[Batería sintética de transferencia](../experiments/summary-task-transfer-v1/RESULTS.md): 11/12 decisiones y 24/24 unidades coinciden con etiquetas del productor. Un resumen completo fue rechazado aunque todas sus unidades se clasificaron como cubiertas. El criterio principal no se cumplió; prioridad: separar insuficiencia de la fuente y omisión del resumen, y tratar inconsistencias antes de integrar el eje en producto.

## Diagnóstico pareado y fuentes largas

[Contraste GLM/Jev](../experiments/sufficiency-axes-v1/README.md): separar fuente suficiente y resumen sin omisiones evita mezclar carencias. [Dos documentos largos reservados localmente](../experiments/sufficiency-long-reserved-v1/RESULTS.md) revelan pérdida de contexto con pasajes anotados y desacuerdos del gold. No se cumple aún el criterio para integrar el nuevo eje en la CLI. La reducción de tokens con selección oracle no es ahorro end-to-end del producto.

## Recuperación real contrastada

[Dos casos recuperados con Ágora](../experiments/sufficiency-real-retrieval-v1/README.md): reducción de tokens de entrada al revisor de 88,72% (Jev) y 90,54% (GLM) frente al contexto completo previo. Se recuperó el contraste entrenamiento/evaluación sin anotaciones, pero quedaron fuera párrafos de otra evaluación. No demuestra exhaustividad ni ahorro seguro end-to-end; integración decisoria sigue pendiente.

## Subpreguntas: resultado de redistribución experimental

[Contraste local](../experiments/sufficiency-subquestions-v1/README.md): las cuotas iguales dejaron fuera un párrafo de 929 bytes pese a 1.989 bytes libres tras deduplicar. Una ampliación experimental por vecinos lo recuperó usando 7.882/8.000 bytes y conservando rangos previos. Sin llamadas API ni cambios de producto; falta validación en casos nuevos antes de proponer estrategia optativa.

## Validación de redistribución en documentos nuevos

[Doce documentos y casos límite](../experiments/shared-neighbor-validation-v1/README.md): integridad, presupuesto y conservación aprobados; a 8.000 bytes la cobertura anotada pasa de 10/29 a 12/29, con mejora en 2/12 documentos y 20,88% más bytes recuperados. Sin llamadas API ni cambios de producto. Candidata experimental, sin justificación para reemplazar el método predeterminado.

## Comparación completa iniciada, detenida por transporte

[Generación y revisión pareadas](../experiments/retrieval-answer-paired-v1/README.md): cinco generaciones válidas y revisadas, tres timeouts de 90 s y parada del transporte; 16 entradas no enviadas. En la primera etapa sólo hubo dos pares completos. Consumo observado mínimo 53.238 tokens; cargos/uso de timeouts desconocidos. La integración permanece pendiente.

## Continuación de comparación pareada

[16 entradas pendientes completadas](../experiments/retrieval-answer-paired-v1/CONTINUATION.md): todas respondieron; 11 válidas revisadas y cinco rechazos de formato/citas. Consolidado: siete pares semánticamente comparables, un caso favorable a redistribución, tres útiles en ambos y tres incompletos en ambos. Persisten tres timeouts originales sin repetir. Sin promoción; consumo conocido 176.605 tokens, con uso de timeouts desconocido.

## Comparación con IDs y límite del revisor

[IDs en ambas rutas](../experiments/retrieval-answer-ids-v1/RESULTS.md): 24 respuestas, 20 candidatos válidos revisados por Jev, dos truncamientos y dos JSON inválidos, sin fallos de transporte. Diez pares comparables: dos favorables a redistribución, uno a cuotas iguales, cuatro útiles en ambas y tres sin utilidad según el criterio en ambas. 225.794 tokens observados, incluida revisión completa. La autorrevisión detectó una discrepancia de Jev con la referencia QASPER sobre identidad del modelo frente a procedimiento de entrenamiento; el resultado bruto permanece intacto. Prioridad: calibrar suficiencia contra referencias externas usando los candidatos conservados, antes de promover o ampliar la muestra. Producto sin cambios.

## Contraste con referencias externas

[Auditoría de los 20 candidatos conservados](../experiments/retrieval-reference-audit-v1/README.md): el productor encuentra diez con cobertura adecuada y diez incompletos frente a referencias QASPER contrastadas con fuente. Un complete de Jev discrepa con la intención del benchmark; una referencia QASPER contiene a su vez una cifra discordante con el texto fuente. Hay huecos de recuperación, omisiones y un riesgo de confundir ausencia en pasajes con ausencia en la fuente completa. No es adjudicación independiente. Siguiente prioridad: evaluar el revisor con ambos alcances explícitos, conservando etiquetas anteriores. Sin nuevas llamadas ni cambios de producto en este contraste.

## Revisión con ámbitos explícitos: mejora parcial

[Ensayo de diez revisiones](../experiments/reviewer-scopes-v1/README.md): una de tres abstenciones cambia correctamente a supported + omitted; dos siguen como unsupported. Tres controles positivos y dos negativos cumplen expectativas. Misma pregunta recibe etiquetas distintas de ambigüedad; aparece además ambiguous junto a omitted pese al criterio de uncertain. Diez llamadas Jev, 93.961 tokens, sin nueva generación. No promoción: siguiente ensayo propuesto separa revisión de pasajes y suficiencia global en llamadas distintas, y fija interpretación antes de candidatos.

## Revisiones separadas: no adoptar el conjunto

[Ensayo separado](../experiments/reviewer-separated-v1/README.md): fidelidad sobre pasajes cumple 8/8 expectativas del productor; suficiencia frente a fuente completa sólo 5/8 y califica tres abstenciones como completas. Claridad evaluada sin fuente marca cuatro de cinco preguntas ambiguas y deriva nueve candidatos; puede reflejar referentes ausentes por diseño. 25 llamadas Jev, 99.237 tokens, sin regeneración. No promoción. Próximo paso recomendado: contrastar suficiencia con otro revisor sobre candidatos conservados y resolver desacuerdos contra fuentes, evitando más ajustes de prompt sobre la misma muestra.

## Contraste GLM de suficiencia

[Mismos diez estados con GLM](../experiments/reviewer-coverage-glm-v1/README.md): 8/8 expectativas de controles frente a 5/8 de Jev; las tres abstenciones quedan correctamente como omitted. Persiste un complete discrepante con QASPER en la pregunta ambigua. Diez llamadas, 74.930 tokens reportados, sin regeneración. GLM comparte familia con el generador y no es adjudicación independiente. Candidato experimental, sin cambio predeterminado: siguiente paso propuesto, batería reservada nueva con configuración congelada y contraste contra referencias.

## Batería nueva de suficiencia GLM

[14 controles sobre seis documentos nuevos](../experiments/coverage-heldout-v1/README.md): 14/14 expectativas del productor, cero falsos complete y todas las llamadas terminadas. Incluye respuestas suficientes, parciales, alteradas y abstenciones necesarias/innecesarias. 90.040 tokens reportados. Corpus nuevo respecto del inventario local acotado; controles mínimos sin citas, no candidatos nuevos del generador ni adjudicación independiente. Configuración congelada, sin ajuste posterior. Próximo paso recomendado: opción experimental explícita en CLI, con informe separado de fidelidad/admisión, replay y fallos simulados antes de una ejecución real. Producto aún sin cambios.

## Opción CLI experimental de suficiencia

Disponible [review-coverage](revision-suficiencia-cli.md): selecciona una parte de candidato por IDs/literal v1/v2, verifica hashes y registra consejo de suficiencia frente a fuente completa suministrada. Replay sin red o una llamada GLM explícita, sin reintentos. Candidato y defaults preservados; siempre requires_review, sin admisión ni evaluación de fidelidad. Replay, rechazo y llamada real comprobados; suite de 470 pruebas aprobada. El informe se conserva en archivos separados, sin recuperación transaccional general. Preguntas ambiguas y adjudicación independiente siguen pendientes.

## CLI contrastada con omisiones reales

[Fuente de 41.578 bytes / 6.474 palabras](../experiments/coverage-cli-long-v1/README.md): dos candidatos reales conservados, omitted para el incompleto y complete para el que incluye ambas limitaciones faltantes. Se localizaron fragmentos sobre BLEU y embeddings presentes sólo en el contexto redistribuido. Dos revisiones CLI, 19.069 tokens, originales intactos y requires_review en ambos. Caso conocido de desarrollo, no escala de 188 páginas ni ahorro total probado. Siguiente paso propuesto: diagnóstico de omisiones con localizadores verificables; la CLI actual entrega sólo clasificación.

## Diagnóstico de omisiones experimental

Disponible [diagnose-omissions](diagnostico-omisiones-cli.md): propuesta separada ligada por hashes a fuente, candidato y revisión, con IDs resueltos a citas y offsets exactos. Dos omisiones conocidas localizadas, dos propuestas adicionales sin adjudicar. El control suficiente agotó 2.048 tokens y quedó rechazado: validación semántica parcial, sin reintento ni reparación automática. Suite de 480 pruebas aprobada. Pendiente: condición explícita de presupuesto para completar el contraste de ambos candidatos; citas válidas no certifican omisión.

## Diagnóstico: presupuesto explícito y control pendiente

[Condición de 4.096 tokens](../experiments/omission-cli-budget-v2/README.md): ambos prompts idénticos a los anteriores; candidato incompleto produce cuatro propuestas, control suficiente termina sin truncamiento pero con JSON inválido. Su texto plantea dos faltantes adicionales cuya materialidad debe revisarse, por lo que la expectativa del control queda cuestionada sin cambiarla retrospectivamente. 26.946 tokens, dos llamadas. CLI admite --max-output-tokens 2048/4096, default intacto; 483 pruebas. Pendiente: eventual reparación como derivado explícito y adjudicación de relevancia, no más aumento automático de presupuesto.

## Derivado de formato y materialidad

[Derivado local explícito](../experiments/omission-format-derived-v1/README.md): eliminado sólo el byte final sobrante, original rechazado intacto, replay válido sin red y dos propuestas con offsets verificados. La evaluación del productor no confirma ninguna como omisión material: una se solapa con diversidad/BLEU y otra añade contexto de origen. No es adjudicación independiente ni corrección del candidato. Prioridad siguiente: rúbrica de requisitos, paráfrasis y ampliaciones opcionales; no más incremento de tokens ni reparación automática.

## Materialidad con requisitos explícitos

[12 controles de rúbrica](../experiments/materiality-rubric-v1/README.md): 12/12 coincidencias con expectativas del productor, incluidas paráfrasis, omisiones, contradicción y cambio de detalle opcional a obligatorio al cambiar la pregunta. 10.991 tokens; dos documentos conocidos, un candidato real y controles sintéticos. Evidencia favorable a evaluar requisitos explícitos, no a descubrirlos automáticamente. Producto sin cambios. Próximo paso: rúbrica optativa versionada ligada a pregunta/fuente, con procedencia y completitud pendiente; nunca convertir conformidad a rúbrica en exhaustividad global.

## Revisión optativa por rúbrica implementada

Disponible [review-rubric](revision-rubrica.md): fuente, candidato y rúbrica fijados
por SHA-256; pregunta exacta, procedencia declarada y evidencia con offsets UTF-8.
Resultado limitado a requisitos suministrados, con exhaustividad no establecida y
revisión requerida. 493 pruebas locales y recorrido CLI por replay con fuente real
y respuesta sintética; cero llamadas nuevas. No cambia los revisores anteriores.
Siguiente paso: contraste con rúbrica revisada por separado y caso reservado.

## Contraste reservado: discrepancia previa a generación

[Primer caso reservado de rúbrica](../experiments/rubric-reserved-v1/README.md):
Jev revisó fuente completa y requisitos antes de existir candidato y devolvió
`deficient`, sin explicación localizada. Se cumplió la parada predefinida: una
llamada, 11.257 tokens; ninguna generación ni evaluación GLM. No se adjudica error
de la rúbrica: posible ambigüedad entre benchmarks y preentrenamiento, con riesgo
de influencia del prompt del productor. Próximo paso: crítica localizada que
permita distinguir defecto de rúbrica de exceso del revisor, sin cambiar el caso
original ni promover completitud global.

## Crítica localizada: rúbrica conservada

[Contraste localizado](../experiments/rubric-localized-v1/README.md): GLM no propuso
defectos; Jev respaldó R1–R4 y no seleccionó un defecto o pasaje que lo demostrara,
con incertidumbre global. Dos llamadas, 26.095 tokens. Rúbrica y rechazo originales
intactos; un fallo de importación posterior a la respuesta GLM se resolvió mediante
validación local sin repetir llamada. No se generaron candidatos ni se acredita
exhaustividad. Próximo paso: candidato real y control de omisión en condición nueva,
conservar discrepancia y evaluar cobertura respecto a la rúbrica.

## Candidato real: rechazo por citas repetidas

[Prueba de candidato y control](../experiments/rubric-candidates-v1/README.md): una
generación GLM terminó normalmente, pero expandió referencias a 15.062 bytes frente
al límite de 12.000; cuatro unidades únicas (5.097 bytes), once usos por afirmación.
Rechazo reproducido localmente. Se detuvo la condición según el plan: cero revisiones,
sin cambios de límites, rúbrica o producto. Pendiente: derivado explícito con referencias
redundantes retiradas tras verificar respaldo; después contrastarlo con el control.
No hay todavía resultado de cobertura de esta pareja.

## Comparación completada con derivado explícito

[Condición derivada](../experiments/rubric-candidates-derived-v1/README.md): se retiraron
tres referencias redundantes sin cambiar afirmaciones ni faltantes; citas de 15.062
a 11.041 bytes. `review-rubric` detectó las tres omisiones del control y marcó los
cuatro requisitos cubiertos en el derivado; ocho etiquetas coinciden con expectativas
del productor. Tres llamadas contando generación, 18.963 tokens. Original rechazado
intacto: éxito asistido, no autónomo. Próxima prioridad: generación que respete el
presupuesto de citas, seguida de comparación lectura selectiva/completa en otro caso
reservado. Sin evidencia todavía de ahorro o exhaustividad global.

## Generación sin reparación: primera condición favorable

[Agrupación de hechos con evidencia compartida](../experiments/citation-grouping-v1/README.md):
candidato intacto válido, cinco usos de citas y 6.824 bytes; R1–R4 cubiertos según
`review-rubric`. Sin cambios de límites ni defaults. La condición previa de unidades
de 1.000 bytes agotó la salida y quedó rechazada; se conserva. Ambas condiciones:
tres llamadas y 27.660 tokens. No acredita fiabilidad general, fidelidad independiente
ni ahorro de lectura. Siguiente contraste: dos documentos reservados, antes de
incorporar la instrucción a producto y comparar lectura selectiva/completa.

## Agrupación en dos casos reservados: respaldo aún parcial

[Contraste reservado](../experiments/citation-grouping-heldout-v1/README.md): dos
respuestas válidas sin reparación, citas de 3.582 y 4.503 bytes y todas las obligaciones
de las rúbricas cubiertas. Jev encontró una afirmación con respaldo insuficiente:
dos ejemplos presentes en otros pasajes no quedaron citados. Original intacto,
sin promoción de defaults. Seis llamadas, 37.408 tokens. Próximo paso: reparación
candidata de los localizadores y control de subafirmaciones; luego comparar lectura
selectiva/completa con costes y fidelidad. No cambia la integración del ecosistema.

## Reparación localizada y primera comparación de lectura

[Derivado con respaldo ampliado](../experiments/citation-support-derived-v1/README.md):
C3 conserva texto y añade tres localizadores; Jev favorece el derivado, con
probabilidades cercanas. No es validación concluyente ni promoción automática.

[Comparación en fuente nueva](../experiments/reading-paired-grouping-v1/README.md):
5.145 frente a 34.053 bytes; 5.164 frente a 26.504 tokens contando generación y dos
revisiones. Ambos cubren la rúbrica y reciben respaldo de Jev, pero la selección
pierde la excepción Automotive/10-core presente en la fuente y en la respuesta
completa. Ahorro observado sin equivalencia de calidad demostrada. Siguiente paso:
control de condiciones/excepciones, ampliación trazable y regresión sobre este caso;
contraste posterior en fuente nueva. Sin cambios de defaults ni integración.

## Recuperación de condiciones: regresión conocida resuelta

[Ampliación experimental](../experiments/condition-expansion-v1/README.md): selector
léxico acotado recuperó Automotive/10-core desde pregunta y rangos iniciales, sin
recibir rúbrica. Lectura de 5.145 a 7.213 bytes; respuesta sin reparación conserva
la excepción, R1–R3 cubiertos y tres afirmaciones respaldadas según Jev. Tres llamadas,
8.186 tokens. Seis pruebas offline y reproducción verificadas. Añade también un
párrafo no necesario: heurística todavía imprecisa. Código sólo experimental,
sin promoción a CLI/default. Próximo paso: fuente reservada, control sin excepción
y condición fuera de presupuesto antes de decidir incorporación.

## Ampliación en fuente reservada: no se promueve

[Validación en métricas de sesgo](../experiments/condition-expansion-heldout-v1/README.md):
la heurística congelada mejora de 1/4 a 2/4 requisitos, pero deja fuera las definiciones
de ΔG y ΔS. Candidatos válidos y afirmaciones respaldadas según Jev no equivalen a
respuesta suficiente. Control sintético revela falso positivo por “only”; control de
presupuesto preserva límites. Seis llamadas, 16.266 tokens; sin tuning ni reparación.
Próximo incremento: propuesta de recuperación adicional ante cobertura incompleta,
buscando definiciones y condiciones con presupuesto y parada explícitos. Sin cambios
de CLI/defaults ni integraciones del ecosistema.

## Propuesta explícita de recuperación disponible

[CLI coverage-plan](recuperacion-cobertura.md) conecta una revisión de rúbrica
incompleta con una propuesta de pasajes adicionales, preservando contexto y hashes,
con presupuesto total y parada explícita. No llama a modelos ni admite memoria.
[Regresión conocida](../experiments/coverage-recovery-v1/README.md): recupera ΔG/ΔS,
de 5.162 a 9.439 bytes dentro de 12.000. El pasaje anotado de BLEU sigue fuera:
no hay declaración de cobertura completa ni nueva respuesta evaluada. Próximo paso:
consumidor explícito para generar un derivado desde la propuesta y evaluarlo; luego
validación reservada. El contrato no es intercambiable con `generate-plan`.
