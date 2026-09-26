# QASPER: comparación de perfiles en artículos nuevos

2026-09-23. Corrida `experiments/qasper-v1/runs/glm-paired-01`.
**Resultado: no promover concise-v1.** Legacy permanece por defecto y concise-v1
experimental, opt-in. No hubo cambios de producto durante la tanda.

## Método

12 artículos nuevos, sin solapamiento con los 12 anteriores; también se excluyó
el artículo usado para inspeccionar el esquema. Selección por ID: ocho preguntas
respondibles y cuatro sin respuesta, una por documento, mismos filtros textuales.
24 consultas, una por perfil/pregunta, orden alternado del primer perfil.
GLM solicitado y reportado glm-5.3-flash; idioma en; temperatura 0; fuente completa
hasta 65536 bytes; prompt 131072 bytes; salida 8192 tokens; socket 90 s; proceso
110 s. Sin reintentos, reparaciones ni ajustes durante la evaluación. Los rechazos
previstos continuaron al siguiente caso y cuentan como predicciones faltantes.

## Balance completo

| Medida | legacy | concise-v1 |
|---|---:|---:|
| Salidas aceptadas | 12/12 | 10/12 |
| Rechazos | 0 | 2 |
| Timeouts | 0 | 0 |
| Abstenciones válidas en cuatro ausencias | 3/4 | 2/4 |
| Abstenciones indebidas en ocho respondibles | 0/8 | 0/8 |
| Answer F1 /100 | 43,50 | 36,87 |
| Evidence F1 /100 | 58,89 | 51,55 |
| Tokens reportados | 66693 | 69123 |
| Segundos de procesos | 197,991 | 181,826 |
| Caracteres de answer en ocho respondibles | 3331 | 2372 |

Answer es 28,79% más corto en el grupo respondible, pero el consumo total sube
3,64%. Instrucciones, explicación y citas también consumen tokens. El tiempo
menor observado no demuestra ventaja estable: hubo caché, una llamada legacy
tardó 67 s y sólo hay una repetición. Total: 135816 tokens, 379,817 s, sin incluir
preparación/revisión; no se calculó coste monetario.

F1 mide similitud textual/coincidencia de párrafos, no porcentaje de verdad.
En las ocho respondibles Answer F1 pasa de 27,74 a 30,30; globalmente empeora.
El desglose oficial none=1.0 de concise excluye predicciones faltantes de la media
por tipo: no significa 4/4 abstenciones. La cuenta de entrega correcta es 2/4.

| Caso | Answer F1 legacy | Answer F1 concise | Evidence F1 legacy | Evidence F1 concise |
|---|---:|---:|---:|---:|
| case-01 | 24.00 | 26.09 | 33.33 | 33.33 |
| case-02 | 26.67 | 25.81 | 33.33 | 40.00 |
| case-03 | 62.57 | 53.75 | 66.67 | 66.67 |
| case-04 | 53.33 | 57.14 | 66.67 | 50.00 |
| case-05 | 15.75 | 17.02 | 33.33 | 28.57 |
| case-06 | 21.05 | 32.43 | 40.00 | 66.67 |
| case-07 | 6.45 | 9.09 | 66.67 | 66.67 |
| case-08 | 12.12 | 21.05 | 66.67 | 66.67 |
| case-09 | 100.00 | 0.00 | 100.00 | 0.00 |
| case-10 | 0.00 | 0.00 | 0.00 | 0.00 |
| case-11 | 100.00 | 100.00 | 100.00 | 100.00 |
| case-12 | 100.00 | 100.00 | 100.00 | 100.00 |

## Hallazgos

Caso 09, definición de edge weights: legacy se abstiene. Concise construye una
respuesta a partir de usos y altera puntuación de una cita; rechazo
answer_quote_mismatch. No se corrigió ni normalizó después.

Caso 10, magnitud de mejora en Nigerian Pidgin: legacy dice que no hay cifra,
pero marca answer (incumple abstención, sin inventar una magnitud). Concise se
abstiene en contenido pero omite quotes=[]; rechazo invalid_concise_answer_shape.
La intención semántica no equivale a entrega válida. Casos 11/12: ambas variantes
se abstienen conforme a las anotaciones.

Los ocho casos positivos conservan los datos centrales en autorrevisión. No se
certifica cada afirmación: concise añade, por ejemplo, afirmaciones de ausencia
global que sus citas no prueban por sí solas. Tampoco garantiza minimalidad:
una respuesta sigue teniendo 727 caracteres.

## Evidencia

En la corrida: protocol.json, freeze.json, execution.json, scores.json, review.json
y respuestas por perfil. Scripts: run_comparison.py y score_comparison.py.
Datos/resultados completos ignorados por Git; referencias fuera del payload.
180 pruebas locales pasaron. Verificados ambos corpus, disjunción, código congelado
y 24 hashes de resultados. Evaluador oficial fijado sin modificaciones.
Autorrevisión del productor, no auditoría independiente. Muestra diagnóstica, una
generación por condición, contaminación de entrenamiento desconocida; no es el
resultado oficial de QASPER completo. Prompt y contrato cambiaron juntos: no se
atribuye el resultado a una sola modificación.

## Recomendación

Mantener legacy por defecto. Primero comprobar si el endpoint de GLM permite
imponer un schema de salida realmente validado por el proveedor; esa capacidad
no se ha comprobado. Si existe, probarla con controles de campos obligatorios,
abstención y citas, conservando el validador local. Si no, diseñar un mecanismo
explícito con costes registrados; no inventar campos ni aceptar salidas inválidas.

Separar los experimentos de formato, concisión y abstención. Afinar con desarrollo
y evaluar después en otra muestra disjunta. Estas dos baterías ya son regresiones
observadas. Recuperación/extracción y fuentes mayores siguen sin comparación.
Sin commit, push ni escritura AN-KLA.
