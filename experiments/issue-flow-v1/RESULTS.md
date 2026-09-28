# Flujo explícito completado — 28 de septiembre de 2026

Se preparó una evaluación desde la revisión guardada, se incorporó una fuente
sintética nueva y se realizó una llamada real a glm-5.3-flash. El candidato
pasó validación y se añadió como segunda revisión. Un proceso Python nuevo
recuperó exactamente ambos registros, fuentes, citas y resultados.

Estado inicial: partial; fecha pendiente, responsable Lina. Nueva fuente q2:
entrega 2026-10-21 y Lina continúa. Resultado: resolved como estado de la cuestión
en el candidato, admission=not_admitted. No se admitió conocimiento canónico.
GLM distinguió aclaración de dato ausente de cambio de decisión; q2 reitera al
responsable, sin computarlo como corroboración independiente. El productor
contrastó respuesta y citas con q1/q2; no revisión independiente.

Una llamada, 3349 tokens reportados, 38.36 segundos; sin reintentos remotos ni
consumo desconocido. El primer lanzamiento mediante runpy falló al importar
adapter por sys.path, antes de crear la corrida o invocar al proveedor. Se corrigió
el lanzador; no se modificó el código congelado para conseguir la respuesta.

336 tests pasan, incluidos siete del adaptador. Cubren preparación sin escritura,
fuente inválida/duplicada/corte, paquete alterado incluso con hash recalculado,
revisión atrasada antes de llamar, actualización durante la llamada mediante
proveedor simulado, salida inválida/consumo desconocido y repetición de paquete.
El test de actualización durante llamada no es una campaña de concurrencia real.

Auditoría: paquete, entrada almacenada y respuesta del proveedor coinciden.
Fuentes de código ejecutadas coinciden con copias congeladas. Hashes del manifiesto
comprobados. Sin cambio de productor, gold ni fuentes después de la llamada.

## Qué demuestra y qué no

Demuestra el flujo explícito local para una cuestión y dos fuentes sintéticas:
preparar -> evaluar -> validar -> registrar candidato -> recuperar en proceso nuevo.
No descubre a qué cuestiones pertenece una fuente. No hay watcher, integración
Skopos/AN-KLA, aprobación automática, políticas multiusuario ni despliegue.
Los hashes no autentican identidad o autoridad de coordinación. Guardar candidate
resolved no prueba verdad externa. Sigue dependiendo del contrato v3 experimental.

No hay transacción distribuida con el proveedor. Una respuesta puede consumir
presupuesto aunque el append sea rechazado por revisión atrasada. El ejecutor
conserva respuesta antes de append; no hay reintento automático. Un error después
del commit requiere inspeccionar la base antes de repetir; no hay clave de
idempotencia de operación en el almacén actual. Llamadas previas fallidas de
otros pilotos siguen registradas separadamente y no se excluyen de costes globales.

## Continuación propuesta

Antes de ampliar fuentes o modelos, consolidar y revisar conjuntamente los pilotos
acumulados, incluyendo una interfaz estable para identidad de operaciones y
recuperación cuando se pierde la respuesta después del commit. Después probar
una fuente local aportada por Skopos mediante contrato, manteniendo este mismo
flujo explícito. No hacen falta más variantes sintéticas sin una hipótesis concreta.

Código: adapter.py y run.py. Resumen: result-glm-01.json. Corrida cruda y SQLite:
runs/glm-01, ignorado por Git. No se tocó src/agora ni contexto canónico.
Base Git d92ce22, main; cambios locales sin commit ni push en esta tarea.
