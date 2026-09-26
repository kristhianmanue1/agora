# Revisión separada de respaldo y pertinencia

Incremento optativo: `agora.split_review.review_split`, contrato nuevo
`agora/split-review/v1`. No modifica los modos v1/v2/v3 ni su CLI predeterminada.

```python
from agora.split_review import review_split
result = review_split(candidate, support_provider, relevance_provider,
                      prompt_budget=200000)
```

Cada proveedor recibe `(system, user)` y devuelve `finish_reason` y `content`
(JSON). Son dos llamadas como máximo, sin reintentos. Ambos prompts se calculan
sobre una copia del candidato y se comprueba su presupuesto conjunto antes de
llamar. El límite es de bytes UTF-8, no de tokens ni dinero. El transporte debe
acotar tiempo y salida. No se incluye aquí un nuevo transporte ni se llama al LLM
al ejecutar los tests.

| Eje | Información visible | Resultado |
|---|---|---|
| Respaldo | Afirmaciones y sus citas | supported / contradicted / insufficient |
| Pertinencia | Pregunta, aspecto y afirmación | relevant / extra / uncertain |

No se entrega el juicio de un eje al otro. Los proveedores deben usar solicitudes
nuevas, sin historial compartido: esta función no controla estado oculto de un
servicio. Si la afirmación contiene referencias ambiguas, el evaluador debe
abstenerse de declarar respaldo; no recibe la pregunta para resolverlas. Que el
prompt lo pida no acredita que el modelo lo cumpla.

Se valida cobertura, IDs, etiquetas, referencias y forma cerrada. Sólo con ambos
ejes completos se emite una recomendación. Un fallo posterior conserva el juicio
anterior para inspección, sin recomendar aprobación. El resultado completo pide
revisión o adjudicación; nunca incorpora memoria ni aprueba el candidato. La
revisión de idioma y de omisiones globales no está implementada en este contrato.

## Evidencia de este incremento

301 tests locales pasan, incluidos ocho nuevos. Cambiar sólo la pregunta conserva
exactamente los bytes enviados al evaluador de respaldo; la pertinencia puede
variar. Esto acredita separación de entradas, no invariancia de respuestas de un
modelo no determinista. Se comprueban errores, cobertura, ausencia de mutación,
presupuesto previo y separación aun cuando un proveedor muta el objeto del caller.
No hubo llamadas pagadas ni comparación semántica con el modo combinado.

Autorrevisión adversarial: la separación puede perder contexto útil si la
formulación depende de pronombres; exige afirmaciones autosuficientes o
insufficient. Dos llamadas pueden aumentar coste/latencia; no se declara ahorro.
Las citas suministradas siguen siendo selección del productor: no demuestran
cobertura del documento, autenticidad ni independencia del revisor.

Siguiente medición: mismos pares de afirmación/citas con preguntas distintas,
comparación contemporánea combinado/separado, etiquetas esperadas fuera del
payload, exactitud por eje y conjunta, errores de transporte, tokens y latencia.
No reetiquetar los ensayos históricos ni contar simulaciones como aciertos del LLM.
