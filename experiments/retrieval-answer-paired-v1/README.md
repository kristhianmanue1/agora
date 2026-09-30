# Comparación pareada de recuperación, generación y revisión

## Fotografía histórica: primera etapa detenida por transporte

La continuación posterior completó los 16 envíos pendientes sin repetir solicitudes previas. Estado consolidado y decisión: [CONTINUATION.md](CONTINUATION.md). Este informe conserva los resultados de la primera etapa.

Se planificaron 12 pares (24 generaciones GLM) sobre los 12 documentos del piloto de cobertura, con presupuesto 8.000 bytes. No son documentos nuevos reservados: ya fueron usados para evaluar recuperación. Se intentaron ocho generaciones: cinco llegaron y pasaron validación de forma y citas, tres agotaron 90 segundos. El transporte heredado paró al tercer error. Dieciséis generaciones no se ejecutaron y no se repitió ninguna solicitud.

Las cinco respuestas conservadas fueron revisadas por Jev contra el documento completo, sin método, rangos recuperados, gold ni respuesta hermana en el payload. IDs neutros y orden barajado. No se afirma ceguera perfecta ante pistas del contenido ni independencia humana. Jev sigue siendo revisor experimental, no árbitro de verdad.

## Protocolo y verificaciones

Mismas preguntas, generador glm-5.3-flash, temperatura 0, 2048 tokens de salida, perfil existente concise-v1 en inglés con citas literales. Orden de métodos alternado por documento. Un solo intento por entrada, timeout 90 s. El freeze de generación y el de revisión conservan hashes. El transporte común declara parada por 401/402/403/429 o tres errores; dicha regla heredada fue la aplicada.

La generación usa el prompt y validador actuales de Ágora sobre los envelopes preparados; es un harness de comparación, no una nueva ruta pública de CLI. Valida shape, finish_reason, citas y pertenencia a pasajes. Los timeouts tienen resultado remoto desconocido y consumo no reportado; no equivalen a respuesta semántica incorrecta.

## Resultado parcial

| Ruta | Planificadas | Intentadas | Válidas | Timeouts | Sin ejecutar | Revisadas | Útiles según Jev |
|---|---:|---:|---:|---:|---:|---:|---:|
| Cuotas iguales | 12 | 4 | 3 | 1 | 8 | 3 | 1 |
| Redistribución | 12 | 4 | 2 | 2 | 8 | 2 | 1 |

Útil aquí exige respuesta no abstencionista, forma/citas válidas y juicio Jev supported + complete. No ejecutado no se convierte en fallo semántico. Se conserva el denominador planificado, pero no se calcula tasa comparativa con ejecución desigual.

Sólo hay dos pares completos: uno con ambas respuestas útiles y otro con ambas incompletas. En ese segundo par Jev señala unsupported en cuotas iguales y supported en redistribución; ambas omitted. El único resultado de la tercera pareja, cuotas iguales, es supported/omitted; su pareja agotó tiempo. No es base para declarar superioridad.

Tres de los doce pares preparados tienen contexto idéntico. Una generación distinta en ese caso sería variabilidad del modelo, no efecto de recuperar más; se registra same_context por par. No hay repeticiones suficientes para estimar estabilidad.

## Consumo y coste

53.238 tokens observados entre cinco generaciones exitosas y cinco revisiones. Es un mínimo: faltan uso y eventuales cargos de las tres generaciones agotadas. Las ocho solicitudes de generación acumularon 352,661 s (incluye timeouts); cinco revisiones 1,904 s. No equivale a tiempo de trabajo total.

- Cuotas iguales: 30.654 tokens observados, con tres generaciones y tres revisiones completadas.
- Redistribución: 22.584 tokens observados, con dos generaciones y dos revisiones completadas.

No comparar esos totales como eficiencia: tienen distinto número de respuestas. La revisión usó documentos completos y su coste forma parte del ledger experimental. Recuperación local: 58.690 frente a 70.944 bytes preparados para las 12 preguntas; sólo un subconjunto llegó a generación. Coste monetario no verificado; no se consultó facturación.

## Decisión y continuación

No incorporar ni promover la redistribución. El lote no demuestra mejora de respuestas suficiente para compensar coste. Causa de los timeouts no determinada: sin HTTP útil, no se atribuye a cuota, red, credenciales ni modelo.

La continuación debe abrir una nueva etapa registrada: comprobar disponibilidad de GLM con una sonda mínima, mantener las tres solicitudes de resultado incierto y decidir si continuar sólo las 16 entradas nunca enviadas. No reiniciar el runner ni reenviar a ciegas las ocho intentadas. Mantener selección, prompts y todos los resultados; si se cambia timeout o tokens, registrar una condición experimental diferente.

La autorización del Operador para los envíos de esta serie sigue vigente. La parada es el límite operativo del protocolo, no una nueva solicitud de permiso para cada lote. No hay cambios de producto, reparación de respuestas ni admisión automática.

## Artefactos

freeze.json/key.json: entradas y asignación de método (no enviadas al revisor). validation.json: resultados de forma/citas y estados no ejecutados. review-freeze.json: cinco entradas elegibles, hash y alcance de cegamiento. result.json: métricas saneadas, pares y estados. Journals y contenido permanecen en inputs/ y runs-*/ ignorados por Git.

prepare.py requiere una carpeta nueva y corpus local. generate.py y review.py rechazan salidas existentes mediante transporte común; no usarlos para repetir este lote. prepare_review.py prepara únicamente respuestas elegibles; score.py recompone resultados sin llamadas.
