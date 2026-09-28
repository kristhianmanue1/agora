# Persistencia v4 y recuperación — 2026-09-28

El consumidor experimental conserva dos candidatos v4 completos: ausencia y
contradicción, ambos partial. La respuesta original y el candidato envuelto por
el host se almacenan por separado. No se inventa una respuesta nueva de GLM.

run.py creó base y backup SQLite, cerró la conexión y lanzó un proceso nuevo con
sólo la ruta del backup y las cabezas esperadas. El hijo recuperó exactamente los
registros completos, incluidos input, citas, alcance, respuesta, candidato y
procedencia. No leyó fixtures ni archivos laterales. Cero llamadas a modelos.

381 tests pasan, incluidos diez nuevos de este consumidor. Verifican roundtrip,
adaptación alterada, rechazo de bases issue-store-v1 e issue-recovery-v1 sin
modificar sus bytes, no sobrescritura, escritor con cabeza obsoleta, rollback ante
fallo de inserción, alteración de payload, deriva del validador, pérdida de cola
con cabeza externa y cambio de definición de pendiente.

## Autorrevisión adversarial

- Conservar sólo el candidato perdería la distinción modelo/host: se guardan
  ambos textos y se verifica que fields/reason no fueron cambiados al adaptar.
- Hash del protocolo aislado omitiría dependencias: el manifiesto incluye
  protocolo, envelope y bridge. Cambios de versiones bloquean reinterpretación.
- Una base antigua abierta accidentalmente podría cambiar de significado:
  application_id/user_version propios; rechazo antes de escrituras de registros.
- Una cola borrada puede parecer historial válido: se comprueba con cabeza
  externa cuando se proporciona. Sin ella la limitación permanece.
- Los hashes no autentican al productor ni protegen frente a sustituir toda la
  base y las referencias externas. SQLite con synchronous=FULL no demuestra
  resistencia a pérdida de energía: ese experimento no se hizo.
- Un backup con dos pendientes no prueba reapertura automática de un asunto al
  llegar evidencia nueva. No hay watcher ni recuperación de operaciones LLM v4.

No hubo revisión independiente, cambio en consumidores previos, admisión AN-KLA
ni despliegue. El resultado es persistencia y recuperación experimental local.

## Próximo paso propuesto

Conectar explícitamente una fuente nueva a este consumidor v4: preparar evaluación
contra cabeza esperada, conservar el alcance ampliado y producir nueva revisión
sin sobrescribir la anterior. Probarlo primero con fixtures locales, incluyendo
respuesta perdida y conflicto de escritor; después una única prueba real si sigue
siendo necesaria. No activar vigilancia automática ni migrar bases previas.
