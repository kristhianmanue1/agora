# Recuperación de operaciones inciertas — experimento v1

28 de septiembre de 2026. Nuevo almacén SQLite con application_id propio y
user_version=2; no migra ni altera bases de issue-store-v1. Reutiliza preparación
de issue-flow-v1 y validación de open-issues-v3 mediante dependencias locales.

El caller conserva un operation_id estable y el paquete exacto. Su reutilización
con otro paquete/configuración se rechaza. Estados:

- attempted: intención persistida antes de llamar. Si al retomar sigue así,
  provider_outcome_unknown bloquea reenvío: el proveedor pudo haber trabajado.
- response_ready: respuesta guardada (incluso si es inválida). Se puede intentar
  finalizar sin otra llamada. Respuesta inválida o revisión atrasada permanecen
  disponibles para inspección; no se reparan ni se fuerza el padre.
- committed: revisión y resultado de operación se guardaron en una transacción.
  Repetir con el mismo ID/paquete devuelve el resultado guardado, no el estado
  más reciente de otra operación. Se verifica su vínculo con la revisión.

No se sostiene una transacción SQL durante la llamada. Cambios concurrentes
pueden impedir el append. Un ID distinto es otra operación y puede consumir otra
llamada: no hay garantía de ejecución única del proveedor. El esquema de IDs y
su conservación son responsabilidad del caller en este piloto.

## Evidencia local

344 tests pasan. Ocho nuevos: confirmación perdida, respuesta lista, timeout
incierto sin reenvío, ID con otro paquete, rollback atómico de revisión/operación,
revisión concurrente, respuesta inválida conservada y revisión desaparecida.
El fallo de actualización de operations se inyecta con un trigger SQLite temporal
en una base de test; al fallar, la revisión también se revierte.

run.py local-01: un proceso hijo invoca proveedor simulado, guarda y cierra base,
pero termina con código 7 sin devolver el resultado. Otro proceso reabre, inspecciona
committed y recupera el mismo resultado. Dos revisiones, una llamada simulada,
cero llamadas remotas. Es pérdida de confirmación de aplicación, no corte eléctrico
ni crash mientras SQLite confirma. Reporte: result-local-01.json.

## Límites y autorrevisión

Hash de operación no autentica actor ni resiste reescritura coordinada por quien
controla la base. No hay credenciales en el almacén. No se declara cifrado propio.
La forma del proveedor abstracto no fuerza por sí sola el modelo configurado:
se registra lo solicitado/reportado y un harness real debe imponer sus límites.
No se implementa reconciliación con el proveedor para attempted ni adopción
manual de respuestas externas. No se elimina incertidumbre suponiendo un aborto.
No hay tests de corte de energía, migración, múltiples hosts o bloqueos prolongados.
Un fallo durante commit exige inspección en nueva conexión, no repetición ciega.

No se cambió código productivo ni memoria AN-KLA. Candidate resolved sigue sin
admisión. Cero pruebas nuevas de fidelidad semántica. Corridas ignoradas por Git.

```bash
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python experiments/issue-recovery-v1/run.py experiments/issue-recovery-v1/runs/NOMBRE_NUEVO
```
