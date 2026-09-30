# Comparación con candidato derivado y control de omisión

**Resultado: las dos revisiones coinciden con las expectativas del productor.**
El control tiene tres omisiones detectadas; el candidato real derivado cubre los
cuatro requisitos. Es evidencia acotada a esta rúbrica, no exhaustividad global.

| Caso | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| Control: sólo SemEval-2018 | covered | missing | missing | missing |
| Candidato real con referencias reparadas | covered | covered | covered | covered |

Se utilizó la CLI pública `review-rubric`, sin modificar producto, prompts o límites.
Ambos conservan `requires_review` y `rubric_completeness: not_established`.
Las expectativas quedaron fijadas antes de las llamadas. El revisor no recibió
las etiquetas ni la identidad de control/derivado. Generador y revisor usan GLM;
no se afirma revisión independiente ni adjudicación del Operador.

## Derivación explícita

La [generación original](../rubric-candidates-v1/README.md) quedó rechazada por
15.062 bytes de citas, frente a 12.000 permitidos. Esta condición nueva conserva
ese rechazo y retira tres referencias redundantes, con auditoría del productor:

- Afirmación 0: retirar abstract; la conclusión conserva el respaldo de comparación
  del modelo sobre cuatro benchmarks.
- Afirmación 1: retirar descripción general de datasets; el párrafo de resultados
  identifica el dataset irónico SemEval-2018 Task 3.A y su uso comparativo.
- Afirmación 4: retirar párrafo de resultados; la descripción general establece
  SemEval-2015 Task 11 y los tweets con formas de lenguaje figurado.

No cambió ninguna afirmación ni la lista de faltantes. Quedan ocho usos de citas,
11.041 bytes resueltos, sobre las mismas cuatro unidades únicas de 5.097 bytes.
`derivation.json` conserva IDs retirados, razones y hashes de original/derivado.
El respaldo semántico de la reducción fue revisado por el productor, sin revisión
independiente. La respuesta original y su rechazo siguen intactos.

El control conserva una cita que menciona los cuatro datasets pero sólo afirma uno:
las tres omisiones fueron detectadas pese a estar esos nombres en el texto citado.
Eso es el resultado más útil de este contraste: no se confundió contexto citado
con información expresada por la respuesta, en este caso concreto.

## Verificación, coste y alcance

`python3 experiments/rubric-candidates-derived-v1/verify.py` comprueba que únicamente
se retiraron los tres IDs declarados, valida el derivado, los hashes y las salidas.
Cero llamadas al verificar. Los dos casos coinciden en sus ocho etiquetas con lo
esperado. No se volvió a ejecutar la suite general porque no cambió producto.

Dos revisiones: 7.982 tokens. Con generación: tres llamadas, 18.963 tokens y 48,721
segundos acumulados de cliente. Coste monetario no informado. Estos totales no
incluyen las rondas anteriores de análisis de rúbrica. Se leyó toda la fuente de
34.003 bytes: no se midió ahorro frente a otra estrategia de lectura.

La pareja ya es desarrollo conocido, no una nueva reserva. La ruta autónoma falló
por exceso de citas; esta prueba demuestra el recorrido con reparación asistida.
No demuestra fidelidad general, corrección de las declaraciones de ausencia del
candidato ni completitud de los requisitos. No hubo admisión de memoria.

## Siguiente incremento recomendado

Prevenir exceso de referencias antes de aceptar la salida, conservando las
asociaciones afirmación-evidencia y el rechazo original cuando corresponda. Evaluar
una estrategia de citas más económica con el mismo límite; no cambiar el cómputo
ni subir presupuestos para convertir este fallo en éxito. Después contrastar lectura
selectiva frente a completa en una nueva fuente reservada, incluyendo el coste de
revisiones y reparaciones. No añadir otra ronda general de opiniones sobre la rúbrica.
