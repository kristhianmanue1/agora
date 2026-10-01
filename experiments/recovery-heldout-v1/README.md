# Batería reservada local: recuperación y fidelidad

Dos documentos QASPER nuevos según inventario local, seleccionados por orden de
hash antes de generación: 1901.05389 y 1909.00871. Se excluyeron documentos hallados
en archivos locales de experimentos de hasta 2 MB; esto no garantiza ausencia de
exposición fuera de ese inventario ni en entrenamiento. La rúbrica deriva de la
primera anotación humana del dataset, sin adjudicación independiente adicional.

Parámetros congelados: inicial 8.000 bytes/top-k 4; recuperación 12.000/top-k 3,
hasta tres párrafos siguientes, consulta idéntica a la pregunta original. Generación
GLM con 4.096 tokens, revisión de rúbrica con 2.048; Jev por afirmación y citas.
Máximo 12 llamadas; no reintentos, reparaciones, cambio de rúbrica ni reselección.

## Resultado observado

| Caso | Fuente / lectura (bytes) | Cobertura GLM | Recuperación | Fidelidad Jev |
|---|---:|---|---|---|
| Modelos de referencia | 35.980 / 7.153 | 2/2 | no_expansion | 1/1 supported |
| Mitigación de sesgo | 30.272 / 7.320 | 2/2 | no_expansion | 5/6 supported; C6 insufficient |

Seis llamadas, 16.508 tokens reportados. Sin precio monetario ni latencia total
medidos. La lectura local del recuperador inspecciona la fuente entera; los bytes
seleccionados no representan ahorro medido de disco ni coste total. Sin brazo de
lectura completa no hay comparación de ahorro con calidad equivalente.

Ambas respuestas iniciales cubrieron la pequeña rúbrica según GLM; ninguna activó
recuperación. Esta batería comprueba la parada sin ampliación en dos casos reales,
pero **no estima eficacia de recuperación ante omisiones en documentos nuevos**.
No sustituimos casos para obtener un resultado favorable.

## Discrepancia abierta

C6 del segundo caso atribuye a los métodos comparados dependencia de listas y pares
de palabras de género, imposición de un binario y problemas con términos como
manager. Su cita incluye esas ideas, pero Jev clasifica el conjunto como insufficient
(probabilidades reportadas: 0,61 insufficient y 0,38 supported). El formato choice
no aporta explicación: no se identifica una causa ni se declara error del generador
por ese voto solo. Se conserva el texto y su cita en `result.json` para adjudicación.

La rúbrica pregunta por WED/CDA; no juzga cada afirmación adicional. Por ello 2/2
requisitos y una afirmación insuficientemente respaldada no son resultados
contradictorios. La respuesta no debe aceptarse automáticamente sólo por cobertura.

## Verificación y continuación

Diez pruebas existentes de recuperación pasaron; tres controles quedan registrados
en `controls.json`: sin omisiones, presupuesto insuficiente y revisión incierta o
contradictoria. Son controles sintéticos del productor, no validación semántica.
`verify.py` reconstruye propuestas y verifica hashes, etiquetas y citas evaluadas.
Los archivos completos en inputs/runs se conservan localmente y no se publican;
la reproducción real requiere esos artefactos. No hubo cambios de producto ni
promoción de defaults, integración o admisión de memoria.

Siguiente: adjudicar C6 con sus citas y contexto; después un protocolo separado de
omisión controlada en fuentes nuevas, con casos y criterios fijados antes de ejecutar.
Ese reto debe etiquetarse como omisión inducida, separado de la frecuencia natural
de fallos. Conservar esta batería sin reescribirla.
