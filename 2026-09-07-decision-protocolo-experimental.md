---
id: decision-protocolo-experimental
autor: OpenAI Codex
fecha: 2026-09-07
proyectos: [agora, aria]
estado: borrador
derivado_de: [proposal, decision-identidad-agora]
---

# Ágora: protocolo experimental y decisiones pendientes

Documento para definir el experimento y las decisiones todavía abiertas. La
solicitud humana actual autoriza preparar este artefacto; no constituye aprobación
de la arquitectura física, construcción del motor, integración con otros productos
ni commit o push. Complementa `proposal`, que conserva su condición de borrador.
La identidad del producto se concilió en `decision-identidad-agora`; este
protocolo sigue siendo borrador y no sustituye las reglas de `AGENTS.md`.

## 1. Identidad fijada y decisiones pendientes

Reconocer Ágora como el sistema independiente de transformación y memoria
estructurada, incluida su superficie de exposición deliberada de artefactos
atribuidos. Motor y superficie son responsabilidades distintas dentro del mismo
producto y se relacionan mediante contratos; no requieren procesos ni
repositorios separados. El experimento puede ser un único proceso local con
módulos internos.

Independiente significa que Ágora puede ingerir, transformar, consolidar,
consultar y publicar sin Skopos, AN-KLA ni otros componentes de Aria. No significa
que deje de ser memoria ni que se renuncie a integrarla posteriormente en la
memoria de agentes de IA.

Cuatro actos permanecen separados: incorporar una fuente, producir o consolidar
una memoria derivada, publicar un resultado en la superficie de Ágora y admitirlo
en AN-KLA u otra memoria de continuidad de un agente. Ninguno implica
automáticamente el siguiente.

**Resultado que se busca:** una persona consulta documentación técnica versionada,
obtiene respuestas con evidencia localizable y puede reconocer qué conclusiones
necesitan revisión cuando cambia una sección.

## 2. Alcance del primer experimento

- Entre tres y cinco documentos técnicos en texto o Markdown, con dos versiones
  controladas y cambios conocidos. Usar material público o sintético sin secretos.
- Una representación de fragmentos originales y una síntesis por sección.
- Consulta de hechos, síntesis entre secciones, excepciones, cambios temporales
  y preguntas cuya respuesta no está en las fuentes.
- Actualización de una fuente existente y conservación de sus versiones.
- Ejecución local, sin servicios de Skopos o AN-KLA. Las llamadas al proveedor de
  modelo deben ser explícitas, configurables y contabilizadas.

Quedan fuera del primer experimento: PDF/OCR, Excel, navegación web, audio,
jerarquía arbitraria L1…Ln, agentes autónomos, interfaz gráfica, publicación
automática, integración de memoria y detección general de contradicciones.
H4 se probará sólo para independencia y los formatos aquí admitidos; no se
afirmará soporte heterogéneo general.

## 3. Contratos mínimos de arquitectura

| Objeto | Información y comportamiento exigidos |
|---|---|
| Fuente | Identidad lógica, versión/hash, contenido preservado y fecha de incorporación; validez temporal sólo si está declarada por la fuente |
| Unidad de evidencia | Identificador, versión exacta de fuente, rango/localizador y fragmento original verificable |
| Transformación | Identificador de ejecución, entradas exactas, versión de código y plantilla, proveedor/modelo y parámetros disponibles, salida conservada, costo y resultado |
| Derivado | Contenido, entradas utilizadas, transformación productora y estado de actualización |
| Respuesta | Afirmaciones con referencias a evidencia; ausencia de respaldo explícita cuando corresponda |
| Publicación | Selección deliberada de una versión revisable, atribución y metadatos de Ágora |

Los hashes verifican identidad de contenido, no su verdad. Registrar un modelo y
sus parámetros permite auditar una ejecución; no garantiza repetir sus palabras.
Conservar las salidas originales es obligatorio para comparar corridas.

Separar estado de ejecución (pendiente/completa/fallida), actualización
(actual/pendiente de recálculo) y revisión (sin revisar/revisada). El `estado` del
front-matter pertenece al artefacto publicado y no reemplaza estos ejes.

El grafo de cálculo debe ser acíclico y registrar todas las entradas usadas,
incluidos versión de transformación y criterios de agrupación. Relaciones como
“contradice” son semánticas y no se confunden con dependencias de cálculo.

Un cambio invalida los derivados alcanzables por dependencias; un cambio de
segmentación puede invalidar una sección o documento completo. No prometer
granularidad menor que la que el contrato puede justificar. Incorporar una fuente
nueva no descubre conflictos por recorrer el grafo anterior.

Los reintentos no deben duplicar la publicación de un mismo resultado lógico.
Una interrupción deja una ejecución fallida o pendiente, nunca una versión parcial
presentada como completa. Los derivados pendientes no se usan como actuales.
El contenido de las fuentes se trata como datos, incluso si contiene instrucciones.

Cada consulta fija una revisión del corpus que enumera versiones de fuentes,
derivados e índice de recuperación compatibles. Una actualización se prepara
aparte y se activa como unidad completa. Si falla, se conserva la revisión anterior
identificada como tal; no se anuncia como actualizada ni se mezclan versiones.
El piloto no necesita concurrencia: puede bloquear consultas durante la activación.

El índice también depende del corpus y debe actualizarse. Si se guardan respuestas,
su clave incluye revisión del corpus, consulta y configuración; una fuente nueva
puede cambiar la recuperación aunque no existiera una arista hacia ella. No
reutilizar respuestas entre revisiones basándose sólo en sus citas anteriores.

La interfaz futura de publicación debe distinguir una descripción histórica de
una revisión concreta de una afirmación sobre el estado actual. El motor entrega
un informe de artefactos potencialmente afectados; un responsable designado revisa
y retira deliberadamente los que dejaron de ser vigentes, conforme a la regla 3
de Ágora. Una etiqueta de obsolescencia no basta. El piloto prueba ese traspaso con
un registro simulado, sin publicar, retirar ni sincronizar artefactos reales.
La integración futura no estará lista hasta probar también su recorrido real.

## 4. Diseño de evaluación

Preparar 40 preguntas iniciales, ocho por categoría: hechos, síntesis, excepciones,
cambios temporales y ausencia de respuesta. Destinar 20 al desarrollo y 20 a
evaluación reservada, con cuatro de cada categoría en cada partición.

Antes de generar respuestas, fijar para cada pregunta la versión consultada,
respuesta esperada, evidencia necesaria, excepciones y errores críticos.
Separar por familias de preguntas: una paráfrasis o la misma pregunta sobre otra
versión no puede quedar en la partición contraria. Compartir documentos entre
particiones limita la conclusión a consultas nuevas sobre ese corpus; no prueba
generalización a documentos nuevos. Un custodio ajeno al ajuste prepara y conserva
preguntas y respuestas reservadas fuera del acceso de los implementadores. Sin
esa separación, el conjunto se declara de desarrollo y el resultado provisional.
Cualquier filtración o ajuste posterior obliga a declarar que dejó de ser reservado.

Comparar cuatro métodos:

1. Fuente completa, sólo en documentos que quepan en contexto; registrar los casos
   no aplicables en lugar de truncarlos silenciosamente.
2. Recuperación plana ajustada con el conjunto de desarrollo.
3. Resúmenes por sección usados directamente para responder.
4. Resúmenes por sección con recuperación descendente de evidencia original.

Todos reciben la misma revisión del corpus y pueden emitir citas con el mismo
formato de localizador. Los resúmenes llevan referencias preservadas durante su
generación; el método 3 responde sólo con resúmenes y esas referencias, mientras
el 4 puede recuperar los fragmentos originales. Ambos usan los mismos resúmenes
congelados: así se aísla la contribución de descender a evidencia. El método plano
comparte fragmentación y modelo de recuperación con el candidato cuando aplique.

Fijar un subconjunto común donde todos los métodos comparados sean aplicables.
Reportar aparte los documentos que no caben en contexto; sus puntuaciones no se
mezclan con las del primer subconjunto para proclamar un ganador. Seleccionar en
desarrollo un comparador por subconjunto: mayor calidad sin errores críticos,
desempatando por menor costo de consulta. Si ninguno es elegible, revisar el
diseño antes de abrir el reservado, en vez de usar un comparador débil.
Designar antes de ejecutar un subconjunto principal con representación de las
cinco categorías en desarrollo y reservado; sólo éste decide el avance. Si no
puede formarse, rediseñar el corpus antes de evaluar. Los demás subconjuntos son
descriptivos y no compensan un fallo del principal. Informar además la comparación
pareada con recuperación plana en todo el reservado, sin atribuir a fuente completa
resultados de documentos que no pudo procesar.
Congelar la pertenencia de preguntas a subconjuntos de aplicabilidad disjuntos e
informar su tamaño por categoría. La comparación adicional contra recuperación
plana es un análisis global separado. No cambiar el subconjunto principal tras
abrir el reservado.

El cuarto método es el candidato experimental. Si gana, una fase posterior podrá
comparar jerarquías más profundas y referentes como RAPTOR. Este piloto no prueba
superioridad frente a todos los sistemas RAG o GraphRAG.

Usar el mismo modelo de respuesta, límite de salida y rúbrica. Versionar las
plantillas específicas de cada método y dar a los comparadores un presupuesto de
ajuste equivalente. Fijar configuraciones antes de abrir la evaluación reservada.
Ejecutar tres corridas de consulta por método; para las consultas reservadas son
hasta 240 respuestas. Mantener fijos índices y resúmenes entre esas corridas:
la variación medida será de consulta, no de construcción del índice ni de síntesis.
Registrar hashes de los objetos reutilizados y declarar este límite en el informe.

La unidad primaria es la pregunta: no tratar las tres corridas como tres preguntas
independientes. Presentar resultados por categoría, dispersión entre corridas y
comparaciones pareadas. Veinte preguntas reservadas sólo permiten una decisión
exploratoria; no certifican márgenes pequeños de equivalencia.

### Rúbrica y mediciones

- Puntuar corrección, cobertura y conservación de excepciones: 0 = incumple,
  1 = cumple parcialmente, 2 = cumple todos los puntos anotados para ese eje.
  Marcar excepciones como no aplicable cuando no existan y excluir ese eje del
  denominador. En preguntas sin respuesta, la salida esperada es abstención
  fundamentada y cobertura evalúa reconocer los límites, no inventar contenido.
  Normalizar primero por pregunta a 0–100 y promediar con igual peso por categoría.
  Reportar también cada componente y categoría; el promedio no oculta fallos críticos.
- Etiquetar cada afirmación como respaldada, contradicha o sin respaldo; admitir
  “ambigua” y enviarla a revisión en lugar de fabricar certeza.
- Verificar mecánicamente que cada cita resuelve a contenido exacto. Después
  evaluar si ese contenido realmente sostiene la afirmación.
- Marcar como críticos: invertir una prohibición, perder una excepción decisiva,
  presentar contenido obsoleto como actual o inventar una respuesta sin evidencia.
- Hacer revisión humana de la evaluación reservada con métodos ocultos y orden
  aleatorio; ocultar etiquetas no garantiza ceguera completa por diferencias de
  estilo. Un segundo revisor resuelve casos ambiguos y críticos antes de revelar
  métodos. Registrar desacuerdos. Sin revisión humana disponible, la fase reservada
  queda pendiente; una evaluación sólo por modelo no habilita avance.
- Medir tokens, costo monetario observado y latencia de ingesta, consulta y
  actualización, junto con volumen almacenado y tiempo de mantenimiento.

Para cada respuesta, calidad = 100 × suma de puntuaciones / (2 × número de ejes
aplicables). Promediar sus tres corridas por pregunta, las preguntas por categoría
y las cinco categorías por igual. Un error crítico en cualquier corrida activa el
criterio de fidelidad aunque el promedio sea alto. Para tokens usar la suma de
todos los pasos de consulta en las mismas preguntas y corridas pareadas; ahorro =
1 − tokens del candidato / tokens del comparador. Informar aparte costo y latencia.

Estos ejemplos fijan la interpretación inicial; el custodio prepara anclas
específicas del corpus antes de puntuar, sin mostrarlas a quienes ajustan el sistema:

| Categoría y respuesta observada | Corrección / cobertura / excepciones | Calidad y observación |
|---|---|---|
| Hecho: entrega el valor y unidad exactos exigidos | 2 / 2 / N/A | 100; cita y respaldo se verifican aparte |
| Síntesis: todos los enunciados son correctos, pero omite uno de dos puntos exigidos | 2 / 1 / N/A | 75; incompleta |
| Excepción: afirma que la regla es universal y omite la excepción decisiva | 0 / 1 / 0 | 16,7; error crítico que impide avance |
| Cambio: usa el valor anterior como si perteneciera a la versión actual | 0 / 0 / N/A | 0; error crítico |
| Sin respuesta: se abstiene e identifica correctamente lo que las fuentes no permiten establecer | 2 / 2 / N/A | 100; no recompensa inventar una respuesta |

Para Q consultas y U actualizaciones, informar costo total = ingesta + suma de
consultas + suma de actualizaciones. Presentar escenarios de uso y el punto de
amortización cuando exista; no elegir Q después para favorecer al candidato.
Preseleccionar un escenario principal de Q y U según el uso esperado. Los tokens
de consulta incluyen todos los pasos internos, entradas y salidas; el costo total
incluye extracción, resúmenes, embeddings, recuperación con modelos y reintentos.
El tiempo humano se informa por separado, sin convertirlo en dinero con una tarifa
implícita. La suma de costos se usa para decidir viabilidad en el escenario principal.

## 5. Criterios de avance y parada

Estos criterios son una propuesta previa a la implementación. Su aceptación y el
presupuesto monetario exacto deben quedar registrados antes de ejecutar modelos.

| Dimensión | Criterio |
|---|---|
| Procedencia estructural | 100 % de citas resolubles y cero entradas inexistentes en las pruebas controladas |
| Fidelidad | Cero errores críticos observados en el conjunto reservado; informar siempre tamaño de muestra y errores no críticos |
| Utilidad exploratoria | En el subconjunto principal y frente a su comparador fijado: al menos 20 % menos tokens de consulta, sin caída observada de calidad global ni por categoría; costo total no mayor en el escenario principal preseleccionado |
| Actualización | Ningún derivado afectado omitido frente al conjunto esperado anotado; medir recálculo extra y costo frente al recálculo completo |
| Independencia | Recorrido completo desde un entorno documentado sin componentes ni configuración privada de Aria |
| Recuperación ante fallos | Reintento sin duplicados lógicos; interrupción sin resultados parciales expuestos como completos |

Avanzar exige cumplir conjuntamente todos los criterios: utilidad únicamente en
el subconjunto principal; fidelidad en todo el reservado; integridad, actualización,
independencia y recuperación en sus pruebas controladas. Un fallo no se compensa
con otro resultado favorable. La conclusión de utilidad queda limitada al alcance
del subconjunto principal y no se extiende a los descriptivos.

El umbral de utilidad sólo habilita un estudio mayor: ausencia de caída observada
no demuestra equivalencia estadística ni garantiza calidad fuera de la muestra.
Se retira el margen inicial de dos puntos por falta de justificación para esta
rúbrica y tamaño de muestra. El 20 % es un objetivo operacional propuesto, no un
umbral científico; debe aceptarse antes de ejecutar. Este criterio tampoco satisface
literalmente H1, que exige mayor fidelidad. No reinterpretar H1 retroactivamente.

Comparar actualización contra recálculo completo con operadores deterministas
para comprobar el grafo. Con modelos, comparar integridad, evidencia y calidad;
no exigir identidad textual de generaciones independientes.

Anotar el conjunto esperado de afectados sin generarlo desde el grafo que se
prueba. Cubrir cambio de hecho, eliminación, inserción, división/fusión de sección,
cambio de plantilla y modificación sin efecto. Incluir una nueva sección con una
excepción fuera de los fragmentos antes recuperados que cambie la respuesta y la
recuperación, para probar el índice sin atribuirle detección semántica
de contradicciones. Medir derivados que debían cambiar y no cambiaron, trabajo
innecesario y fallos de activación. Cero omisiones es un requisito de corrección;
la eficiencia incremental es una medición separada, no una garantía por diseño.

Detener la corrida ante errores de integridad, contaminación del conjunto
reservado o agotamiento del presupuesto. No hacer una afirmación de ventaja si
falla un criterio. Una corrección requiere nueva versión y repetir las pruebas
afectadas; si se usó el reservado para corregir, preparar otro reservado.

Limitar el piloto a una implementación y una ronda de ajuste en desarrollo. Si
no aparece ventaja, documentar el resultado y decidir entre simplificar, ampliar
la evaluación con una razón concreta o cerrar la hipótesis para este caso de uso.
Un resultado negativo no prueba inutilidad universal; uno positivo tampoco
autoriza industrialización.

## 6. Secuencia de trabajo y entregables

| Paso | Entregable | Condición para continuar |
|---|---|---|
| 1. Fijar frontera interna | Identidad ya decidida: motor de memoria y superficie son partes de Ágora; falta elegir estructura física y límites de módulos | Arquitectura revisable y autorización explícita de construcción |
| 2. Congelar evaluación | Corpus, versiones, preguntas, rúbrica y errores críticos | Custodio y revisores disponibles; partición por familias; manifiesto con hashes y reservado inaccesible al ajuste |
| 3. Congelar contratos | Esquemas, oráculo de invalidación, fallos, escenario Q/U, límites monetario y de horas | Valores concretos registrados; contratos revisables y autorización de construcción/ejecución |
| 4. Recorrido completo | Ingesta → síntesis → consulta con evidencia → cambio → actualización | Integridad, aislamiento y recuperación de fallos comprobados |
| 5. Comparación | Resultados por método y categoría, costos y límites | Criterios aplicados sin ajustes retrospectivos |
| 6. Decisión de continuidad | Avanzar, simplificar o cerrar, con evidencia | Autoridad nueva para ampliar alcance o integrar productos |

No hace falta construir un catálogo ni un marco genérico de agentes para realizar
este experimento. La estrategia de binarios debe decidirse antes de incorporar
el primero a Ágora; el piloto de texto permite posponer esa inversión.

## 7. Trabajo sobre la superficie documental actual

El validador del front-matter sigue siendo una mejora acotada y distinta del
motor. Antes de implementarlo, aclarar seis campos siempre presentes más
`superado_por` condicional, y cómo resolver referencias a artefactos retirados
de la superficie. Una posibilidad es un índice de referencias históricas
reconstruible desde Git; requiere decisión, no se introduce en este documento.

Ese validador puede comprobar forma, unicidad y referencias. No demuestra por
sí mismo vigencia semántica, veracidad ni autorización de publicación.

## 8. Fundamentos y límites de las fuentes externas

- [RAPTOR](https://arxiv.org/abs/2401.18059): antecedente de agrupación y resúmenes
  recursivos; impide presentar la jerarquía por sí sola como novedad.
- [GraphRAG](https://www.microsoft.com/en-us/research/publication/from-local-to-global-a-graph-rag-approach-to-query-focused-summarization/):
  antecedente para preguntas globales sobre un corpus; no demuestra la utilidad
  de este candidato ni reemplaza su evaluación.
- [W3C PROV](https://www.w3.org/TR/prov-overview/): referencia para entidades,
  actividades y responsables; no certifica que una inferencia esté respaldada.
- [Dependencias en Bazel](https://bazel.build/versions/7.1.0/concepts/dependencies):
  referencia sobre dependencias reales y declaradas; su aplicación a este motor
  es una analogía de diseño, no una prueba de invalidación semántica.
- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents):
  respalda comenzar con flujos simples y añadir complejidad según evaluación.

Estas fuentes informan la propuesta. Los umbrales, alcance y decisiones aquí
planteados son recomendaciones para este experimento, no estándares externos.

## 9. Ronda adversarial del 7 de septiembre

Revisión fresca por un segundo agente sin conversación previa, contrastada con
una revisión local. Se afinó este mismo borrador para evitar dos versiones activas.

| Hallazgo aceptado | Corrección incorporada |
|---|---|
| Dependencias registradas no cubren información antes ausente | Revisión de corpus e índice, activación coherente y prueba de una excepción nueva fuera de las citas previas |
| Puntuación y comparador admitían elecciones retrospectivas | Fórmula, ejemplos, tratamiento de N/A, desempate y subconjunto principal predefinidos |
| La partición podía filtrar preguntas y exagerar generalización | Familias separadas, custodio y límites explícitos al corpus evaluado |
| Tres corridas podían ocultar una síntesis inicial afortunada | Índice congelado declarado; variabilidad de preparación no evaluada |
| Invalidar un derivado no retira una publicación obsoleta | Informe de afectación, responsable de retirada y simulación del traspaso |
| Ahorro de consulta podía ocultar costo total o falsa precisión | Escenario Q/U, costos completos, límite de horas y retiro del margen de dos puntos |

La revisión afina un protocolo para decisión; no es validación empírica del motor.
Dictamen final del revisor independiente, tras verificar las correcciones:
**apto para decisión humana, sin bloqueos dentro del alcance revisado**. La
segunda lectura cerró además la cobertura del subconjunto principal y la regla
conjunta de avance. Este dictamen no autoriza construcción ni ejecución.
Permanecen por resolver estructura física, fronteras de módulos, niveles de
memoria, configuración de CLI y modelos, corpus, personas revisoras, presupuesto y
aceptación de los criterios antes de construir y ejecutar.
