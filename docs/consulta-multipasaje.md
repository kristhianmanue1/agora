# Consulta de múltiples pasajes — incremento local

Estado 2026-09-22: consumidor y comparación de recuperación implementados;
comparación de respuestas GLM **parcial**, detenida por dos errores HTTP.
No hay integración Skopos/AN-KLA ni admisión automática. El estado local inicial
fue sin commit; el Operador autorizó posteriormente commit y push el 2026-09-22.
La publicación del código no completa la comparación semántica pendiente.
Los directorios runs/ conservan evidencia local excluida de la publicación.

## Capacidades y fronteras

`agora.passages.query_passages` consume el proveedor de archivos del incremento1,
conserva fuente/revisión/rangos y genera como máximo una solicitud. Tres rutas:

- `source`: fuente completa, dentro de un presupuesto explícito.
- `reference`: rangos preseleccionados por el llamador; control diagnóstico.
- `retrieve`: coincidencia de palabras en párrafos (casefold, términos >2caracteres
  y lista pequeña de palabras comunes). Orden por número de términos distintos
  compartidos y posición; hasta tres semillas, vecinos si caben en presupuesto.

La recuperación recorre texto completo localmente. No embeddings, modelo de
búsqueda ni ampliación adaptativa después de una respuesta insuficiente. No elimina
acentos ni detecta sinónimos. Un párrafo demasiado grande se omite y se informa.
La expansión de vecinos es fija; puede agregar contexto irrelevante o perderlo.
No se afirma recuperación exhaustiva de significado ni preservación de conflictos.

`agora/passage-query/v0.1` es un esquema nuevo. Mantiene prompt, selección, respuesta
estructurada recibida, procedencia de citas y estados. No modifica/reinterpreta
`source-query/v0.3`; `agora.review` anterior aún no acepta este formato. La revisión
actual se hace contra JSON y fuente. No se presenta una ejecución nueva como legado.

Las citas deben existir enteras en un pasaje: no se admiten uniones artificiales
entre pasajes ni metadatos de localización como evidencia. Se registran rangos
UTF-8 del original, primera coincidencia por cada pasaje que contiene la cita;
no prueba cuál usó el modelo ni soporte semántico de la afirmación.
Los resultados conservan `review_status: unreviewed`, `semantic_support:
not_verified`, `memory_admission: not_performed`.

## Uso explícito con proveedor

Desde raíz, con fuente autorizada para transmisión y ZAI_API_KEY en entorno:

```bash
PYTHONPATH=src python3 -m agora.passage_cli \
  --source fuente.txt --source-id documento-1 --sha256 HASH \
  --question '¿Qué plazos constan?' --mode retrieve \
  --content-budget 1800 --prompt-budget 65536 \
  --model glm-5.3-flash --max-output-tokens 2048 --timeout-seconds 90 \
  --out nueva-corrida
```

`reference` requiere uno o más `--range INICIO:FIN`; otros modos los rechazan.
Para `source`, aumentar explícitamente `--content-budget` para toda la fuente.
La CLI sí transmite contenido al proveedor; no es un comando de lectura local.

Separa máximo del archivo (proveedor16MiB), contenido (consumidor hasta4MiB), JSON
del envelope (8MiB) y prompt (system+user, no envoltorioHTTP). Ninguno equivale a
un presupuesto en tokens. El límite de contexto del modelo no se infiere de bytes.
La búsqueda admite fuente hasta4MiB y65536párrafos, con límites adicionales del
inventario/envelope heredados; no garantiza que cualquier fuente bajo4MiB quepa
con cualquier metadato o escape. Si excede, rechaza antes del modelo.

## Estados y fallos

- `no_retrieval_candidates`: búsqueda sin coincidencias; cero llamadas.
- `retrieval_budget_exhausted`: hubo coincidencias, ninguna cabía; cero llamadas.
- `not_found_in_supplied_material`: abstención del modelo sobre lo suministrado;
  no demuestra ausencia global, incluso cuando leyó toda la fuente.
- `candidate`: respuesta estructuralmente válida, pendiente de revisión semántica.
- `rejected` / `failed`: fallo conservado; no equivale a respuesta válida.

Estos estados completan una operación, no necesariamente satisfacen la pregunta.
Una falta de candidatos no es una respuesta correcta por sí misma.
Si falla proveedor, se conserva selección/prompt y tipo de error. Para HTTPError,
la versión actual guarda código HTTP, nunca cuerpo, URL ni motivo potencialmente
sensible. Los intentos históricos glm-01 sólo guardaron el tipo HTTPError; su
código concreto es desconocido y no se reconstruye por inferencia.
JSONHTTP inválido o respuesta excesiva no conservan el cuerpo bruto: no se puede
adjudicar semánticamente ese contenido perdido. No se almacena reasoning_content.

La CLI usa un destino nuevo; archivo de resultado no garantiza escritura atómica.
El timeout90s limita operaciones socket, no tiempo total. El runner experimental
impone110s al subproceso; tras deadline el resultado del proveedor es desconocido,
no se reintenta ni se presume que no hubo consumo remoto.
Hashes tomados antes/después detectan deriva durante ejecución. El piloto además
corre una copia congelada; hashes por sí solos no autentican proceso/proveedor.

## Verificación

99 pruebas locales OK:87previas+12 del consumidor. Cobertura: evidencia distante,
citas en bytes UTF-8, límites de prompt, fuente cambiada, búsqueda vacía vs
presupuesto insuficiente, citas que cruzan pasajes/metadatos, abstención acotada,
fallos de proveedor y códigoHTTPsin detalles sensibles. Transporte real probado
sólo hasta los erroresHTTPdescritos, no éxito del proveedor.

## Comparación reproducible y resultado observado

`experiments/passage-comparison-v1/` conserva corpus sintético14.543bytes,
cinco preguntas/rangos/criterios y protocolo previo. Corpus conocido por productor,
sin holdout, con distractores repetidos: diagnóstico, no generalización.

Diagnóstico sin proveedor:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 \
  experiments/passage-comparison-v1/check_retrieval.py \
  --out experiments/passage-comparison-v1/runs/nuevo-local/retrieval.json
```

| Caso | Pasajes de referencia presentes en recuperación | Bytes entregados |
|---|---|---:|
| Q1 plazos contradictorios | Sí |628|
| Q2 responsable y partida distante | Sí |716|
| Q3 formulación con sinónimos | No; cero candidatos |0|
| Q4 importe no documentado | Sí, párrafo sobre Lago |714|
| Q5 responsable local | Sí |716|

Source y reference contienen los rangos esperados en5/5. Eso es cobertura de
rangos fijados, no cinco respuestas correctas. EnQ4recuperar el párrafo de Lago
no demuestra ausencia de importe fuera de él. Q3expone debilidad léxica y no puede
contarse como ahorro logrado gracias a abstención. No se cambió el recuperador
para acertar esta pregunta después de verla fallar.

El ensayoGLMglm-01 ejecutó sólo Q1-source y Q1-reference: ambos HTTPError, una
solicitud por ruta, código HTTP no conservado, uso/modeloefectivo desconocidos.
El runner paró tras dos fallos consecutivos. No se ejecutaron las otras13rutas
ni se reintentó. Código/entradas congelados, tiempos y errores en runs/glm-01.
Sin respuestas útiles, no hay comparación de fidelidad ni tokens/coste real.
La ausencia de usage no prueba consumo cero. No atribuimos causa alHTTPError.

Los resultados locales están ignorados en Git. El reporte local de recuperación
incluye hashes y el ensayoGLMsu freeze.json. Cambios posteriores para registrar
códigosHTTPno se atribuyen a las dos llamadas anteriores.

Revisión separada review_large_source_plan condicionó avance a congelar el código,
medir tiempo y limitar interpretaciones. Se ejecutó copia congelada y se mantuvo
la parada. No es auditoría externa. Próximo paso: diagnosticar acceso/proveedor y
fijar una nueva corrida antes de intentar comparación semántica. No hay promoción
de la ruta automática ni afirmación de fidelidad o ahorro de tokens.
