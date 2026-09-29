# Transferencia de controles de omisión a cuatro dominios

Batería sintética de desarrollo, no políticas reales ni casos reservados de un corpus externo. Excepciones, responsables, plazos y cifras; tres casos por dominio (completo, omitido operativo, omitido descriptivo). Mismos criterios y preguntas tipadas que summary-task-sufficiency-v2. La única adaptación del runner es el límite de 12 casos.

Gold y entradas congelados antes del envío. Máximo 12 llamadas a Typesafe/Jev jev-1.13.0, 90 s cada una, cero reintentos, autorizado por el Operador para esta serie. Inputs y respuestas completas quedan fuera de Git; no se envía gold. No modifica producto ni defaults.

Autorrevisión adversarial: fixtures cortos y explícitos, dos unidades manuales, mismo productor del gold, sin adjudicación independiente. No permite estimar rendimiento en documentos largos ni requisitos dispersos. Casos del mismo dominio son dependientes. La omisión de excepción no niega explícitamente la excepción: se distingue información ausente de afirmación falsa. Los controles descriptivos detectan rechazo indiscriminado de resúmenes breves. No se ajustará el gold después de observar respuestas.

## Resultado

Ejecutado: 11/12 decisiones y 24/24 unidades coinciden; un resultado inconsistente. Criterio principal no cumplido. Véanse [resultados y límites](RESULTS.md). No repetir el journal ni cambiar etiquetas para convertir el resultado en pase.
