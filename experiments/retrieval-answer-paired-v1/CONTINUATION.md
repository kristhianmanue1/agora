# Continuación: 16 entradas nunca enviadas

## Resultado de ejecución

La sonda mínima GLM devolvió JSON esperado en 2,775 s, modelo reportado glm-5.3-flash y 177 tokens. Se reanudaron sólo las 16 entradas sin journal previo, en runs-generation-02; todas recibieron respuesta dentro de 90 s, sin reintentos. Los ocho journals originales conservaron sus hashes. No se repitieron las tres solicitudes agotadas.

Once respuestas nuevas pasaron validación; cinco fueron rechazadas (cuatro answer_quote_mismatch y una invalid_concise_answer_shape). No se repararon. Jev revisó únicamente las once válidas en un registro separado y con el mismo criterio y cegamiento originales. Los fallos de formato/cita no son fallos de transporte y no se borran del análisis.

## Balance consolidado de los 24 intentos originales

| Ruta | Intentadas | Timeouts conservados | Rechazo local | Válidas/revisadas | Útiles según Jev |
|---|---:|---:|---:|---:|---:|
| Cuotas iguales | 12 | 1 | 3 | 8 | 3 |
| Redistribución | 12 | 2 | 2 | 8 | 5 |

No quedan entradas nunca enviadas. «Útil» conserva la definición previa: respuesta, no abstención, forma/citas válidas, y Jev supported + complete. Es un juicio experimental; no adjudicación humana. Los denominadores conservan todos los intentos y no permiten confundir rechazo local con error semántico.

Siete pares tienen dos respuestas válidas revisadas: tres both_usable, tres neither_usable y uno shared_win. Cinco pares permanecen incompletos para contraste semántico. No se calcula superioridad poblacional a partir de esta muestra ni se imputan resultados a llamadas agotadas. Los 12 documentos ya eran de desarrollo, y la continuación ocurre en otro momento.

## Mejora localizada comprobada

En 1909.11706 se pregunta qué modelo obtuvo mejores resultados, SVM o Random Forest. La ruta de cuotas iguales se abstiene; la redistribución recupera dos frases con las exactitudes de ambos modelos bajo dos condiciones de etiquetado, y responde SVM. La inspección del productor comprueba que ambas citas están presentes en el contexto ampliado y ausentes del anterior: positive-pair-audit.json contiene hashes y resultado del cotejo. Eso evidencia utilidad del texto añadido en este caso; no atribuye toda diferencia entre rutas a recuperación en lugar de no determinismo.

## Coste observado y límites

Consolidado: 176.605 tokens conocidos, incluida la sonda de 177. Cuotas iguales: 87.752; redistribución: 88.676. Son consumos observados de generación y revisión, no costes finales comparables: las rutas tienen distinto número de generaciones completadas y documentos revisados. Falta uso y posibles cargos de las tres solicitudes agotadas. No hay coste monetario verificado.

Tiempos acumulados de generación: 251,220 s iguales y 339,393 s redistribución (incluyen timeouts originales). Revisión: 3,330 s y 3,383 s. Son tiempos de solicitudes, no reloj total del trabajo. Los tiempos y tokens de las etapas nuevas permanecen distinguibles en los journals. La revisión con texto completo consume la mayoría de tokens: no se presenta el ahorro de recuperación como ahorro de todo el proceso.

Tres pares tenían contexto idéntico: se conserva ese indicador para no atribuir diferencias a recuperación. Ningún resultado convierte agreement con Jev en garantía de fidelidad.

## Decisión

La continuación autorizada está completa; la comparación general conserva tres resultados remotos inciertos y cinco rechazos locales. Mantener la redistribución experimental y optativa, sin cambiar producto ni método predeterminado.

Antes de ampliar otra vez la muestra, conviene resolver los rechazos de formato/citas usando las referencias por ID ya existentes, como nueva condición experimental para ambas rutas. La comparación actual usó el mismo perfil concise-v1 con citas literales en ambos brazos. No reetiquetar ni reparar silenciosamente los resultados de este lote. Cualquier nueva evaluación debe conservar ese cambio de condición, presupuesto y separación de casos de desarrollo/reservados.

## Recuperación y reproducción

result.json, validation.json y las revisiones originales permanecen sin cambios. El consolidado está en result-resumed.json; validation-02.json y review-freeze-02.json describen sólo esta continuación. continuation-01.json enumera IDs nuevos y hashes previos protegidos. prepare_review_02.py y score_resumed.py permiten validar y recomponer desde los registros; el primero requiere directorio nuevo. No ejecutar generadores o sonda otra vez sobre este lote.
