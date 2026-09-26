# Suficiencia de evidencia: evaluador en observación

## Resultado y alcance

Existe una API local `agora.sufficiency.assess` que pregunta si los pasajes
suministrados bastan para responder toda una pregunta. No está conectada como
control automático de la recuperación ni tiene CLI de producto. Su proveedor es
un callable; el ensayo usa GLM, sin instalar ni consultar TypeSafe.

El patrón adoptado es separar recuperación y evaluación semántica. El juicio se
conserva como `model_judgment_unverified`, con `mode: observe_only`,
`action_taken: none`, `memory_admission: not_performed` y
`semantic_verification: not_performed`. Una etiqueta suficiente no acredita verdad.

La API verifica identidad/revisión del original, hash del envoltorio, reconstrucción
exacta de los pasajes y tipos JSON, límites de presupuesto, forma del resultado y
literalidad de las citas. La revisión detectó que igualdad Python acepta `0 == False`;
se corrigió comparando serializaciones y se añadió un caso de regresión.
La explicación y la suficiencia semántica siguen siendo juicios del modelo.
Leer el original localmente para verificar su hash no equivale a enviarlo al modelo.

## Ensayo GLM: 22 de septiembre de 2026

Protocolo y casos: `experiments/sufficiency-v1/`. Evidencia local ignorada por Git:
`experiments/sufficiency-v1/runs/glm-01/`. Código, fuentes, criterios y protocolo
congelados antes de las llamadas. Siete casos nuevos, sintéticos y conocidos por el
productor; no son una evaluación ciega ni una muestra de documentos grandes.
Modelo solicitado y reportado por el proveedor: `glm-5.3-flash`; eso no constituye
verificación independiente del backend. Credencial existente del laboratorio,
inyectada sólo en el entorno del proceso, sin registrar su valor.

| Caso | Propiedad | Resultado observado |
|---|---|---|
| E1 | Identidad explícita | sufficient, adecuado |
| E2 | Coincidencia temática sin respuesta | insufficient, adecuado |
| E3 | Sólo una parte de una pregunta doble | insufficient, adecuado |
| E4 | Dos plazos sin resolución de vigencia | uncertain, adecuado |
| E5 | Preguntar por ambos plazos registrados | Rechazado por formato |
| E6 | Ausencia explícitamente documentada | sufficient, adecuado |
| E7 | Pronombre ambiguo | insufficient, adecuado |

E5 devolvió `decision: suficiente` en español en lugar del enum `sufficient`.
Su explicación y citas incluían ambos plazos, pero no cumplió el contrato.
No se normalizó ni se repitió la llamada. No se contabiliza como éxito ni como
falso rechazo semántico. E3 pide una referencia adicional además del importe;
es más de lo estrictamente necesario. En E4 las resoluciones faltantes deben
entenderse como alternativas posibles, no como requisitos acumulativos.

- 6 juicios estructuralmente válidos y 1 rechazo de formato.
- 0 aprobaciones erróneas observadas en los 4 casos negativos.
- 2 aprobaciones válidas entre 3 positivos; el restante fue el rechazo de formato.
- 7 llamadas, sin reintentos; 4 452 tokens reportados y 86,373 segundos sumados
  de los procesos por caso. No se calculó coste monetario ni ahorro frente a baseline.
- 21 archivos congelados y 7 resultados verificados por SHA-256.
- Suite local: 118 pruebas aprobadas (11 del evaluador). Sin acciones automáticas.

Otro agente revisó código y resultados en el mismo entorno; no fue una auditoría
externa. Coincidió en mantener exclusivamente el modo de observación.

La ausencia de falsas aprobaciones en cuatro casos no demuestra precisión general.
Las reglas del prompt anticipan estas clases de problemas. Hay que conservar tanto
los fallos como los éxitos y medir explicaciones, no solamente etiquetas.

## Continuación recomendada

Primero endurecer el cumplimiento del enum sin reinterpretación silenciosa y
validarlo con un conjunto nuevo. Después evaluar documentos mayores y preguntas
preparadas fuera del diseño del prompt: comparar pasajes recuperados, juicio de
suficiencia y respuesta respaldada contra la fuente. Medir también tokens del juez,
lectura local, coste total y errores de recuperación. Mantener observación hasta
obtener evidencia suficiente para decidir por separado cualquier automatización.

Este incremento no integra Skopos o AN-KLA, no admite memorias y no publica cambios.

## Ensayo posterior

El [ensayo con fuente mayor](suficiencia-fuente-mayor.md) encontró una falsa
suficiencia en una pregunta global. Sus resultados complementan este ensayo;
los siete resultados anteriores permanecen intactos.
