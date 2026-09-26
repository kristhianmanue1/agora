# Piloto externo AttrEval-GenSearch — 01

## Objetivo y procedencia

Comparar el revisor v1 con el revisor por detalles v2 sobre afirmaciones y etiquetas
externas, sin generar respuestas nuevas. No se evalúa recuperación, español ni
capacidad general de Ágora sobre documentos largos.

Fuente: [AttrScore, autores OSU-NLP](https://github.com/OSU-NLP-Group/AttrScore),
artículo *Automatic Evaluation of Attribution by Large Language Models* (Yue et
al., 2023). Datos: [osunlp/AttrScore](https://huggingface.co/datasets/osunlp/AttrScore),
archivo `AttrEval-GenSearch.csv`, revisión
`467dcdd2cd31f9b5e8625491f3bdf7af90943a8d`.
La ficha de esa revisión declara Apache 2.0 y versión de datos 0.2, con correcciones
de anotaciones anteriores. Se conservan ficha, CSV y hashes en `inputs/download.json`.
No se descarga entrenamiento ni se ejecuta código remoto. El conjunto se usa
localmente; no se republican sus textos en este informe.

El CSV fijado contiene **242 filas**: 81 `Attributable`, 33 `Contradictory` y
128 `Extrapolatory`. Etiquetas externas son referencia experimental, no verdad
infalible. Sus correcciones históricas y posibles ambigüedades deben conservarse.

## Muestra fijada

Doce ejemplos: cuatro por categoría. Identidad por SHA-256 de query/answer/reference,
orden por hash con semilla `agora-attrscore-pilot-01`, sin repetir pregunta normalizada
no vacía ni referencia exacta. Orden final por hash, sin nombres de caso que revelen
la categoría. Todos los 242 registros caben en los límites del consumidor: no hubo
exclusiones por tamaño o campos vacíos. La muestra es de desarrollo, no un nuevo
conjunto de prueba independiente ni el benchmark completo.

Se mantienen **íntegros y en inglés** pregunta, respuesta y referencia. Cada
respuesta original es una afirmación del consumidor; v2 puede dividirla por
detalles. La referencia completa se incorpora como una cita literal. Los casos
son fixtures verificadas localmente, no generaciones nuevas de GLM. No se traducen,
parafrasean, recortan ni resuelven URLs con fuentes actuales.

Mapa de etiquetas:

| Dataset | Ágora, propiedad `support` |
|---|---|
| Attributable | supported |
| Contradictory | contradicted |
| Extrapolatory | insufficient |

`Extrapolatory` no se mapea a `relevance: extra`. La pertinencia y el idioma pueden
aparecer en los dictámenes, pero no tienen etiquetas de referencia en esta batería
y no forman parte de la exactitud de clasificación. Tampoco existen etiquetas
por detalle: la métrica se calcula sobre la afirmación completa.

## Protocolo pareado

Mismos doce casos para v1 y v2, orden alternado de versiones por caso. Modelo
solicitado `glm-5.3-flash`, temperatura 0, máximo 8192 tokens de salida por llamada,
timeout de transporte 180 s y proceso de revisión 200 s. Máximo 24 llamadas,
196608 tokens de salida reservados; no es consumo esperado ni techo monetario
exacto. Fallo de transporte, integridad o uso desconocido detiene la tanda.
Rechazos estructurales con uso conocido se conservan y la tanda continúa.
No hay reparación, reintento ni cambio de prompts a mitad de la comparación.

El código de ambos revisores, casos, CSV, transporte y protocolo se congelan antes
de las llamadas. El CSV y `gold.json` se usan sólo para selección y puntuación;
el payload del modelo sólo lleva idioma, pregunta, aspectos, afirmación, cita y
faltantes. La auditoría comprueba igualdad exacta de ese payload con el fixture.

Las definiciones de métricas se fijaron en el protocolo antes de ejecutar.
La implementación del script de puntuación se añadió durante la corrida, con
pruebas específicas; no se afirma que ese script estuviera en el freeze inicial.
Se registra su hash al auditar. No se modifican métricas según los resultados.

## Métricas y denominadores

- Matriz de confusión de tres clases con columnas separadas `failed` y `not_run`.
- Exactitud sobre los doce casos; fallos y no ejecutados no se eliminan.
- Macro-F1: promedio no ponderado del F1 de las tres clases. Un fallo cuenta como
  clase verdadera no recuperada, nunca como predicción de evidencia insuficiente.
- Afirmaciones sin respaldo aceptadas: gold contradicted/insufficient → supported,
  sobre ocho ejemplos negativos.
- Afirmaciones respaldadas rechazadas: gold supported → contradicted/insufficient,
  sobre cuatro positivos. Fallos operativos de positivos se informan aparte.
- Cobertura de dictámenes válidos, tokens reportados y tiempo por versión,
  incluidos rechazos. Se conserva todo uso desconocido explícitamente.
- Comparación pareada: ambas correctas, sólo v1, sólo v2, ninguna, sin pareja.

Cuatro ejemplos por clase no permiten una conclusión estable ni comparar esta
exactitud directamente con resultados publicados sobre todo el dataset. No se
hacen afirmaciones de significación estadística. Un caso público puede formar
parte del entrenamiento de GLM; no se conoce esa exposición.

## Reproducción y límites

Scripts bajo `experiments/attrscore-v1/`: `fetch.py`, `prepare.py`, `run.py`,
`worker.py`, `score.py`, `audit.py`. Inputs y runs están gitignored; conservar el
expediente local es necesario para reproducir las llamadas exactas. La auditoría
reproduce validación local sin nuevas llamadas y comprueba el código actual contra
el congelado. No reemplaza adjudicación independiente de desacuerdos.

270 pruebas locales pasaron, incluidas cuatro sobre puntuación: denominadores
con fallos, separación fallo/rechazo semántico, confusión entre contradicción e
insuficiencia y rechazo de etiquetas/IDs desconocidos. No se modificó producto
para adaptarlo a los resultados de esta batería.

## Resultado observado — 2026-09-24

Las 24 llamadas terminaron sin reintentos, fallos de transporte ni truncamientos.
La auditoría verificó hashes de código/entradas congelados, payload sin etiquetas,
y reproducción local de las respuestas guardadas. Evidencia detallada:
`experiments/attrscore-v1/runs/glm-01/{freeze,execution,audit}.json` y dictámenes
por versión/caso. El proveedor reportó `glm-5.3-flash`; esto no es introspección
independiente del backend.

| Métrica | v1 | v2 |
|---|---:|---:|
| Dictámenes estructuralmente válidos | 11/12 | 12/12 |
| Coincidencias con gold original | 8/12 | 6/12 |
| Macro-F1, tres clases | 0.6984 | 0.4524 |
| Gold negativo clasificado supported | 1/8 | 1/8 |
| Gold supported clasificado insufficient/contradicted | 1/4 | 4/4 |
| Gold supported con fallo estructural | 1/4 | 0/4 |
| Tokens reportados, incluidos fallos | 20 364 | 38 005 |
| Segundos acumulados de llamadas | 277.639 | 504.130 |

Total: 58 369 tokens y 781.769 segundos de llamadas. V2 consumió un 86.6% más
tokens. No se calculó coste monetario; caché y clases de tokens impiden convertir
ese porcentaje directamente en facturación. Comparación pareada: ambas acertaron
6 casos, sólo v1 acertó 2, sólo v2 ninguno y ninguna acertó 4. No hubo casos sin
pareja. El fallo de v1 en case-01 fue `invalid_claim_review`, por campos adicionales;
no se reparó ni se puntuó el contenido rechazado como respuesta válida.

## Autorrevisión adversarial: qué significa y qué no significa

Esta revisión la realizó el mismo agente que preparó el piloto. No hubo adjudicador
independiente. La menor concordancia de v2 no demuestra por sí sola menor fidelidad:
la inspección de los desacuerdos revela diferencias entre el gold y el contrato
estricto de respaldo exclusivo en el fragmento. No se alteraron etiquetas,
métricas, prompts ni resultados después de observarlos.

- **case-09, desajuste entre respaldo y pertinencia.** La pregunta pide CVPR 2020,
  pero respuesta y referencia hablan de 2022 y coinciden en su porcentaje. Ambos
  revisores devuelven `support: supported`, `relevance: extra` y
  `recommendation: needs_revision`. El gold es Extrapolatory. El contador
  `unsupported_accepted` registra una discordancia del mapeo sobre support;
  **no demuestra una aprobación indebida del sistema**. El contrato separa dos
  propiedades que esta etiqueta no distingue. La descripción preliminar de este
  caso como aceptación sin respaldo se corrige con esta inspección.
- **case-01:** v2 cuestiona que el especial sea el más reciente, algo no establecido
  por el fragmento. El gold Attributable no cambia; la discrepancia es defendible
  bajo el contrato estricto. V1 permanece fallo estructural.
- **case-03:** v2 detecta fecha exacta y calificadores ausentes. V1 reconoce en su
  explicación que la fecha no consta y aun así marca supported. Esa contradicción
  entre razón y etiqueta importa para Ágora aunque v1 coincida con el gold.
  Exigir también ubicación geográfica explícita muestra una decisión pendiente
  sobre qué inferencias de conocimiento común admite el evaluador.
- **case-04:** ambos cuestionan plataforma y tipo de datos ausentes del fragmento,
  aunque el gold sea Attributable. Es una diferencia de alcance verificable, no
  prueba automática de que ambos revisores estén equivocados.
- **case-12:** v2 rechaza la atribución a una página personal no identificada en la
  cita. V1 la acepta por plausibilidad. El dataset incluye URL como metadato, pero
  no se envía al revisor: mejorar procedencia sería otro experimento. Una URL sola
  tampoco demuestra autoría. No se debe suplir esta ausencia por conocimiento externo.
- **case-11:** ambos marcan insuficiencia donde el gold marca contradicción: el
  fragmento anuncia aceptación en 2022 y la respuesta afirma publicación en 2021.
  Distinguir publicación previa y aceptación requiere una rúbrica explícita;
  ambos pidieron revisión, aunque fallaron la clasificación externa de tres clases.

Por tanto, el piloto demuestra viabilidad operativa y mide concordancia externa y
consumo. No demuestra que v1 sea globalmente más fiel, que v2 sea superior por
ser más estricto, ni que alguno pueda aprobar automáticamente respuestas.
Doce casos en inglés tampoco validan español, recuperación, documentos largos,
ahorro de lectura o calidad de generación. Las 270 pruebas validan comportamiento
local del software, no la corrección semántica de GLM.

## Recomendación concreta

1. Mantener v1 como opción predeterminada existente y v2 experimental; no promover
   ninguno a aprobación automática ni cambiar el producto para subir esta puntuación.
2. Antes de gastar en una muestra mayor, adjudicar los seis casos discrepantes con
   una rúbrica explícita: respaldo textual, pertinencia y procedencia por separado;
   definir inferencias permitidas y contradicción frente a ausencia de información.
   Conservar gold original y añadir la adjudicación separada, con autor y fundamento.
3. Añadir en una siguiente evaluación una métrica de recomendación final distinta
   de support. Una salida `needs_adjudication` tampoco equivale a aprobación. No
   reclasificar retrospectivamente case-09 para mejorar la exactitud publicada aquí.
4. Fijada esa rúbrica, usar una muestra nueva reservada sin duplicados respecto a
   estos doce; después considerar RAGTruth para errores localizados por fragmento.
   Ampliar la muestra ahora repetiría una comparación parcialmente desalineada.

Este incremento incorpora arnés experimental, cuatro pruebas de métricas y este
informe. No modifica código de producto ni memoria canónica. No se realizó commit
ni push; el árbol contiene además trabajo acumulado de incrementos anteriores.

### Seguimiento — revisión separada 2026-09-24

Los seis desacuerdos cuentan ahora con [revisión por una instancia separada y
rúbrica explícita](adjudicacion-attrscore-01.md). Es un análisis posterior consultivo;
conserva el gold y las métricas de este piloto. No convierte esa muestra seleccionada
en una prueba independiente ni implica ratificación humana.
