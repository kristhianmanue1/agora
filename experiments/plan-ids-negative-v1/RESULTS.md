# Resultado: controles negativos del manual DPM

## Conclusión acotada

Se cumple el criterio principal congelado: Jev no acepta ninguna de las tres alteraciones y acepta los cuatro controles respaldados. Coincidencia exacta: **6/7**. No modifica el estado de admisión del candidato ni promueve a Jev como revisor predeterminado.

| Caso | Etiqueta previa del productor | Jev |
|---|---|---|
| Tres controles positivos | supported | supported (3/3) |
| Atribución al encabezado equivocado | contradicted | contradicted |
| Instrumentar sin autorización previa | contradicted | contradicted |
| Extensión a todas las dependencias federales | insufficient | contradicted |
| Omisión que no afirma permiso de instrumentar | supported | supported |

## Desacuerdo conservado

El fragmento de la Coordinación de Servicios Administrativos respalda funciones sobre recursos de la Dirección de Prestaciones Médicas. No establece ni niega explícitamente su competencia sobre todas las dependencias federales. Según la rúbrica congelada, esa ampliación carece de respaldo: insufficient. Jev eligió contradicted. Conservamos la etiqueta previa y contamos el desacuerdo; no es una adjudicación independiente.

Esto separa dos propiedades: detectar una afirmación no respaldada y diagnosticar correctamente por qué no está respaldada. El primer control pasó; el segundo no fue perfecto. Rechazar una afirmación como respaldada no autoriza a declarar falso su contenido ni a cerrar automáticamente una cuestión.

## Ejecución y comprobaciones

- Modelo reportado por API: jev-1.13.0; siete llamadas, cero errores y cero reintentos; timeout por llamada: 90 s.
- Tokens: 4053 entrada + 317 salida = 4370; suma de tiempos de petición: 2.404 s. No es el tiempo total de preparación ni una estimación monetaria.
- Hashes de entradas y etiquetas verificados contra freeze.json antes del análisis. State del request comprobado contra pregunta, evidencia y afirmación; gold no enviado.
- La revisión automática bloqueó el primer intento antes del proceso. Tras autorización explícita del Operador se ejecutó una única corrida. No existía journal previo.
- Respuestas completas y fragmentos locales excluidos de Git; resultados saneados en [result.json](result.json). El informe no depende de interpretar las probabilidades como confianza calibrada.

## Límites y autorrevisión adversarial

Batería sintética de desarrollo de siete casos, preparada y etiquetada por el mismo agente; tres controles positivos reutilizados. No es muestra independiente, reservada ni representativa. Una sola corrida, sin comparación pareada con GLM. La prueba revisa afirmaciones sobre pasajes: no mide recuperación, omisiones de un resumen completo, exhaustividad del manual ni corrección clínica.

El control de omisión muestra que una afirmación puede ser respaldada aunque no incluya un paso decisivo para operar. Por ello, fidelidad de afirmaciones y suficiencia para la tarea requieren controles separados. No usar este resultado para considerar adecuada una guía de instrumentación que omita la autorización.

## Siguiente paso recomendado

Mantener Jev como candidato a revisor. Separar en la evaluación futura **respaldo de cada afirmación** de **información indispensable para la tarea**. Construir un par de resúmenes que tengan afirmaciones verdaderas, pero sólo uno conserve la autorización necesaria; comprobar si la revisión actual detecta esa omisión antes de ampliar el producto. La adjudicación independiente de etiquetas sigue pendiente.
