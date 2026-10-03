# Segunda lectura y controles del revisor — 2026-10-03

## Resultado

Se completaron cuatro llamadas GLM y dos llamadas Jev, sin reintentos. Es una
regresión de casos ya conocidos de `../memos-long-reserved-v3/`, no otra batería
reservada ni una nueva comparación simultánea contra MemOS. No cambia código.

| Caso | Resultado de segunda lectura | Interpretación |
|---|---|---|
| 1901.05415-q1 | Rechazado: salida truncada | El fragmento recupera etiquetado humano, pero no es una respuesta válida. |
| 1901.05415-q2 | Rechazado: cita no literal | Recupera cifras de ambos objetivos; altera el espacio en `SECREF18 )`. No se acepta ni repara silenciosamente. |
| 1905.10039-q1 | Candidato | Recupera las tres definiciones de métricas omitidas en primera lectura. |
| 1905.10039-q2 | Candidato | Recupera familias de modelos y combinaciones; subsisten nombres de variantes perdidos en la extracción. |

Las dos primeras preguntas se precisaron antes de llamar; cambian pregunta y
cantidad de texto, por lo que no se atribuye su resultado únicamente a leer más.
Las dos últimas conservan la pregunta. Se entregó el texto completo disponible,
no necesariamente todo el contenido del PDF: QASPER contiene `INLINEFORM0`.
En particular, el umbral de calificaciones positivas del artículo no es legible.
El control sintético sí especifica 3–5, pero no puede usarse para completar el artículo.

## Jev: separa errores, pero confunde respaldo con cobertura

Se congelaron seis controles (tres correctos y tres con errores u omisiones),
dos ejes por control, evaluados en orden directo e inverso. Las etiquetas esperadas
no se enviaron. Jev coincidió en 22 de 24 decisiones; son seis controles repetidos,
no 24 casos independientes. Todas las etiquetas observadas se conservaron entre
órdenes; sus probabilidades no fueron iguales.

En ambas ejecuciones rechazó como `unsupported` una afirmación verdadera sobre
el clasificador porque no respondía al etiquetado humano. La etiqueta esperada era
`supported` y `omitted`: está respaldada, pero no contesta lo solicitado. Detectó
las cifras intercambiadas y la invención de un segundo artículo; aceptó los tres
controles positivos. Las etiquetas y esta inspección pertenecen al productor,
sin adjudicación humana independiente. Jev no revisó las cuatro respuestas nuevas.

## Coste y evidencia

- Segunda lectura GLM: **45 829 tokens**, incluidos ambos rechazos; 111.36 s sumados.
- Primera lectura v3 + segunda: **62 757 tokens** (16 928 + 45 829).
- Controles Jev: **7 006 tokens**, aparte del generador y de los 26 646 de revisión v3.
- Cero llamadas nuevas a MemOS; no se modificaron AN-KLA, Skopos ni sus resultados.
- No se calcularon dólares ni costes de infraestructura/embeddings.

`freeze.json` fija preguntas, controles, presupuestos y límites antes de la ejecución.
Los receipts conservan respuestas originales, rechazos, modelo reportado, usage,
hashes de implementación/fuente y tiempos. Se omiten prompts y texto íntegro de
los documentos; pueden reconstruirse con las fuentes fijadas por hash de v3.
Los ejecutores conservan rutas temporales del entorno original; para reproducir,
preparar las fuentes indicadas y entregar las credenciales mediante Llavero.
El manifiesto del banco verifica integridad; no adjudica verdad semántica.

## Decisión propuesta y siguiente incremento

Mantener Jev como revisor auxiliar. El control de citas y el de salida incompleta
hicieron visible el fallo, pero el recorrido aún no ofrece cuatro respuestas útiles.
Priorizar una reparación explícita y acotada: respuestas breves y referencias por
identificador en el recorrido que aún solicita citas literales. Conservar rechazo,
respuesta derivada y coste; no ampliar indefinidamente tokens ni relajar fidelidad.
Después repetir estos dos fallos como regresión y sólo entonces abrir nuevos casos
reservados. Dos candidatos mejores no demuestran ahorro: esta segunda lectura
costó más que la primera campaña completa de Ágora.
