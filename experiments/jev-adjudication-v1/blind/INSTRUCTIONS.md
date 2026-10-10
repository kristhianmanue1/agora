# Adjudicación documental ciega

Recibirás 12 fichas `items/J-*.json` y siete textos `sources/S-*.txt`. Usa sólo
este directorio. Cada ficha señala su fuente, pregunta, requisitos, respuesta
y limitaciones declaradas. Los códigos no identifican origen, proveedor ni
resultado de revisiones previas. Algunas preguntas se repiten: juzga cada
respuesta por separado, usando sólo su fuente y requisitos.

Copia `scorecard-template.csv` a un archivo de trabajo. No cambies los códigos
ni la pregunta. Para cada fila, completa:

- `question_clarity`: `clear`, `ambiguous` o `uncertain`. Usa `ambiguous` si la
  pregunta admite objetivos materialmente distintos que cambian una respuesta
  completa. La mera falta de datos en la fuente no vuelve ambigua la pregunta.
- `support`: `supported` si todas las afirmaciones materiales, incluidas las
  declaraciones de ausencia y sus límites, se sostienen en la fuente completa;
  `unsupported` si alguna excede o contradice la fuente; `uncertain` si no
  puedes resolver el respaldo. Una respuesta incompleta con afirmaciones
  verdaderas puede ser `supported`.
- `coverage`: `complete` si la respuesta entrega correctamente todos los
  elementos solicitados y establecidos por la fuente; `omitted` si falta o se
  niega uno material, aun cuando la respuesta reconozca una limitación;
  `justified_abstention` si la respuesta se abstiene y la fuente no establece
  lo pedido; `uncertain` si la ambigüedad o el texto impiden decidir.
- `support_evidence` y `coverage_evidence`: indica archivo y líneas o un
  fragmento localizable. Para una ausencia, especifica el alcance revisado y
  los términos buscados. No uses otras respuestas como fuente.
- `material_omissions`: enumera los elementos faltantes, si los hay.
- `notes`: registra dudas, referencias rotas o diferencias de alcance.

No infieras que `response_status: answered` garantiza completitud ni que
`abstained` es correcto. No corrijas la respuesta antes de calificarla. Si el
texto no permite un juicio fiable, usa `uncertain` y explica por qué.

Entrega tu hoja completa y fija su hash antes de recibir la llave de
procedencia o etiquetas de otros revisores. Este paquete evalúa respaldo
frente a la fuente completa y cobertura de la pregunta; no califica citas
individuales, coste del proveedor ni utilidad de la respuesta para usuarios.
