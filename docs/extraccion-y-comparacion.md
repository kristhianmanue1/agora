# Extracción literal y comparación de rutas — incremento local

## Propósito y estado

Ágora puede preparar una selección literal vinculada a una pregunta y consultar
la fuente directa o esa selección sin fabricar un resumen previo. La selección
es explícita, por números de línea; no hay búsqueda ni detección automática de
contradicciones. No se considera una memoria general de la fuente.

Código original adaptado al contrato local, sin copiar código de terceros ni
incorporar nuevas dependencias. Referencias de diseño:

- RECOMP: selección/compresión orientada a consulta, https://github.com/carriex/recomp.
- CAHM: reincorporar evidencia original al transformar, https://aclanthology.org/2025.findings-acl.289/.
- RAG Techniques: comparación pedagógica de rutas, https://github.com/NirDiamant/RAG_Techniques.

No es una implementación ni reproducción de los resultados de esos proyectos.
RAPTOR, grafos, modelos de compresión y conexión a Skopos/AN-KLA quedan pendientes.

## Selección sin llamadas a modelos

Desde la raíz, con `PYTHONPATH=src`:

```bash
python3 -m agora.extract --source fuente.txt --sha256 HASH_FUENTE \
  --question '¿Qué consta sobre la fórmula?' --line 1 --group 1,2 \
  --budget 4096 --out seleccion.json
```

El caller identifica las líneas, incluyendo grupos de evidencia que deben
conservarse juntos. Seleccionar cualquiera de un grupo incluye todas, incluso
por transitividad entre grupos. Una contradicción no declarada puede perderse.
Si el resultado excede el presupuesto, falla: nunca elimina parte de un grupo
para hacerlo caber. Los localizadores también cuentan en el presupuesto.

`literal-selection/v0.1` conserva bytes, separadores originales, offsets UTF-8
[start,end), hash de fuente, pregunta y líneas seleccionadas. Los separadores
reconocidos son los de `str.splitlines`, incluidos CRLF y U+2029. La vista marca
cada línea como extracto separado; no implica continuidad entre pasajes.
Límite de fuente actual: 4096 bytes. No se sobrescribe la salida existente.
Los grupos representan una decisión del caller; no son una certificación.

## Consulta de las tres rutas

```bash
python3 -m agora.query --mode source --source fuente.txt --sha256 HASH_FUENTE \
  --question '¿Qué consta sobre la fórmula?' --model glm-5.3-flash --out consulta-directa

python3 -m agora.query --mode extract --source fuente.txt --sha256 HASH_FUENTE \
  --selection seleccion.json --selection-sha256 HASH_SELECCION \
  --question '¿Qué consta sobre la fórmula?' --model glm-5.3-flash --out consulta-extracto
```

Esas consultas sí transmiten su documento al proveedor configurado y requieren
el alcance de transmisión autorizado. Cada ruta nueva usa como máximo una
solicitud, sin reintentos. El modo `summary` anterior sigue disponible y requiere
`--summary-run`/`--run-sha256`; `--force-source` conserva su comportamiento legado.

La selección se reconstruye y compara antes de llamar al proveedor; cambios de
fuente, pregunta, partes o contenido inconsistente fallan. Si hay subpreguntas,
se declaran con los mismos `--part` y orden al seleccionar y consultar. Las citas deben estar dentro
de un pasaje literal, no en los localizadores añadidos. Si falta respuesta en
una selección, se informa `not_in_selection`, nunca ausencia en la fuente entera.
No hay recuperación automática en esta ruta para mantener la comparación aislada.

Los prompts de síntesis y consulta piden conservar conjuntamente contradicciones,
no asignar pronombres ambiguos ni reparar transcripciones o inferir unidades.
Esto es orientación al modelo, no un control semántico. `unreviewed` y
`semantic_support=not_verified` se mantienen incluso con citas válidas.

## Evaluación y límites

Las pruebas locales usan fuente sintética y proveedor simulado; comprueban
integridad, presupuesto, límites de citas, rutas y abstención diferenciada.
No prueban mejoras de GLM. La selección manual es un control/oráculo para medir
qué ocurre cuando el contexto fue elegido explícitamente, no un recuperador
automático. En una comparación real debe declararse su coste humano y evitar
seleccionar evidencia mirando las respuestas del modelo.

Siguiente evaluación: mismas preguntas y modelo para fuente directa, selección
literal y síntesis; puntuar contradicciones, negaciones, atribución, citas,
omisiones y abstención; contar preparación y consultas. Reservar casos nuevos.
La respuesta previa puede ser más barata: no imponer compresión donde no sirve.
El piloto real congelado no se modifica ni se reejecuta en este incremento.

El presupuesto de extracción mide únicamente el documento entregado, incluidos
localizadores. No equivale al prompt completo ni a tokens o coste del proveedor.
En modo legado `summary`, una respuesta conocida puede sobrevivir con procedencia
`summary` si el paso fuente se abstiene. La etiqueta de recuperación no demuestra
corroboración semántica; las rutas nuevas no heredan ese mecanismo.

## Verificación del incremento (2026-09-17)

- Suite ejecutada: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests`: **61 tests, OK** (48 previos y 13 nuevos).
- Revisión separada de `/root/review_real_excerpt`: encontró la vinculación
  incompleta de subpreguntas; se corrigió y confirmó el cierre por inspección.
  El revisor no ejecutó la suite; el resultado anterior pertenece al ejecutor.
- Ejercicio local con el fragmento real: seleccionar la línea 6 y declarar el
  grupo [6,7] conservó ambas líneas. Documento generado: 326 bytes con
  localizadores; fuente: 2233 bytes. Cero llamadas al modelo. Esto no demuestra
  que la respuesta sea correcta ni mide ahorro total del sistema.
- Los 29 archivos del manifiesto del piloto anterior conservan sus hashes.
- AN-KLA de Ágora: verify OK, revisión 3. Plantilla de contexto antigua detectada,
  no actualizada; no escritura de memoria ni adopción canónica en este incremento.
- Sin nuevas dependencias, commit, push, publicación ni modificaciones de AGENTS.
  Los cambios anteriores del árbol permanecen y no se atribuyen a este trabajo.
