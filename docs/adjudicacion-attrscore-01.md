# Revisión separada de desacuerdos AttrScore — 01

Fecha: 2026-09-24. Estado: revisión consultiva completada; sin ratificación humana
ni cambios de producto. Complementa [el piloto](piloto-attrscore-01.md); no sustituye
sus etiquetas, métricas ni dictámenes. Registro legible por máquina:
`experiments/attrscore-v1/adjudication-01.json`.

## Resultado y alcance

Una instancia distinta del productor revisó los seis desacuerdos. Sus juicios de
respaldo coinciden con v2 en esos seis casos. Esto apoya la interpretación de que
parte de la discordancia con AttrScore procede de diferencias en lo que se evalúa.
**No demuestra superioridad general de v2**: los casos se seleccionaron después
de observar errores y la rúbrica fue suministrada por el productor.

No se cambió el resultado original: v1 8/12 y v2 6/12 coincidencias con gold,
20 364 y 38 005 tokens respectivamente. No se calculó una nueva exactitud usando
estos juicios posteriores como si fueran una prueba reservada.

## Separación conseguida

El agente `/root/attrscore_separate_review` recibió contexto nuevo (`fork_turns:
none`), las instrucciones del proyecto y las rutas a seis fixtures. Informó haber
leído únicamente AGENTS.md, AN-KLA.md, esos seis JSON y sus TXT. No consultó gold,
runs, informes, dictámenes anteriores, web ni GLM. La primera lectura incluía el
prompt del productor embebido en los JSON; no leyó los prompts de los revisores.
Sabía que los seis casos eran desacuerdos: no hubo cegamiento sobre la selección.
La ausencia de exposición a etiquetas corresponde sólo a esa fase inicial. Tras
fijar sus juicios, leyó esta consolidación con etiquetas visibles para comprobar
atribución y límites. Solicitó precisar esa temporalidad y atribuir al consolidador
las propuestas de acción `needs_revision`; ambas correcciones se incorporaron.
Esas acciones son una derivación del principal, no campos emitidos por el revisor.

Es separación entre instancias y respecto de etiquetas según el registro de trabajo
y declaración del revisor, no aislamiento de acceso impuesto técnicamente, revisión
humana, independencia institucional ni diversidad de modelos demostrada. El modelo
efectivo de esa instancia carece de telemetría independiente. El principal preparó
la rúbrica y consolidó el resultado; el Operador conserva la autoridad de aceptación.

## Rúbrica analítica strict-fragment-multiaxis/01

Se explicita aquí para esta revisión, después del piloto original; no se presenta
como criterio prerregistrado de ese piloto ni cambia contratos de producción.

1. **Respaldo del claim completo:** todas las afirmaciones materiales deben estar
   sustentadas, incluidas fecha, cantidad, condición y atribución explícita. Se
   admiten paráfrasis e inferencias lógicas necesarias, no conocimientos externos
   ni completar contexto ausente. Una proposición material sin soporte produce
   `insufficient`. Se conserva además qué parte sí tiene respaldo.
2. **Contradicción:** incompatibilidad explícita o lógicamente necesaria. Ausencia
   de un dato no es contradicción. Aceptación, publicación y prepublicación son
   eventos distintos salvo que el texto los identifique expresamente.
3. **Pertinencia:** debe responder al sujeto, tiempo y propiedad solicitados. Un
   hecho verdadero sobre otro año puede ser `supported` y `extra`. Los casos con
   núcleo pertinente y detalles adicionales conservan una nota mixta; no se fuerza
   su totalidad a irrelevante ni se añade un enum al producto.
4. **Procedencia:** una atribución escrita permite constatar lo que afirma el
   fragmento, no autenticar su autor externo. Si la atribución está en el claim,
   también cuenta en el respaldo íntegro; registrarla por separado explica el
   fallo, no elimina esa obligación. Una URL por sí sola no autentica autoría.
5. **Salida:** detalle material insuficiente o pregunta equivocada → revisión.
   Incluso respaldo, pertinencia y procedencia satisfechos no equivalen a aprobación
   automática ni a cobertura completa del documento.

## Seis casos resueltos bajo esa rúbrica

| Caso | Gold original | Juicio separado: soporte / pertinencia | Motivo decisivo |
|---|---|---|---|
| 01 | Attributable | insufficient / relevant | Identifica el especial y año, pero no establece que sea el último. |
| 03 | Attributable | insufficient / relevant, detalles adicionales | Faltan fecha exacta y crecimiento de los brotes; ausencia de casos no acredita historia de reportes. |
| 04 | Attributable | insufficient / relevant, detalle adicional | El fragmento no menciona metilación ni plataforma Illumina 450 K. |
| 09 | Extrapolatory | supported / extra | La tasa de 2022 está respaldada; se preguntó por 2020. |
| 11 | Contradictory | insufficient / relevant | Aceptación en 2022 no excluye toda publicación en 2021; faltan afiliación y ancla de «reciente». |
| 12 | Attributable | insufficient / relevant | Tasa respaldada; atribución a la página de Lei Feng no establecida. |

En 03 se establece textualmente la atribución del aviso al CDC; en 11, la
coautoría, pero no ETH. Nada de ello autentica las fuentes externamente. El caso
04 tampoco permite convertir una estimación probabilística en diagnóstico
clínico definitivo. Son ejemplos históricos de evaluación, no información médica
actual. En 12 una rúbrica que excluyera procedencia del soporte produciría otro
juicio; aquí se incluye porque forma parte expresa de la afirmación evaluada.

## Comportamiento final, separado de support

Conteo descriptivo posterior de las 24 salidas existentes, sin nuevas llamadas:

| Recomendación | v1 | v2 |
|---|---:|---:|
| needs_revision | 9 | 12 |
| needs_adjudication | 2 | 0 |
| Fallo estructural sin recomendación | 1 | 0 |

No es una métrica de exactitud: no existe gold separado para esta acción. En
particular `needs_adjudication` no significa aprobación. El contador original
`unsupported_accepted` mide discordancia entre gold y support, no aceptación
operativa. Sus valores se conservan con esta advertencia interpretativa.

## Consecuencia práctica y siguiente prueba

Mantener v1 como predeterminado existente y v2 experimental. El problema encontrado
no justifica relajar v2 para coincidir artificialmente con gold ni desplegarlo
como filtro final. Pedir revisión en todo puede ocultar incapacidad para reconocer
casos válidos; rechazar más no es, por sí mismo, mayor calidad.

El siguiente bloque recomendado es pequeño: **seis pares de controles nuevos**,
con dos ejemplos por dimensión (respaldo, pertinencia y procedencia). Cada par
cambia sólo una propiedad y conserva un positivo completamente sustentado. Las
expectativas se fijan antes de llamar al proveedor y se mantienen separadas del
payload. Ejemplos y respuestas de este piloto no se reutilizan como prueba nueva.
La procedencia se evalúa como atribución textual; autenticación externa queda
fuera de ese ensayo.

Criterios: cada versión debe reconocer tanto el positivo como el defecto del par;
registrar omisiones de defectos, rechazos de positivos, fallos de formato y consumo
por separado. Reportar acierto del par completo además del caso individual: pedir
siempre revisión no puede aprobar el control positivo. Ningún resultado de seis
pares demuestra generalización. Antes de ejecutar, fijar materiales y expectativas;
si la inspección encuentra ambigüedad, resolverla antes de generar dictámenes.
Sólo después conviene ampliar una muestra externa reservada. Los controles son
una herramienta diagnóstica propia, no un benchmark público ni resultados oficiales.

## Verificación y límites operativos

Se verificaron el freeze completo, la igualdad del código de producto con el
congelado, los 24 hashes de resultados contra el ledger, sus hashes semánticos de
candidatos y la igualdad de los seis fixtures leídos con los congelados. El registro
adjunta hashes del gold, audit y freeze. No se modificaron esos archivos.

AN-KLA verificó rev 3; el contexto mostró la advertencia preexistente de cambio
fuera del bloque administrado. La recuperación utilizó scan-fallback y un checkpoint
histórico, no prueba del estado actual. El bloqueo lector requirió ejecutar la
lectura fuera del sandbox restringido; no se alteraron registros ni controles.

Este incremento sólo añade el registro y este informe, y enlaza desde el anterior.
Sin nuevas llamadas GLM, cambios de producto, memoria, commit o push. Las 270 pruebas
corresponden al incremento anterior; no se presentan como pruebas nuevas de esta
revisión documental. No se promueve ni publica ninguna versión.
