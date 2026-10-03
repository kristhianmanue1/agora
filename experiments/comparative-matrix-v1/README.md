# MemOS frente a AN-KLA, Ágora y Skopos

## Conclusión

Sí hay un banco operativo para comparar capacidades concretas. No hay todavía
una evaluación suficiente para declarar un ganador global, sustituir un componente
ni considerar al conjunto ARIA una integración desplegada.

MemOS tiene el recorrido de extracción, almacenamiento, búsqueda y conversación
funcionando en esta instalación local. AN-KLA tiene evidencia más específica de
transiciones gobernadas. Ágora permite fijar fuentes, citar pasajes y declarar una
lectura parcial, pero eso no asegura fidelidad. Skopos conserva y localiza fuentes;
la interpretación de esas fuentes es una función distinta que debe evaluarse.

## Matriz de resultados

«No probado» significa ausencia de evidencia en esta comparación, no ausencia de
la función en el producto. «Limitado» identifica una propiedad demostrada sólo en
las condiciones descritas. Las columnas corresponden a componentes, no a sustitutos
con las mismas responsabilidades.

| Propiedad | MemOS local con parches | AN-KLA 0.1.0b24 | Ágora | Skopos |
|---|---|---|---|---|
| Conservar una fuente y volver a ella | Original conservado en metadatos de casos cortos; memorias derivadas omiten detalles | Conserva registros suministrados e historia; no se probó como capturador automático | Fuente fijada por hash, pasajes y posiciones exactas | Texto y hash exactos en dos turnos Codex; prueba adicional de transcripción diarizada |
| Responder preguntas | Operativo, con omisiones y detalles inventados observados | No evaluado como generador de respuestas | Operativo con citas, abstención y lectura parcial; omisiones e inversión de cifras observadas | Su analizador existe; no se comparó aquí su calidad de respuestas |
| Corregir información y consultar lo vigente | Feedback local corregido y filtro `activated` demostrados en campaña previa; no equivale a consulta vigente por defecto | `supersede` retira el registro anterior de la consulta vigente y conserva su revisión | Detecta cambios de fuente; no se probó consolidación automática general | `search` sobre índice y `query` con comprobación de fuente son contratos distintos; MongoDB no se revalidó aquí |
| Recuperar estado de trabajo | No probado con un contrato equivalente | Checkpoint y resume comprobados | No probado como checkpoint equivalente | No probado como checkpoint equivalente |
| Rechazar operaciones obsoletas o no permitidas | No probado como control de acciones equivalente | Planes obsoletos rechazados; deny/allow y argv modificado por `attest` | Rechaza fuente modificada; no es bloqueo general de herramientas | Parser experimental rechaza entrada inválida y fuente modificada; no es control de acciones |
| Hacer visible una lectura incompleta | Abstenciones textuales observadas; sin garantía contractual equivalente probada | Expone recuperación de registros; no evalúa suficiencia semántica de un documento | `requires_expansion` y `document_absence_established:false` comprobados | Preservar una transcripción no acredita que audio, hablantes o acuerdos sean correctos |
| Fallos conocidos | Extracción malformada puede aparentar éxito vacío; parche limita una causa. Confusión Cohen/Fleiss en respuesta | Pruebas no cubren host hostil, bypass directo ni concurrencia multiproceso | Cita literal válida no detectó inversión precisión/recall; recuperación omitió respuestas presentes | No se ha demostrado aquí ingesta universal ni interpretación fiable de reuniones |
| Estado de integración | API local operativa | Biblioteca/CLI probada en laboratorio | Prototipo ejecutable y CLI | Parsers y funciones de consulta; prueba actual acotada |

## Pruebas nuevas de este bloque

- **AN-KLA:** reproducción nueva en stores sintéticos: supersede, revisión histórica,
  checkpoint/resume, planes obsoletos y control real deny/allow/argv modificado.
  Todos los asserts pasaron. Sólo el control `attest`; no controla comandos que
  el harness ejecute directamente. Ninguna escritura en la memoria habitual.
- **Skopos y Ágora:** dos fuentes sintéticas de contradicción y corrección;
  captura exacta, hash correcto, pasajes exactos y rechazo de fuente alterada.
- **Ágora:** cuatro tests de alcance de lectura pasaron, incluidos modos literal
  e identificadores y recuperación vacía.
- **Skopos:** cuatro tests del parser diarizado pasaron: posiciones UTF-8,
  tiempos/entradas inválidas, fuente modificada y no inferir fecha desde el nombre.
  Es código experimental local sin seguimiento; no se presenta como publicación
  ni como prueba de reconocimiento de audio o identidad de hablantes.
- **MemOS:** dos peticiones de lectura: salud del servicio y get_all del cubo de
  regresión. Continúa activo en 9696 y conserva cinco memorias; hashes del parche
  siguen iguales. Las respuestas y sus errores proceden de la regresión previa,
  no de llamadas nuevas en este bloque.

**Cero llamadas nuevas a modelos en este bloque.** No se presenta la evidencia
histórica como una nueva campaña simultánea para los cuatro sistemas. La revisión
semántica acumulada es del productor contra referencias externas, no independiente.

## Costes observados: campañas separadas

| Campaña | MemOS: ingestión | MemOS: consultas | MemOS: total | Ágora: consultas | Condición |
|---|---:|---:|---:|---:|---|
| Largos v1, dos documentos / cuatro preguntas | 30 135 | 5 218 | 35 353 | 15 780 | Incluye dos rechazos Ágora; antes del control de alcance |
| Largos v2, dos documentos / cuatro preguntas | 33 560 | 5 291 | 38 851 | 13 792 | Incluye una ingestión MemOS vacía y dos abstenciones por sistema |
| Regresión tras activar parche, un documento / dos preguntas conocidas | 13 534 | 1 682 | 15 216 | No ejecutado en ese bloque | Cinco memorias; respuesta con error Cohen/Fleiss |

Unidades: tokens reportados por el proveedor. Incluyen razonamiento y fallos.
No incluyen coste monetario calculado, energía, infraestructura ni embeddings
monetizados. Ágora realiza lectura local del documento: sus tokens de contexto
LLM no miden todos los bytes leídos por el sistema. Las campañas usan prompts y
mecanismos diferentes; v2 respondió en español con Ágora y en inglés con MemOS.
No se deriva un porcentaje global de ahorro, fidelidad ni amortización.

AN-KLA y la captura Skopos aquí comprobada no usaron LLM. Comparar ese cero con
el coste de generar una respuesta sería comparar trabajos distintos. Skopos sí
puede utilizar un modelo para análisis, fuera del tramo medido en esta matriz.

## Qué decide esta evidencia

1. **Mantener MemOS como referencia operativa de memoria conversacional.** Es
   útil para comparar el recorrido, pero las memorias extraídas no reemplazan
   automáticamente los originales ni sus verificaciones.
2. **Mantener separados los contratos.** La combinación futura sería: Skopos
   aporta fuentes; Ágora prepara representaciones/evidencia; AN-KLA conserva
   continuidad y transiciones gobernadas. Esta combinación sigue siendo una
   dirección arquitectónica, no una integración demostrada por estas pruebas.
3. **Priorizar fidelidad y fallos visibles.** El mayor riesgo observado ya no
   es arrancar el servicio: es perder un detalle, completarlo indebidamente y
   responder con apariencia de respaldo. La verificación literal de citas y
   la validación JSON no resuelven por sí solas ese riesgo.

## Siguiente batería para una comparación más fuerte

Congelar antes de ejecutar fuentes, preguntas, referencias, versiones, idioma,
presupuestos, número de repeticiones y criterios de aceptación. No reutilizar
los casos vistos como si fueran reservados. Separar:

- **Captura:** bytes, localizadores, versiones, rechazo de fuente cambiada y
  conservación de incertidumbre. Skopos frente a la ruta de entrada de MemOS.
- **Recuperación y respuesta:** mismas fuentes/preguntas/idioma, medición de
  evidencia recuperada, omisiones y afirmaciones sin respaldo. Ágora frente a
  MemOS; contar ingestión, consulta y segunda lectura por separado y acumuladas.
- **Continuidad:** corrección explícita, vista vigente, historia y recuperación
  de tarea. AN-KLA frente a las funciones MemOS que realmente expongan esos
  contratos; si no hay equivalente verificable, marcar no comparable.
- **Robustez:** JSON inválido, cero memorias, fallo de red, repetición accidental
  y operación obsoleta. El fallo debe ser visible y no confundirse con éxito.

La evaluación externa debe revisar afirmaciones y excepciones, no sólo números
de citas ni coincidencias de palabras. Más de un intento por caso permitirá
observar variabilidad; no se fija ahora un umbral estadístico sin diseñar muestra.

## Evidencia

- `refresh.json`: comprobaciones nuevas, versiones, estado local y límites.
- `matrix.json`: matriz estructurada y hashes de antecedentes consultados.
- `../memos-long-reserved-v2/`: campaña congelada y fallos conservados.
- `../memos-activation-v1/`: activación y regresión posterior, separada.
- `../scope-vigency-repair-v1/`: filtro vigente y ampliación explícita anteriores.
- `../ankla-transitions-v1/`: ejecutor reproducible y alcance del control.

Los parches MemOS siguen locales; Skopos tiene cambios locales preexistentes.
Las revisiones Git por sí solas no identifican esos cambios, por eso refresh.json
conserva el estado observado y los hashes pertinentes. El manifiesto del banco
verifica integridad relativa a sus hashes, no verdad semántica ni autenticidad
frente a quien pueda editar a la vez datos y manifiesto.
