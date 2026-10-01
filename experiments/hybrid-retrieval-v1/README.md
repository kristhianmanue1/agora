# Fusión léxica y estructural: mejora parcial, una regresión

Cuatro casos conocidos, sin proveedores. Candidatos de los selectores previos,
cada uno con límite 12.000 bytes. Fusión congelada antes de puntuar: preservar título,
repartir cuotas iguales por bytes nuevos, deduplicar rangos y redistribuir el sobrante
alternando léxico/estructural. Se conservan rangos enteros; no se recortan citas.
Los selectores y la fusión no reciben rúbricas; éstas puntúan después de seleccionar.

| Caso | Baseline | Estructural | Híbrido | Bytes híbrido |
|---|---|---|---|---:|
| Modelos preentrenados | 0/1 | 1/1 | 1/1 | 11.346 |
| Validación cruzada | 0/3 | 3/3 | 3/3 | 11.442 |
| Modelos de referencia | 1/1 | 0/1 | **0/1** | 11.738 |
| Mitigación de sesgo | 1/1 | 0/1 | 1/1 | 10.983 |

Los conteos corresponden a párrafos anotados, no exactitud semántica de respuestas.
La mezcla conserva los dos aciertos estructurales y recupera uno de los controles,
pero pierde un acierto léxico. Son cuatro casos de desarrollo conocidos, no una tasa
estimada de fiabilidad. No se generaron respuestas ni se midieron tokens de modelo.

## Regresión preservada

En modelos de referencia, el párrafo anotado de 1.026 bytes queda fuera mientras
sólo restan 262 bytes. Se encuentra expresamente en skipped_ranges. La cuota y el
orden de los rangos no aseguran preservar los pasajes relevantes. No se modificó
la regla tras observar esto. Tampoco se amplió el presupuesto ni se eligió el
selector ganador usando etiquetas de evaluación.

Los artefactos quedan en freeze.json, result.json y regression.json. Tests: combinación
positiva, deduplicación, presupuesto/título, UTF-8 y reproducción completa incluida
la regresión. No hay cambios de producto/defaults ni admisión.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 experiments/hybrid-retrieval-v1/tests.py
PYTHONDONTWRITEBYTECODE=1 python3 experiments/hybrid-retrieval-v1/run.py
```

La ejecución requiere dataset y fuentes locales anteriores; hashes en freeze.json.
La rúbrica de modelos preentrenados sigue siendo una referencia incompleta; no se
reinterpretan los resultados como completitud del documento.

## Decisión

No promover esta fusión. Siguiente condición recomendada: preservar explícitamente
los rangos del baseline y añadir estructura sólo con el espacio restante, informando
qué queda fuera; si el contexto necesario no cabe, devolver insuficiencia de presupuesto
sin descartar silenciosamente lo ya seleccionado. Esto garantiza conservación de
rangos, no relevancia ni suficiencia. Congelar y evaluar esa condición por separado;
si pasa los controles, contrastar después con documentos nuevos antes de usar API.
