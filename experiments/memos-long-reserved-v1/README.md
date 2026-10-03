# Reparación local de feedback y documentos largos reservados

> Corrección posterior: [scope-vigency-repair-v1](../scope-vigency-repair-v1/README.md)
> comprobó que el filtro anterior tenía forma incorrecta. Con la sintaxis nativa
> sí se separan activos y archivados. Se conservan debajo observaciones históricas.

## Resultado principal

El fallo de escritura de feedback se reprodujo, se identificó contra logs/código y
se corrigió en una instancia temporal. No queda validado el recorrido completo de
vigencia: search todavía devolvió archivados, incluso al pedir filter status activated.
El benchmark largo terminó: cuatro consultas, sin reintentos ni ajuste posterior.
Ambos sistemas tienen omisiones. Este bloque no autoriza sustituir componentes.

## Reparaciones realizadas en MemOS

Base a7367d07e55db61099f7b4e2c1108bc5831a24f3 más configuración local preexistente.
El log del cubo original registró AttributeError: Neo4jCommunityGraphDB carecía de
search_by_keywords_like. Se añadió consulta parametrizada, con cubo obligatorio y
estado activo. Regresión: tres errores antes; tres tests pasan después.

La primera verificación real con ese arreglo recuperó un recuerdo, pero _doc_filter
lo descartó: el clasificador interpretó el proyecto Cedar como nombre de documento.
Se modificó process_feedback_core para que solicitudes con retrieved_memory_ids
explícitos sigan la ruta semántica que recibe esos IDs, sin ir al reemplazo global
por nombre de archivo. Regresión: un test falla antes y pasa después.

Ambos parches están en el checkout de MemOS, SIN commit/push. Copia exacta y tests
bajo feedback-fix/. Se preservaron cambios previos en docker-compose, settings,
uv.lock y el lanzador. No se cambiaron rutas públicas, dependencias ni esquemas.
La instancia habitual 9696 no se reinició: mantiene el código cargado anteriormente;
un reinicio posterior podría cargar estos cambios locales. No confundir código
editado con despliegue autorizado/completado.

Instancia de ensayo 127.0.0.1:9697, mismo grafo/vector, sólo cubos nuevos. No es un
backend físicamente aislado ni una prueba de aislamiento multiusuario. Se cerró
al terminar. Cuatro tests stdlib pasan. make format falló porque falta Poetry;
pytest y Ruff tampoco están instalados. No se instalaron paquetes ni se eludieron
hooks. No hay gate completo ni publicación del parche de MemOS.

## Verificación de feedback y límites

En el último cubo, feedback devolvió dos operaciones update; las versiones antiguas
quedaron archived y las nuevas contienen Wednesday replacing Tuesday, historical
only. get_all mostró cuatro registros activos con el texto corregido y dos archivados:
no se atribuye el duplicado a una causa no investigada. La búsqueda devolvió tanto
activos como archivados. Pedir filter status activated devolvió aún archivados.
También persiste una fecha especulada desde la ingestión original. Por tanto:
**escritura corregida en el caso, fidelidad y recuperación sólo vigente pendientes**.
La API sigue pudiendo convertir otros errores internos en operaciones vacías; no
se cambió su contrato público ni se certifica que HTTP 200 implique aplicación.

## Documentos reservados y protocolo

QASPER test local: 1601.03313 (45163 bytes) y 1602.07563 (63243 bytes), primeras dos
preguntas de cada uno. Selección por ID ordenado y tamaño 40-100 KB, excluyendo IDs
hallados en artefactos experimentales previos; ver freeze.json. Reserva respecto a
ese historial local, no garantía de que un proveedor nunca entrenó con los artículos.
No es benchmark ciego independiente. Referencias no enviadas a modelos ni usadas
para seleccionar documentos. Se consultaron después de terminar Ágora, mientras
la última consulta MemOS ya fijada seguía en ejecución; no se modificó nada.

MemOS temporal con parches: dos cubos nuevos, una ingestión por artículo, get_all,
search+chat por pregunta; 14 HTTP, cero reintentos, timeout 180 s, max_tokens 2048,
relativity 0.1, top_k 10, sin internet ni memoria de respuestas.
Ágora base 35b04fbad98feb28628fddf3ccfabe1672677c31: passage_cli real, GLM 5.3 Flash,
cuatro llamadas, 12000 bytes de lectura por pregunta, top_k 6, max_tokens 2048,
timeout 180 s, temperatura 0. No reparación de respuestas rechazadas en este bloque.
Los prompts/rutas difieren: comparación de sistemas configurados, no del modelo solo.
Skopos no intervino en este bloque; su prueba de captura está en el expediente anterior.

## Omisiones y respuestas

| Caso | Ágora | MemOS |
|---|---|---|
| Corrección gramatical | Omite método POS y afirma que no hay más detalle | Omite método POS; dice que la información disponible no lo especifica |
| Transiciones entre frases | Rechazo: salida incompleta al llegar a 2048 tokens | Recupera evaluación manual 0-3 |
| Orden de clases de sentimiento | Rechazo: salida incompleta, aun teniendo evidencia seleccionada | Omite aumento de acuerdo del 18% y comparación de medidas |
| Tamaño suficiente de datos | Omite las dos respuestas de referencia y da otros ejemplos | Recupera aproximación de 100000 anotaciones con cautela |

Juicio del productor contra anotaciones QASPER, no revisión independiente ni nota
estadística. MemOS: 2/4 respuestas centrales recuperadas, 2/4 omisiones críticas.
Ágora: 2/4 rechazos y 2/4 respuestas candidatas con omisión crítica. No se excluyen
rechazos del denominador ni se equipara cita válida con respuesta suficiente.

Referencias de tamaño discrepan por alcance: estimación general 100000 y ejemplo
polaco 150000. No se fuerza una cifra única. El texto conserva placeholders de
fórmulas/tablas del dataset; una evidencia de tabla no textual no se cuenta como
párrafo disponible. En las cuatro preguntas sí hay evidencia textual relevante.

Recall literal de párrafos gold en la selección Ágora, tras deduplicar: 0/1, 1/2,
1/1 y 0/2. Es cobertura de evidencia anotada, no recall semántico universal. La
omisión en q1 y q4 empieza en recuperación; el rechazo q3 ocurre pese a recuperar
el párrafo decisivo. comparison.json conserva respuestas, citas y métricas.

## Coste medido: ingestión y consultas

| Medida | MemOS | Ágora |
|---|---:|---:|
| Tokens LLM de ingestión observados | 30135 | Sin ingestión LLM persistente en esta ruta |
| Tokens LLM de cuatro consultas | 5218 | 15780 |
| Total LLM observado | 35353 | 15780 |
| Tiempo de ingestión | 86.30 s | Lectura local incluida en cada consulta |
| Tiempo sumado de consultas | 54.93 s | 95.83 s |

MemOS creó cinco recuerdos por artículo. Los tokens se extrajeron de responses del
proveedor en logs vinculados por x-trace-id, deduplicados por response id: dos llamadas
de ingestión y cuatro de respuesta. Cero eventos LLM observados en search/get_all;
no equivale a coste cero de embeddings o infraestructura. Modelos reportados y usage
están en memos-usage.json. No se publican logs globales, secretos ni razonamiento.

Ágora seleccionó 11633, 10245, 7688 y 9625 bytes por consulta. Lee cada archivo
completo localmente para verificarlo/buscar; esa reducción NO representa ahorro de
lectura total del sistema. Sus 15780 tokens incluyen los dos intentos rechazados.
MemOS paga ingestión inicial y puede reutilizarla: cuatro consultas no establecen
punto de amortización. No se midieron coste monetario, embeddings, almacenamiento,
consumo energético ni recuperación posterior a cambios. No extrapolar un ganador
por tokens, tiempo o calidad de sólo estos dos documentos.

## Recomendación concreta

1. Mantener el parche de MemOS como candidato local; cerrar filtro de vigencia,
   duplicados y gates antes de promoverlo al servicio habitual.
2. En Ágora, usar evidencia de suficiencia/segunda lectura antes de declarar ausencia
   en todo el documento; mejorar cobertura del párrafo decisivo y distinguir esa
   omisión de agotamiento de salida. No aumentar presupuesto a ciegas.
3. Reservar estos casos como regresiones ya vistas. Un siguiente benchmark necesita
   documentos nuevos; no volver a llamar reservados a estos mismos artículos.

Scripts exactos, freezes y resultados están en este expediente; rutas de laboratorio
quedaron fijadas en scripts. runs/ guarda fuentes públicas, gold y respuestas locales
excluidas de Git. No se ejecutó una segunda reproducción de la campaña. No se
modificó producto Ágora, no hubo nueva integración ni revisión independiente.
