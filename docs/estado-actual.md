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

## Generación explícita desde recuperación verificada

`generate-recovery` reconstruye la propuesta y verifica entradas antes de una única
llamada. Conserva candidato padre, revisión, propuesta y respuesta derivada por hash.
[Recorrido real](../experiments/recovery-generation-v1/README.md): ΔG/ΔS incorporados,
4/4 requisitos cubiertos según GLM y 7/7 afirmaciones respaldadas según Jev, una de
ellas con probabilidades cercanas a insuficiencia. 9.439 bytes, tres llamadas,
10.260 tokens reportados. 508 tests del producto; reproducción local verificada.
Es una regresión conocida, sin promoción a estrategia predeterminada. Próximo paso:
validación en casos nuevos con controles y parámetros fijados; revisar afirmaciones
limítrofes. El motor completo de memoria y las integraciones siguen pendientes.

## Batería nueva: parada correcta y discrepancia de fidelidad

[Dos documentos reservados localmente](../experiments/recovery-heldout-v1/README.md):
ambos cubren 2/2 requisitos según GLM, por lo que `coverage-plan` no amplía.
Jev respalda 6/7 afirmaciones; C6 del segundo caso queda insufficient, sin explicación
causal en el formato de respuesta. Se conservan afirmación y cita para adjudicación.
Seis llamadas, 16.508 tokens reportados; controles y reconstrucción local pasaron.
No hubo activaciones reales de recuperación: su generalización sigue sin comprobarse.
Próximo paso: adjudicar la discrepancia y preparar, por separado, un reto de omisiones
controladas con protocolo previo. Sin cambios de producto ni promoción de defaults.

## Reto inducido: recuperación activada, sin cierre satisfactorio

[Dos fuentes nuevas con semillas sintéticas](../experiments/recovery-induced-v1/README.md):
las omisiones activan propuestas de 9.548 y 9.650 bytes. Primer candidato rechazado
por texto posterior al JSON; segundo válido y parcial, pero revisión de cobertura
agotada (2.048 tokens, contenido vacío). Jev respalda lo dicho por el segundo,
sin demostrar que cubra la pregunta. Los pasajes exactos de la rúbrica quedan fuera
de ambos contextos. Seis llamadas, 17.611 tokens; reproducción offline verificada,
sin reintentos ni promoción. C6 anterior tiene contraste contextual documentado,
no adjudicación independiente. Siguiente: comparar recuperación offline separando
los fallos de selección, formato y presupuesto del revisor antes de otra condición.

## Comparación offline: el cuello de botella sigue en selección

[Cuatro variantes a igual presupuesto](../experiments/retrieval-comparison-v1/README.md)
no recuperan los párrafos anotados de los dos casos conocidos. El párrafo de modelos
queda en puesto léxico 29; las líneas de validación cruzada no comparten términos con
la pregunta. Limpiar palabras frecuentes y ampliar por sección desde las mismas
coincidencias no resuelve estos casos. Cuatro tests y reproducción del baseline
pasaron; cero llamadas. La rúbrica de modelos omite GPT-2/XLNet mencionados en su
propia evidencia: no basta para demostrar completitud. Sin promoción ni cambios
productivos. Próximo paso propuesto: listas/encabezados y relaciones de sección,
con evaluación separada de la suficiencia de las rúbricas antes de volver a API.

## Estructura documental: recuperación mejor, pero no universal

[Comparación offline en cuatro casos conocidos](../experiments/structure-retrieval-v1/README.md):
encabezados + listas recuperan los párrafos omitidos en los dos fallos (1/1 y 3/3),
pero pierden los aciertos del baseline en otros dos casos (0/1 y 0/1). Misma cota
12.000 bytes; cero llamadas, cuatro tests y reproducción pasaron. Se usó estructura
QASPER disponible, no extracción general desde PDF. Sin promoción ni cambios de
producto. Próximo candidato: combinar recuperación léxica y estructural bajo un
presupuesto común, comprobar regresiones y luego fuentes nuevas; no elegir por
etiquetas retrospectivas ni declarar suficiencia semántica a partir de rangos.

## Fusión a presupuesto fijo: tres casos cubiertos, una regresión

[Combinación offline congelada](../experiments/hybrid-retrieval-v1/README.md):
recupera todos los párrafos anotados en tres de cuatro casos conocidos; pierde el
párrafo de modelos de referencia que el baseline conservaba. Son 1.026 bytes omitidos
con sólo 262 libres. Cinco tests y reproducción pasaron; cero llamadas, sin cambios
de producto ni promoción. Próxima condición propuesta: preservar baseline y añadir
estructura con presupuesto restante, declarando insuficiencia cuando no cabe; después
casos nuevos. No confundir conservación de rangos con fiabilidad semántica.

## Presupuestos comparados: 12.000 no es un óptimo

[Barrido 8/12/20/32 KB](../experiments/budget-sweep-v1/README.md): el híbrido recupera
los párrafos anotados de 2/4, 3/4, 4/4 y 4/4 casos conocidos. 20 y 32 generan las
mismas selecciones. Contraste real en dos casos: cinco candidatos válidos con rúbrica
cubierta y respaldo Jev, uno rechazado por formato; sin reintentos. 16 llamadas,
39.225 tokens, 102,080 s acumulados de ejecuciones; precio monetario no medido.
Tres tests y replay pasaron. Sin cambio de defaults: no hay óptimo general probado.
Siguiente propuesta: ampliación por etapas conservando rangos, con parada cuando no
haya ganancia; validar después en fuentes nuevas y rúbricas suficientes.

## Ampliación conservadora por etapas: ensayo offline con fuentes nuevas

[Acumulación de rangos](../experiments/staged-retrieval-v1/README.md) conserva lecturas
previas y respeta 8/12/20/32 KB. Los cuatro controles alcanzan sus párrafos anotados;
dos fuentes nuevas también, ambas ya desde 8 KB. No prueban reparación de omisiones
nuevas. Cinco tests/replay pasaron; cero llamadas. La parada usa candidatos de todas
las etapas calculados previamente y no demuestra suficiencia semántica ni ahorro
local. Sin integración/defaults. Próximo recorrido: revisión explícita de cobertura
y fidelidad entre etapas, presupuesto acumulado y salida de insuficiencia.

## Etapa actual: recorrido explícito integrado, todavía piloto

La [CLI de lectura revisada](lectura-revisada-cli.md) permite revisar cobertura
con contexto, revisar fidelidad y determinar la siguiente acción con archivos
vinculados por hash. Conserva el revisor anterior; la revisión contextual utiliza
una versión experimental explícita. No admite memoria ni ejecuta vigilancia.

[Distinción y segunda lectura](../experiments/scoped-flow-v1/README.md): cinco
controles de ausencia contextual, omisión y contradicción recibieron las etiquetas
esperadas. Son controles del productor, sin adjudicación independiente. En un caso
real previamente detenido, la ruta pasó de información faltante a ampliación:
7.680 → 14.409 bytes, después 2/2 requisitos cubiertos y fidelidad respaldada por
Jev. El candidato original se conserva; el derivado queda para revisión explícita.
Diez llamadas, 18.964 tokens reportados; reproducción verificada.

[Fuentes nuevas y formatos](../experiments/scoped-generalization-v1/README.md): dos
documentos QASPER reservados localmente (40.772 y 37.439 bytes), un Markdown y un
JSONL sintéticos. Dos resultados quedaron como candidatos para revisión, uno con
evidencia insuficiente y otro con inspección de fidelidad requerida pese a cubrir
la rúbrica. Markdown y JSONL se leen como texto UTF-8; esto no demuestra extracción
PDF/Word ni interpretación general de formatos. Doce llamadas, 24.608 tokens;
reproducción verificada. Los cuatro rechazos anteriores a HTTP por comparación de
tuplas/listas se conservan: se corrigió la reproducción JSON de planes y se probó
la nueva condición por separado, sin reintentar llamadas al proveedor.

Verificación del incremento: 520 pruebas automatizadas pasaron. Total experimental:
22 llamadas y 43.572 tokens reportados, sin reintentos de proveedor; precio monetario
no medido. Estos resultados no prueban ahorro general ni ausencia de omisiones.
La clasificación de omisiones usa rangos de referencias suministradas: no descarta
evidencia equivalente en otras partes. Las cotas son por llamada; no existe un
presupuesto acumulado persistente entre comandos manuales.

Siguiente etapa recomendada: adjudicar los desacuerdos con etiquetas independientes,
ampliar fuentes reservadas y medir omisiones y coste total contra lectura completa.
Después evaluar extracción de otros formatos preservando localizadores. Catálogo,
consolidación y admisión gobernada, e integración contractual con Skopos y AN-KLA,
siguen pendientes del producto completo; no bloquean este recorrido independiente.

### Seguimiento: los dos pendientes tienen causas distintas

[Diagnóstico reproducible](../experiments/pending-resolution-v1/README.md): dos
anotaciones humanas preexistentes respaldan que la respuesta QASPER incluye
Visual7W; no es una fuente sin respuesta. La segunda lectura de 9.334 → 13.168 bytes
no recuperó ese nombre. Resultado: 1/2 requisitos cubiertos, fidelidad respaldada,
insuficiencia conservada. Tres llamadas, 13.074 tokens; reproducción offline pasó.
Se requiere mejorar la selección, no asumir que más párrafos bastan.

En JSONL ambas afirmaciones estaban respaldadas; el desacuerdo afecta únicamente
al límite sobre posibles cambios posteriores. La inspección recomienda responder
«miércoles según el registro hasta las 09:15» y separar esa respuesta de su límite
temporal. No se aplicó reparación ni se sustituyó el dictamen original. Sigue
pendiente adjudicación independiente; el ensayo no cambia producto ni defaults.

### Cierre técnico de esta fase y capacidad incorporada al producto

[Último bloque acotado](../experiments/phase-exit-v1/README.md): la CLI dispone de
`retrieve-structured`, conectado a `generate-plan` mediante contrato v3 experimental.
Valida estructura contra fuente, conserva el baseline y añade rangos bajo presupuesto.
No depende de código experimental externo ni sustituye contratos/defaults existentes.
Contra el baseline del producto mejora referencias en cuatro de ocho casos conocidos;
seis casos reúnen todas las referencias. No equivale a exactitud semántica ni
validación reservada. Los controles temporales Jev coincidieron en 2/4 etiquetas del
productor: limitación explícita, sin promoción. Una llamada, 1.250 tokens.

Cierre técnico recomendado de estas iteraciones: usar lo implementado en piloto
supervisado y conservar límites, sin más ajustes automáticos del mismo benchmark.
Verificación: 525 pruebas pasaron, incluido el recorrido CLI con generación replay;
no se ejecutó generación live con el nuevo selector. La aceptación pertenece al
Operador. Otra fase debe fijar objetivo, presupuesto y
salida propios; el motor completo no tiene una fecha de terminación acordada.

### Comparación externa acotada: MemOS local

[Dos casos conocidos](../experiments/memos-comparison-v1/README.md): MemOS recuperó
Visual7W y el benchmark abierto propio que la lectura anterior de Ágora omitía.
En la corrección temporal retuvo miércoles sobre martes, pero añadió fecha del evento
y fechas de calendario ausentes del original. También infirió interés personal al
recibir el artículo. Conservó texto fuente/hash en metadatos; eso no vuelve verdaderas
las inferencias. Los tres umbrales devolvieron los mismos recuerdos en ambos casos.

16 solicitudes HTTP, cero reintentos; tokens/coste interno no medidos. No es igualdad
de presupuesto: MemOS procesó la fuente completa antes de buscar. Sin cambios a su
configuración ni integración productiva. Recomendación: proveedor opcional de recuperación
sólo mediante contrato de evidencia original, separando inferencias y fechas de captura
vs evento. El benchmark queda cerrado con resultado mixto, sin reemplazar componentes.

### AN-KLA frente a MemOS: bloque sintético cerrado

[Cuatro casos, dos condiciones](../experiments/ankla-memos-v1/README.md): AN-KLA
0.1.0b24 recuperó literalmente los ocho inputs y ambos stores de laboratorio
verificaron integridad. MemOS conservó varios contenidos centrales, pero una
conversación de retoma devolvió cero memorias tras HTTP 200, y la corrección temporal
volvió a incorporar fechas no suministradas. 32 solicitudes HTTP sin reintentos;
llamadas internas, tokens y coste no medidos. Memoria vigente de Ágora sin cambios.

No hay equivalencia de ranking: cuatro registros por store AN-KLA frente a un cubo
por caso MemOS. No se probaron supersede/checkpoint ni enforcement. Recomendación:
conservar AN-KLA para registros explícitos gobernados; MemOS sigue siendo candidato
auxiliar, con comprobación de ingestión y procedencia antes de cualquier integración.

### Transiciones AN-KLA y acción de laboratorio: verificadas con límites

[Ensayo y reproducción limpia](../experiments/ankla-transitions-v1/README.md): supersede
retira el registro anterior de recuperación vigente y preserva su revisión; checkpoint
show/resume conservan working-state-v2; planes de checkpoint y escritura con revisión
obsoleta son rechazados sin cambiar CURRENT. AN-KLA 0.1.0b24, cero llamadas a modelos.

attest run rechazó una acción no permitida antes de crear el archivo marcador. En otro
store, el argv exacto autorizado creó el marcador; alterar el destino volvió a bloquear.
Es bloqueo efectivo de esa ruta, no sandbox global ni integración con la ejecución de
agentes. Memoria declarativa no configura permisos. No se cambió código productivo ni
se instaló control de ejecución fuera del laboratorio.

### MemOS: equivalentes de transiciones inspeccionados

[Ensayo nativo de feedback](../experiments/memos-transitions-v1/README.md): un cubo
sintético nuevo, siete solicitudes HTTP y cero reintentos. La corrección Tuesday →
Wednesday respondió 200 pero cero operaciones; get_all conservó la memoria y search
siguió devolviendo Tuesday. La ingestión añadió una fecha no suministrada. Resultado
limitado a un caso; no se determinó la causa interna ni una tasa de fallos.

No se identificó checkpoint de tarea ni ejecución con allowlist en la API inspeccionada.
Existen serialización y hooks de versión, sin equivalencia transaccional demostrada.
No se ejecutó restauración sobre el grafo compartido ni se atribuyó bloqueo a una
respuesta del chat. Próximo paso: diagnóstico acotado de feedback y control positivo
de actualización antes de cualquier integración.

### MemOS, Skopos y Ágora: comparación de funciones

[Dos casos sintéticos](../experiments/memos-skopos-agora-v1/README.md): Skopos
conservó texto/sello mediante su parser Codex; Ágora recuperó párrafos exactos,
rechazó fuente alterada y produjo dos respuestas candidatas con cinco citas cada una.
MemOS conservó fuentes en metadatos y contenido central, pero añadió fechas probables
en la contradicción. Corrección dentro del texto no prueba actualización por feedback.

31 tests dirigidos pasaron; 10 solicitudes MemOS y dos generaciones Ágora. Sin
comparación de coste total, generalización, MongoDB vivo ni integración nueva.
Los componentes cubren funciones distintas; no hay evidencia para sustituirlos.

### Feedback MemOS reparado parcialmente y bloque largo reservado

[Informe](../experiments/memos-long-reserved-v1/README.md): se identificaron método
Neo4j ausente y ruta de feedback que perdía IDs explícitos. Dos parches locales
sin publicar en MemOS; cuatro regresiones pasan. La instancia temporal aplicó
corrección y archivó anteriores, pero search devolvió archivados aun con filtro
activo. Fidelidad temporal y recuperación vigente siguen pendientes.

Dos artículos QASPER de 45/63 KB, cuatro preguntas: MemOS recuperó dos respuestas
centrales y omitió detalles críticos en dos; Ágora produjo dos candidatos con omisión
y rechazó dos salidas incompletas. 35353 tokens MemOS (30135 ingestión + 5218 consulta)
frente a 15780 Ágora; embeddings/infraestructura/dinero no medidos. Sin promoción,
sin ganador general y sin ajustes posteriores a las respuestas.

### Alcance de lectura y filtro de vigencia: seguimiento corregido

[Implementación y prueba](../experiments/scope-vigency-repair-v1/README.md): Ágora
incorpora `--scope-guard` optativo, contrato multipasaje v0.3. Lecturas parciales
quedan `candidate_requires_expansion`; la segunda lectura sigue siendo explícita.
527 tests pasan. Dos lecturas completas recuperaron los puntos centrales omitidos
en casos ya conocidos, con 26663 tokens adicionales: no nuevo resultado reservado.

Se corrige el diagnóstico anterior de MemOS: el filtro debe usar
`{"and":[{"status":"activated"}]}`. Con esa forma devolvió sólo activos y el
control inverso sólo archivados. Chat respondió miércoles y fecha desconocida.
No hubo nuevo parche MemOS ni reinicio de 9696; los dos arreglos previos continúan
locales, pendientes de gates completos. No tratar búsqueda sin filtro como vigente.

### Banco verificable y scope-guard en generate-plan

[Base del banco](../experiments/benchmark-bank-v1/README.md): generate-plan incorpora
--scope-guard para citas literales e IDs y expone presupuesto verificado y necesidad
de ampliar. Dos recorridos CLI con respuestas conservadas pasan sin HTTP.
verify_benchmark_evidence.py comprueba hashes, denominadores y tokens de la campaña
conservada; no certifica semántica ni costes no observados.

Herramientas instaladas en entorno temporal autorizado: make format pasó en copia
desechable de MemOS, pytest dirigido 55 passed / 3 integración Neo4j skipped. Se
aplicó sólo formato a archivos propios. Parches locales sin publicar ni promover.


### Identificadores en el consumidor multipasaje (v0.4 optativa)

`passage_cli --citation-mode ids` conecta las unidades por identificador existentes,
limita el texto de salida y conserva los faltantes por aspecto. Incluye control de
alcance; el modo literal y sus contratos anteriores siguen disponibles. No añade
reparación automática ni admisión de resultados. Pruebas y repetición de los dos
rechazos conocidos: [refinement-v2](../experiments/refinement-v2/README.md).


### Reparación asistida del caso de fórmula faltante

[Expediente](../experiments/focused-label-v1/README.md): selección manual de cuatro párrafos, tres llamadas (8.790
tokens), dos respuestas estructuralmente válidas rechazadas por el productor y una
reparación final que conserva el dato faltante. Sin cambio de código ni aceptación
automática. La candidata mantiene alcance parcial; mostrar `missing` junto a
`answer` es necesario para no ocultar el límite. No es nueva comparación MemOS.


### Respuesta, faltantes y alcance visibles en la CLI

`passage_cli` muestra juntos respuesta, `missing`, alcance y necesidad de ampliar.
`python3 -m agora.passage_view <result.json>` permite inspección local sin proveedor,
con hash del archivo y advertencia de que mostrar no equivale a verificar. Los
resultados históricos no se alteran y los rechazos no se presentan como candidatos.
548 tests pasan; validado con el caso real de fórmula faltante sin llamadas API.
Guía y compatibilidad de stdout: [consulta multipasaje](consulta-multipasaje.md).


### Plan explícito reproducible de pasajes

`plan-passages` fija rangos manuales, fuente y pregunta; `generate-plan` los
reconstruye antes de usar un proveedor o respuesta guardada. El caso de fórmula
faltante se reprodujo por CLI sin HTTP, conservando respuesta, faltantes y alcance
parcial. 554 tests pasan. [Expediente](../experiments/explicit-plan-v1/README.md).
Esto habilita repetición controlada; todavía no demuestra selección automática.
