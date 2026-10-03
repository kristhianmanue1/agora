# Campaña reservada v2: ejecutada, con fallos observados

Dos fuentes QASPER: 68 958 y 45 390 bytes UTF-8, dos preguntas por fuente.
Selección determinista sin consultar respuestas: primeros identificadores no
presentes en los artefactos locales revisados, entre 40 000 y 100 000 bytes.
No se afirma ausencia en entrenamiento del modelo ni representatividad estadística.

`freeze.json` fija hashes, configuración y límites: 14 peticiones HTTP MemOS,
4 generaciones Ágora, cero reintentos, 180 segundos por petición, salida máxima
4096 tokens por respuesta. El límite HTTP no limita las llamadas internas de MemOS;
se medirán por separado. Ágora recibe hasta 12 000 bytes de pasajes por pregunta;
MemOS ingiere la fuente completa una vez. Esa diferencia es parte del mecanismo
comparado, por lo que se contabiliza ingestión además de consultas.

Las etiquetas se mantienen fuera del contexto generador. Se reconstruyen desde
el dataset local fijado por hash y las primeras dos preguntas de cada documento;
el hash de gold.json conserva la identidad de las referencias originales.
Los fallos, abstenciones y rechazos permanecen en el denominador. Se evalúan
omisiones importantes, respaldo, tokens y tiempos; no sólo número de citas.
La comparación con etiquetas externas realizada por el productor no equivale a
adjudicación independiente. Los resultados de la ejecución posterior se conservan abajo; freeze.json permanece como registro previo, sin reescribirlo.

## Resultados observados

| Medida | MemOS | Ágora |
|---|---:|---:|
| Documentos / preguntas | 2 / 4 | 2 / 4 |
| Tokens ingestión | 33 560 | No hay ingestión LLM previa |
| Tokens consultas | 5 291 | 13 792 |
| Tokens totales observados | 38 851 | 13 792 |
| Segundos ingestión | 103,63 | No aplica |
| Segundos consultas, suma | 59,18 | 56,07 |
| Abstenciones | 2 | 2 |

Son tokens reportados por GLM, incluidos razonamiento y respuestas fallidas. Los
14 HTTP MemOS corresponden a 6 recibos LLM; Ágora hizo 4 llamadas. No hay reintentos
al proveedor. Un intento previo de lanzamiento de Ágora fue rechazado por Llavero
antes de iniciar el consumidor por usar una ruta relativa del intérprete.
Las consultas MemOS incluyen búsqueda y chat; no es medición de coste monetario,
infraestructura ni amortización. Los servicios compartieron equipo y proveedor.

### Fallos encontrados

1. **MemOS: ingestión vacía con mensaje de éxito.** El segundo documento produjo
   JSON con una coma sobrante antes del cierre. El proveedor terminó con `stop`;
   no fue truncamiento. `parse_json_result` devuelve `{}` sin lanzar excepción.
   Add devuelve HTTP 200, mensaje de éxito y `data: []`; get_all y búsquedas
   confirman cero memorias. Se gastaron 13 545 tokens en esa ingestión fallida.
   Replay local del resultado real y control sintético reproducen el vacío;
   el control positivo con JSON válido conserva su contenido. No se corrigió
   el producto ni se repitió la ingestión durante la campaña.
2. **Ambos: omisión de pruebas cualitativas en uso cotidiano.** Para MagiCoder,
   los tres anotadores contestan sí a la pregunta sobre pruebas con farmacólogos.
   La fuente menciona pruebas cotidianas y resultados cualitativos preliminares.
   Ese párrafo no llegó al contexto consultado por ninguno. Sus respuestas «no»
   se centran en ausencia de un ensayo controlado con tiempo medido, una afirmación
   más estrecha. Hay que distinguir ambos tipos de evidencia. No se resuelve la
   discrepancia convirtiendo automáticamente cualquier anotación en verdad.
3. **Ágora: inversión numérica pese a citas correctas.** La respuesta enumera
   «precisión y recall (86%/88%; 64%/63%)», mientras que la fuente dice recall
   86/64 y precisión 88/63. Validar que existe la cita no detectó esa inversión.
4. **Ágora: búsqueda insuficiente.** Se abstuvo ante la pregunta sobre baselines,
   aunque el documento sí describe dos. El párrafo no estuvo entre los recuperados.
   Su segunda abstención pregunta por ausencia de una hipótesis: no debe forzarse
   una respuesta negativa general a partir de una lectura parcial.

La respuesta de Ágora sobre acuerdo de anotación coincide en lo central con las
referencias. MemOS coincide en lo central sobre ausencia de hipótesis explícita;
la explicación adicional de MemOS está marcada como inferencia, sin validación
independiente de cada detalle. No se calcula un ganador con cuatro preguntas.

## Evidencia y límites

`result.json` separa tiempos y tokens; `assessment.json` contiene valoración del
productor; `references.json` conserva etiquetas externas sin datos de anotadores.
`agora-receipts.json` y `http-receipts.json` conservan estados, procedencia y hashes;
`memos-usage.json` conserva recibos del proveedor sin razonamiento. Las respuestas
están en `comparison.json`. Los resultados originales y las fuentes completas
permanecen localmente en `/tmp/memos-long-reserved-v2`.

`parser-probe.json` y `probe_parser.py` reproducen el parser con controles y cero
llamadas al proveedor; `extraction-candidate.json` contiene sólo la salida final
malformada necesaria para reproducir el fallo, sin razonamiento ni credenciales.
Los ejecutores usan las rutas locales originales; no son instaladores portables.
No ejecutar nuevamente run_memos.py como si fuera una comprobación sin efectos:
crea cubos nuevos y consume llamadas. Los cuatro hashes candidatos MemOS fueron
verificados antes del arranque. Ágora no cambió código respecto a la revisión
congelada. El servidor temporal 9697 se detuvo al terminar; 9696 no fue reiniciado.

Ágora respondió en español y MemOS en inglés: prompts, ruta de recuperación e
ingestión son diferentes. Es comparación de recorridos configurados, no una
ablación causal ni una prueba de que uno de los modelos sea mejor. El máximo de
4096 tokens corresponde a respuestas, no al extractor interno de MemOS. Las
etiquetas son humanas externas; la adjudicación de este expediente es del productor.

## Continuación propuesta

- En una regresión separada, hacer visible el fallo de extracción vacío en MemOS;
  una reparación sintáctica debe ser explícita y validada, no ocultar el fallo.
- Añadir al revisor de Ágora un caso que cambie la asociación de cifras y métricas
  manteniendo citas exactas, con su control positivo correcto.
- Ejecutar la segunda lectura explícita para las omisiones, con presupuesto nuevo;
  conservar estos resultados de primera lectura y medir el coste acumulado.
- Después usar nuevos casos reservados y adjudicación separada antes de promover.
