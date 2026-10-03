# Consulta de múltiples pasajes — incremento local

> Alcance temporal: este documento conserva el incremento y sus resultados originales. Para capacidades y pendientes actuales, consultar [estado actual](estado-actual.md). Las cifras y próximos pasos de corridas anteriores no se reinterpretan como estado presente.

Actualización: la comparación posterior `glm-02` sí se completó; resultados y
límites en [comparacion-multipasaje-glm-02.md](comparacion-multipasaje-glm-02.md).
El estado de interrupción descrito abajo corresponde a la primera corrida.

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

## Protección explícita del alcance (v0.3)

Añadir `--scope-guard` activa `agora/passage-query/v0.3`. Si la lectura es parcial,
una respuesta queda `candidate_requires_expansion` y `requires_expansion: true`.
No cerrar una conclusión sobre la fuente completa con ese resultado. Ampliar con
una nueva invocación explícita, por ejemplo `--mode source --scope-guard`, fijando
el mismo hash y presupuestos suficientes. No se envía una segunda llamada automática.

`answer_scope` distingue `selected_passages` y `full_source`;
`document_absence_established` permanece false. Ni leer todo ni resolver citas
certifica soporte semántico. Sin el flag se conservan v0.1/v0.2. El código de salida
cero indica finalización de la operación, no aceptación de la respuesta.

[Ensayo de recuperación y límites](../experiments/scope-vigency-repair-v1/README.md).

### Desde la CLI de pendientes

El comando `generate-plan` también admite `--scope-guard`, tanto con
`--citation-mode literal` como `--citation-mode ids`. Muestra `requires_expansion`,
`reading_budget_bytes` del plan verificado y la política de ampliación explícita.
La ausencia de pasajes no dispara una llamada ni demuestra ausencia documental.
No se inicia automáticamente reading-route ni generate-recovery.


## Identificadores y respuesta acotada (opción v0.4)

En `agora.passage_cli`, añadir `--citation-mode ids` activa
`agora/passage-query/v0.4`. El modo `literal` sigue siendo el predeterminado.
La opción reutiliza `build_units` y `validate_ids`: el modelo selecciona unidades
por identificador y el consumidor resuelve texto literal y offsets UTF-8.
No convierte pertenencia a la fuente en respaldo semántico comprobado.

Ejemplo: en la invocación anterior conservar fuente, hash, pregunta y presupuestos,
añadir `--citation-mode ids` y usar un directorio `--out` nuevo. Cada ejecución
permite una llamada, sin reparación ni segunda lectura automática. La credencial
se entrega mediante el entorno, preferentemente con Llavero.

El contrato nuevo devuelve `parts` con `claims`, `missing` y citas resueltas.
Límite verificable: seis afirmaciones, cuatro faltantes y 2.000 caracteres totales
de texto de afirmaciones y faltantes. No cuenta las citas resueltas en ese límite;
sí conserva sus presupuestos separados (12 ocurrencias y 12.000 bytes por aspecto).
Una respuesta truncada, un ID desconocido/duplicado o un exceso se rechaza, sin
recortar ni salvar silenciosamente el resultado.

El control de alcance está incluido aunque no se pase `--scope-guard`:
`candidate_requires_expansion` para respuestas a lecturas parciales;
`candidate_partial` cuando el texto completo disponible deja faltantes declarados.
`not_found_in_supplied_material` nunca acredita ausencia documental. El campo
`semantic_support` permanece `not_verified`.

La reparación es una ejecución explícita con expediente nuevo vinculado al rechazo
anterior. No sobrescribir el resultado original ni mezclar coste de ambos intentos.
Regresión y límites: [refinement-v2](../experiments/refinement-v2/README.md).


### Presupuesto de razonamiento del proveedor

`--reasoning-effort low|high|max` envía y registra la selección explícita.
Al omitirlo, se conserva el comportamiento previo del proveedor. No es un límite
duro de tokens ni garantiza finalización. Z.AI documenta estos valores para
GLM-5.3/Flash y no permite desactivar su razonamiento:
[contrato oficial](https://docs.z.ai/guides/capabilities/thinking), consultado
2026-10-03. Otros modelos pueden tener restricciones diferentes.
El límite `--max-output-tokens` también puede consumirse en razonamiento; acotar
los caracteres de respuesta no basta para evitar truncamientos. La prueba adicional
con `low` se conserva aparte de los intentos con la configuración predeterminada.


## Presentación conjunta e inspección sin proveedor

La salida JSON de `agora.passage_cli` conserva `execution_status`, `answer_status`
y `http_attempts`, y añade una vista `agora/passage-display/v1` con `answer`,
`missing`, `answer_scope`, `requires_expansion`, estado de revisión y advertencias.
Los consumidores deben presentar respuesta y faltantes juntos. `result.json`
conserva el contrato original y la evidencia completa; no se modifica para renderizar.
Los consumidores que exigían exactamente las tres claves antiguas de stdout deben
adaptarse a los campos adicionales de la vista; no hay cambio del archivo result.

Para inspeccionar un resultado ya guardado, sin credencial ni llamada al proveedor:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m agora.passage_view \
  experiments/focused-label-v1/repair/default-receipt.json
```

La inspección muestra también ruta y SHA-256 del archivo leído. El hash identifica
los bytes observados, no certifica autenticidad ni fidelidad. La vista no cambia
estados, revisa semántica, amplía lecturas ni admite memoria. El código de salida 0
del inspector significa que mostró el archivo, incluso si éste contiene un rechazo.

En resultados anteriores sin `missing`, la vista muestra `null` y explica que los
faltantes no están declarados; nunca transforma eso en `[]`. Alcance desconocido
permanece `unknown`, y flags desconocidos permanecen `null`. Las ejecuciones fallidas
o rechazadas muestran su diagnóstico; no rescatan el texto del proveedor como
respuesta candidata. El comando rechaza JSON ambiguo con claves duplicadas y
archivos mayores de 16 MiB. Los datos guardados continúan siendo datos no verificados.

Validación del 2026-10-03: 548 pruebas locales pasan, incluyendo el receipt real de
fórmula faltante, compatibilidad aditiva, ausencia desconocida y rechazo sin rescate.
Cero llamadas externas en esta validación.


## Plan de pasajes elegidos explícitamente

`agora_issues.py --workspace <workspace> plan-passages` prepara el contrato
`agora/explicit-passage-plan/v1`. Requiere `--source`, `--source-id`,
`--source-sha256`, `--question`, uno o varios `--range START:END`, `--budget`
y `--out`. El workspace se crea previamente con `init`. No llama al proveedor.

`generate-plan` admite este plan mediante los argumentos existentes: `--source`,
`--plan`, `--expected-plan-sha256`, la misma `--question`, `--citation-mode ids`
y `--response` para replay (o `--live` sólo por decisión explícita). El plan liga
la pregunta; cambiarla, alterar fuente o inconsistencia interna produce rechazo
antes del proveedor. El control de alcance está siempre activo para este contrato.

[Ejemplo completo reproducible](../experiments/explicit-plan-v1/README.md).
No equivale a selección automática ni prueba de suficiencia semántica. Mostrar el
resultado con `agora.passage_view` conserva juntos respuesta, faltantes y alcance.
