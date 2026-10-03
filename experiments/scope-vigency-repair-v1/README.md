# Vigencia MemOS y alcance de lectura Ágora

## Corrección del diagnóstico de MemOS

El ensayo anterior pidió filter {"status":"activated"}. resolve_filter_for_cube
interpreta claves simples como nombres de cubo. La forma común es
{"and":[{"status":"activated"}]}; alternativamente, un mapa por cubo.
No se cambió código MemOS en este bloque: corregimos la invocación del ensayo.
El formato correcto devolvió un recuerdo activo y ningún archivado. El control
inverso con status archived devolvió los dos registros archivados. Chat con filtro
activo respondió Wednesday y fecha exacta desconocida, tratando Tuesday como historia.
Tres solicitudes sobre el cubo sintético previo; sin nuevas escrituras de contenido.
Las consultas pueden registrar uso interno, por lo que no se afirma store inmutable.

Esto enmienda la interpretación de memos-long-reserved-v1: aquel resultado no probaba
que un filtro correctamente expresado fuera ignorado. La búsqueda sin filtro no es
una vista de vigentes; no inferir vigencia por posición o relevancia. La forma simple
se descarta silenciosamente, lo que sigue siendo un riesgo de integración. No se
modificó el contrato/API ni se certifica todo el filtrado multiusuario.

Instancia temporal 9697, con los dos parches locales anteriores, cerrada al terminar.
9696 no se reinició. Parches MemOS siguen sin publicar, sin gate completo de Poetry/
Ruff/pytest; este bloque no levanta esas limitaciones ni elimina inferencias/duplicados.

## Cambio de producto Ágora

query_passages(..., scope_guard=True) y CLI --scope-guard activan
agora/passage-query/v0.3. Contratos previos conservan su comportamiento sin el flag.
Se declara reading_scope al modelo y se registran answer_scope, requires_expansion,
document_absence_established=false. Una lectura parcial con respuesta válida queda
candidate_requires_expansion, aunque la cita sea literal. La respuesta original se
conserva para inspección; no se reescribe ni se atribuye soporte semántico automático.

Es una condición de uso para consumidores de v0.3, no un sandbox ni un detector
semántico de frases falsas. El consumidor debe respetar requires_expansion antes de
cerrar una pregunta sobre la fuente completa. No autoriza llamadas automáticas ni
conclusiones globales. La CLI imprime el estado; exit 0 informa ejecución terminada,
no aceptación de una conclusión. coverage partial se trata conservadoramente, incluso
si lo único excluido fueran separadores de párrafos.

## Pruebas

Dos nuevas regresiones fallaron antes y pasan después. Suite completa: 527 tests,
OK. Se repitieron localmente las dos respuestas erróneas conservadas: ambas quedan
candidate_requires_expansion bajo v0.3. Replay no significa nuevas respuestas LLM.

Se hicieron luego dos lecturas completas explícitas con la CLI real: artículos
1601.03313 y 1602.07563, mismos hashes y preguntas del ensayo previo; max_output_tokens
4096, timeout 180 s, presupuesto fuente 100000 bytes y prompt 131072. GLM reportó
glm-5.3-flash. Ambas completaron como candidate, sin reintentos ni reparación de
salida. Recuperaron POS/matching/manual fallback y 100000 anotaciones con ejemplo
polaco de 150000. Juicio del productor sobre puntos centrales de gold; no revisión
independiente de cada afirmación añadida. semantic_support sigue not_verified.

Consumo de estas dos llamadas: 10601 + 16062 = 26663 tokens. La recuperación costó
más que la primera lectura parcial. No es un benchmark reservado nuevo: se eligieron
dos fallos conocidos, se aumentó alcance de fuente y límite de salida, y se cambió
la instrucción de alcance. No podemos atribuir causalmente la mejora a una sola
variable. Los otros dos rechazos del benchmark anterior no se reejecutaron aquí.

## Pendientes y siguiente uso

Usar --scope-guard en este consumidor y ampliar lectura explícitamente si se quiere
responder sobre toda la fuente. Falta integrar selección de segunda lectura con
presupuesto/coste apropiado en más recorridos; no se cambia el predeterminado de
otras CLI. En MemOS, expresar filtro nativo correcto y verificar estados devueltos.
No promover sus parches locales hasta completar gates y revisión de integración.

result.json publica respuestas/citas/consumo e identidad de fuentes; runs/ conserva
los registros completos locales fuera de Git. run_agora.py conserva la secuencia
exacta con rutas locales: no ejecutarlo sobre el directorio ya existente. No se ha
realizado una segunda reproducción en un laboratorio limpio.
