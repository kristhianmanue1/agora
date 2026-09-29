# Diagnóstico pareado de suficiencia: fuente vs resumen

Cuatro contrastes del caso de cifras: tarea original, tarea acotada a módulo/cantidad, omisión del límite y tarea que exige botones ausentes en la fuente. Dos ejes distintos: source_sufficiency y summary_coverage relativa a información presente. Protocolo/etiquetas fijados antes de ocho llamadas (cuatro GLM, cuatro Jev), 90 s/caso, cero reintentos. GLM glm-5.3-flash (JSON, temperatura 0, 2048 tokens salida); Jev jev-1.13.0 (choice). Mismo state, distinto envoltorio de API.

## Resultado

Ambos proveedores coinciden en los cuatro pares: original insufficient/complete; bounded sufficient/complete; omission sufficient/omitted; source-gap insufficient/complete. Frente a hipótesis congeladas, source 3/4 y summary 4/4 por proveedor. El original tenía uncertain como hipótesis de ambigüedad: se conserva ese desacuerdo.

Esto apoya separar insuficiencia de fuente de omisión del resumen. No demuestra por qué Jev rechazó el caso histórico ni que una nueva rúbrica lo arregle en general. No se repitió el prompt antiguo; hubo cambio explícito del objeto evaluado. Ver [revisión separada](INDEPENDENT_REVIEW.md) y [resultados saneados](result.json).

GLM y Jev no se toman como árbitros independientes entre sí por coincidir; sus salidas son dos observaciones. No modifica defaults ni producto. Análisis de costes y continuación en la batería de documentos largos.
