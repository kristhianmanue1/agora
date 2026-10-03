# MemOS local frente a dos casos conocidos de Ágora

Comparación diagnóstica autorizada: dos cubos nuevos, artículo QASPER público y
registro temporal sintético. No se usó kris_cube ni se cambiaron código/configuración
de MemOS. Referencia local a7367d0 con modificaciones de configuración preexistentes;
GLM 5.3 Flash configurado por el servidor, no acreditado por telemetría independiente.

## Diseño fijado antes de ejecutar

16 solicitudes HTTP: por caso crear cubo, añadir fuente completa, get_all inicial,
buscar con 0.45/0.3/0.1, chat con 0.1 y get_all final. Cero reintentos. Historial
explícitamente vacío; add_message_on_answer=false; writable_cube_ids vacío en chat.
No internet. No se ajustaron umbrales tras ver resultados. Timeout del cliente no
constituye cancelación del servidor. Las llamadas internas a proveedores no se
midieron ni quedaron limitadas por el número de solicitudes HTTP.

No es igualdad de presupuesto: MemOS extrajo memorias desde la fuente completa;
Ágora previamente generó desde pasajes seleccionados. Es evidencia de comportamiento
del recorrido completo, no una comparación aislada de algoritmos o modelos.

## Resultados

| Caso | Extracción | Memorias | Búsqueda | Respuesta |
|---|---:|---:|---|---|
| QASPER Visual7W | 59,481 s | 5 | Mismos IDs/textos en tres umbrales | Incluye Visual7W y benchmark abierto propio |
| Corrección temporal | 25,316 s | 1 | Mismo ID/texto en tres umbrales | Conserva miércoles sustituyendo martes; añade fechas no presentes |

Chat: 11,264 s y 13,739 s respectivamente. Latencia observada una sola vez, sin
estimación estadística. Tokens, coste monetario y llamadas LLM internas no medidos.

### Aporte comprobado

MemOS recuperó la respuesta QASPER que la lectura anterior de Ágora dejó incompleta.
No hizo falta reducir relativity en estos casos: 0.45 devolvió los mismos recuerdos.
Todas las memorias recuperadas conservaron texto fuente completo y el hash suministrado.
IDs y texto de memorias coincidieron antes/después del chat; no se afirma inmutabilidad
de todo el estado interno. Las referencias Fact del chat no se validaron como citas
por intervalo original ni se adjudicaron todas las afirmaciones numéricas adicionales.

### Límites comprobados

La extracción temporal añadió una reunión el 2 de octubre de 2026, fecha que no figura
en el fixture. También propuso 6/7 de octubre como fechas de martes/miércoles, con
calificación de inferencia. El chat heredó esos añadidos. La fecha de ingestión no
establece la fecha del evento: distinguir ambas es necesario antes de admitir memoria.

Al ingresar el artículo se generó además UserMemory sobre un supuesto interés personal
del usuario. En esta prueba es una inferencia del sistema, no una preferencia declarada.
Es una razón para separar memoria de usuario y evidencia documental al evaluar uso ARIA.

Ágora también había expresado correctamente la corrección de días, pero Jev cuestionó
la advertencia sobre posibles cambios posteriores. No hay una victoria general de un
sistema: hay mejora de recuperación y riesgos diferentes de transformación.

## Decisión recomendada

No reemplazar Ágora ni conectar automáticamente memorias. MemOS es candidato a proveedor
opcional de recuperación: un adaptador futuro debe devolver identidad/versión/localizador
y evidencia original, marcar inferencias y separar fecha de captura de fecha del hecho.
La verificación de afirmaciones debe contrastar la fuente, no sólo el resumen MemOS.
Esta comparación queda cerrada con resultado mixto; un adaptador es otro incremento
que requiere alcance propio. No se prolonga el benchmark para obtener un ganador.

## Conservación y reproducción

freeze.json fija fuentes, preguntas, cubos y umbrales. result.json conserva resultados
saneados sin embeddings. runs/ contiene solicitudes/respuestas locales ignoradas; los
dos cubos de prueba permanecen para inspección, sus IDs están en freeze.json. No se
eliminaron ni se admitieron en AN-KLA. No se deben reejecutar escrituras sobre ellos.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 experiments/memos-comparison-v1/verify.py
```

verify.py es offline: comprueba hashes, solicitudes acotadas a los cubos, fuentes,
respuestas, etiquetas de procedencia y conservación de IDs/textos. La inspección
semántica es del mismo agente, no una adjudicación independiente. Se requieren los
artefactos locales para reproducción completa. No se ejecutó la suite de MemOS,
ya que no se modificó su implementación.
