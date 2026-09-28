# Resultado del piloto de cuestiones abiertas

Ejecución glm-01 completada el 27 de septiembre de 2026, desde Ágora d92ce22
más los archivos experimentales locales congelados en el manifiesto de la ejecución.
Seis escenarios sintéticos, dos momentos y dos brazos; 24 llamadas reales a
GLM, modelo solicitado y reportado `glm-5.3-flash`, sin reintentos ni consumo
 desconocido. No se enviaron transcripciones ni audio reales.

## Resultado

| Métrica | Todas las fuentes (`full`) | Fuentes + evaluación anterior (`tracked`) |
|---|---:|---:|
| Evaluaciones completadas | 12 | 12 |
| Valores según gold | 12/12 | 12/12 |
| Derivados afectados según gold | 12/12 | 12/12 |
| Estado según gold | 10/12 | 12/12 |
| Relación según gold | 9/12 | 10/12 |
| Coincidencia conjunta literal | 7/12 | 10/12 |
| Cierres indebidos observados | 0 | 0 |
| Tokens totales reportados | 20708 | 19705 |
| Tiempo sumado de llamadas (s) | 279.400 | 243.354 |

Total: 40413 tokens y 522.754 segundos sumados de transporte. No se calculó
coste monetario. Estas diferencias no prueban ahorro general ni causalidad.
La etapa inicial usa prompts idénticos entre brazos: sus diferencias son
variabilidad de ejecuciones, no efecto de memoria.

Ambos brazos conservaron el responsable faltante; no adoptaron la fecha de
otro proyecto; rechazaron la copia como corroboración independiente; aplicaron
el cambio legítimo; reabrieron el pendiente tras retirar la única fecha y
señalaron el aviso dependiente para revisión. Este último es sólo un ID devuelto:
no se cambió un documento real ni se propagó una invalidación persistente.

Los valores y explicaciones se contrastaron manualmente con los fixtures.
Autorrevisión del productor, no adjudicación independiente. Todas las citas
pasaron comprobación literal; esta comprobación no establece soporte semántico.

## Autorrevisión adversarial del método

1. **Categorías insuficientemente definidas.** `clarification` y `update` se
   solapan si no se define que update exige un valor previo distinto. El modelo
   llamó update a completar una fecha ausente. También hubo partial/update.
2. **Caso irrelevante mezclado.** c2 habla de Brisa pero además reitera que Alba
   sigue pendiente. `irrelevant` y `clarification` son interpretaciones posibles.
3. **Estado y corroboración mezclados.** En duplicate, full usa partial con
   date=null; tracked usa open. Ambos reconocen correctamente un único origen.
   La rúbrica no definió si parcial se refiere a campos llenos o a respaldo.
4. **Dependencias y criterios declarados.** No se evalúan descubrimiento de
   pendientes, recuperación, resolución de identidad, autoridad autenticada,
   dependencias transitivas, concurrencia ni resistencia a grandes corpus.
5. **Una repetición, un productor del gold.** No hay estimación de fiabilidad,
   holdout ni revisión independiente. Los criterios explícitos facilitan casos.
6. **Historial correcto o casi correcto.** No se inyectaron evaluaciones
   anteriores falsas: no se demostró resistencia al arrastre de errores.

Se preservan gold, prompts, intentos y discrepancias sin corregir resultados
retroactivamente. El conteo 7/12 frente a 10/12 NO respalda superioridad.
Resultado de los comportamientos sustantivos: favorable en estos casos.
Resultado comparativo: inconcluso. No adoptar estas etiquetas como contrato estable.

## Próximo incremento propuesto

Separar `observed_value`, `support_status` y `missing_requirements`; derivar el
estado operativo mediante reglas explícitas. Definir la relación respecto de
una afirmación o campo, permitiendo varias relaciones en una misma fuente.

Antes de ampliar: corregir la especificación en una nueva versión, congelar gold
nuevo y casos no usados para ajustar el prompt; incluir historial previo erróneo,
fuente tardía de un periodo anterior, una refutación parcial y un derivado sin
afectación. Mantener la lectura completa como referencia. No decidir todavía
base de grafos, motor persistente, integración o admisión AN-KLA.

## Reproducción y archivos

- `build_cases.py`, `cases.json`, `gold.json`: fixtures y expectativas congeladas.
- `protocol.py`: prompt y validador de forma/referencias.
- `run.py`: ejecución limitada, sin reintentos, con historial por caso.
- `audit.py`: comprobación posterior de manifiesto y comparabilidad de entradas.
- `result-glm-01.json`: resultados sintéticos, dictámenes y manifiesto.
- `runs/glm-01/`: peticiones, respuestas y código congelado; ignorado por Git.

Comandos locales (sin llamadas al proveedor):

```bash
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests
PYTHONDONTWRITEBYTECODE=1 python3 experiments/open-issues-v1/audit.py experiments/open-issues-v1/runs/glm-01
```

Validación local: 310 tests pasan, incluidos cinco controles nuevos. El primer
comando de suite omitió PYTHONPATH=src y falló por importación; el comando
corregido pasó. Manifiesto verificado y doce pares con mismas fuentes/prompt,
salvo la evaluación previa del brazo tracked en su segunda etapa.

No se modificó código productivo, AGENTS.md, datos reales ni memoria AN-KLA.
