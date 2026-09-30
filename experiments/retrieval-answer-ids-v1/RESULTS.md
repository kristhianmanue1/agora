# Resultado: IDs en ambas rutas, sin promoción

## Resultado observado

Se enviaron las 24 solicitudes previstas, una por contexto. Todas respondieron. Veinte salidas pasaron el contrato de IDs y se revisaron con Jev; dos agotaron la salida y dos devolvieron JSON inválido. No hubo timeouts ni reintentos. En las respuestas admitidas no se detectaron IDs desconocidos. Los rechazos impiden afirmar que todas las salidas hayan tenido referencias válidas.

| Medida | Cuotas iguales | Redistribución |
|---|---:|---:|
| Intentos | 12 | 12 |
| Candidatos válidos y revisados | 10 | 10 |
| Rechazos locales | 2 | 2 |
| Útiles según el criterio congelado y Jev | 5 | 6 |
| Answered / partial / not_in_passages válidos | 6 / 2 / 2 | 6 / 3 / 1 |
| Tokens generación: entrada / salida | 21.231 / 11.401 | 24.248 / 12.148 |
| Tokens revisión: entrada / salida | 76.796 / 925 | 78.121 / 924 |
| Total tokens | 110.353 | 115.441 |
| Segundos acumulados generación / revisión | 221,931 / 5,170 | 244,226 / 5,060 |

Diez pares con ambas respuestas válidas: dos favorables a redistribución, uno favorable a cuotas iguales, cuatro útiles en ambas y tres sin utilidad según el criterio en ambas. Dos pares incompletos por rechazos. Los pares incompletos no se convierten en fracasos semánticos; los rechazos sí cuentan en el denominador operativo de 12 intentos por ruta.

Consumo total observado: **225.794 tokens**, sin llamadas de uso desconocido en este lote; 69.028 de generación y 156.766 de revisión. Son tokens reportados por proveedores distintos, no una unidad de facturación uniforme ni coste monetario verificado. La revisión con fuente completa domina el consumo. Redistribución consumió 5.088 tokens adicionales. No queda demostrado ahorro total. Los tiempos son sumas de solicitudes, no el tiempo total de trabajo ni una medición completa del pipeline.

Los modelos reportados por los journals son glm-5.3-flash y jev-1.13.0. Los resultados completos están en result.json y validation.json.

## Autorrevisión adversarial

1. **La procedencia no demuestra fidelidad.** IDs resueltos por código eliminan la necesidad de copiar citas, pero una cita válida puede respaldar una afirmación irrelevante o dejar incompleta la respuesta. Las 14 pruebas existentes de test_evidence_ids pasaron; no son validación semántica.
2. **Comparación histórica confundida por formato y ejecución.** El lote anterior usó concise-v1 literal, tuvo tres timeouts y otra distribución de revisiones. Aquí cambian el contrato de salida y el prompt. No se atribuye la mejora de admisión 16→20 exclusivamente a IDs, ni se presenta el mayor consumo como estimación causal del coste de IDs.
3. **Dos mejoras con evidencia añadida.** En 1803.08419, el contexto redistribuido contiene el pasaje sobre límites de BLEU y promedios de embeddings ausente del otro contexto. En 1909.11706 contiene los resultados SVM/Random Forest ausentes del otro contexto. audit.py comprueba pertenencia de citas y registra hashes en adversarial-audit.json. Es inspección del productor, no adjudicación independiente ni prueba general de superioridad.
4. **Discrepancia material del revisor.** En 1909.02322, la pregunta “What is the model trained?” es ambigua. QASPER espera la identidad del modelo: Condense-Abstract, con BiLSTM y decodificador LSTM con atención. Ambos candidatos describen el procedimiento de entrenamiento; ninguno identifica ese modelo. Jev calificó cuotas iguales como complete y redistribución como omitted. El aparente triunfo de cuotas iguales queda cuestionado por la referencia externa. Se conserva el puntaje bruto; no se reemplaza por una etiqueta del productor ni se modifica la pregunta retrospectivamente. Las referencias se inspeccionaron después de la revisión y no se enviaron a los modelos.
5. **Una muestra por ruta y corpus conocido.** Tres pares tienen contextos idénticos; diferencias potenciales no serían efecto de recuperación. La muestra es de desarrollo y no hay adjudicación humana. No permite promoción general.

## Decisión y siguiente paso

Mantener métodos y revisores predeterminados sin cambios. La ronda autorizada está completada y los rechazos quedan preservados, sin reparación silenciosa.

Antes de ampliar el corpus o aumentar presupuestos: contrastar las evaluaciones de suficiencia de los 20 candidatos válidos con las respuestas y evidencias externas de QASPER, separando pregunta ambigua, recuperación insuficiente, omisión del generador y error del revisor. Empezar con los resultados ya conservados: no requiere repetir generación. Mantener las etiquetas de Jev como evidencia original y cualquier evaluación posterior como capa separada. Después decidir si hacen falta otra adjudicación, una condición con más salida o integración en CLI.
