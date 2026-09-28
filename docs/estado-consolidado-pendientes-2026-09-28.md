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
