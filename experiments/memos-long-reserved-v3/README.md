# Comparación v3: nuevas fuentes, español y revisión separada

## Resultado

Campaña ejecutada: dos documentos QASPER nuevos en el historial local, cuatro
preguntas, mismas fuentes/preguntas y respuestas en español. GLM 5.3 Flash fue
reportado en ambos recorridos; Jev 1.13.0 revisó las respuestas anonimizadas contra
la fuente completa. Una ejecución por caso, sin reintentos ni segunda lectura.

No hay ganador global ni promoción automática. MemOS suministró más detalle útil
en algunas respuestas; ambos omitieron información y la revisión Jev no resolvió
todas las discrepancias. El cambio de proveedor no convierte la revisión en una
garantía ni en adjudicación humana independiente.

## Qué se fijó y qué sigue siendo diferente

- Fuentes: 1901.05415, 45 557 bytes; 1905.10039, 41 435 bytes. Selección por orden
  de ID no visto en artefactos locales, tamaño 40–100 KB y primeras dos preguntas.
  No se afirma ausencia en entrenamiento ni representatividad estadística.
- Preguntas originales en inglés, iguales en ambos sistemas; respuestas solicitadas
  en español. Máximo 4096 tokens de respuesta y 180 s por llamada, temperatura 0.
- Ágora: 12 000 bytes de pasajes, top-k 6, control de alcance activo, cuatro llamadas.
  Todos los resultados quedaron como `candidate_requires_expansion`.
- MemOS: fuente completa ingerida una vez en cubo nuevo; búsqueda con filtro de
  memorias activas, top-k 10 y relativity 0.1; 14 HTTP y seis recibos LLM.
  El límite de respuesta no se interpreta como límite del extractor interno.
- Jev: dos llamadas, una por documento; nombres de productores ocultos y orden de
  candidatos aleatorio. Evaluó respaldo frente a fuente completa, cobertura y
  claridad. No recibió etiquetas humanas ni nuestras valoraciones.
- Los prompts y mecanismos de recuperación siguen siendo diferentes. Es comparación
  de recorridos configurados, no experimento que aísle una sola variable causal.
- La preparación inicial encontró títulos de sección nulos. Se normalizaron a texto
  vacío antes de congelar; no hubo llamadas al proveedor en ese intento.

## Resultados por pregunta

Las etiquetas de esta tabla son **salidas del revisor**, no veredictos aceptados.

| Pregunta | Jev: Ágora | Jev: MemOS | Contraste con referencias y fuente |
|---|---|---|---|
| Cómo se estima satisfacción | Respaldada / completa | Respaldada / completa | Ambas explican predicción, pero omiten la obtención de etiquetas con evaluadores y escala 1–5 pedida en las referencias humanas. Interpretación/cobertura por adjudicar. |
| Cuánto mejoró el rendimiento | No respaldada / omisión | Respaldada / completa | Jev marca la pregunta ambigua. Una referencia humana busca 9.4 puntos/31% en diálogo; otra, 0.28/0.42 F1 del clasificador. MemOS ofrece la primera, Ágora la segunda y limita su lectura. No convertir estas etiquetas en un ganador resuelto. |
| Qué métricas se usaron | Respaldada / omisión | No respaldada / omisión | La fuente define exact match del esquema, exact match de límites y Rouge-1; ambos dejan información fuera. Ágora recuperó 3/5 párrafos de referencia pero no explicó ambas variantes exact match. |
| Qué modelos se compararon | No respaldada / omisión | Respaldada / completa | MemOS enumera familias de baselines, pero al final habla de dos trabajos distintos —HiStGen y WIKIOG— cuando la fuente suministrada es un solo artículo. Jev no lo señaló. Ágora no recuperó la lista completa. |

El texto QASPER contiene `INLINEFORM` y `TABREF`; algunas etiquetas de métricas y
modelos no se conservan legibles. No debemos exigir que el modelo invente los
subíndices ausentes. Sí podemos exigir que preserve las definiciones disponibles.
La coincidencia literal de un párrafo se usa como diagnóstico de recuperación,
no como medida completa de recall semántico.

En la pregunta de mejora, los pasajes de Ágora no contienen 9.4 ni 31%. Su declaración
limitada a esos pasajes no debe reinterpretarse como ausencia en toda la fuente.
Se conserva el juicio discrepante de Jev, sin corregirlo ni repetirlo hasta que
coincida con el productor. Las probabilidades devueltas por Jev se archivan como
salida del proveedor, no como confianza calibrada de la evaluación.

## Coste observado

| Tramo | Tokens | Tiempo acumulado de peticiones |
|---|---:|---:|
| MemOS: ingestión | 25 548 | 70.18 s |
| MemOS: consultas | 5 490 | 73.77 s |
| MemOS: total generación | 31 038 | 143.95 s |
| Ágora: consultas | 16 928 | 100.77 s |
| Jev: revisión de ambos | 26 646 | Registrado por llamada en review-results.json |

Jev se contabiliza aparte, sin asignar artificialmente la mitad de tokens a cada
sistema. Coste monetario, infraestructura y embeddings no calculados. Los tiempos
son sumas por tramo, no latencia total del bloque, y compartieron máquina/proveedor.
La fuente local completa puede leerse para recuperar pasajes aunque sólo parte
llegue al LLM. Menos tokens no implica mayor fidelidad.

## Interpretación y próximos pasos

1. El banco ya admite una revisión separada de otro proveedor con identidades
   ocultas, pero aún necesita adjudicar discrepancias importantes. Un revisor
   automático adicional no sustituye una referencia explícita por pregunta.
2. Resolver primero las dos ambigüedades observadas: cómo se estima frente a cómo
   se etiqueta satisfacción, y mejora de diálogo frente a mejora de clasificación.
   Cualquier reformulación abrirá otra prueba; no cambia los resultados congelados.
3. Preparar controles con errores pequeños pero decisivos: intercambio de métricas,
   confusión entre estudios y omisión de calificadores. Incluir sus controles
   correctos antes de confiar decisiones de aceptación al revisor.
4. Probar segunda lectura con presupuesto separado sobre las omisiones verificadas,
   manteniendo coste acumulado y versión original. Esta campaña no la ejecutó.
5. Repetir después en fuentes nuevas y con evaluación externa suficiente. Una única
   ejecución de cuatro preguntas no acredita superioridad estadística.

AN-KLA y Skopos mantienen los controles por función de la matriz previa. No se
reinterpretan como participantes generadores de estas ocho respuestas, ni se
presenta una integración de todo ARIA que esta campaña no ejecutó.

## Artefactos

- freeze.json y protocol.json: configuración previa y hashes de ejecutores.
- cases.json: preguntas e identidad de fuentes; references.json: etiquetas humanas
  saneadas, mantenidas fuera del contexto de generadores y revisor.
- comparison.json: respuestas y evidencia recuperada; assessment.json: contraste
  del productor, explícitamente sin adjudicación independiente.
- review-results.json: resultados originales Jev; blind-key.json y review-labels.json:
  correspondencia revelada después para auditar. No son secretos de acceso.
- http-receipts.json, agora-receipts.json y memos-usage.json: contabilidad y trazas
  saneadas sin credenciales ni razonamiento del generador.
- Los requests completos Jev y originales permanecen en
  `/tmp/memos-long-reserved-v3-ready`; no se publican documentos completos.

El cegamiento es parcial: Jev no recibe nombres, pero el estilo de respuesta puede
revelar el origen; además ve las dos respuestas por pregunta. El productor preparó
el protocolo y realizó el contraste posterior. No hubo adjudicador humano separado.
Los ejecutores conservan rutas locales: no son instaladores portables ni deben
repetirse como si fueran verificadores sin coste o efectos.
