# Ampliación experimental para condiciones y excepciones

**La regresión conocida pasó:** se recuperó la excepción Automotive/10-core y la
respuesta original la conservó con cita, sin reparación. No se promueve a default.

## Mecanismo construido

`expansion.py` recibe fuente UTF-8, pregunta y rangos iniciales. Escanea párrafos
buscando simultáneamente coincidencias de términos de la pregunta y señales como
`except`, `excluded`, `only`, `unless`, `whereas` y equivalentes españoles.
Ordena por coincidencia con pregunta y contexto inicial; añade hasta dos párrafos
completos sin superar 10.000 bytes totales. Conserva rangos previos y offsets.
Registra candidatos omitidos por presupuesto y no declara exhaustividad semántica.
No consume rúbrica, respuestas de referencia, candidato completo ni el nombre
Automotive. La selección local sí lee la fuente completa: no ahorra acceso a disco.

Es una heurística diseñada después de observar este fallo. Señales explícitas y
coincidencias léxicas no detectan toda excepción ni verifican relevancia. Puede
fallar con sinónimos, condiciones implícitas, tablas, lenguas distintas o párrafos
muy grandes; `only` también recupera detalles ajenos a la condición buscada.

## Condición congelada

Mismo documento QASPER `2001.04346`, pregunta y fragmentos iniciales de la
[comparación anterior](../reading-paired-grouping-v1/README.md). Rúbrica explícitamente
enmendada: R1/R2 conservados; R3 pide mantener la excepción conocida. Esa enmienda
sólo se usa al evaluar, no para recuperar. El generador recibió la selección ampliada
sin rúbrica; se conservaron prompt de agrupación, límites y modelos previos.
Una generación GLM, una revisión por `review-rubric`, una revisión Jev por afirmación.
Ningún reintento, cambio de pregunta, reparación o sustitución de caso.

## Resultado

| Medida | Selección inicial | Ampliación | Fuente completa anterior |
|---|---:|---:|---:|
| Bytes enviados al generador | 5.145 | 7.213 | 34.053 |
| Tokens de generación y dos revisiones | 5.164 | 8.186 | 26.504 |
| Excepción Automotive/10-core conservada | No | Sí | Sí |

R1–R3: `covered`. Jev: tres afirmaciones `supported`. El candidato intacto pasa
validación. El modelo declara la exclusión en 10-core porque quedan pocos usuarios
e ítems. La reducción observada frente al total histórico completo es 69,11%, pero
no constituye una comparación replicada ni garantía general de calidad equivalente.
El segundo párrafo añadido trata interpretabilidad y no era necesario para recuperar
la excepción; se conserva para mostrar el coste de una señal demasiado amplia.

El total incluye estas tres llamadas, no desarrollo, trabajo humano ni construcción
de rúbrica. Precio monetario no informado. No sumar ni sustituir retrospectivamente
resultados de condiciones anteriores. El respaldo de proveedores no es adjudicación.

## Verificación

Seis pruebas offline cubren señal+tema, presupuesto, preservación inicial, UTF-8,
párrafos repetidos, ausencia de señales y rangos inválidos. Ejecutar:

```bash
python3 experiments/condition-expansion-v1/test_expansion.py
python3 experiments/condition-expansion-v1/verify.py
```

El segundo comando verifica hashes, reproducción exacta de selección, recuperación
del pasaje de regresión, rúbrica separada y candidato sin reparación, además de
vínculos de revisores. Cero HTTP. Artefactos completos locales ignorados; respuestas
y hashes conservados en `result.json`. No cambió código en `src/agora`, contratos
públicos, defaults ni memoria; la nueva función sigue en el experimento.

## Siguiente paso

Congelar esta heurística y probarla en otra fuente reservada con una condición
que modifique la respuesta. Incluir un control sin excepción para medir ampliaciones
innecesarias y un caso donde la condición no quepa en presupuesto. Sólo después
considerar exponer una opción de CLI. Cuando no logre evidencia suficiente, declarar
alcance parcial o pedir ampliación explícita; no convertir “sin señales” en “sin
excepciones”. No afinar repetidamente sobre Automotive para simular generalización.
