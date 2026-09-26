# Revisor experimental v3: certeza, alcance y pertinencia

**Estado actual, 2026-09-25:** continuación completada; las 16 posiciones se
intentaron, con 15 dictámenes y el timeout original conservado. V3 no mostró una
ventaja global en estos controles y permanece experimental. Véase el cierre de
continuación al final; los apartados del primer intento son históricos.

## Cambio y límite

Fecha: 2026-09-24. `review_evidence(..., review_version="v3")` añade una razón
separada para pertinencia y comprobaciones por detalle de certeza y alcance.
`review_candidate(..., review_version="v3")` permite usarlo con los presupuestos
existentes. Los valores predeterminados siguen siendo v1 para la llamada simple
y v2 para la revisión acotada. No se promueve ninguna versión automáticamente.

El modelo declara certeza `preserved/overstated/uncertain` y alcance
`same/different/uncertain`. El código conserva su etiqueta como `model_support`
y deriva `support`: alcance diferente/incierto → insufficient; un supported
con certeza exagerada/incierta → insufficient. Una contradicción sobre el mismo
objeto permanece contradicción aunque denuncie una excepción omitida. Primero se
valida todo el esquema y las referencias: los flags no excusan una salida inválida.
Se conserva cobertura literal del claim y procedencia model_reported de los checks.

Esto impide contradicciones entre flags declarados y resultado final. **No prueba
que los flags sean verdaderos.** Si el modelo juzga mal tanto etiqueta como checks,
el código puede seguir aceptándolos estructuralmente. No hay aprobación automática.
La pertinencia compara claim y pregunta, nunca cita y pregunta. La razón separada
hace visible esa decisión, pero no demuestra que sea correcta.

## Formato y proveedor

La [documentación oficial de Z.ai](https://docs.z.ai/guides/capabilities/struct-output)
muestra `response_format: {"type":"json_object"}` y validación de esquema en el
cliente. No se presume enforcement servidor de json_schema para este endpoint/modelo.
El ensayo solicita modo JSON para **ambas versiones**. No se reparan salidas ni se
ignoran campos desconocidos. El prompt v3 enumera campos cerrados y lugares para
explicaciones, pero es guidance; el control ejecutable sigue siendo la validación.
Que una petición acepte JSON mode no prueba que el backend imponga el esquema.

## Protocolo fijado antes de llamadas

Cuatro pares, ocho casos sintéticos nuevos en inglés, fijados antes del cambio:

| Par | Contraste | Expectativa |
|---|---|---|
| attributed_account | relato atribuido / afirmación sin atribución | supported / insufficient |
| measurement_binding | modificador en su medición / modificador de otro objeto | supported / insufficient |
| answer_relevance | pregunta que contesta el claim / pregunta sobre otra propiedad | relevant / extra; ambos insufficient |
| exception | máximo sin excepciones / fuente con excepción explícita | supported / contradicted |

«Positivo» significa control del eje examinado: el positivo de pertinencia NO
está sustentado y debe pedir revisión. No se equipara positividad a aprobación.
El cambio semántico por par está en un único campo; derivados y hashes cambian.
Gold separado, orden por hash, ninguna etiqueta en payload. Una afirmación
respaldada pertinente sólo conduce a needs_adjudication.

Comparación v2/v3, ambos JSON mode, GLM-5.3-Flash, temperatura 0, inglés, 8192 tokens
máximos de salida, transporte 180 s, trabajador 200 s. Máximo 16 llamadas y 131072
tokens reservados de salida, no presupuesto monetario. Sin reintentos. Fallos de
transporte/integridad o uso desconocido detienen la tanda; rechazos estructurales
con consumo conocido se cuentan y continúan. No se afinan prompts en esta tanda.

Freeze previo incluye código, preparación, worker, runner, transporte, puntuación,
auditoría, entradas y este protocolo. Métricas exactas por support, relevance,
language y recommendation; acierto conjunto por caso y par; fallos incluidos,
consumo y tiempo. Los checks de certeza/alcance se inspeccionan sin inventarles
gold retrospectivo. No se atribuirá una mejora aislada a JSON mode: ambos brazos
lo usan y no hay brazo v2 sin JSON en este ensayo.

Se reevalúan además los recibos históricos localmente con v1/v2, sin nuevas llamadas,
para verificar que las salidas de esas versiones se conservan. Sus documentos y
recibos no se editan. Las auditorías antiguas que exigen igualdad de TODO el código
actual con el congelado detectarán el nuevo incremento; eso no altera sus resultados
históricos ni obliga a sobrescribirlos.

## Resultado del primer intento — histórico

La tanda se detuvo en la sexta llamada: v3/case-03 devolvió TimeoutExpired desde el
subproceso de transporte a los 180.084 segundos, sin contenido ni recibo de uso.
El runner salió con código 2 conforme a su regla de parada. No hubo reintento,
aumento de límites ni reanudación automática. Se desconoce si el proveedor consumió
tokens en esa llamada; no se le asigna consumo cero. El timeout no identifica por
sí solo una causa del modelo, del servidor o de la red.

| Estado de los ocho casos previstos por versión | v2 | v3 |
|---|---:|---:|
| Llamadas intentadas | 3 | 3 |
| Dictámenes válidos y coincidentes con expectativas | 3 | 2 |
| Intentos fallidos sin respuesta | 0 | 1 |
| Casos no ejecutados | 5 | 5 |
| Pares completamente ejecutados y acertados | 0/4 | 0/4 |
| Subtotal conocido de tokens | 8 116 | 8 035 |
| Uso desconocido | 0 llamadas | 1 llamada |
| Tiempo de intentos, segundos | 110.846 | 289.471 |

El subtotal conocido conjunto es 16 151 tokens; **el total es desconocido**.
Ningún par quedó completo: no se interpreta 0/4 como cuatro fallos semánticos,
ni los 3 y 2 aciertos como tasas comparables de calidad. El ensayo no permite
concluir que v3 supere a v2 ni que no rechace controles positivos.

Sí se observó una intervención local relevante: en v3/case-01 el modelo etiquetó
dos detalles como supported y simultáneamente certainty=overstated. El agregador
los convirtió en insufficient, conservando los labels originales y las razones
del ajuste. En case-02 el modelo ya detectó el modificador insuficiente y no
necesitó ajuste. La intervención no establece la veracidad general de los checks.

Las cinco respuestas recibidas tienen formato válido. Es evidencia acotada de
compatibilidad de estas peticiones con JSON mode; no demuestra eliminación de
campos extra en general ni ventaja causal de ese modo. Los controles de pertinencia
y el negativo de excepciones no llegaron a ejecutarse en vivo.

## Comprobaciones y autorrevisión

- **289 pruebas locales pasaron**, incluidas once nuevas para v3: downgrade de
  certeza, alcance diferente/incierto, conservación de contradicción del mismo
  alcance, rechazo de referencias faltantes, extras y checks inválidos, separación
  de pertinencia, inmutabilidad y selección explícita en el revisor acotado.
- Reproducción offline de **96 dictámenes históricos**, conservando resultados,
  prompts y los cinco rechazos estructurales. Sin llamadas adicionales y sin
  sobrescribir evidencia anterior. Archivo inputs/compatibility.json.
- La auditoría congelada asumía disponibilidad de respuesta del proveedor. Para
  este cierre se añadió audit_partial.py después del timeout; verifica los mismos
  hashes y métricas, reproduce las cinco respuestas disponibles y registra que
  una no puede reproducirse. Se declara esa ampliación posterior: no se presenta
  como código prerregistrado ni se cambia el auditor congelado.
- Freeze y producto actual coinciden para esta tanda. La evidencia está en
  experiments/review-guards-v3/runs/glm-01, incluido audit-partial.json y el hash
  del auditor complementario. Inputs/runs permanecen gitignored.

Autorrevisión del productor: los flags semánticos siguen dependiendo de GLM;
la regla local sólo aplica consecuencias coherentes. Un fallo en flags y etiquetas
puede pasar inadvertido. La razón separada de pertinencia mejora trazabilidad,
no demuestra su corrección. Los límites de esquema siguen cerrados: no se reparan
ni aceptan respuestas con campos desconocidos para mejorar la puntuación.
No hubo revisor independiente en este incremento.

## Uso y cierre del primer intento — histórico

```python
review_evidence(candidate, provider, review_version="v3")
review_candidate(candidate, bounded_provider, review_version="v3")
```

El provider sigue siendo el responsable de respetar timeout y límites. JSON mode
se configuró en el adaptador de este ensayo; la API neutral no impone ese parámetro
a proveedores arbitrarios. La salida v3 tiene esquema propio y comprobaciones
model_reported; los consumidores deben seleccionarla explícitamente.

Estado: **PARCIAL respecto de la validación en vivo; implementación y comprobaciones
locales completas**. Mantener v3 experimental. Antes de nuevas llamadas, definir una
continuación separada que conserve este intento fallido, sus cinco resultados y
el consumo desconocido. No presentar una reanudación como una tanda original sin
fallos ni repetir automáticamente una llamada cuyo consumo no se conoce.

Sin promoción de versión, commit, push, cambios de contexto canónico ni escrituras
en memoria. El cierre del ensayo se documentó el 2026-09-25; el protocolo previo
conserva su fecha original.

## Continuación 2026-09-25 — cierre actual

El Operador autorizó continuar. Se ejecutaron **sólo las diez posiciones no
intentadas**, en runs/glm-01-continuation-01, con el mismo código, gold, orden
relativo, GLM-5.3-Flash, JSON mode, 8192 tokens de salida y timeout de 180 segundos.
No se repitió v3/case-03 ni se reemplazaron los cinco resultados previos. El runner
comprueba los hashes de TODOS los archivos del intento base antes de cada llamada;
la auditoría confirma que su ledger inicial permanece idéntico y que las llamadas
nuevas pertenecen exclusivamente a los diez slots declarados antes de continuar.

Las diez llamadas nuevas finalizaron con formato válido, sin timeout ni reintento.
El código de producto no cambió en esta continuación. Sus 289 pruebas corresponden
al incremento previo; esta fase verificó congelación, planificación de continuación,
payloads, resultados y reproducción local, sin repetir innecesariamente esos tests.

### Resultado acumulado, incluido el fallo original

| Métrica | v2 | v3 |
|---|---:|---:|
| Posiciones intentadas | 8/8 | 8/8 |
| Dictámenes válidos | 8/8 | 7/8 |
| Casos correctos en los cuatro ejes | 6/8 | 6/8 |
| Pares completos correctos | 3/4 | 2/4 |
| Support correcto | 6/8 | 6/8 |
| Relevance correcta | 8/8 | 7/8 |
| Recommendation correcta | 8/8 | 7/8 |
| Timeouts conservados | 0 | 1 |
| Tokens conocidos | 18 065, total conocido | 26 411, subtotal; total desconocido |
| Segundos de intentos acumulados | 218.790 | 507.004 |

Subtotal conjunto conocido: **44 476 tokens**, más el uso desconocido del timeout.
No se compara un total conocido con otro incompleto mediante un porcentaje exacto.
Tiempo conjunto: 725.794 segundos de intentos. No hay posiciones sin intentar.
El flag complete=false de audit-continuation.json significa que no todas devolvieron
salida válida; all_slots_attempted=true y new_calls=10 documentan que la continuación
sí terminó su alcance. Las 15 respuestas se reprodujeron localmente; la llamada sin
respuesta sólo se verifica como intento, no se inventa una salida para reproducirla.

### Hallazgo nuevo y límite de v3

En case-05 y case-06 la fuente dice que el pasaje **no identifica** un animal; no
afirma que Elian no tuviera uno. El gold fijado pide insufficient ante el claim de
que tenía un zorro. V2 devolvió contradicted en ambos. V3 acertó case-05, pero en
case-06 también convirtió falta de información en negación del hecho.

Claim y cita son idénticos entre esos dos casos; sólo cambia la pregunta. V3
cambió su juicio de soporte al cambiar la pregunta, aunque en este ejemplo el
claim es explícito y no requiere desambiguación contextual. La pertinencia sí debe
cambiar; el respaldo de esa afirmación concreta no. Es un contraejemplo útil para
separar las dos decisiones, no motivo para cambiar gold retrospectivamente.

La recomendación final fue needs_revision en los tres errores semánticos, por lo
que aquí la clasificación incorrecta no generó una recomendación de aprobación.
Tampoco permite ignorar el error: los labels y las explicaciones son información
que otros consumidores podrían usar. En v3/case-06 los checks fueron scope=same y
certainty=preserved junto a contradicted; la regla local no puede corregir un
conjunto de juicios coherente internamente pero equivocado respecto de la fuente.

El beneficio local observado en el primer intento se conserva: dos supported
incompatibles con certainty=overstated se degradaron. Ese mecanismo no se tradujo
en una ventaja global demostrada: v3 empató aciertos por caso, acertó menos pares,
tuvo el timeout y su subtotal de tokens ya supera el total de v2.

### Recomendación actual

**No promover v3 ni ampliar ahora una batería grande.** Mantener las opciones y
predeterminados existentes. No se ha medido una ventaja suficiente que justifique
usar v3 de forma general ni una cascada automática de revisores.

La próxima corrección debe ser pequeña: convertir este par en regresión explícita
para distinguir ausencia de información de negación de un hecho, y exigir estabilidad
del juicio de soporte al variar sólo una pregunta que no cambia el significado del
claim. Antes de añadir más campos o llamadas, medir si esa corrección mejora el error
con controles nuevos y sin perder los positivos. Los casos observados se usarían
como regresiones, nunca como nueva evidencia reservada.

Cierre de este encargo: continuación completada, sin nuevas llamadas pendientes.
El fallo histórico y la falta de evidencia para promover v3 permanecen visibles.
Sin commit, push, cambios de producto, promoción ni escritura de memoria en esta fase.
