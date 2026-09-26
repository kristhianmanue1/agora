# Respaldo estable ante cambios de pregunta — ensayo 01

## Diagnóstico de generación posterior

La sonda aislada transport-diagnostic-01 respondió {"ok":true}, finish_reason=stop,
en 3.381 segundos, con 212 tokens reportados y reported_model=glm-5.3-flash.
Se fijaron antes de llamar: 1 intento, 1024 tokens máximos, 60 segundos de
transporte, 65 de proceso y cero reintentos. Evidencia:
experiments/review-invariance-v1/runs/transport-diagnostic-01/{protocol,request,receipt}.json.
Esta sonda acredita una generación mínima en ese momento; no explica los fallos
anteriores ni valida el prompt largo, la fidelidad o la batería. Sus 212 tokens
se contabilizan aparte. La batería conserva 2 fallos y 6 casos no ejecutados.
Siguiente paso actualizado: evaluar separación de respaldo y pertinencia y
comparador opcional TypeSafe antes de ampliar el ensayo. Investigación entregada
en la conversación; no se instaló ni llamó TypeSafe.

## Estado de la batería — continuación 01

**PARCIAL.** La continuación autorizada intentó sólo case-02, nunca enviado antes.
Falló a los 90.710 segundos con RuntimeError, sin respuesta ni uso reportado.
La parada por fallo de transporte impidió enviar los otros seis casos.
No hubo reintentos de case-01 ni case-02. Acumulado: 2 intentos fallidos,
0 respuestas válidas, 6 casos sin intentar, 0 pares evaluables y 2 consumos
desconocidos. No se puede estimar exactitud semántica ni consumo total.

La comprobación GET al endpoint recibió 401 sin autenticación en 0.465 s y 200
con autenticación en 0.604 s. Demuestra respuesta HTTP en esas condiciones,
no disponibilidad de generación POST, ausencia de saturación ni causa del fallo.

La auditoría verificó que la ejecución original conserva todos sus hashes,
que sólo se agregó un caso pendiente, y que código, gold y payload permanecieron
fijos. Cero respuestas disponibles para replay. Evidencia:
experiments/review-invariance-v1/runs/glm-01-continuation-01/audit-continuation.json
SHA256: 8814a7ccfc4ec8da6a156fcbd52469d7828dbab9cb66545b7e27bf3363f9080f.

Se detectó una pérdida de observabilidad: worker.py elevaba RuntimeError antes de
guardar el recibo de transporte fallido. Se prepararon variantes separadas
worker_diagnostic.py y transport_diagnostic.py, sin alterar snapshots anteriores:
guardan recibo y código HTTP, sin cuerpo de error, cabeceras ni credenciales.
Una prueba local con HTTP 503 simulado conservó el diagnóstico y mantuvo estado
failed; no hizo conexiones. Estas variantes todavía no se usaron con GLM.
293 pruebas de producto pasan; diff --check pasa. Sin cambios de producto en esta
continuación, sin commit/push, sin memoria ni contexto canónico modificados.

**Próximo paso:** un diagnóstico de generación aislado con el transporte nuevo,
presupuesto explícito y parada ante fallo; no continuar consumiendo casos del
ensayo hasta obtener ese diagnóstico. No elevar automáticamente tokens/tiempo:
la evidencia disponible no demuestra que el límite sea la causa.

Los apartados de resultado inicial que siguen son históricos; este estado los
supersede para cobertura y siguiente acción, conservando su procedencia.

## Protocolo fijado antes de las llamadas

Revisión optativa v3-r2: distingue ausencia de información de negación del hecho.
Conserva el esquema v3 y las comprobaciones locales; agrega instrucciones al
modelo, no un verificador semántico independiente. Los modos predeterminados no cambian.

Tres pares nuevos: respaldo explícito, contenido no especificado y negación
explícita. Un cuarto par reproduce el fallo histórico de Elian. En cada par son
idénticas la afirmación autosuficiente y su cita; cambia únicamente la pregunta.
El respaldo debe permanecer correcto y estable; la pertinencia debe cambiar.
No se permite que dos respuestas igualmente equivocadas pasen el criterio.

Ocho llamadas como máximo a glm-5.3-flash, 8192 tokens de salida por llamada,
reserva máxima 65536; temperatura 0, modo JSON, idioma inglés, 180 segundos
de transporte y 200 por proceso. Sin reintentos. Parada por fallo de transporte,
acceso, integridad o consumo desconocido; rechazos estructurales se conservan.
Se congelan fuentes, entradas, gold separado, scripts y protocolo antes de llamar.
No se envían etiquetas esperadas. Se informa cada caso, par, fallos, tokens y tiempo.
Los dos casos históricos se separan de los seis nuevos al puntuar.

Criterio diagnóstico: 8/8 casos y 4/4 pares correctos, incluyendo pertinencia,
idioma y recomendación. Un resultado favorable sólo acredita estos controles.
Sin comparación contemporánea contra v3 anterior, no se atribuye causalidad ni
superioridad. No se prueba español, documentos largos ni generalización.
needs_adjudication solicita revisión humana; nunca significa aprobación.

Reproducción: preparar fixtures una sola vez con prepare.py, ejecutar run.py con
ZAI_API_KEY en el entorno y PYTHONPATH=src; auditar con PYTHONPATH=src python3
experiments/review-invariance-v1/audit.py. Los resultados e inputs están ignorados
por Git; este informe no equivale a publicar el paquete de evidencia.

## Resultado inicial — histórico

**PARCIAL: corrección implementada; comportamiento del modelo sin verificar.**

La primera llamada (case-01: contenido no especificado, pregunta pertinente)
terminó con TimeoutExpired a los 180.078 segundos. No llegó una respuesta ni
telemetría de consumo. El ejecutor detuvo la batería conforme al protocolo:
1 intento fallido, 0 respuestas válidas, 7 casos sin ejecutar, 0 pares evaluables.
No hubo reintento ni ampliación de presupuesto. No se infiere la causa del timeout.

El subtotal conocido de tokens es 0 y existe 1 consumo desconocido: **el consumo
total no es cero ni puede calcularse**. Los ceros de aciertos y pares del JSON son
contadores de cobertura, no una estimación de exactitud semántica de GLM.

La auditoría comprobó hashes de entradas/código/scripts, igualdad de afirmaciones
y citas dentro de cada par, cambio de pregunta, payload sin gold y hash del fallo.
No pudo reproducir respuestas: no existe ninguna. El campo compuesto
freeze_and_local_replay_verified=true significa que pasaron las comprobaciones
aplicables; en este intento la cantidad de respuestas reproducidas es **0**.
El modelo solicitado fue glm-5.3-flash; modelo reportado/efectivo desconocido
porque no se recibió respuesta.

Evidencia local, ignorada por Git:
- runs/glm-01/execution.json: registro del intento.
- runs/glm-01/v3/case-01/result.json: diagnóstico TimeoutExpired.
- runs/glm-01/audit.json: cobertura y comprobaciones.
- SHA256 freeze.json: 95f2d1989dc83f0dfd76e140b6fafb3f3bfb21a63eb5079fed100d7195558655
- SHA256 audit.json: 197bc5a348dc0e3d8af5c858bf5668d05a15a478dd2f86d46d7d5ab0b95b9630

## Cambios y verificación local

evidence_checks.py agrega las instrucciones de separación de ejes y tipos de
negación; evidence_review.py registra prompt_revision=v3-r2. No cambian los
validadores, la agregación ni los modos por defecto. La instrucción sobre
invariancia no constituye enforcement semántico.

293 pruebas locales pasan. Cuatro nuevas comprueban que estabilidad equivocada,
pertinencia incorrecta, fallos y casos ausentes no producen un par aprobado.
Autorrevisión adversarial del diff contra el código congelado del ensayo anterior;
sin revisor independiente. git diff --check pasó; el repositorio ya contenía
numerosos cambios anteriores, incluidos módulos aún sin seguimiento.

## Continuación propuesta tras el primer intento — histórica

Primero revisar disponibilidad y latencia del proveedor antes de otro bloque.
Una continuación debe preservar este intento y fijar por separado su presupuesto:
sólo siete casos nunca enviados; case-01 queda como resultado desconocido sin
reintento implícito. Un eventual reensayo de case-01 debe identificarse como nuevo.
No ampliar baterías ni promover v3 por estos resultados. No hubo commit, push,
activación, cambio de contexto canónico ni escritura en memoria.

