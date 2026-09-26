# QASPER: línea base con fuente completa

2026-09-23. Corrida: `experiments/qasper-v1/runs/glm-baseline-01`.
Estado: ejecución y evaluación completadas; resultado diagnóstico, no certificación.

## Resultado

12 consultas, 12 respuestas estructuralmente aceptadas, 0 timeouts, 0 rechazos.
Modelo solicitado y reportado: `glm-5.3-flash`; 64793 tokens reportados,
169,784 segundos sumados de los procesos de consulta. El tiempo no incluye
preparación y revisión. Sin reintentos. Hubo tokens de entrada cacheados en
algunas llamadas: no es una comparación de latencia controlada ni coste monetario.

Evaluador oficial fijado: Answer F1 **32,49/100**, Evidence F1 **53,89/100**.
Son medias de similitud textual y coincidencia de párrafos citados; **no son
porcentajes de respuestas correctas ni medición completa de fidelidad**.
Muestra: 12 artículos, textos de 12–43 KB. No es la puntuación del test completo.

| Caso | Referencia | Conducta | Answer F1 /100 | Evidence F1 /100 | Tokens | Segundos |
|---|---|---|---:|---:|---:|---:|
| case-01 | respondible | respuesta | 15.79 | 50.00 | 4740 | 29.03 |
| case-02 | respondible | respuesta | 18.18 | 40.00 | 5005 | 13.73 |
| case-03 | respondible | respuesta | 8.89 | 66.67 | 3892 | 9.29 |
| case-04 | respondible | respuesta | 8.70 | 66.67 | 9146 | 9.38 |
| case-05 | respondible | respuesta | 18.18 | 40.00 | 5805 | 12.76 |
| case-06 | respondible | respuesta | 10.17 | 66.67 | 4241 | 12.99 |
| case-07 | respondible | respuesta | 60.00 | 66.67 | 5537 | 7.96 |
| case-08 | respondible | respuesta | 50.00 | 50.00 | 7341 | 7.71 |
| case-09 | sin respuesta | respuesta | 0.00 | 0.00 | 3974 | 15.02 |
| case-10 | sin respuesta | abstención | 100.00 | 100.00 | 4521 | 19.65 |
| case-11 | sin respuesta | abstención | 100.00 | 100.00 | 4380 | 6.78 |
| case-12 | sin respuesta | respuesta | 0.00 | 0.00 | 6211 | 25.50 |

## Hallazgos que importan

- Las ocho preguntas respondibles recibieron respuestas que conservan el dato
  central según la autorrevisión. No hubo abstenciones erróneas en ese grupo.
  Esto no equivale a una adjudicación independiente de todas las afirmaciones.
- De cuatro preguntas sin respuesta, sólo dos produjeron abstención: casos 10/11.
- Caso 09: atribuye al conjunto un procedimiento de anotación manual descrito
  de manera general en la introducción. Las citas existen, pero no prueban la
  atribución específica. Los tres anotadores señalan ausencia de respuesta.
- Caso 12: responde “Partially” con resultados en inglés/español, aunque añade
  que no se demuestra rendimiento general en lenguas de pocos recursos. Esa
  salvedad no satisface el contrato de abstención para la pregunta planteada.
- Varias respuestas correctas en su núcleo son mucho más largas que la
  referencia. También citan más párrafos de los anotados. Esto reduce las F1;
  no permite ignorarlas ni convertir la revisión cualitativa en nueva métrica
  oficial. Una cita adicional puede ser útil o innecesaria: requiere revisión.
- Caso 01: los anotadores discrepan entre Yes y una respuesta matizada sobre
  Twitter/Reddit. Se conservaron todas las referencias; no se eligió una después.
- Caso 09 tiene inconsistencia interna en el corpus: título/abstract SemEval
  2018 y cuerpo SemEval 2017. La transformación conserva el original. No se
  corrigió el corpus ni se retiró la pregunta para mejorar el resultado.

## Evidencia y método

Generación sin etiquetas de referencia en el payload; código, entradas y
parámetros congelados antes de llamar al proveedor. Fuente completa, idioma en,
temperatura 0, salida 8192 tokens, socket 90 s y proceso 110 s. Muestra y
protocolo: [Batería QASPER](bateria-qasper.md). Sin cambios de prompt durante
la campaña y sin ejecución de recuperación o recorrido en esta tanda.

`run_baseline.py` registra cada resultado y coste. `score_baseline.py` verifica
hashes, exporta predicciones y aplica el evaluador oficial fijado. En la corrida:
`protocol.json`, `freeze.json`, `execution.json`, `predictions.jsonl`,
`scores.json` y `review.json`. Referencias y resultados completos ignorados por
Git. Autorrevisión del productor, no evaluación ciega ni revisión independiente.

171 pruebas locales pasaron. Verificados el corpus preparado, código congelado,
receipts de las 12 respuestas y citas por bytes al exportar. No se modificó
código de producto durante la ejecución. Sin commit, push ni escritura AN-KLA.

## Próximo paso recomendado

Priorizar dos cambios en desarrollo separado: (1) respuesta breve separada de
la explicación/citas, para que la métrica mida el dato solicitado; (2) ejemplos
y comprobaciones de correspondencia entre sujeto, alcance y propiedad de la
pregunta y lo que realmente afirma la fuente. Una introducción general o el
objetivo de un programa no prueba lo realizado en un experimento concreto.

Usar fixtures nuevos y partición de desarrollo. Esta muestra queda como
regresión ya observada: no ajustar sobre ella y llamarla prueba inédita.
Después congelar otra evaluación y comparar lectura completa con recuperación
y extracción usando el mismo idioma/modelo y coste total. No se ha demostrado
todavía ahorro ni superioridad frente a otra ruta.
