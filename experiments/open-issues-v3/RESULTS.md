# Cuestiones abiertas v3 — piloto acotado completado

27 de septiembre de 2026. Cuatro solicitudes reales a glm-5.3-flash, modelo
solicitado y reportado; todas completadas sin reintentos ni consumo desconocido.
Se conservaron los rechazos y el timeout de v2. Base local Ágora d92ce22 más
archivos experimentales; ninguno de estos pilotos está publicado por esta tarea.

## Qué se corrigió

- Prompt precisa que relations contiene cadenas y da un ejemplo de forma neutro.
  No se aceptan ni reparan objetos donde se esperan cadenas.
- change_source_ids vincula cada cambio a fuentes existentes citadas.
- Dependientes declaran fuentes base y fuentes ya revisadas con identidad/hash.
  Fuentes modificadas o snapshots incongruentes se rechazan.
- affected es candidato a revisión por cambio no revisado del campo pertinente.
  No significa falsedad, desactualización demostrada ni invalidación automática.
  No basta comparar valores: importa qué evidencia ha sido revisada.

## Resultado observado

| Caso | full | tracked |
|---|---|---|
| Retirar fecha, conservar responsable | Correcto; partial, sólo date reabierta | Correcto; igual |
| Cambiar fecha, conservar responsable | Correcto; fecha 2026-10-28, Lina | Correcto; igual |
| Candidatos de revisión en ambos casos | Sólo schedule | Sólo schedule |
| Documento del responsable y aviso ya revisado | No señalados | No señalados |

Coincidencia con los seis ejes del gold: 2/2 por brazo. Las cuatro respuestas
cumplen el formato y sus citas aparecen literalmente en fuentes. Valores,
explicaciones y fuentes de cambio contrastados por el productor: autorrevisión,
no revisión independiente. Las dos parejas usan las mismas entradas salvo
antecedente; fuentes textuales de los casos se conservaron respecto de v2.

| Consumo | full | tracked |
|---|---:|---:|
| Tokens reportados | 6480 | 7941 |
| Segundos sumados de llamadas | 68.066 | 86.824 |

Total v3: 14421 tokens y 154.890 s. No se calculó coste monetario.
V2 + v3 conservan 31898 tokens conocidos y una solicitud v2 de consumo desconocido.
No presentar esa suma como coste total cerrado. El piloto v1 queda aparte.

## Verificación y límites

321 tests pasan. Seis controles nuevos verifican propagación sólo al dependiente
no revisado, versiones alteradas, formato incompatible, cambios sin cita,
revisión repetida y snapshot ausente. No son evaluación semántica del modelo.
Manifiesto congelado, igualdad de entradas por pareja y fuentes de v2 verificados.

Las versiones y revisiones de dependientes son declaraciones del fixture, no
recibos autenticados. Tener un snapshot no prueba que la revisión estuvo bien
hecha. La selección de cambios por el modelo puede equivocarse. No se evalúan
recuperación, descubrimiento de pendientes, grafos transitivos, concurrencia,
autoridad real ni persistencia de transiciones. El algoritmo no debe usarse
como invalidación de producción a partir de metadata no confiable.

Una corrida por caso, fixtures/gold del mismo productor, sin holdout independiente.
V3 cambia prompt y metadata: no atribuir causalmente el éxito al ejemplo JSON
ni comparar puntuaciones v2/v3 como si fueran el mismo tratamiento.
Ambos brazos aciertan; no se demuestra ventaja de agregar el antecedente.

## Continuación recomendada

Se completaron los dos escenarios pendientes en v3; no se reetiquetan como éxito
los intentos fallidos de v2. Evitar otra ampliación mecánica de fixtures.

Siguiente paso: consolidar este contrato experimental y probar un recorrido local
persistente pequeño: guardar pendiente, incorporar una fuente nueva, producir una
revisión y reabrir el almacén para recuperar exactamente el estado y su evidencia.
Comparar siempre con lectura completa. No conectar todavía AN-KLA ni desplegar
vigilancia automática. Las llamadas al modelo y sus transiciones seguirían siendo
explícitas. Esto es propuesta, no implementación realizada.

Artefactos: protocol.py, cases.json, gold.json, run.py, README.md y
result-glm-01.json. Evidencia cruda preservada en runs/glm-01 (ignorada por Git).
Sin cambios de src/agora, AGENTS.md, datos reales ni memoria persistente.
Sin commit ni push en esta tarea.
