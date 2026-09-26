# Evaluación de idioma, tamaño de citas y revisión automática

## Decisión y alcance

Incremento experimental; no promoción a modo predeterminado. Se mantiene literal
por defecto y 4096 bytes para las unidades cuando se solicita `ids`. Reducir el
límite a 1024 no mejoró esta muestra. La revisión automática es separada,
provisional y puede fallar: no aprueba respuestas ni memoria.

Dos documentos QASPER v0.3 de 16–32 KB, no usados en las dos baterías iniciales
ni en el piloto anterior de IDs. Selección por ID de documento/pregunta ordenados,
elegibilidad textual y tamaño, antes de las llamadas. No son documentos grandes
representativos de todos los usos de Ágora. Corpus público: contaminación de
entrenamiento desconocida. No se calcula F1 oficial con respuestas traducidas.

- N1, `1603.07252`, *Neural Summarization by Extracting Sentences and Words*:
  pregunta si comparan con métodos abstractivos. Referencia: sí, nn-abs.
- N2, `1603.08868`: pregunta qué clasificadores entrenan. Referencia: regresión
  logística multinomial con ridge, perceptrón multicapa, SVM/SMO y J48.

Las anotaciones de referencia se conservan aparte y no entran en generación ni
revisión. Se solicita español en ambas variantes. El único parámetro distinto
entre cada par es el máximo de bytes por unidad; el orden se alterna. No hay
réplicas suficientes para una estimación estadística ni adjudicación independiente.

## Primera campaña: `runs/glm-01`

Código, protocolo y entradas congelados; GLM-5.3-flash, temperatura 0,
8192 tokens máximos de salida, timeout HTTP 180 s y proceso 200 s.
Diez llamadas, sin reintentos ni reparaciones: cuatro generaciones, cuatro
revisiones y dos revisiones de controles. Los fallos permanecen en los resultados.

| Caso y unidad máxima | Generación aceptada | Tokens generación | Bytes citados | Referencias |
|---|---:|---:|---:|---:|
| N1 / 4096 | Sí | 9934 | 3048 | 4 |
| N1 / 1024 | Sí | 9922 | 3048 | 4 |
| N2 / 4096 | Sí | 7572 | 1490 | 5 |
| N2 / 1024 | Sí | 7628 | 3097 | 7 |

Son bytes de citas reconstruidas contando repeticiones, no tamaño del paquete
JSON ni tokens de entrada. Las cuatro salidas están en español y contienen la
respuesta principal según autorrevisión contra las referencias públicas. Esto
no equivale a fidelidad de todas las afirmaciones añadidas.

Total: **54912 tokens, 265.789 s** sumando procesos medidos. Generación: 35056
tokens. Revisión: 19856 tokens, incluidos los controles y rechazos. Uso conocido
en todas las llamadas, sin timeout. Preparación y autorrevisión no entran en esos
tiempos. No se estima coste monetario con una tarifa no consultada.

### Qué detectó y qué falló

Sólo **2/6 revisiones** cumplieron el contrato de salida. Las otras cuatro
incluyeron cercas Markdown y fueron rechazadas, sin extraer ni reparar su JSON.

- Control de idioma: detectó la respuesta anterior en inglés pese a pedir español.
- Control semántico sintético: combina una afirmación correcta, una atribución al
  sujeto equivocado y una negación invertida; la revisión falló en formato.
  No cuenta como control semántico aprobado de extremo a extremo.
- N2/4096: revisión válida; marcó la regresión lineal como contenido adicional
  porque no es un clasificador. Conservó `needs_revision`.
- N1/4096, N1/1024 y N2/1024: revisiones rechazadas por formato.

La fixture semántica es una respuesta sintética deliberadamente incorrecta, no
una generación GLM. El control de idioma reutiliza intacto un resultado anterior.
Ambos son controles conocidos, no holdout.

## Autorrevisión adversarial

1. **Cita literal sin respaldo suficiente.** En N2/1024, afirmación 2 dice
   “niveles A1-C1”, pero sus dos citas sólo acreditan metodología compartida y
   cinco clases. La fuente puede contener el rango; estas citas no lo prueban.
   Los IDs siguieron siendo válidos. Riesgo residual: fragmentar puede separar
   condiciones y obliga a seleccionar unidades suficientes para cada afirmación.
2. **Más fragmentos no implica menos lectura.** Los totales citados son 4538 bytes
   con 4096 y 6145 con 1024. Se mantiene 4096. Una sola muestra no establece el
   tamaño óptimo; las citas elegidas de N1 ni siquiera cambiaron de tamaño.
3. **Veracidad y pertinencia son distintas.** La regresión lineal adicional puede
   ser fiel a la fuente y exceder la pregunta. La revisión debe conservar ambas
   dimensiones, sin convertir detalles accesorios en hechos falsos.
4. **Fallo de transporte semántico.** Un dictamen en formato no aceptado no puede
   liberar una respuesta. La recomendación favorable sigue requiriendo
   adjudicación; no existe ruta automática de publicación.
5. **Separación insuficiente para independencia.** Productor y revisor usan el
   mismo modelo; esta instancia preparó, implementó y revisó el experimento.
   No se afirma revisión independiente ni consenso.

## Reproducción

`PYTHONPATH=src python3 experiments/evidence-review-v1/audit.py` verifica hashes
congelados, referencias/offsets contra bytes originales y vínculo entre revisión
y candidato. No vuelve a llamar al proveedor ni verifica verdad semántica.
Los directorios `inputs/` y `runs/` están excluidos de Git; el protocolo operativo,
preparación y auditoría son archivos revisables del repositorio. La reproducción
completa requiere conservar los artefactos locales además de los scripts.

## Seguimiento tras corrección: `runs/format-02`

Se añadió al prompt del revisor la prohibición explícita de Markdown/cercas y
comentarios fuera del objeto JSON. No se relajó el parser ni se extrajeron objetos
desde respuestas inválidas. Además, la API rechaza un idioma explícito vacío en
vez de sustituirlo silenciosamente por el predeterminado.

Se congeló la versión corregida y se ejecutaron **tres llamadas nuevas** sobre
los controles de idioma, soporte y el caso conocido N2/1024. No son casos nuevos
ni reemplazan la primera tanda. Resultado: **3/3 dictámenes estructuralmente
válidos**, 10986 tokens y 109.171 s, sin reintentos ni uso desconocido.

- Idioma: identificó de nuevo la respuesta en inglés como `mismatch`.
- Control semántico: etiquetó correctamente las tres afirmaciones como
  `supported`, `insufficient` y `contradicted`.
- Caso real N2/1024: **falló el criterio predefinido de A1–C1**. Marcó la
  afirmación 2 como `supported` mientras su explicación reconoce que esos
  niveles no aparecen en ninguna cita. Es un falso positivo de respaldo integral,
  no un éxito por mencionar el problema en prosa. Sí señaló la regresión lineal
  como `extra`; por ello el resultado general recomendó `needs_revision`.

No debe contarse la advertencia general por otro motivo como detección del
calificativo no respaldado. Este fallo muestra que formato válido, explicación
razonable y etiqueta correcta son propiedades diferentes. El revisor conserva
`adjudication: not_performed`; ningún resultado favorable se admite automáticamente.

**Balance completo del incremento:** 13 llamadas, **65898 tokens y 374.960 s**
de procesos medidos, incluyendo controles, fallos y seguimiento. No es coste de
una sola consulta ni una prueba de ahorro. Se conservan ambos protocolos y
resultados, no una métrica combinada que oculte el cambio de prompt.

## Verificación final y continuación

**231 pruebas locales** pasaron, incluidas transmisión de parámetros de idioma y
unidad, preservación de offsets/UTF-8, rechazo de Markdown, identificadores de
citas inválidos, revisiones incompletas y ausencia de promoción del candidato.
Las pruebas con proveedores simulados comprueban comportamiento del software;
no sustituyen la evidencia de las llamadas reales.

`audit.py` verifica la primera tanda contra su código congelado;
`audit_followup.py` verifica el seguimiento y su coincidencia con el código
actual. Este último registra por separado los dos controles satisfactorios y
`real_missing_qualifier_flagged: false` como regresión observada.

**Recomendación:** conservar 4096 y revisión sólo consultiva. El siguiente
incremento debe exigir respaldo de cada detalle material de la afirmación,
separar afirmaciones compuestas e identificar detalles sin respaldo mediante
campos estructurados. Si existen esos detalles, `supported` debe ser incompatible
con ellos. Eso puede evitar contradicciones de forma, pero no demostrar que el
revisor detecte todos los detalles: seguirá necesitando controles y otra muestra.
No volver a reducir fragmentos ni ampliar corpus indiscriminadamente antes de
atender este falso positivo conocido. Una evaluación independiente sigue pendiente
para cualquier promoción, y no forma parte de la autorrevisión aquí realizada.
