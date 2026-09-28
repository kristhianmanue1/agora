# Pendientes y evidencia posterior: consolidación técnica

Estado: prototipo local experimental. No producto integrado ni memoria admitida.
Los seis pilotos iniciales fueron publicados en main mediante b49e86f; SHA
remoto verificado. Las notas de ausencia de publicación en informes anteriores
describen el cierre histórico de cada piloto. No se modifica AGENTS.md ni se reinterpreta como
implementado todo el motor de Ágora.

| Pieza | Resultado verificado | Límite principal |
|---|---|---|
| open-issues-v1 | 24 llamadas, valores correctos en seis casos | Categorías ambiguas; sin superioridad demostrada |
| open-issues-v2 | Antecedente falso y fuente tardía, ambos brazos | Timeout y formato rechazado preservados |
| open-issues-v3 | Refutación parcial y dependientes: 4/4 válidas | Dependencias y revisiones declaradas |
| issue-store-v1 | Tres revisiones y recuperación exacta en procesos nuevos | SQLite local, sin pruebas de corte eléctrico |
| issue-flow-v1 | Fuente nueva, llamada GLM, candidato y reapertura exacta | Un caso sintético, sin admisión |
| issue-recovery-v1 | Confirmación perdida recuperada sin duplicado | Proveedor simulado; resultado remoto incierto no reenviado |

## Recorrido disponible en los experimentos

1. El caller indica cuestión, revisión esperada y nueva fuente versionada.
2. Preparación reconstruye un paquete verificable desde la revisión guardada.
3. Una operación identificada reserva la evaluación; el proveedor devuelve una
   propuesta cuyo contenido sigue siendo dato falible.
4. Se conserva la respuesta; se valida forma y citas y se guarda una revisión
   candidata con comparación de padre. Operación y revisión se confirman juntas.
5. El caller puede recuperar resultado sin repetir la llamada si está committed;
   si sólo está attempted se reconoce incertidumbre y se impide reenvío automático.

Los escenarios 1-5 están distribuidos entre módulos experimentales reutilizados,
no constituyen una CLI pública estable. La capa nueva de recuperación se probó
con proveedor simulado; la llamada real pertenece a la capa anterior issue-flow-v1.

## Hallazgos incorporados y riesgos residuales

- Procedencia, soporte semántico, estado de cuestión y admisión están separados.
- No se confunde fuente llegada después con decisión vigente por mera recencia.
- affected sólo propone revisión: no declara documentos falsos o desactualizados.
- Un resumen o evaluación previa puede corregirse contra las fuentes.
- No se fuerza escritura sobre una revisión atrasada, ni se repite una operación
  incierta para obtener una aparente confirmación.
- La independencia de fuentes, autoridad, pertinencia, detección de pendientes y
  exactitud semántica siguen sin garantías generales. Autorrevisión del productor.
- Los hashes no demuestran autenticidad. Revisiones declaradas de dependientes
  todavía no son recibos verificables de una revisión bien hecha.

Verificación final: 344 tests pasan; ocho nuevos sobre recuperación. Demostración
local con proceso hijo sin confirmación y recuperación por ID: una llamada
simulada, dos revisiones; cero llamadas nuevas al modelo en este incremento.

## Próxima decisión concreta

Revisar/publicar el conjunto como experimento, preservando corridas privadas y
fallos. Antes de ampliar: fijar interfaz de entrada de fuente (identidad, versión,
localizador, bytes y completitud) y probar un único paquete sintético exportado
por Skopos con el flujo recuperable. Lectura mediante adaptador, sin escritura
directa entre almacenes ni integración obligatoria. No añadir watcher.

Puntos de entrada: experiments/issue-recovery-v1/README.md, luego
experiments/issue-flow-v1/README.md y experiments/open-issues-v3/README.md.
Este documento consolida evidencia; no autoriza publicación ni despliegue.

## Actualización: puente sintético con Skopos

Se añadió experiments/skopos-issue-bridge-v1: exportador de Skopos ejecutado
sobre fuente sintética, verificación contra fetch, dos citas nativas y operación
recuperada sin duplicar. Evaluador simulado; cero llamadas nuevas al modelo.
347 tests pasan. No se modificó Skopos ni se publicó su trabajo local pendiente.

Antes de una fuente real: incluir paquete/recibo en un respaldo recuperable por
hash y exponer completitud al evaluador. Actualmente esos metadatos están en
archivos laterales, no íntegramente en el historial o prompt de evaluación.
Esta limitación impide presentar el puente como integración productiva completa.

## Actualización: paquete autocontenido v2

experiments/skopos-issue-bridge-v2 resuelve la dependencia de archivos laterales
para recuperar procedencia: paquete íntegro dentro del texto de fuente versionado,
backup SQLite y recuperación exacta en proceso nuevo. La limitación de v1 sigue
siendo histórica, no describe v2. Metadatos de completitud llegan al evaluador
simulado y el wrapper añade una política explícita. 351 tests pasan; cero llamadas
nuevas al modelo. No se acredita todavía conducta semántica de GLM sobre ausencias
en selecciones parciales ni aplicación automática por consumidores antiguos.

## Actualización: lectura parcial con GLM real

experiments/partial-selection-v1 completa dos evaluaciones reales: mantiene fecha
pendiente al omitir su segmento, y la resuelve al ampliar la selección. Reconoce
que ambos paquetes comparten origen. 13 612 tokens; 221,184 segundos; sin reintentos.
Paquetes recuperados desde SQLite y prompt de sistema ligado a la operación.
Autorrevisión de explicaciones y citas favorable sólo para este caso sintético;
el antecedente ya declaraba la fecha pendiente. No acredita ausencia sin
antecedentes, contradicciones ni robustez general. 351 pruebas pasan.
Detalle y próximos casos: experiments/partial-selection-v1/RESULTS.md.

## Actualización: ausencia fría y contradicción

experiments/partial-selection-v2 ejecutó dos llamadas GLM (9713 tokens). La
contradicción quedó abierta, con ambas fechas citadas y responsable conservada.
La ausencia sin antecedente fue bien delimitada en la explicación, pero el
validador rechazó evidence vacía con missing_evidence. No se considera aprobada
esa salida ni se corrigió silenciosamente. 355 tests pasan, incluida reproducción
de esta limitación. La prioridad es un contrato versionado que separe citas de
soporte y alcance revisado, antes de seguir acumulando llamadas o integrar la API.
Detalle: experiments/partial-selection-v2/RESULTS.md.

## Actualización: contrato v4 para ausencia sin cita afirmativa

experiments/open-issues-v4 permite evidence vacía sólo en missing, con alcance
suministrado registrado por el host y validado contra identidad, versión y
fragmentos del input. Las citas de los otros estados siguen siendo obligatorias.
Replay explícito de las dos respuestas preservadas: ausencia=partial/missing,
contradicción=partial/disputed; campos originales intactos. 371 tests pasan;
cero llamadas nuevas. El rechazo histórico v3 no cambia. El contrato nuevo aún
no está adoptado por SQLite/recovery: el siguiente paso es un consumidor versionado
con recuperación y rechazo de bases incompatibles, sin migración silenciosa.

## Actualización: persistencia v4 aislada

experiments/issue-store-v2 adopta v4 en una base nueva, conserva respuesta original
y candidato/alcance por separado y rechaza bases anteriores sin modificarlas.
Backup recuperado exactamente en proceso nuevo sin archivos laterales. 381 tests
pasan; cero llamadas a modelos. Los consumidores previos siguen intactos.
Siguiente: llegada explícita de fuente y evaluación candidata con cabeza esperada
sobre este consumidor, primero mediante fixtures. No hay watcher ni recuperación
de operaciones de proveedor v4 todavía. Véase experiments/issue-store-v2/RESULTS.md.

## Actualización: flujo incremental recuperable v4

experiments/issue-flow-v4 conecta explícitamente fuente nueva, evaluación y nueva
revisión con request persistido e ID estable. Prueba local: hijo confirma y sale
sin devolver respuesta; padre recupera sin duplicar proveedor simulado. Se conserva
revisión original y alcance pasa de una a dos fuentes. 393 tests pasan; cero llamadas
reales. Consumidores anteriores intactos; base nueva sin migración automática.
Pendiente: una prueba GLM acotada sobre este flujo y posterior consolidación de
entrada CLI, sin añadir watcher. Evidencia: experiments/issue-flow-v4/RESULTS.md.

## Actualización: prueba GLM v4 rechazada por formato

Una llamada real sobre issue-flow-v4: 6407 tokens, 94,994 s, sin reintento.
GLM añadió una comilla invertida tras el JSON; rechazo Extra data, sin segunda
revisión. Respuesta exacta conservada en response_ready y recuperada en proceso
nuevo sin volver a llamar al proveedor. 394 tests pasan; el ensayo GLM completo
no pasó. Próxima prioridad: tratamiento explícito/versionado de salida inválida,
con original preservado y rechazo de reparaciones ambiguas, antes de nueva llamada
o CLI consolidada. Evidencia: experiments/issue-flow-v4/RESULTS-GLM-01.md.
