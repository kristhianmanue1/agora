# MemOS: correcciones, checkpoints y control de acciones

## Resultado del bloque acotado

MemOS local, HEAD `a7367d07e55db61099f7b4e2c1108bc5831a24f3`, con cambios
preexistentes en docker/docker-compose.yml, src/memos/settings.py, uv.lock y
scripts/run_memos_zai.sh. El HEAD no describe por sí solo toda la configuración
que corre. GLM 5.3 Flash configurado; identificador efectivo no acreditado por
estas respuestas. Servicio http://127.0.0.1:9696. Un cubo sintético nuevo;
ninguna modificación del código/configuración de MemOS ni de cubos previos.

### 1. Corrección semántica: fallo observado

Se añadió una reunión aprobada de Cedar para Tuesday, sin fecha de calendario.
La ingestión creó un recuerdo e incorporó una hipótesis de fecha October 6, 2026,
no suministrada. Después se envió feedback síncrono: Wednesday reemplaza Tuesday,
con historial de conversación, los IDs recuperados y el cubo de escritura explícito.

El servicio respondió HTTP 200, `Memory feedback successfully`, con
`record: {add: [], update: []}`. La consulta posterior conservó idénticos ID, texto,
status activated, version 1, history y evolve_to vacíos. La búsqueda recuperó
Tuesday y no Wednesday. **La corrección no se aplicó en este caso.**

La ingestión y la recuperación previas funcionaron como controles de disponibilidad
básica. No hubo un control positivo exitoso de actualización: no se concluye que
MemOS sea incapaz de corregir cualquier memoria. Un solo caso tampoco estima
una tasa de fallos. No se cambiaron prompts ni umbrales para conseguir éxito.

El código ofrece más de una causa compatible con respuesta vacía: juicio de feedback
sin candidatos válidos y excepción capturada en process_feedback_core. No se inspeccionaron
logs de servidor ni se atribuye el fallo a una causa particular.

### 2. Checkpoint: no hay equivalente demostrado en esta API

El OpenAPI observado tiene 26 rutas y no expone checkpoint/resume/restore de estado
de tarea. El código sí contiene TreeTextMemory.dump/load y export_graph/import_graph:
son serialización de memoria, no prueba de checkpoint transaccional con revisión
base, rechazo de estado obsoleto y reanudación como los comprobados en AN-KLA.

No se ejecutaron dump/load contra el grafo compartido. import_graph hace MERGE por
ID de nodo; cambiar el nombre de cubo no demuestra aislamiento de una restauración.
TreeTextMemory.drop exporta y borra la base: está fuera del ensayo. Probar backups
requiere una instancia desechable de grafo/vector y una prueba de restauración propia.
Delete/recover por record_id tampoco equivale a checkpoint de tarea.

### 3. Bloqueo efectivo: sin mecanismo equivalente identificado

En las rutas del servicio y búsquedas en src/memos no se encontró una ruta equivalente
a attest run con allowlist de argv. Hay autenticación/permisos de API y ámbitos de
cubos; esas fronteras son distintas a permitir o rechazar ejecución de un comando.
No se ejecutó una sonda de comandos ni se usó una negativa del chat como prueba.
La conclusión se limita a la superficie inspeccionada, no a todos los plugins o
versiones posibles de MemOS.

### Versionado: capacidad de código, no garantía de este ensayo

_single_update_operation_with_versions invoca un hook de versionado. Ante una
excepción tiene fallback sin archived_item; si falla añadir el archivo histórico,
registra un warning y puede continuar la actualización. No es evidencia de una
transacción inseparable entre actualizar y preservar historia. Aquí no hubo update,
por lo que conservación histórica de correcciones queda sin demostrar.

## Evidencia, reproducción y límites

result.json publica observaciones sintéticas, tiempos y hashes de las siete llamadas
(una lectura OpenAPI y seis POST). runs/ conserva solicitudes y respuestas locales,
excluidas de Git. Cero reintentos de cliente; llamadas internas, tokens y coste no
medidos. No hubo revisión independiente ni cambio de producto. La inspección posterior
fue una autorrevisión de alcance y conclusiones.

Con servidor compatible ya disponible y autorización para un nuevo cubo y llamadas
al modelo configurado:

```bash
python3 experiments/memos-transitions-v1/reproduce.py /tmp/NEW-UNUSED-DIRECTORY
```

El directorio debe ser nuevo. La reproducción no se ha ejecutado nuevamente; resultados
no deterministas pueden variar. No elimina el cubo: su identificador queda en la primera
respuesta, para conservar evidencia. El script registra intento antes de enviar y no
repite operaciones con resultado incierto. Los asserts de preparación del informe
verificaron igualdad antes/después y recuperación vieja, no éxito del producto.

## Recomendación

Conservar AN-KLA para las transiciones explícitas ya probadas. Antes de integrar
feedback de MemOS, exigir lectura posterior que compruebe la corrección y tratar
operaciones vacías como no aplicadas. Próximo diagnóstico acotado: observar logs
exclusivamente del cubo/trace del ensayo para distinguir clasificación vacía de error
interno; añadir un control positivo de actualización en otro cubo. No ampliar el
benchmark ni sustituir componentes hasta resolver esa discrepancia.
