# Comparación inicial de revisores GLM y Jev

## Resultado

Jev merece pasar a una batería reservada más difícil. Este piloto no justifica
reemplazar todavía al revisor por defecto ni atribuir fidelidad general.

| Medida | GLM 5.3 Flash | Jev 1.13.0 |
|---|---:|---:|
| Respuestas válidas | 24/24 | 24/24 |
| Coincidencias con etiquetas prefijadas | 22/24 | 24/24 |
| Afirmaciones indebidamente aceptadas | 0/16 | 0/16 |
| Español | 11/12 | 12/12 |
| Inglés | 11/12 | 12/12 |
| Latencia mediana por petición | 5,204 s | 0,339 s |
| Suma de duraciones de peticiones | 171,282 s | 49,071 s |
| Tokens de entrada reportados | 5.729 | 10.728 |
| Tokens de salida reportados | 2.739 | 1.104 |
| Tokens totales reportados/sumados | 8.468 | 11.832 |

49 llamadas nuevas en total: 24 por revisor y una previa para la CLI. No hubo
reintentos. No se conoce el cargo monetario por petición: los tokens no permiten
concluir que Jev haya sido más barato. Los tokenizadores y envoltorios son distintos.

Los dos desacuerdos de GLM pertenecen a la misma situación traducida: dos notas
registran cifras diferentes y ninguna sustituye a la otra. La afirmación «la nota B
es la medición autorizada» quedó `contradicted` en GLM e `insufficient` en Jev.
La evidencia no establece autoridad; tampoco la refuta explícitamente. La etiqueta
prefijada es `insufficient`. Es un error de clasificación sin falsa aceptación.

## Qué se comprobó en la CLI

Una llamada real de GLM, con los ejemplos sintéticos y configuración congelada de
8192 tokens máximos de salida, produjo JSON aceptable: segunda revisión guardada,
`execution_origin=live_provider`, `assessment_status=resolved`, `not_admitted`.
La recuperación devolvió la misma revisión sin llamar al proveedor. No necesitó
reparación. Consumo reportado: 1.759 tokens de entrada y 4.594 de salida, 6.353 total.
La ruta de rechazo y reparación conserva la evidencia local de la etapa anterior;
no se presenta como fallo provocado en esta llamada nueva.

## Límites y decisión propuesta

Son 24 controles escritos por este agente, 12 situaciones traducidas, con una
sola ejecución por proveedor. No son 24 observaciones independientes, un benchmark
externo ni evidencia sobre documentos grandes. Las etiquetas no recibieron revisión
humana independiente. La autorrevisión no cambia ese límite.

GLM y Jev recibieron idénticos pares evidencia/afirmación y criterios; se respetó la
salida tipada de Jev y JSON en GLM. Se comparan configuraciones utilizables de API.
Ningún revisor puede detectar una excepción documental que no recibe. `insufficient`
es una clasificación del respaldo; no equivale a abstención técnica ni fallo.

**Siguiente paso:** mantener GLM como generador y probar ambos revisores sobre una
selección reservada de AttrScore y casos de documentos grandes con evidencia
incompleta, contradicciones y excepciones. Fijar etiquetas antes, repetir los casos
sensibles y medir falsas aceptaciones, omisiones, estabilidad y coste facturado.
Jev sigue siendo opcional; no se cambió configuración predeterminada ni admisión.

## Evidencia reproducible

- [Protocolo, límites y comandos](../experiments/reviewer-comparison-v1/README.md).
- [Resultados y matriz de confusión](../experiments/reviewer-comparison-v1/result-01.json).
- [Operación real de CLI](../experiments/reviewer-comparison-v1/cli-live-operation-01.json).
- Peticiones y respuestas finales de ambos proveedores: `records-glm.jsonl` y
  `records-jev.jsonl` en el mismo directorio; sólo contienen controles sintéticos.
- [Hashes de código y evidencia](../experiments/reviewer-comparison-v1/evidence-sha256.json).
- 424 tests pasan, incluidos tres nuevos para entradas equivalentes, formato de
  salida y cómputo de errores y respuestas ausentes. Sin revisión independiente.

Contrato de Jev contrastado con el [Quick start oficial](https://docs.typesafe.ai/introduction/quickstart).
