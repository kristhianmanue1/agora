# Resultado: ahorro de lectura con riesgo de perder contexto

## Decisión

**No se cumple el criterio para integrar el control en la CLI de producto.** Separar los ejes resuelve la ambigüedad conceptual, pero los documentos largos revelan insuficiencia de fuente que ambos modelos pasan por alto en el contexto corto. No hay promoción de Jev ni control nuevo activado.

## Observaciones y etiquetas

- Ambos modelos detectan omisión en c01 al ver el artículo completo, aunque gold esperaba complete. La revisión separada coincide: faltan datos de evaluación presentes, y el corpus Wikipedia cumple principalmente papel de entrenamiento. No es correcto contar automáticamente esta discrepancia como error del modelo.
- Jev considera complete c03 con pasaje anotado; GLM lo considera omitted. Ambos consideran suficiente esa fuente corta. El revisor separado la juzga insuficiente para identificar los conjuntos de evaluación. El contexto reducido oculta la distinción entrenamiento/evaluación.
- Los cuatro casos de idiomas coinciden con gold en ambos modelos. Los idiomas omitidos son inglés, francés y alemán.
- Se conservan gold, respuestas y revisión separados. No se recalcula un marcador corregido como si fuera referencia independiente definitiva: c03/c04 mantienen ambigüedad de cobertura según el contrato.

## Consumo medido y concordancia con gold original

| Proveedor | Contexto | Tokens entrada | Tokens salida | Segundos acumulados | Fuente | Resumen |
|---|---|---:|---:|---:|---:|---:|
| jev | Completo | 53807 | 379 | 1.738 | 4/4 | 3/4 |
| jev | Anotado | 3869 | 378 | 1.302 | 4/4 | 4/4 |
| glm | Completo | 49784 | 1681 | 34.891 | 4/4 | 3/4 |
| glm | Anotado | 2594 | 1292 | 30.251 | 4/4 | 3/4 |


Reducción de tokens de entrada jev: 92.8% en estas cuatro llamadas pareadas.

Reducción de tokens de entrada glm: 94.8% en estas cuatro llamadas pareadas.

Los denominadores conservan cuatro llamadas por contexto. Son 16 llamadas completadas, cero errores/reintentos: 113.784 tokens totales reportados entre ambos proveedores. El diagnóstico sintético previo consumió otros 5.241 tokens en ocho llamadas. Total del turno: 24 llamadas y 119.025 tokens; sin reintentos. Los tiempos son de solicitudes, no preparación humana ni proceso total de investigación. Tokens de salida GLM pueden incluir el consumo reportado más allá del JSON visible. Coste monetario total no verificado: no se consultó ledger ni se fijó tarifa aplicable. Reportamos consumo total entrada+salida, no una cifra monetaria inventada.

La reducción no acredita ahorro seguro: no incluye recuperar pasajes ni su revisión y utiliza anotaciones privilegiadas. La pérdida observada de contexto impide concluir «leer menos sin perder lo importante».

## Revisión independiente: alcance real

Otra instancia revisó inputs con IDs neutrales, sin gold ni salidas de proveedores; su informe identifica citas y ambigüedad. Es separación del productor, pero comparte entorno/modelo declarado; no es adjudicación humana ni independencia de proveedor. GLM es el contraste externo a Jev, y tampoco su acuerdo equivale a verdad. El revisor examinó pasajes pertinentes de los largos, sin afirmar lectura integral de cada carácter.

## Qué falta antes de integración

1. Fijar que summary_coverage juzga pérdida de información presente y que source_sufficiency no se deduce de esa cobertura.
2. Incorporar casos reservados sobre papel semántico (entrenamiento vs evaluación), junto con fuentes insuficientes. Adjudicar c03/c04 antes de usar etiquetas corregidas como referencia.
3. Volver a medir recuperación real, generación y revisión, incluyendo todos sus tokens/costes, sin usar selección oracle como ahorro del producto.
4. Sólo entonces integrar un resultado explícito de revisión requerida, manteniendo ejes separados y sin admisión automática. Esta condición no está satisfecha hoy.

El trabajo actual completa el diagnóstico pareado y el piloto largo acotado. No declara cerrada la validación general solicitada ni la integración condicionada.
