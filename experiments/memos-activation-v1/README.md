# MemOS: activación en 9696 y regresión del documento conocido

Se reinició el proceso habitual con el lanzador existente y el mismo directorio
de trabajo, `/Users/krisnova/www/aria/llavero`. No se desinstaló ni se borraron datos.
El nuevo proceso respondió a /health. Código local incluye la reparación limitada
de comas sobrantes en JSON, previamente validada con 75 tests del lector.

En un cubo nuevo, el documento conocido 1801.05617 (45 390 bytes) produjo cinco
memorias. get_all confirmó cinco y las dos búsquedas recuperaron cinco. Las dos
respuestas tuvieron contexto. Siete HTTP, tres recibos GLM 5.3 Flash, 15 216 tokens
observados; sin reintentos. Es una regresión, no un nuevo documento reservado.

La extracción nueva produjo JSON válido: no se observó el aviso de reparación.
Este recorrido prueba operación con el código actualizado, pero no atribuye el
éxito únicamente al parche. El replay previo de la respuesta malformada sí ejercitó
el parche y recuperó cinco elementos sin llamadas ni persistencia.

La respuesta sobre baselines coincide en lo central con la fuente. En la respuesta
sobre acuerdo se conservaron 0.69 y 0.59, pero se añadió Cohen para ambos idiomas:
la fuente usa Cohen para neerlandés y Fleiss para inglés. La memoria extraída
conservó sólo Kappa sin esa distinción; el chat añadió una especificación incorrecta.
La revisión es del productor, no una adjudicación independiente.

El servicio queda activo en 9696. Los cambios MemOS siguen locales, sin commit/push.
El fallo genérico de reportar éxito con otras extracciones vacías sigue pendiente;
la reparación actual cubre sólo comas estructurales sobrantes. No hay certificación
semántica. Resultados históricos v2 permanecen intactos.

Evidencias: result.json y parser-validation.json. Registros originales locales:
/tmp/memos-9696-activation. El próximo control debe distinguir extracción vacía,
recuperación insuficiente y afirmación añadida sin respaldo, antes de repetir una
comparativa con documentos nuevos.
