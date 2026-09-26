# Controles pareados de revisión — 01

## Protocolo previo a llamadas — 2026-09-24

Objetivo: distinguir detección de defectos de rechazo indiscriminado. Seis pares
nuevos redactados para diagnóstico, dos por dimensión. Son material sintético
en inglés, no benchmark público ni una muestra representativa de documentos.
No reutilizan ejemplos de AttrScore. No evalúan recuperación ni generación.

| Par | Manipulación negativa | Esperado: support / relevance |
|---|---|---|
| quantity | Claim cambia 18 por 19 frente a «exactamente 18» | contradicted / relevant |
| latest | Fuente pierde declaración explícita de última versión | insufficient / relevant |
| year | Pregunta cambia año; claim y fuente se conservan | supported / extra |
| subject | Pregunta cambia espécimen; claim y fuente se conservan | supported / extra |
| author | Fuente pierde atribución al autor reclamado | insufficient / relevant |
| publication | Fuente pierde nombre del boletín reclamado | insufficient / relevant |

Todos los positivos esperan supported / relevant. Idioma esperado: match.
Positivos esperan needs_adjudication, **nunca aprobación**; negativos,
needs_revision. Una sola manipulación semántica en question/reference/claim por
par; también cambian hashes y derivados del JSON. Los pares author/publication
miden atribución textual mediante support: no autentican autores ni prueban un
clasificador independiente de procedencia. Ambos usan eliminación de atribución,
por lo que su cobertura es estrecha.

Expectativas separadas en inputs/pilot-01/gold.json, fijadas antes de llamadas.
Orden por hash de contenido con semilla agora-review-controls-01; IDs no revelan
par ni polaridad. El modelo recibe pregunta, claim y referencia completa, sin gold.
Fixtures construidas mediante query_evidence y proveedor simulado; no se presentan
como generaciones de GLM. Los dictámenes sí serán llamadas reales.

El agente separado /root/attrscore_separate_review revisó prepare.py y gold.json
antes de ejecutar. No encontró ambigüedades bloqueantes; sus precisiones sobre
manipulación semántica, atribución textual, acción y cobertura se incorporan aquí.
Vio expectativas: es revisión del diseño, no adjudicación ciega. No revisó runner
ni fixtures resultantes; el principal verifica éstos localmente.

## Límites y medición fijados

Comparación v1/v2 sin cambios de producto, mismo glm-5.3-flash, temperatura 0,
8192 tokens máximos de salida, 180 s por transporte, 200 s por proceso trabajador.
24 llamadas como máximo, sin reintentos; 196608 tokens de salida reservados, no
presupuesto monetario exacto. Fallo de transporte, acceso, integridad o uso total
desconocido detiene la tanda. Rechazo estructural con uso conocido se conserva y
continúa. Orden de versiones alternado por caso.

Se congela código de producto, preparación, worker, transporte, runner, puntuación,
auditoría, entradas y este protocolo antes de la primera llamada. No se ajustan
expectativas ni prompts durante la ejecución.

Métricas: coincidencia exacta por support, relevance, language y recommendation;
acierto conjunto por caso y por par completo; positivos y negativos acertados por
separado. Fallos y no ejecutados permanecen en los denominadores de 12 casos y
6 pares. Las explicaciones libres se inspeccionan, no se puntúan con criterios
inventados después. Se informa consumo y tiempo incluyendo rechazos. Los revisores
no tienen eje provenance explícito: no se inventa una métrica sobre ese campo.

Pedir revisión siempre no supera los controles positivos. Acertar los seis pares
sólo demostraría esos mecanismos en estos ejemplos, no generalización ni capacidad
de aprobación autónoma. Si hay fallos, se conserva el resultado sin repararlo ni
reintentar para obtener un aprobado.

## Resultado observado

24 llamadas completadas, sin reintentos, truncamientos ni fallos de formato o
transporte. El proveedor reportó glm-5.3-flash. La auditoría verificó el freeze,
el código de producto sin cambios, los hashes de resultados y la reproducción
local de validación. Comprobó que los payloads contienen sólo pregunta/aspectos,
claim, cita, idioma y faltantes, sin gold ni identidad del par.

| Métrica | v1 | v2 |
|---|---:|---:|
| Formato válido | 12/12 | 12/12 |
| Casos correctos en los cuatro ejes | 8/12 | 12/12 |
| Positivos correctos | 5/6 | 6/6 |
| Negativos correctos | 3/6 | 6/6 |
| Pares completos correctos | 3/6 | 6/6 |
| Support correcto | 8/12 | 12/12 |
| Relevance correcta | 12/12 | 12/12 |
| Idioma correcto | 12/12 | 12/12 |
| Recommendation correcta | 9/12 | 12/12 |
| Tokens reportados | 10 707 | 17 698 |
| Tiempo acumulado de llamadas, segundos | 181.223 | 245.348 |

Total: 28 405 tokens, 426.571 segundos de llamadas. V2 consumió 65.3% más tokens;
no es porcentaje de coste monetario, que depende de clases de tokens y caché.
No se conoce exposición del modelo a otros datos de entrenamiento, pero estos
controles se redactaron específicamente para esta tanda.

Evidencia: `experiments/review-controls-v1/runs/glm-01/` contiene protocolo,
freeze, ejecución, auditoría y request/receipt/result por caso y versión.
Inputs y runs permanecen gitignored; su conservación local es necesaria para
reproducir las comprobaciones exactas. Preparación, puntuación y auditoría quedan
en scripts reproducibles. `audit.py` no llama al proveedor.

### Fallos concretos

- **case-03 y case-04, atribuciones ausentes:** v1 reconoció en su explicación que
  la cita no identifica al autor o boletín. Aun así marcó el claim íntegro supported
  y needs_adjudication. Eso incumple la rúbrica fijada; no significa que aprobara
  automáticamente la respuesta. V2 marcó insufficient / needs_revision y también
  acertó los positivos correspondientes.
- **case-08, positivo del par subject:** claim y cita coinciden literalmente. V1
  pidió evidencia independiente y marcó insufficient, mezclando respaldo textual
  con autenticación externa. El revisor recibe citas aportadas por el consumidor;
  igualdad textual no demuestra que sean autorreferenciales. El ensayo no certifica
  verdad externa de la fuente. V2 reconoció el respaldo literal.
- **case-11, negativo del mismo par:** v1 repitió la exigencia de independencia,
  fallando support, pero sí detectó el sujeto equivocado y pidió revisión. V2
  separó correctamente supported de extra. El rechazo final correcto no oculta
  ese error de clasificación.

## Interpretación y continuación

Este resultado **refuta, para estos seis pares, la hipótesis de que v2 sólo pide
revisión indiscriminadamente**: reconoció los seis positivos. No refuta esa
posibilidad en otros textos. Tampoco cambia el resultado del piloto AttrScore,
que usa otra distribución y etiquetas que no coinciden siempre con este contrato.

Hay evidencia concreta a favor de v2 para revisión estricta por detalles en estos
controles. Sigue sin justificar promoción automática a predeterminado, corrección
de v1 basada sólo en estos ejemplos ni aprobación autónoma. No se modificó producto.
El ensayo tuvo una ejecución por condición, muestras cortas en inglés y rúbrica
alineada con la finalidad del revisor por detalles; no demuestra estabilidad,
ventaja general, rendimiento en español o documentos largos.

Siguiente paso recomendado: una muestra nueva reservada de **24 casos externos**,
sin coincidencias de pregunta, respuesta o referencia con los doce ya usados.
Mantener por separado el score original de AttrScore y las observaciones sobre
respaldo, pertinencia y acción. Fijar selección y criterios antes de las llamadas;
no relabelar gold para favorecer v2. Examinar tanto casos que pide revisar como
los que considera sustentados, y registrar coste. No se ejecutó esa ampliación
en este incremento. Su resultado decidiría si compensa usar v2 para revisiones
estrictas; no se construirá una cascada v1→v2 sin medirla, porque los errores de
v1 pueden no activar una segunda revisión.

## Verificaciones locales

274 pruebas pasaron, incluidas cuatro nuevas sobre puntuación pareada: siempre
pedir revisión no supera positivos; fallos/ausencias permanecen en denominadores;
soporte no sustituye pertinencia; IDs, predicciones y pares inválidos se rechazan.
Antes de llamadas se comprobó una manipulación semántica por par, doce fixtures
válidos y ausencia de claims reutilizados de AttrScore. No se repararon resultados
ni se ajustaron expectativas después de observarlos.

AN-KLA verificó rev 3, contexto correcto con advertencia preexistente fuera del
bloque administrado. Sin escritura de memoria, cambios de producto, commit o push.

### Revisión del informe final

La misma instancia separada que revisó el diseño contrastó este informe con
`audit.json` y los cuatro dictámenes discrepantes de v1. Dio conformidad acotada,
sin hallazgos materiales. Esta fase tuvo expectativas y resultados visibles; no
fue evaluación ciega ni adjudicación humana. No repitió auditoría de freeze,
pruebas o verificación de los 24 recibos, que corresponden al principal.
