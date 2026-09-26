# Batería QASPER e idioma configurable

Estado: implementación local y preparación verificadas, 2026-09-23.
Campaña GLM: línea base ejecutada; [resultados](qasper-linea-base-01.md).
Sin publicación ni admisión a memoria.

## Idioma

`agora.routed_cli --response-language es|en`, por defecto `es`.
API: `query_routed(..., response_language='en')`. El prompt español conserva
su texto anterior; inglés sustituye únicamente la instrucción de idioma. Citas,
fuente e identificadores no se traducen. Valores desconocidos se rechazan antes
de llamar al proveedor. El presupuesto cuenta el prompt del idioma elegido.

Resultado nuevo: `agora/routed-query/v0.2`, con `response_language`. No se
reescriben receipts v0.1. Consumidores que exijan el schema anterior deben
adoptar explícitamente v0.2. El resto de CLIs mantiene su conducta anterior.
El idioma es una instrucción, no un detector o garantía del idioma producido.

## Batería construida

`src/agora/qasper.py` prepara el JSON original QASPER v0.3 sin dependencias
nuevas. `experiments/qasper-v1/prepared/pilot-01/` contiene:

- `model_inputs/`: fuentes textuales, preguntas originales y partes; sin etiquetas.
- `references/`: respuestas originales, anotaciones, párrafos y exclusiones.
- `freeze.json`: hashes de los archivos preparados; comprobados antes de exportar.

Separación lógica de archivos, no aislamiento de procesos ni control de acceso.
El futuro ejecutor sólo debe leer `model_inputs`; el evaluador lee referencias.
Los archivos descargados/preparados y las corridas permanecen ignorados por Git.

Selección determinista: primero 8 respondibles y después 4 sin respuesta, IDs
ordenados dentro de cada estrato, un artículo por pregunta. Límite de fuente:
65536 bytes UTF-8. Fuente: título, abstract, secciones y párrafos; conserva un
mapa de bytes. No se descargan ni procesan imágenes. Una pregunta original ocupa
una sola parte, sin descomposición manual guiada por respuestas.

936 preguntas elegibles; exclusiones con un motivo principal por pregunta:
211 por evidencia visual, 164 por desacuerdo de respondibilidad, 92 por evidencia
sin correspondencia única, 41 sin evidencia y 7 por tamaño. La muestra tiene
12 artículos y fuentes entre 12361 y 42614 bytes. No representa todavía fuentes
muy grandes. Se conservan las distintas respuestas de los anotadores: el filtro
resuelve sólo acuerdo sobre respondibilidad, no acuerdo semántico total.

La preparación inspeccionó esquema/anotaciones del test; no es revisión ciega.
El ejemplo leído manualmente no quedó en la muestra. No se seleccionó por salidas
del modelo y el desarrollo usó fixtures sintéticos. No usar esta muestra para
ajustar prompts y luego presentarla como evaluación inédita. La contaminación
por entrenamiento del modelo es desconocida.

## Procedencia y reproducción

Datos oficiales [QASPER v0.3](https://qasper-dataset.s3.us-west-2.amazonaws.com/qasper-test-and-evaluator-v0.3.tgz).
Ficha [Ai2/QASPER](https://huggingface.co/datasets/allenai/qasper), CC-BY-4.0
declarada; conservar atribución a Dasigi et al., NAACL 2021.
Evaluador consultado e inspeccionado: [revisión fijada](https://github.com/allenai/qasper-led-baseline/blob/afd0fb96bf78ce8cd8157639c6f6a6995e4f9089/scripts/evaluator.py).
URLs, tamaños y hashes completos: `experiments/qasper-v1/inputs/provenance.json`.
Los datos se leyeron del miembro JSON del archivo, sin extracción indiscriminada.

Desde la raíz, usando un directorio de salida nuevo:

```bash
PYTHONPATH=src python3 -m agora.qasper prepare \
  --dataset experiments/qasper-v1/inputs/test.json \
  --out /tmp/qasper-pilot-new
PYTHONPATH=src python3 -m agora.qasper export \
  --prepared experiments/qasper-v1/prepared/pilot-01 \
  --results RUTA_RESULTADOS --out PREDICCIONES_NUEVAS.jsonl
python3 experiments/qasper-v1/inputs/evaluator.py \
  --gold experiments/qasper-v1/prepared/pilot-01/references/gold.json \
  --predictions PREDICCIONES_NUEVAS.jsonl
```

El exportador comprueba fuente, pregunta, idioma, parte y citas/anclas; no
certifica autenticidad de receipts. Traduce abstención explícita a `Unanswerable`.
Un timeout, rechazo o salida ausente queda como predicción faltante, no como
abstención acertada. Las citas se mapean a párrafos originales: Evidence F1
mide aquí párrafos citados, no todos los recuperados ni entailment semántico.

## Verificación realizada

Controles sintéticos con el evaluador oficial: Answer F1/Evidence F1 = 1/1 para
respuestas correctas, 0/0 para incorrectas; ausencia = dos predicciones faltantes
con puntuación cero. No son puntuaciones de Ágora. Además, 12 consultas con fake
provider verificaron ruta completa, prompt inglés y ausencia de campos de
referencia en el payload; no comprueban comprensión del modelo.

Script reproducible: `experiments/qasper-v1/validate_local.py`.
Evidencia: `experiments/qasper-v1/runs/local-validation-01.json`.
El script usa una ruta de resultado exclusiva; para otra corrida debe nombrarse
otra salida conservando la anterior. Ninguna llamada al modelo en este incremento.

## Protocolo propuesto antes de la ejecución (conservado)

1. Congelar código, corpus y parámetros; ejecutar **12 llamadas de línea base**
   con fuente completa, GLM `glm-5.3-flash`, idioma `en`, temperatura 0,
   máximo 8192 tokens de salida, socket 90 s y proceso 110 s por pregunta.
   Fuente 65536 bytes, prompt 131072 bytes. Máximo de salida solicitado en toda
   la tanda: 98304 tokens; no es presupuesto total ni precio. Los tokens de
   entrada se registran aparte. Máximo temporal secuencial: 22 minutos más
   preparación local. Sin reintentos automáticos; detener ante credenciales,
   integridad o fallos de configuración; registrar timeout y continuar la
   siguiente pregunta según protocolo congelado.
2. Puntuar con el evaluador fijado y revisar respaldo/omisiones separadamente.
   Registrar costes y fallos de las 12, sin eliminar casos difíciles.
3. Preparar comparación pareada con recuperación y recorrido. Requiere extender
   idioma a esas rutas o unificar el consumidor; hoy el idioma configurable sólo
   está implementado en `query_routed`. No presentar una comparación multirruta
   como ya lista. Incluir coste de extracción y mismo modelo/idioma por ruta.
4. Añadir después evidencia anotada como control diagnóstico y QMSum en otra
   batería. No enviar respuestas de referencia al modelo; el control con pasajes
   anotados debe distinguirse expresamente de recuperación autónoma.

Criterio del piloto: producir una tabla por pregunta con estado, F1 de respuesta,
F1 de párrafos citados, abstención, tokens y tiempo; además revisión de fidelidad.
No fijar umbral de superioridad retrospectivamente ni declarar puntuación oficial
sobre todo QASPER. La fuente completa es el primer punto de comparación.

## Comparación posterior en artículos nuevos

[Resultados pareados](qasper-comparacion-perfiles-01.md): concise-v1 no se
promueve; sus respuestas son más cortas, pero tuvo dos rechazos, menos
abstenciones válidas y mayor consumo total. Legacy sigue por defecto.
