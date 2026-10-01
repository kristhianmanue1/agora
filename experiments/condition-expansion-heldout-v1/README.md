# Validación externa al caso de desarrollo: ampliación aún insuficiente

**Decisión: conservar como experimental; no promover a default.** La heurística
congelada mejora cobertura de 1/4 a 2/4 requisitos en una fuente nueva, pero omite
ΔG y ΔS. Un control sintético también demuestra ampliación irrelevante.

## Selección y condiciones

QASPER `2004.04498`, 34.030 bytes; pregunta “What metrics are used to measure bias
reduction?”. Primer caso elegible según ranking SHA-256 de semilla fija, excluyendo
identificadores del inventario local previo. La selección ocurrió antes de ejecutar
la expansión o recibir salidas de modelos; no se sustituyó el caso. La reserva es
local, no afirmación sobre exposición en entrenamiento. Muestra restringida a fuentes
30–60 KB y preguntas respondibles con varias referencias extractivas.

Rúbrica del productor basada en la primera anotación humana: Accuracy, ΔG, ΔS, BLEU.
BLEU es control de calidad de traducción, no medida directa de sesgo; las respuestas
mantienen esa distinción. La rúbrica no se mostró al generador ni al selector.

La misma pregunta produce selección inicial léxica (presupuesto 8.000, top-k 4), y
la función congelada de `condition-expansion-v1` añade como máximo dos párrafos
hasta 10.000 bytes. Se conserva hash del selector; no hubo tuning, reintentos,
reparación, aumento de presupuesto o cambio de criterios tras observar resultados.

## Resultados reales

| Medida | Inicial | Ampliada |
|---|---:|---:|
| Bytes enviados al generador | 3.735 | 5.162 |
| Bytes de citas, contando usos | 5.908 | 4.381 |
| Requisitos cubiertos | 1/4: BLEU | 2/4: Accuracy y BLEU |
| Afirmaciones respaldadas según Jev | 4/4 | 3/3 |
| Tokens: generación y dos revisiones | 8.414 | 7.852 |
| Segundos acumulados de llamadas | 38,966 | 38,709 |

Ambos candidatos originales son estructuralmente válidos, con citas dentro de
presupuesto, sin reparación. Ninguno declara faltantes pese a las omisiones de
rúbrica; la revisión de cobertura sí las detecta. Los párrafos que definen ΔG y ΔS
existen en la fuente y no se solapan con ninguno de los contextos entregados.
La brecha se origina en recuperación; el generador además no reconoce aquí su
insuficiencia. No se confunde respaldo de lo dicho con cobertura de lo necesario.

El selector añadió un párrafo de resultados que menciona WinoMT accuracy y otro
sobre el conjunto WinoMT. La mejora no incluye las definiciones de las otras dos
métricas. Menos tokens en el brazo ampliado no demuestra eficiencia general:
cambiaron longitud de salida y trabajo de revisión; es una sola ejecución por brazo.
Seis llamadas, 16.266 tokens. Precio monetario y coste de preparación humana no
medidos. El recuperador sigue leyendo el archivo entero localmente.

## Controles sin red

| Control | Esperado | Observado |
|---|---|---|
| Sin señal de excepción | No añadir | No añade |
| Exclusión explícita relevante | Añadir | Añade |
| Exclusión fuera de presupuesto | Preservar inicial, registrar descarte | Cumple |
| Detalle irrelevante con “only” | No añadir | **Añade: falso positivo** |

Los controles son del productor, pequeños y sintéticos; no se presenta 3/4 como
estimación estadística. `controls.json` conserva el resultado contrario a lo esperado.
No detectar señales sigue significando búsqueda inconclusa, nunca “no hay excepciones”.

## Verificación y estado

`python3 experiments/condition-expansion-heldout-v1/verify.py` reproduce selección
ampliada, controles, fuentes, candidatos originales, offsets y vínculos de revisores,
y comprueba que las dos definiciones faltantes están fuera de los pasajes entregados.
Cero HTTP. La auditoría documental comprueba referencias locales. Artefactos completos
en directorios locales ignorados; respuestas y hashes en `result.json`. No cambió
`src/agora`, la CLI, los defaults ni la memoria. Suite general no repetida porque
no cambió código de producto; no se presenta la validación semántica como aprobada.

## Estado del plan y siguiente incremento

- CLI y trazabilidad: disponibles para el piloto.
- Límites y conservación de fallos: verificables en los recorridos ejercitados.
- Cobertura y fidelidad: controles separados, aún con rúbricas limitadas y juicios
  probabilísticos; no constituyen aceptación automática.
- Recuperación eficiente: ahorro observado en otros casos, generalización pendiente;
  la heurística de condiciones es auxiliar, no solución suficiente.
- Skopos/AN-KLA y memoria completa: no se activaron integraciones ni consolidación.

Siguiente paso: conectar un resultado de cobertura incompleta con una propuesta
explícita de nueva recuperación. Buscar definiciones de la información pedida y
condiciones relevantes, no sólo palabras de exclusión. Registrar presupuesto restante,
pasajes nuevos y qué carencias se intentan resolver. Si no mejora o agota el límite,
terminar con alcance parcial o proponer lectura completa. Probar primero esta brecha
como regresión conocida y después otra fuente reservada, sin usar respuestas oro
como términos ocultos de búsqueda ni afinar sólo para ΔG/ΔS.
