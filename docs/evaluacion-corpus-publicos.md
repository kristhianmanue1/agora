# Evaluación de Ágora con corpus públicos

Investigación inicial: 2026-09-23. Preparación implementada posteriormente; campaña GLM no ejecutada.
Estado actual y uso: [Batería QASPER](bateria-qasper.md).
Objetivo: medir fidelidad, omisiones y coste con referencias externas, además de
las regresiones locales. La investigación inicial no modificó código; el incremento
posterior de idioma y preparación se documenta en el enlace anterior.

## Selección crítica

| Recurso primario | Aporte | Uso recomendado y límite |
|---|---|---|
| [QASPER](https://huggingface.co/datasets/allenai/qasper), [artículo](https://aclanthology.org/2021.naacl-main.365/), [evaluador](https://github.com/allenai/qasper-led-baseline/blob/main/scripts/evaluator.py) | Artículos completos, preguntas, respuestas y evidencia; incluye preguntas sin respuesta. | Primera batería de respuesta y abstención. Conservar varias anotaciones; evidencia visual no equivale a texto recuperable. |
| [QMSum](https://github.com/Yale-LILY/QMSum) | Reuniones, consultas generales/específicas, resúmenes humanos y rangos relevantes para consultas específicas. | Segunda batería de síntesis y omisiones. Las consultas generales no tienen esos rangos; ROUGE no demuestra fidelidad. |
| [ALCE](https://github.com/princeton-nlp/ALCE) | Código y datos para evaluar corrección y calidad de citas. | Adoptar distinción entre corrección de respuesta, precisión y cobertura de citas. Sus jueces automáticos también pueden equivocarse. |
| [LongBench v1](https://github.com/THUDM/LongBench/tree/main/LongBench), [v2](https://github.com/THUDM/LongBench) | Tareas de contexto largo; v1 incluye QASPER/QMSum y evaluación de compresión. V2 usa opción múltiple. | Escala posterior. No contar QASPER y su subconjunto LongBench como evidencia independiente. V2 no sustituye evaluación de síntesis ni citas. |
| [WikiContradict](https://arxiv.org/abs/2406.13805), [ConflictBank](https://github.com/zhaochen0110/conflictbank) | Conflictos documentales reales y conflictos entre conocimiento recuperado e interno. | Ampliación adversarial. No equivalen exactamente a preservar dos cifras sin precedencia; adaptar y etiquetar cualquier cambio de tarea. |

QASPER declara CC-BY-4.0 en su ficha; QMSum y ALCE muestran MIT en sus repositorios.
Antes de incorporar archivos, fijar revisión y conservar licencias/atribución del
material concreto, distinguiendo datos y código. No se instaló software externo.

## Piloto propuesto: pequeño, reproducible y sin fuga de respuestas

1. Empezar con 12 preguntas QASPER: 8 respondibles con evidencia textual y 4
   sin respuesta, si las anotaciones permiten esa selección sin ambigüedad.
   Selección determinista por ID dentro de estratos fijados, nunca por resultados.
   Registrar exclusiones por figuras/tablas, desacuerdo y tamaño; no extrapolar
   los resultados textuales a lectura visual. Es una muestra diagnóstica.
2. Preparar adaptación en desarrollo; congelar preguntas de evaluación de otra
   partición, sin solapamiento de documentos. Un benchmark público puede haber
   estado en el entrenamiento del modelo: holdout local no elimina contaminación.
3. Comparar, con el mismo GLM y configuración, fuente completa cuando quepa,
   recuperación lexical actual y recorrido/extracción. Una ruta sin presupuesto
   se registra como no ejecutable, sin truncar silenciosamente el documento.
4. Añadir un control con evidencia anotada suministrada directamente: diagnostica
   síntesis, pero no cuenta como recuperación exitosa. Las respuestas de referencia
   nunca entran al prompt; los pasajes anotados sólo entran a ese control explícito.
5. Conservar documento original, transformación textual, mapa de párrafo a bytes,
   revisión, hashes, pregunta, referencias, parámetros y resultado de cada intento.
   Mantener las etiquetas fuera de los archivos que consume el proveedor.
6. Añadir luego 6 consultas QMSum (3 generales y 3 específicas) como batería
   separada. No mezclar puntuaciones de QA y resumen en una media opaca.

## Corrección necesaria antes de comparar

La instrucción actual de `routed_query` exige respuestas en español. QASPER y
QMSum son referencias en inglés. Para evaluación comparable, hacer configurable
el idioma conservando español por defecto, y ejecutar la rama inglesa con
fuentes/referencias originales. Traducir el benchmark crea una variante y requiere
revisión propia; no permite atribuirle directamente las puntuaciones oficiales.
Una pregunta original se conserva como una parte; descomponerla manualmente con
conocimiento de la respuesta daría pistas y debe registrarse como otra condición.

## Qué medir

- Respuesta: métrica oficial de la versión fijada y revisión de afirmaciones.
- Recuperación: precisión/recobrado de párrafos de evidencia, según anotaciones;
  no confundir párrafo recuperado con todos los hechos conservados.
- Abstención: aciertos ante ausencia y abstenciones erróneas ante presencia.
- Citas: literalidad/anclas y respaldo semántico, evaluados por separado.
- Síntesis: hechos requeridos conservados/omitidos y afirmaciones sin respaldo.
  La rúbrica de hechos se fija antes de ver la salida, como evaluación adicional.
- Operación: rechazos de formato, timeouts y rutas no ejecutadas, sin descartarlos
  de los denominadores de éxito extremo a extremo.
- Coste: tokens totales de extracción, síntesis y revisión; tiempo total; lecturas
  repetidas y coste inicial frente al amortizado sobre un número declarado de
  consultas. Tokens de intentos sin recibo permanecen desconocidos.

Fijar límite de llamadas/tokens/tiempo antes de ejecutar el piloto. Detener el
caso al agotarlo, sin reintento automático. Informar diferencias pareadas por
pregunta; una muestra pequeña no demuestra superioridad general.

## Autorrevisión adversarial

Un corpus publicado aporta referencias compartidas, no verdad infalible. Una
cita literal puede respaldar mal la afirmación; un resumen similar puede omitir
una condición decisiva; un juez LLM puede repetir el error del productor.
Conservar casos españoles locales y el documento real como regresiones separadas.
Comparar principalmente Ágora frente a fuente directa con el mismo modelo; las
puntuaciones de artículos sólo son comparables al reproducir versión, partición,
contexto, idioma y métrica. No afirmar posición de leaderboard con este piloto.

## Resultado local que precede a la batería

N2 pasó en `routed-query-v1/runs/glm-02-n2`: 1030 tokens, 10,747 s, dos importes
preservados, autor de aprobación desconocido y condición de pago conservada.
Autorrevisión, un caso sintético conocido; el timeout previo sigue registrado.

Próximo incremento recomendado: adaptador QASPER y validación local del evaluador
con controles correctos/incorrectos, sin lanzar aún una campaña masiva. Después,
congelar muestra y presupuesto y ejecutar la comparación acotada.
