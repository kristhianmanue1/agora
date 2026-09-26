# Piloto externo AttrEval-GenSearch — 02

## Protocolo fijado antes de llamadas

Fecha: 2026-09-24. Comparación v1/v2 sin modificar revisores, después del piloto
externo de doce casos y los seis pares de controles. Aquí se evalúan **24 casos
externos nuevos**, ocho por clase original. Es un subconjunto estratificado de
desarrollo, no un resultado oficial del benchmark ni una estimación representativa
de prevalencias de producción. No se mezclarán sus métricas con controles sintéticos.

Datos locales previamente descargados de
[osunlp/AttrScore](https://huggingface.co/datasets/osunlp/AttrScore), revisión
`467dcdd2cd31f9b5e8625491f3bdf7af90943a8d`, AttrEval-GenSearch.csv, SHA-256
`20e04c78161c0cbb6506507220ec04fdd035db24540279228d61479381187ca2`.
No se descargó una revisión nueva ni se ejecutó código remoto.

## Selección reservada y límites

242 filas originales; se excluyen 22 por coincidencia de pregunta, respuesta **o**
referencia con los doce casos previos. Coincidencia significa espacios normalizados
y comparación sin distinción de mayúsculas, no similitud semántica. Quedan 220
filas elegibles. Se eligen ocho por clase por hash, semilla
`agora-attrscore-pilot-02`, descartando también repeticiones entre seleccionados;
se registran tres colisiones durante la selección. No se excluyeron casos por
conocer resultados del modelo, ni se tradujeron, truncaron o editaron las fuentes.
No se asegura separación de temas, sitios ni conocimiento previo del modelo.

Reservada significa que esos 24 casos no se usaron en las llamadas previas del
piloto local; no demuestra ausencia del corpus en el entrenamiento de GLM. El
corpus original y la experiencia con otros doce casos ya eran conocidos. El gold
sirve para estratificar y puntuar, nunca se envía al modelo. Se conserva sin cambios:
Attributable → supported; Contradictory → contradicted; Extrapolatory → insufficient.
Las limitaciones de ese mapeo, documentadas en el piloto 01, siguen aplicando.

## Ejecución y criterios de parada

48 llamadas máximas, v1/v2 pareadas y orden alternado por caso. GLM-5.3-Flash,
temperatura 0, inglés original, 8192 tokens máximos de salida por llamada,
180 s por transporte y 200 s por trabajador. Máximo reservado: 393216 tokens de
salida; no es estimación de consumo ni límite monetario exacto. Sin reintentos,
reparación de JSON ni cambios de prompts o expectativas durante la tanda.

Fallo de transporte/acceso/integridad o uso total desconocido detiene la tanda;
rechazo estructural con uso conocido se conserva y continúa. Fallos y no ejecutados
permanecen en el denominador. Se congelan entradas, código de producto, transporte,
runner, preparación, puntuación, auditoría y este protocolo antes de la primera llamada.

## Dos lecturas separadas del resultado

1. **Concordancia con etiquetas originales:** exactitud sobre 24 casos, macro-F1 de
   tres clases, matriz con failed/not_run y comparación pareada. Los contadores
   unsupported_accepted y supported_rejected se conservan por continuidad, pero
   significan desacuerdo support/gold; no aprobación operativa ni error adjudicado.
2. **Comportamiento del revisor:** distribuciones de pertinencia y recomendación,
   inspección de explicaciones tanto de supported como de casos que piden revisión.
   No hay gold independiente de pertinencia/acción; por tanto, sus conteos no son
   exactitud ni tasas de seguridad. Las observaciones cualitativas no reemplazan
   etiquetas después de observar resultados.

Se informan formato válido, todos los tokens reportados y tiempo por versión.
No se estiman euros/dólares sin tarifa y clases de uso verificadas. Una llamada
por caso no demuestra estabilidad. No se evalúan recuperación, generación, español,
documentos largos, autenticidad externa ni aprobación automática. Ninguna mejora
numérica por sí sola promoverá v2 a predeterminado o activará una cascada.

## Resultado observado — 2026-09-24

Las 48 llamadas finalizaron. No hubo reintentos, timeouts ni uso desconocido.
Hubo cuatro rechazos estructurales con consumo conocido: tres v1 y uno v2.
Se verificaron freeze, selección reproducible, fuentes íntegras, ausencia de gold
en payloads, hashes de resultados y reproducción local de validación. El proveedor
reportó glm-5.3-flash en los recibos; eso no acredita introspección independiente
de su backend.

| Métrica | v1 | v2 |
|---|---:|---:|
| Dictámenes válidos | 21/24 | 23/24 |
| Coincidencias con gold original, fallos incluidos | 15/24 (62.5%) | 18/24 (75.0%) |
| Macro-F1, tres clases | 0.6465 | 0.7619 |
| Gold negativo clasificado supported | 0/16 | 0/16 |
| Gold supported clasificado insufficient/contradicted | 3/8 | 3/8 |
| Gold supported con fallo estructural | 2/8 | 1/8 |
| Tokens reportados, incluidos rechazos | 33 870 | 69 711 |
| Segundos acumulados de llamadas | 535.171 | 1072.889 |

Total: **103 581 tokens y 1608.060 segundos** de llamadas (aproximadamente
26 min 48 s). V2 consumió **105.8% más tokens** y aproximadamente el doble de
tiempo. No se estima coste monetario. Comparación pareada: 14 casos acertados por
ambas, 4 sólo por v2, 1 sólo por v1 y 5 por ninguna; no hubo casos sin pareja.

Distribuciones descriptivas, sin gold propio para estos ejes:

| Salida | v1 | v2 |
|---|---:|---:|
| needs_revision | 19 | 19 |
| needs_adjudication | 2 | 4 |
| Recomendación no disponible por fallo | 3 | 1 |
| Relevance: relevant | 19 | 23 |
| Relevance: extra | 2 | 0 |

`needs_adjudication` no es aprobación. Cero predicciones supported contra gold
negativo no demuestra ausencia de afirmaciones insuficientemente sustentadas:
el gold no representa exactamente la rúbrica estricta, y hay fallos sin dictamen.
Los números no certifican seguridad ni fidelidad general.

## De dónde procede la ventaja de v2

- **case-08, case-16 y case-24:** v2 coincide con gold donde v1 no produjo un
  dictamen estructuralmente válido. Son ventajas operativas, no evidencia de que
  v1 hubiera emitido una clasificación válida peor.
- **case-03:** ambos produjeron salida válida; v2 dijo contradicted y v1
  insufficient. Sólo v2 coincide con gold. La explicación de v1 distingue posibles
  fechas de medición del salario; la de v2 usa la diferencia numérica. No se
  adjudica aquí que coincidir con gold resuelva toda esa ambigüedad.
- **case-11:** v1 coincide con gold y v2 falla formato.

Por tanto, tres de los cuatro aciertos exclusivos de v2 corresponden a fallos de
formato de v1. La mejora neta de tres puntos no debe describirse como demostración
de superioridad semántica. No se eliminan fallos del score principal para producir
una comparación más favorable.

## Autorrevisión adversarial de los resultados

El principal inspeccionó preguntas, respuestas y referencias de los 24 casos y
los dictámenes guardados, incluyendo los supported y los que piden revisión.
Esta fase tiene resultados y etiquetas disponibles; **no es revisión independiente
ni adjudicación humana**. Las observaciones no modifican gold ni puntuaciones.

| Hallazgo | Evidencia y efecto | Consecuencia propuesta |
|---|---|---|
| Campos adicionales invalidan salidas | v1: case-08 reason_note, case-16 relevance_note, case-24 quote_indices_used; v2: case-11 relevance_detail. Todos rechazados, incluso cuando una etiqueta interna parece razonable. | Mejorar cumplimiento de formato en generación, conservando el validador; no reparar silenciosamente ni repuntuar la tanda. |
| V2 pierde atribución y grado de certeza | case-08: la fuente presenta el origen del helado como relato atribuido a Epperson; v2 reconoce esa diferencia pero da supported a una afirmación categórica. Coincide con gold, pero tensiona su contrato de preservar certeza. | Añadir un control pareado de relato atribuido frente a hecho establecido antes de corregir el revisor. |
| V2 puede desvincular un detalle de su medición | case-21: marca supported «incluyendo fiordos e islas» aunque reconoce que la cita vincula esa inclusión a otra cifra. El claim completo queda insufficient por otros detalles. | Evaluar cada detalle en el contexto del claim completo; el acierto global no valida todas sus partes. |
| V1 confunde pertinencia de cita y respuesta | case-10: la respuesta sí contesta qué animal, pero v1 devuelve extra porque el fragmento no menciona ese animal. Support insufficient es razonable; extra juzga el objeto equivocado. | Separar explícitamente relevancia de la respuesta y suficiencia de su evidencia. |
| Gold y contrato estricto siguen divergentes | Ambos cuestionan detalles ausentes en case-04, case-07 y case-18, aunque gold sea Attributable. En case-13 y case-21 ambos marcan insuficiencia donde gold dice contradicción. | Conservar ambas lecturas, sin convertir automáticamente discrepancia en error del modelo o del dataset. |

En case-01 ambos respaldan el contenido porque la cita reproduce sus afirmaciones;
esa relación textual no demuestra verdad científica externa. En case-19 aceptan
una publicación de 2022 como «reciente», pero no existe fecha de referencia explícita
en el payload; ese adjetivo conserva una ambigüedad temporal. En case-20/23 la
inferencia de contradicción depende de tratar las listas de cargos/autores como
exhaustivas: formato de lista no equivale por sí solo a garantía de completitud.
Ninguno de estos ejemplos convierte este ensayo en validación científica, médica
o jurídica de las fuentes históricas.

## Decisión técnica recomendada

**Mantener v2 experimental y consultivo. No promoverlo automáticamente ni construir
una cascada v1→v2 a partir de este resultado.** V2 cumplió los seis pares sintéticos
y aquí obtuvo más coincidencias externas, pero duplicó el consumo y conserva fallos
de formato y de fidelidad por detalle. El resultado del primer piloto (v1 8/12,
v2 6/12) tampoco se borra: muestras y distribuciones distintas producen resultados
distintos; no hay una victoria uniforme.

El siguiente bloque útil es corregir los defectos observados, en vez de aumentar
otra vez el tamaño de la batería:

1. **Formato:** conservar los cuatro recibos fallidos como regresiones. Evaluar
   generación estructurada compatible con el proveedor y un esquema cerrado;
   nunca tratar un JSON reparado como la salida original válida.
2. **Certeza y alcance:** controles nuevos que obliguen a conservar atribuciones,
   negaciones, excepciones y vínculo entre cifra y modificador; revisar el mecanismo
   de revisión por detalles sin confiar sólo en que el prompt lo exija.
3. **Pertinencia:** control donde la respuesta es pertinente pero la cita resulta
   insuficiente, para impedir que se mezclen esos dos ejes.

Fijar esos controles antes de cambiar producto, comprobar positivos y negativos,
y medir la corrección con ejemplos nuevos. Las muestras ya observadas quedan como
regresión, no como nueva prueba reservada. Esta recomendación no se implementó en
el incremento actual; tampoco se modificaron revisores para favorecer las métricas.

## Entregables y comprobaciones

- Scripts reproducibles bajo experiments/attrscore-v2; score reutiliza las mismas
  definiciones del piloto 01, y en esta tanda tanto score como audit se congelaron
  antes de las llamadas.
- Evidencia local gitignored bajo experiments/attrscore-v2/runs/glm-01:
  protocol.md/json, freeze.json, execution.json, audit.json y request/receipt/result
  por versión/caso. Inputs y recibos deben conservarse para reproducir la auditoría.
- **278 pruebas locales pasaron**, incluidas cuatro nuevas para selección: exclusión
  por cada campo, deduplicación entre clases, fallo cuando faltan casos distintos y
  selección determinista. No equivalen a exactitud semántica.
- AN-KLA verificó rev 3; contexto correcto con aviso preexistente fuera del bloque
  administrado. Sin escritura de memoria, cambios de producto, commit o push.
