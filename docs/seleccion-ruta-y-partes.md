# Selección de ruta y respuestas por partes

## Resultado implementado

La nueva API `agora.routed_query.query_routed` y CLI `python3 -m agora.routed_cli`
priorizan la fuente completa cuando caben tanto sus bytes como el prompt real
(instrucciones, preguntas, estructura JSON y fuente). Si no cabe, consumen un
recorrido aportado y verificado, o devuelven `traversal_required` sin llamar al modelo.
Nunca inician un recorrido de varias llamadas ni elevan presupuestos automáticamente.

`--full-source-budget` limita la selección de lectura completa, no es un límite
universal de contexto ni de gasto. `--prompt-budget` se aplica también a la evidencia
retenida. Ambos se expresan en bytes; `--max-output-tokens` limita por separado la
salida solicitada al proveedor. No son límites monetarios ni prueba de que el modelo
terminará de responder. El valor por defecto de salida de esta nueva CLI es 8192.

La solicitud contiene entre una y ocho partes explícitas, con identificador y pregunta.
Cada parte debe aparecer exactamente una vez en la respuesta. Una parte desconocida
conserva `not_in_document`; el resultado global se etiqueta `candidate_partial` y
expone `unanswered_parts`, sin borrar las respuestas conocidas. Recorrido parcial,
evidencia vacía y necesidad de recorrido tienen estados distintos y no generan
una respuesta. El resultado es candidato, no certificado semántico.

Contrato nuevo: `agora/routed-query/v0.1`. Admite como máximo 12 citas por parte:
hasta 96 en ocho partes. No conserva el máximo global de la consulta anterior de
una sola parte. Los contratos anteriores no cambian ni se reinterpretan sus rechazos.
Las citas deben pertenecer literalmente a un pasaje y tienen anclajes en el original;
no pueden construirse pegando fragmentos separados.

Se extrajo `verify_traversal` como función reutilizable, conservando el comportamiento
anterior. Comprueba reconstrucción y revisión, no autentica receipts ni demuestra que
las nuevas partes estén semánticamente contenidas en la pregunta del recorrido.
Esa relación la declara quien prepara la solicitud. La descomposición en partes es
explícita; no se implementó un descompositor automático.

## Uso

`parts.json` contiene una lista como:

```json
[
  {"id":"components", "question":"Enumera los componentes de la primera etapa."},
  {"id":"later", "question":"Describe las etapas posteriores por año."}
]
```

```bash
PYTHONPATH=src python3 -m agora.routed_cli \
  --source /ruta/fuente.txt --source-id identidad --sha256 SHA256_FUENTE \
  --question 'Pregunta general' --parts /ruta/parts.json \
  --model glm-5.3-flash --out /ruta/salida-nueva
```

Opcional: `--traversal /ruta/recorrido.json --traversal-sha256 SHA256_RECORRIDO`.
La identidad, revisión y pregunta general deben coincidir con el recorrido.
Cuando la fuente completa cabe, se prefiere esa ruta y no se necesita validar el
registro opcional para responder. El resultado indica qué ruta se utilizó y por qué.
La salida es `result.json`: respuestas por partes, pendientes, citas y procedencia.
No se aplana en un párrafo que oculte una parte sin respuesta. Las CLI anteriores
siguen disponibles y no adoptan automáticamente este contrato.

## Pruebas y ensayo del 23 de septiembre de 2026

159 pruebas locales OK, incluidas 14 específicas nuevas: frontera de presupuesto,
overhead de prompt, rutas, recorrido parcial, registro alterado, cita que cruza
pasajes, parte omitida, parte pendiente, exceso de citas, identidad y revisión.
Una prueba confirma el límite del método: una explicación semánticamente incorrecta
puede pasar la estructura y permanece `semantic_support: not_verified`.

Código y casos congelados antes de cuatro solicitudes GLM, sin reintentos; modelo
solicitado y reportado en las respuestas recibidas `glm-5.3-flash`, temperatura 0,
salida máxima 8192 tokens, socket 90 s y deadline de proceso 110 s.

| Caso | Ruta | Resultado | Tokens reportados |
|---|---|---|---:|
| R1, propuesta anterior en cuatro partes | Fuente completa | Candidata; conserva seis componentes y las demás partes | 8558 |
| R2, misma regresión con umbral artificialmente bajo | Recorrido reutilizado | Candidata; conserva seis componentes y las demás partes | 5558 |
| N1, caso nuevo de acciones por fase y fecha no acordada | Fuente completa | Candidata; seis acciones y estado de fecha conservados | 905 |
| N2, conflicto de importe y autorizante desconocido | Fuente completa | Timeout; sin respuesta semántica evaluable | Desconocidos |

R1 y R2 usan cuatro subpreguntas preparadas explícitamente después de conocer el
fallo: regresión guiada, no comparación causal ni evaluación ciega. N1 y N2 son
casos nuevos conocidos por el productor. Se comprobaron 26 archivos congelados,
cuatro hashes de resultados y los anclajes de las citas recibidas.

Se recibieron 15021 tokens reportados; no es el consumo total porque N2 terminó
sin receipt. No hubo reintento de N2. Su salida parcial está probada mediante fakes
locales, pero el comportamiento semántico de GLM en ese caso queda sin evaluar.
Los 5558 tokens de R2 no incluyen los 19527 de extracción histórica: construir el
recorrido y responder de esta manera sumaría 25085, frente a 8558 de lectura completa
para esta regresión. La reutilización es específica de una pregunta, no un índice general.

La autorrevisión adversarial encontró un matiz residual: R1 dice que el presupuesto
no está aprobado; la fuente acredita que es un borrador, no el estado de aprobaciones
externas. R2 usa la formulación más precisa «no acredita». No hay verificación externa
de ese estado, ni validación clínica o presupuestal del documento. Ninguna candidatura
se promovió a memoria ni a respuesta certificada. No participó un revisor independiente.

Evidencia local ignorada por Git: `experiments/routed-query-v1/inputs/` y
`experiments/routed-query-v1/runs/glm-01/`. Los resultados anteriores siguen intactos.

## Continuación

Mantener la lectura completa como primera opción dentro del presupuesto. Antes de
promover la síntesis, completar la evaluación de respuestas parciales y contrastar
más fuentes con criterios previos de omisión; no basta con que todas las partes
aparezcan en JSON. N2 requiere un ensayo posterior separado si se quiere obtener
su respuesta real. Quedan sin implementar reanudación de recorridos, descomposición
automática y certificación semántica. No hubo commit ni push.

## Reintento separado de N2 — 2026-09-23

`experiments/routed-query-v1/runs/glm-02-n2/` conserva una nueva llamada con
los mismos parámetros, fuente y código congelado de glm-01. Respondió en
10,747 s, con 1030 tokens reportados y `candidate_partial`: conserva 18 y 22
sin precedencia, `approver=not_in_document` y validación administrativa antes
de pagar. Autorrevisión contra la fuente y anclas de bytes satisfactoria;
no hubo revisor independiente. La respuesta parcial es la conducta esperada.
El timeout anterior y su consumo desconocido permanecen intactos. Este caso
queda evaluado, sin demostrar fiabilidad general ni eliminar el fallo operativo.

## Idioma y schema v0.2

El incremento posterior añade `response_language=es|en`, español por defecto,
y emite `agora/routed-query/v0.2`. Los receipts históricos v0.1 se conservan.
Uso y pruebas: [Batería QASPER](bateria-qasper.md).

## Perfil opcional de respuesta breve

`--answer-profile concise-v1` activa resultado v0.3 con explicación separada;
el valor por defecto legacy conserva v0.2. Desarrollo y límites:
[Respuesta breve y alcance](respuesta-breve-y-alcance.md).
