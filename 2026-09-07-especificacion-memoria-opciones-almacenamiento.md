---
id: especificacion-memoria-opciones-almacenamiento
autor: OpenAI Codex
fecha: 2026-09-07
proyectos: [agora, aria]
estado: borrador
derivado_de: [proposal, decision-identidad-agora, decision-protocolo-experimental]
---

# Memoria estructurada: especificación técnica y dos opciones de almacenamiento

Propuesta técnica para el núcleo experimental independiente de Ágora descrito en
`decision-protocolo-experimental`. La solicitud actual autoriza incluir MongoDB
como opción 2 y realizar revisión adversarial. No selecciona definitivamente un
backend ni autoriza construir, desplegar o publicar en Git. Independiente describe
su operación sin otros componentes de Aria, no un producto separado de Ágora.

## 1. Decisión recomendada

**Opción 1: SQLite para el piloto local. Opción 2: MongoDB para un servicio
compartido cuando exista ese requisito y capacidad de operarlo.** Ambas deben
cumplir el mismo contrato de evidencia y revisiones. No se exige implementar las
dos para empezar ni demostrar una migración entre ellas en el primer piloto.

| Dimensión | Opción 1 — SQLite | Opción 2 — MongoDB |
|---|---|---|
| Encaje inicial | Un proceso local, corpus pequeño | Servicio accesible por varios procesos o equipos |
| Modelo | Tablas y relaciones explícitas | Colecciones con documentos acotados y referencias |
| Integridad | Restricciones SQL y verificación del dominio | Validadores, índices únicos y verificación del dominio |
| Activación de revisión | Transacción local corta | Transacción corta en replica set, con política de lectura/escritura explícita |
| Operación | Archivo local y procedimiento de respaldo | Servidor, topología, acceso, monitoreo y respaldo |
| Índice de recuperación | FTS5 opcional o recuperador independiente | Recuperador independiente para comparar almacenamiento; búsqueda nativa requiere evaluación propia |
| Motivo para elegir | Menor superficie operativa en el piloto | Necesidad concreta de servicio compartido o infraestructura MongoDB ya verificada |

Varios clientes no demuestran por sí solos que SQLite sea insuficiente, ni que
MongoDB haga falta. La elección definitiva depende de concurrencia de escritura,
latencia, disponibilidad y esfuerzo operativo medidos. Esta tabla no es un benchmark.

## 2. Núcleo común

Python con versión soportada y dependencias fijadas, biblioteca más CLI JSON,
contratos Pydantic estrictos y esquema de intercambio versionado. Modelos y
recuperadores son adaptadores; el núcleo no importa Skopos ni AN-KLA.

| Entidad | Contrato mínimo |
|---|---|
| Source | Identidad lógica y procedencia del documento |
| SourceVersion | Source, bytes originales, hash de contenido y fecha de incorporación |
| EvidenceUnit | Versión exacta, rango de bytes UTF-8 y fragmento verificable |
| TransformationRun | Identidad de ejecución, entradas, versión de operador/plantilla, modelo/configuración, salida preservada y costo |
| DerivedRepresentation | Síntesis por sección, afirmaciones y sus referencias particulares |
| Dependency | Salida y entradas de cálculo, incluidas configuración y reglas de segmentación |
| CorpusRevision | Manifiesto de versiones, derivados e índice compatibles |
| QueryRun | Consulta, revisión fijada, unidades recuperadas, respuesta y métricas |

Identidad lógica, hash de bytes e identidad de ejecución son distintos. No usar
ObjectId o claves SQL como contrato externo: los identificadores del dominio son
cadenas opacas generadas por el motor y preservadas al exportar.

Cada estructura tiene `schema_version`. Las referencias incluyen identificador y
versión exacta cuando corresponda. Los hashes de estructuras usan una codificación
canónica documentada y probada; nunca el JSON/BSON serializado por defecto del backend.
Las fechas de incorporación y los intervalos de validez declarados por las fuentes
son campos diferentes. Ausencia de validez temporal se representa explícitamente.

Separar ejecución, inclusión en revisión, evaluación semántica y revisión humana.
Una puntuación del recuperador no representa confianza en la verdad. Una referencia
resoluble no demuestra respaldo semántico. Las salidas originales del modelo se
preservan: volver a ejecutar no garantiza el mismo texto.

El piloto admite texto UTF-8 y Markdown, sin transformación silenciosa del original.
Si normalizar cambia coordenadas, producir un objeto separado con correspondencia
al original. Segmentar por estructura y conservar orden y pertenencia a sección.
El grafo de cálculo es acíclico; las relaciones semánticas se mantienen separadas.

## 3. Revisiones, fallos y límites de concurrencia

El piloto permite un solo constructor/activador por corpus en ambas opciones.
Contenido de versiones y derivados completados es inmutable por contrato del
servicio; usuarios con acceso directo a la base podrían violarlo. Verificar hashes
detecta divergencias de contenido; no convierte al almacén en evidencia inviolable.
No se contempla borrado ni recolección de objetos en el piloto.

1. Capturar fuentes y preparar objetos de una revisión candidata no visible.
2. Calcular afectados y generar derivados fuera de transacciones largas.
3. Construir un índice asociado a esa revisión; validar miembros, hashes y referencias.
4. Sellar el manifiesto y el índice: después no se alteran sus miembros.
5. Activar con comparación de la revisión anterior esperada, registrando resultado
   y revisión activa en una transacción corta. Si cambió la base, abortar y reevaluar.

El contrato de almacenamiento expone preparar objetos, sellar revisión, activar
contra base esperada, leer por revisión e inspeccionar operación. No filtra al
dominio sesiones MongoDB ni conexiones SQL. La activación escribe el resultado
durable de la operación y el puntero activo en la misma transacción. Se rechaza
reutilizar un identificador de operación con entradas distintas: se vincula a un
digest de solicitud que incluye corpus, revisión candidata y base esperada.

Cada consulta resuelve la revisión activa una sola vez y conserva ese identificador.
Todas sus lecturas e índices deben corresponder al manifiesto fijado. No se promete
leer la última revisión en presencia de una activación concurrente; sí una completa
y declarada. La antigua permanece consultable y no se anuncia como actualizada.

Fallo de preparación conserva la revisión activa anterior. Una respuesta perdida
durante activación obliga a inspeccionar por identificador de operación. Encontrar
el resultado confirma la activación histórica aunque luego cambie el puntero;
no encontrarlo todavía no demuestra abort. El estado público es indeterminado
hasta obtener resultado confirmado o aborto confirmado por el protocolo del backend.
Ante commit MongoDB incierto, usar el reintento del mismo commit/sesión según el
driver, con plazo acotado; no crear otra operación para eludir la incertidumbre.
Un error transitorio que requiere repetir la transacción es un caso distinto del
commit desconocido: la repetición conserva identidad y solicitud, vuelve a comprobar
la base y consulta primero si existe resultado confirmado.
Si vence el plazo, conservar el identificador y reportar indeterminado, bloqueando
nuevas activaciones de ese corpus hasta reconciliar. No inferir durabilidad de un
timeout ni declarar éxito por observar sólo objetos preparados.
[Reintentos de transacciones PyMongo](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/crud/transactions/)

Reintentos de persistencia no repiten llamadas al
modelo dentro de callbacks transaccionales. No se promete una única ejecución
remota cuando un proveedor pierde la respuesta de una solicitud.

Una inserción puede cambiar la recuperación aunque no figure entre las citas
anteriores. Índices y cachés incluyen revisión de corpus y configuración; una
respuesta nunca se reutiliza entre revisiones por conservar sus citas anteriores.

## 4. Opción 1: perfil SQLite

Datos originales y metadatos se almacenan juntos para el corpus pequeño. Tablas
con restricciones de unicidad, claves foráneas activadas por conexión y tipos
estrictos donde apliquen. Verificar versión efectiva de SQLite y capacidades al
iniciar; no asumirlas por la versión de Python.

Transacciones de escritura cortas, archivo en almacenamiento local y parámetros
de durabilidad registrados. WAL sólo si se necesita concurrencia entre lectores y
escritor; no habilita múltiples escritores simultáneos ni un archivo compartido
entre equipos. [SQLite WAL](https://www.sqlite.org/wal.html)

FTS5 es un índice derivado opcional. Debe buscar sobre el corpus de la revisión
fijada; filtrar resultados antiguos después de calcular un ranking global no basta
si otras revisiones alteran sus estadísticas. Para el piloto se puede reconstruir
un índice aislado por revisión, con costo contabilizado.
[FTS5](https://www.sqlite.org/fts5.html)

Usar un respaldo consistente mediante la API de backup y probar restauración en
un destino vacío. Una copia de archivos en uso no sustituye ese procedimiento.
[SQLite Backup](https://www.sqlite.org/backup.html)

En ambas opciones, registrar si el índice está dentro de la base o es externo.
Un respaldo de base no incluye por sí solo archivos externos. Preservar salidas
de modelos, vectores si existen y configuración exacta; incluir los índices externos
sellados o reconstruirlos de esos objetos sin nuevas llamadas al modelo. Restaurar
no habilita consultas hasta verificar manifiesto e índice. La preparación de un
índice externo debe confirmar su persistencia antes de activar la revisión.

## 5. Opción 2: perfil MongoDB

Colecciones para las mismas entidades del dominio. Incrustar sólo atributos
acotados que se leen juntos; evidencias, ejecuciones, dependencias y miembros de
revisión no forman arrays de crecimiento indefinido dentro de un único documento.
El manifiesto puede referenciar documentos de pertenencia separados con conteo y
digest verificados. El límite BSON es 16 MiB por documento; hay que fijar límites
del piloto por debajo de él, incluyendo metadatos y codificación. Los objetos que
excedan el límite se rechazan explícitamente; GridFS/blobs se decidirían en otra
fase. [Límites MongoDB](https://www.mongodb.com/docs/manual/reference/limits/)

La opción propuesta requiere un replica set para transacciones entre documentos;
un servidor standalone no satisface este perfil. Antes de seleccionar despliegue,
fijar versión/FCV, driver, topología y comportamiento ante pérdida de nodos. Tener
replica set no demuestra alta disponibilidad por sí mismo.
[Transacciones](https://www.mongodb.com/docs/manual/core/transactions-production-consideration/)

Propuesta para la activación: `readPreference=primary`, `readConcern=snapshot` y
commit con `writeConcern={w: majority, j: true}`, comprobando compatibilidad de la
topología elegida. Los objetos preparados también deben tener confirmación durable
antes de activar. Cada consulta usa una sesión causal, primary y lectura majority
desde la resolución del puntero hasta la última lectura, manteniendo su orden
causal aun al reintentar. Referencias ausentes producen error, nunca omisión
silenciosa. Inmutabilidad, ausencia de
borrado y manifiesto sellado permiten terminar una consulta sobre su revisión aun
si se activa otra. No confundir esa coherencia con una promesa de lectura más reciente.
[Write concern](https://www.mongodb.com/docs/manual/reference/write-concern/),
[Lecturas](https://www.mongodb.com/docs/manual/core/read-isolation-consistency-recency/)

La sesión causal evita retroceder a una lectura anterior a la del puntero; no
garantiza que ese puntero sea el más reciente. Si la sesión se pierde, reiniciar
la consulta completa sin mezclar resultados parciales.
[Sesiones causales](https://www.mongodb.com/docs/manual/core/causal-consistency-read-write-concerns/)

Un índice único protege identificadores y claves de idempotencia; la existencia de
referencias y ausencia de ciclos se verifica en el dominio antes del sellado. Los
validadores de colección no son claves foráneas. Las restricciones efectivas se
prueban con escrituras inválidas. [Índices únicos](https://www.mongodb.com/docs/manual/core/index-unique/)

MongoDB implementa JSON Schema draft 4 con diferencias y extensiones BSON. No
instalar directamente un esquema de intercambio de otro dialecto: mantener una
traducción explícita y casos comunes de aceptación/rechazo, incluidas fechas,
enteros, campos desconocidos y nulos. El contrato externo es independiente de BSON.
[$jsonSchema](https://www.mongodb.com/docs/manual/reference/operator/query/jsonSchema/)

El respaldo del piloto se toma sin escritores, sobre la base completa y mediante
herramientas compatibles con la versión seleccionada; verificar restauración en un
destino vacío, manifiestos, contenido e índices. Este procedimiento no demuestra
recuperación a un instante ni disponibilidad continua. Credenciales fuera de
artefactos y registros; acceso limitado al corpus del experimento.

## 6. Recuperación y comparación justa

Contrato común: consulta + revisión + filtros + presupuesto → unidades, puntajes,
método, configuración y traza. No equiparar FTS5, búsqueda textual de MongoDB y
servicios de búsqueda/vectoriales por compartir una etiqueta de “búsqueda”.

Si se comparan backends, reproducir las mismas entradas y lecturas con objetos y
salidas del modelo congelados. Usar el mismo recuperador independiente sobre el
mismo corpus; separar latencia de almacenamiento, recuperación y generación.
No atribuir al backend una mejora obtenida cambiando ranking, modelo o corpus.
Las prestaciones de búsqueda nativa se evalúan en un experimento distinto, con
versión, despliegue, costo y visibilidad del índice explícitos. No se presupone su
disponibilidad ni su participación en una transacción de la base.

Para el piloto de memoria sigue vigente la comparación de cuatro métodos del
protocolo. Si se incorpora búsqueda semántica, vectores congelados y búsqueda
exacta bastan para el corpus pequeño; mismo adaptador para candidato y comparador.
La jerarquía permanece fragmentos → síntesis por sección, sin profundidad arbitraria.

## 7. Criterios técnicos y elección

| Prueba | Resultado exigido en cualquier backend implementado |
|---|---|
| Referencias/bytes | Toda cita resuelve al fragmento exacto y revisión correcta |
| Activación interrumpida | Revisión anterior o nueva completa, nunca combinación |
| Conflicto de base | Activación contra revisión anterior incorrecta es rechazada |
| Resultado perdido | Resultado confirmado o indeterminado explícito; ausencia del registro no se interpreta como aborto |
| Desconexión de activación | Fallos antes y después del commit mantienen identidad de operación y no crean una segunda activación |
| Cambio de primary | Consulta conserva causalidad o reinicia sin mezclar resultados; no continúa con una sesión perdida |
| Cambio de fuente/índice | Una excepción nueva fuera de citas antiguas afecta la consulta |
| Aislamiento de ranking | Añadir revisiones históricas no cambia recuperación de la revisión fijada |
| Reintento | Sin duplicación lógica; costos remotos inciertos declarados |
| Datos inválidos | Tipos inválidos rechazados al ingresar; referencias inexistentes y ciclos impiden sellar/activar |
| Respaldo | Restauración de base e índice externo, o reconstrucción sin modelos, devuelve la misma evidencia bajo ranking/configuración congelados |

Antes de medir, fijar límites de corpus y objeto, presupuesto de horas/dinero,
concurrencia objetivo y presupuesto de latencia. No inventar objetivos de escala
para favorecer una opción. Una comparación de backends aplica el mismo límite de
tamaño del contrato a ambos y reporta por separado los límites físicos de cada uno.
El perfil local con un escritor favorece SQLite por
simplicidad operativa; MongoDB pasa a preferido si existe una necesidad de servicio
compartido y su despliegue satisface los mismos contratos con costo aceptado.

No hay mediciones aún. Una implementación futura comienza con un solo backend;
la interfaz de dominio permite evaluar el otro cuando haya una razón concreta.
El siguiente paso de diseño es fijar la estructura física, los niveles de memoria,
la configuración de CLI y modelos y las fronteras internas de Ágora, seguido de
congelar contratos y evaluación según el protocolo.

## 8. Revisión adversarial

Revisión fresca de un segundo agente, sin memoria ni conversación anterior,
contrastada con documentación oficial y una revisión local.

| Hallazgo aceptado | Afinación incorporada |
|---|---|
| Ausencia de resultado no demuestra aborto de activación | Estado indeterminado, digest de solicitud, reintentos diferenciados y pruebas de desconexión |
| Lecturas majority aisladas no expresan orden causal | Una sesión causal por consulta y prueba de cambio de primary |
| Backup de base puede omitir índices externos | Inventario de componentes, preservación/reconstrucción y verificación antes de servir |

El revisor independiente confirmó el cierre de los tres hallazgos y la
correspondencia de las pruebas. **Dictamen final: apto como especificación de diseño
y apoyo a la decisión, sin nuevos bloqueos sustantivos.** Versiones, topología y
contratos ejecutables se concretarán al autorizar implementación.

No se ha implementado ni medido ningún backend. La comparación sigue siendo una
recomendación para decisión, no una certificación de durabilidad o disponibilidad.
