# Recuperación por aspectos: mejora parcial y límite de síntesis

2026-09-23. Ensayo acotado completado; no se promovió una capacidad del producto.
Predecesor: [fuente grande](fuente-grande-comparacion-01.md).
Evidencia local excluida de Git: `experiments/large-source-v1/runs/aspects-01`.

## Método

Misma fuente NaturalOWL de 138223 bytes, pregunta G1, criterios, consumidor
`passage_cli`, prompt base legacy, GLM 5.3 Flash, temperatura 0 y salida máxima
8192 tokens. Formato de proveedor omitido. Código del producto idéntico al ensayo
previo. Se revisó explícitamente el timeout a 180 segundos de socket y 200 de
proceso para ambas llamadas. Dos llamadas nuevas, sin reintentos. El timeout
anterior permanece inalterado; su consumo sigue siendo desconocido.

Descomposición **manual** de la pregunta en seis búsquedas: nombres, planes,
selección, evaluación/automatización, recursos manuales e idiomas. Es un caso de
desarrollo conocido, no una descomposición autónoma ni una evaluación independiente.
No se usaron rangos de las referencias para seleccionar evidencia.

Cada aspecto usa el recuperador léxico existente: inicialmente top_k=1 con
2000 bytes, unión deduplicada; después una pasada de ampliación top_k=2 con
4000 bytes por aspecto, aceptando sólo nuevos párrafos que quepan en 12000 bytes
totales. Unión inicial 5140 bytes; final 7667 bytes en 19 rangos. Las búsquedas
recorren localmente toda la fuente doce veces, sin llamadas LLM de extracción.
Por tanto no se afirma reducción de lectura local ni eficiencia del selector.
El orden de aspectos y coincidencias condiciona el reparto del presupuesto.

Selección, scripts, código, fuente y criterios se congelaron antes de llamar.
La vía reference recibe sólo los rangos seleccionados, la misma pregunta y las
mismas reglas de respuesta; no recibe etiquetas de cobertura ni las referencias.

## Resultados

| Ruta nueva | Bytes fuente enviados | Tokens totales | Segundos | Estado |
|---|---:|---:|---:|---|
| Por aspectos | 7667 | 5423 | 43.258 | Candidata aceptada; incompleta |
| Directa | 138223 | 38677 | 114.833 | Rechazada: 13 citas, máximo 12 |

Total nuevo: **44100 tokens**, 158.091 segundos sumando procesos, sin timeout
nuevo. Los tokens no equivalen a coste monetario: la llamada directa reportó
30592 tokens de prompt en caché. No se midieron preparación/revisión ni tarifa.
No se presenta ahorro a igual calidad: una ruta sigue incompleta y la otra no
cumple el contrato. Sumando el ensayo anterior: 84362 tokens conocidos más el
consumo desconocido del timeout original.

## Revisión de los seis criterios originales

| Criterio | Recuperación inicial | Por aspectos |
|---|---|---|
| Frases nominales, alineación, anotaciones | Omitido | Conservado |
| Plantillas/semillas, anotaciones, Maximum Entropy | Omitido | Conservado |
| Selección humana entre cinco vs primero automático | Omitido | Conservado |
| Resultado semiautomático y fracaso de automatización total | Conservado | Parcial |
| Recursos manuales iguales entre configuraciones | Parcial | Parcial |
| Otros idiomas como trabajo futuro | Conservado | Conservado |

La nueva ruta recupera los tres procedimientos antes omitidos. Pero pierde la
formulación explícita del resultado negativo de automatización total, que ahora
sólo aparece como objetivo futuro. Sigue sin establecer que los otros recursos,
especialmente text plans, permanecen manuales e iguales en las cuatro
configuraciones. Estos hechos no estaban en los pasajes seleccionados.

Hay cuatro criterios completos y dos parciales; no es una puntuación estadística
ni una garantía de fidelidad. La regresión en el criterio de resultado muestra
que reemplazar una selección puede perder evidencia útil anterior. Disponer de
una coincidencia por aspecto no prueba cobertura semántica. Además, quedaron
4333 bytes libres: el fallo no se explica simplemente por presupuesto agotado.

Las ocho citas aceptadas coinciden con sus rangos UTF-8. Autorrevisión del
productor contrastada con los pasajes y criterios, no revisión independiente.

## Lectura directa

La respuesta terminó con `stop`, JSON parseable y 13 citas literalmente presentes
en la fuente. El validador exige como máximo 12 (`query.py`) y devolvió
`invalid_answer_shape`. No hubo recorte, reparación ni promoción. El texto bruto
menciona los seis criterios, pero incluye detalles adicionales cuya totalidad no
se certifica aquí; no se cuenta como entrega válida ni como baseline exitosa.

La nueva ejecución completa la observación pendiente del comportamiento con
mayor tiempo, pero **no obtiene una baseline aceptada para G1**. Ampliar el tiempo
resolvió este timeout puntual, no el cumplimiento del contrato ni la fidelidad.

## Verificación

`audit_aspects.py`: hashes congelados, resultados, código actual y citas
verificados. Rangos válidos UTF-8, unicidad y presupuesto total comprobados.
Sintaxis y `git diff --check` pasaron. No hubo cambios en src/tests ni nueva
suite del producto: los 183 tests previos siguen vinculados al código idéntico.

## Decisión y próximo paso

No promover la recuperación por aspectos como solución completa ni relajar el
límite de citas para aceptar esta respuesta a posteriori. Detener reintentos
idénticos y separar los dos fallos observados.

Siguiente experimento recomendado: un control positivo de **contexto suficiente**,
seleccionado explícitamente por el revisor, que reúna los pasajes necesarios de
los seis criterios dentro de 12000 bytes, conservando también las limitaciones y
los controles experimentales. Registrar que usa referencias conocidas y por ello
no mide recuperación automática. Una sola síntesis nueva permitiría comprobar si
la entrega completa cabe en el contrato antes de invertir en mejorar el selector.

Si ese control funciona, el incremento siguiente será el selector por aspectos:
preservar evidencia útil anterior, dedicar búsquedas específicas a límites y
condiciones, y dejar cobertura `not_verified` hasta una revisión real. La
selección léxica por sí sola no puede declarar un aspecto semánticamente resuelto.

## Control posterior

El [control con contexto suficiente](control-contexto-suficiente-01.md) recibió
los pasajes necesarios, pero fue rechazado: 15 citas y una cita alterada. Se
identificó además que el prompt base no comunica el máximo de 12 del validador.
