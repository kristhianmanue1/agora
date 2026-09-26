# Revisión experimental de idioma y evidencia

## Alcance

La consulta de evidencia admite `--response-language es|en` (es por defecto)
y `--max-unit-bytes N` (4096 por defecto; 4–12000). El tamaño sólo afecta a
`--citation-mode ids`. El modo literal sigue siendo predeterminado. El prompt
explicita el idioma de afirmaciones y faltantes aunque pregunta/fuente estén en
otro idioma; nombres y citas se preservan. Esto es una instrucción al modelo,
no detección ni garantía: `language_status` permanece `not_verified`.

Las unidades largas prefieren cortes en espacios de la segunda mitad del
presupuesto; si no los hay, cortan en frontera UTF-8. Los fragmentos son literales
y mantienen offsets. No se eliminan palabras ni se incorporan solapamientos.
Párrafos adyacentes siguen disponibles en la entrada completa. El corte puede
separar una negación o condición: el productor debe citar todas las unidades
necesarias. Una unidad menor no demuestra ahorro ni fidelidad mayor.

## Revisor separado

`agora.evidence_review.review_evidence(candidate, provider)` recibe un candidato
estructuralmente aceptado y realiza como máximo una llamada. Puede utilizarse
con el transporte del llamador; el runner del piloto incluye un transporte GLM
acotado. No se ejecuta automáticamente desde la CLI de generación.

Evalúa:

- Idioma de afirmaciones y elementos `missing`, excluyendo citas originales.
- Respaldo de cada afirmación por sus propias citas: `supported`, `contradicted`
  o `insufficient`.
- Pertinencia respecto de pregunta/aspectos: `relevant`, `extra` o `uncertain`.

El contrato `agora/evidence-review/v1` exige una fila por afirmación, índices de
citas existentes y motivos acotados. Una respuesta incompleta, Markdown o JSON
inválido se rechaza sin reparar. El SHA-256 del candidato vincula el dictamen
al artefacto exacto; no acredita identidad de quien lo produjo.

Una observación negativa produce `needs_revision`; una favorable,
`needs_adjudication`. Nunca cambia el candidato, su `semantic_support`, ni lo
admite en memoria. La validez de los índices de una revisión tampoco demuestra
que su razonamiento sea correcto. El llamador conserva y verifica la procedencia
del candidato: el revisor no vuelve a abrir la fuente.

## Límites que permanecen

Es revisión automática probabilística. Usar el mismo modelo en otra llamada no
constituye adjudicación independiente. Sólo ve las citas seleccionadas: no puede
certificar omisiones, cobertura global ni la ausencia de un dato en la fuente.
También puede fallar en formato, idioma, interpretación y pertinencia. No decide
publicación ni aceptación del Operador. Hay que medir su coste adicional y probar
controles positivos y negativos antes de atribuirle capacidad de detección.

El idioma de los motivos del revisor no tiene un requisito contractual; el idioma
evaluado es el texto de la respuesta candidata. No hay correcciones ni reintentos
automáticos, y la ausencia de una revisión válida nunca significa aprobación.

Piloto: `experiments/evidence-review-v1/`, dos documentos públicos nuevos,
comparación 4096/1024 y dos controles conocidos; protocolo y código congelados
antes de las llamadas. Resultados: `docs/evaluacion-revision-evidencia-01.md`.

## Resultado observado

El piloto encontró un falso positivo real: el revisor puede escribir `supported`
y reconocer en el motivo que un detalle de la afirmación no está en las citas.
El contrato actual valida forma e índices, pero no detecta esa contradicción
semántica. Por ello sólo emite recomendaciones provisionales y no habilita
aprobación automática. Los tres controles posteriores al ajuste de formato dieron
salidas JSON válidas; la corrección del formato no corrigió ese falso positivo.

## Continuación optativa por detalles

Existe una revisión v2 optativa: `docs/revision-evidencia-por-detalle.md`.
Conserva v1 y calcula la etiqueta global a partir de juicios por fragmento literal.
El piloto y sus límites se registran en `docs/evaluacion-revision-detalles-01.md`.
No reemplaza ni reinterpreta los resultados v1 descritos arriba.
