# Recuperación y nueva revisión sin localizador prefijado

## Resultado

El recuperador existente encontró el pasaje decisivo con la pregunta y la
 afirmación como única consulta. Ambos revisores acertaron las cuatro evaluaciones
posteriores. No se modificó el recuperador, los prompts ni el proveedor predeterminado.

| Presupuesto de recuperación | Texto recuperado | Abstract + pasajes enviados | GLM | Jev |
|---|---:|---:|---:|---:|
| 4096 bytes | 3645 B | 5341 B | 2/2 | 2/2 |
| 8192 bytes | 7245 B | 8947 B | 2/2 | 2/2 |

En ambas consultas y presupuestos se incluyó el pasaje de bytes [29017,30392)
que establece la dependencia de un planificador externo. Este localizador sólo se
consultó después para medir el resultado; no fue entrada de la búsqueda.
Las dos afirmaciones opuestas generan la misma selección de pasajes. Por tanto,
no son cuatro temas ni cuatro documentos distintos: es una propiedad conocida.

El paquete menor es el 4.60% de los 116094 bytes del documento completo.
Esta proporción corresponde a texto entregado, no a ahorro monetario ni a lectura
local: el recuperador escanea toda la fuente y el adaptador la relee para verificarla.
El presupuesto mayor no mejoró los resultados en este ensayo. No se concluye que
4096 bytes sean suficientes para todas las consultas.

## Método y trazabilidad

- Consulta literal: pregunta anterior + salto de línea + afirmación anterior.
- Recuperador sin cambios: lexical-paragraph-overlap/v0.1, top_k=3, con vecinos
  cuando caben. No se añadieron sinónimos, frase ancla, ubicación o gold.
- Presupuestos fijados antes de recuperar; no hubo ajustes para lograr el resultado.
- Fuente fijada por hash. Rangos recuperados, bytes y hashes conservados en selection.json.
- Abstract anterior conservado; pasajes añadidos literalmente. El modelo no recibe
  cuál pasaje es decisivo ni el juicio previo. Es una nueva revisión vinculada al
  caso anterior, no una explicación retrospectiva del modelo.
- Criterios fijados sobre la evidencia seleccionada antes de las llamadas: dependencia
  externa supported; ejecución interna contradicted. Son criterios del productor,
  sin revisión independiente; no etiquetas oficiales QASPER.

## Límites y autorrevisión

Es desarrollo sobre un fallo conocido en el documento QASPER 1811.00051, no holdout.
Aunque no se entregó el localizador al algoritmo, el diseñador conocía el caso.
La búsqueda léxica favorece afirmaciones que comparten vocabulario con la fuente;
este ensayo no mide paráfrasis, otros idiomas, múltiples fuentes o excepciones
repartidas. Cada paquete se evaluó una vez por modelo; no mide estabilidad aquí.

La presencia del párrafo esperado se mide por cobertura de rango, no demuestra
completitud semántica de toda la selección. Recuperar cero pasajes no prueba ausencia;
agotar el presupuesto tampoco. Un resultado supported no activa admisión automática.
No se añadió vigilancia ni escritura en AN-KLA.

## Continuación recomendada

Incorporar este recorrido probado a una acción explícita de CLI: seleccionar
una revisión y afirmación, preparar pasajes adicionales con presupuesto, inspeccionar
el paquete y ejecutar una nueva evaluación vinculada al original. Mantener el
origen, la revisión de fuente, los rangos, el coste y la condición not_admitted.
No dispararlo automáticamente por acuerdo entre modelos ni por un umbral elegido
tras ver resultados. Después probar esa interfaz con nuevos casos reservados.

## Ejecución y evidencia

8 llamadas reales, cero reintentos o fallos. GLM solicitado/reportado glm-5.3-flash:
6330 tokens de entrada y 480 de salida, 6810 total, 13.475 s sumados.
Jev solicitado/reportado jev-1.13.0: 7348 de entrada y 182 de salida, 7530 total,
1.186 s sumados. No se verificó el cargo monetario.

432 tests pasan, incluidos dos nuevos que comprueban consulta sin oráculo,
revisión y rangos literales, y presupuesto insuficiente distinguido de ausencia.
Se reprodujo la selección y se verificaron inputs congelados, peticiones y salidas.
No hubo revisión independiente. No se alteraron contratos existentes del producto.

[Protocolo](../experiments/retrieved-expansion-v1/README.md),
[selecciones](../experiments/retrieved-expansion-v1/selection.json),
[resultados](../experiments/retrieved-expansion-v1/result-01.json).
Fuente: QASPER v0.3, Dasigi et al., representación textual del corpus CC-BY 4.0;
no se verificó el PDF editorial. Inputs completos locales ignorados; recibos y
hashes publicados, sin duplicar el texto documental completo.
