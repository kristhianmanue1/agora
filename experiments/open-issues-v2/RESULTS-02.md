# Continuación v2 glm-02 — resultado parcial

27 de septiembre de 2026. Tres solicitudes intentadas de seis previstas.
Dos completadas; una rechazada por formato. Sin reintentos ni reparación de JSON.
Se conservaron intactos casos, gold, prompt y ejecución glm-01. El nuevo límite
HTTP es 180 s y el de proceso 190 s. No se modificó código productivo ni memoria.

## Evidencia

| Caso / brazo | Resultado | Tokens | Segundos |
|---|---|---:|---:|
| late_source / tracked | Coincide con todos los ejes del gold | 6045 | 101.471 |
| late_source / full | Coincide con todos los ejes del gold | 4217 | 62.158 |
| partial_refutation / full | Rechazado: invalid_relation | 3701 | 49.955 |

Ambos brazos mantuvieron 2026-10-21 y Lina. El acta recibida después corresponde
al 2026-09-20 y no reemplaza la decisión del 2026-10-05. Citas literales válidas;
contraste semántico manual por el productor, no revisión independiente.

En el rechazo, GLM devolvió `relations` como objetos `{source_id, relation}`;
el contrato exige una lista de cadenas. El contenido crudo distingue fecha
retirada y responsable conservado, pero no es un resultado válido del contrato.
No se transformó ni puntuó como éxito. La discrepancia revela además que el
prompt no ejemplifica explícitamente el tipo JSON de cada elemento; conviene
corregir esa precisión antes de atribuir el fallo únicamente al modelo.

Consumo conocido de glm-02: 13963 tokens; 213.584 s sumados de llamadas.
Sumando glm-01 hay 17477 tokens conocidos y una solicitud anterior de consumo
desconocido: no es un coste total cerrado. No se calculó coste monetario.
El hecho de que la nueva llamada demorara 101.471 s no demuestra qué ocurrió
internamente en la anterior que agotó 90 s.

## Autorrevisión adversarial adicional

Se reprodujo localmente un contraejemplo con la salida válida de late_source:
se añadió un dependiente de date que ya representa 2026-10-21. El cálculo actual
lo incluye en affected porque encuentra update en la historia del campo.

Eso sirve como selección conservadora de candidatos a revisión, pero NO prueba
que el documento esté desactualizado. Para una invalidación precisa hacen falta
identidad y versión de las entradas usadas por cada derivado, más una comparación
con el cambio relevante. No sustituir esa comprobación por coincidencia de valor:
dos valores iguales pueden proceder de fuentes diferentes o perder su respaldo.
No se alteró el contrato durante esta ejecución ni se publicó una invalidación.

## Estado y siguiente paso

Completados entre glm-01 y glm-02: antecedente falso y fuente tardía, ambos brazos.
Pendientes: refutación parcial (un intento rechazado) y dependencia no afectada
(no ejecutada). El piloto completo sigue PARCIAL. No hay evidencia de superioridad
con historial ni de fiabilidad general.

Recomendación: antes de más llamadas, precisar el formato JSON con un ejemplo
de forma neutro, añadir revisión/versionado de dependencias y probar localmente
el control de un derivado ya actualizado. Congelar una versión nueva y luego
probar los dos casos pendientes. Esta recomendación no se ha implementado.

Verificación local: 315 tests pasan; manifiesto congelado válido, igualdad de
casos/gold/prompt con glm-01 y par con mismas fuentes salvo antecedente comprobada.
Todos los archivos siguen locales, sin commit ni push; las corridas crudas están
ignoradas por Git. `result-glm-02.json` conserva resultados y rechazo sintéticos.
