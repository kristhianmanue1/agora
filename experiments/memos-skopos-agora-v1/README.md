# MemOS frente a Skopos y Ágora: dos casos sintéticos

## Alcance y condiciones

Ensayo autorizado de dos fuentes cortas: contradicción pendiente y corrección explícita.
Los textos, preguntas y expectativas se fijaron antes de recibir respuestas (cases.json).
Expectativas del productor, sin etiquetado independiente ni ciego. No son documentos
reservados, largos ni una batería estadística. No hay ranking general de productos.

Skopos se probó mediante su parser Codex real: el texto común se envolvió en JSONL
sintético. No se probó MongoDB, búsqueda de corpus, análisis LLM ni ingesta de reuniones.
Su piloto de reuniones vive en experiments y no equivale a un conector desplegado.
Ágora usó FileSourceAdapter, prepare y la CLI passage_cli con GLM, 2048 bytes de
contenido, top_k 3, 2048 tokens máximos de salida, timeout 180 s, temperatura 0.
MemOS recibió el mismo texto completo en dos cubos nuevos: add síncrono, get_all,
search (relativity 0.1, top_k 10), chat (1024 tokens máximos, temperatura 0), sin
internet ni escritura de respuesta. GLM configurado en MemOS; sin identidad efectiva
acreditada en estas respuestas. Ágora recibió reported_model glm-5.3-flash.

No son prompts ni presupuestos equivalentes: MemOS interpreta durante ingestión y
consulta; Ágora recibe pasajes con un contrato de citas. Se comparan recorridos
configurados, no modelos aislados. No se alteró configuración después de ver respuestas.

## Resultados observados

| Componente | Contradicción | Corrección explícita |
|---|---|---|
| Skopos, captura | Conservó texto exacto y sello verificable | Conservó texto exacto y sello verificable |
| Ágora, recuperación + respuesta | Conservó conflicto y monto/responsable desconocidos; 5 citas literales | Miércoles reemplaza martes; fecha desconocida, Priya responsable, presupuesto pendiente; 5 citas |
| MemOS, ingestión + respuesta | Conservó conflicto y ausencias, pero añadió fechas probables October 6/7 que la fuente no contiene | Conservó corrección, ausencia de fecha, responsable y aprobación pendiente; añadió marca temporal de captura |

MemOS creó tres recuerdos por caso y conservó el texto fuente completo en metadatos
sources de todos ellos. Conservación de original no implica fidelidad de cada derivado.
El caso de corrección fue un texto que ya contenía la corrección: **no prueba que
feedback pueda actualizar un recuerdo anterior**. No corrige el fallo del ensayo
memos-transitions-v1.

Ágora seleccionó los tres párrafos de cada texto y verificó sus bytes/localizadores.
El envelope marca partial porque no incluye separadores entre párrafos: no se afirma
cobertura byte a byte completa. Se conservaron los contenidos de todos los párrafos.
Modificar el archivo después de fijar su hash produjo source_revision_mismatch en
ambos casos. La validación de citas comprueba literalidad/localización; el juicio
semántico favorable es revisión del productor, no garantía automática ni independiente.

## Qué significa para la arquitectura

Skopos aporta captura y procedencia; no debe confundirse esa propiedad con resolver
contradicciones. Ágora aporta lectura seleccionada y respuestas candidatas vinculadas
a evidencia. MemOS aporta extracción/organización/recuperación semántica, con costes
y riesgos adicionales de interpretación. Skopos también dispone de análisis LLM,
pero esta prueba no lo ejecutó ni lo evaluó.

MemOS puede ser un proveedor opcional de recuerdos para localizar antecedentes.
En estos casos no hay evidencia que justifique sustituir Skopos o Ágora. Una futura
conexión debe devolver fuente, revisión, localizador y texto original; el consumidor
ha de distinguir recuerdo derivado de evidencia y comprobar ambos. No se implementó
esa integración.

## Verificación y costes

10 llamadas HTTP MemOS y 2 al proveedor de Ágora, sin reintentos de red. Ágora reportó
926 y 1214 tokens totales (2140 sumados); MemOS no reportó consumo total interno.
No se calcula ahorro ni coste monetario comparable. Tiempos por llamada en result.json.
No se comprobó aislamiento mediante cubo señuelo; usar cubos nuevos limita el alcance
operativo, pero no certifica control de acceso multiusuario.

Tests ejecutados: Skopos test_captura.py 20/20; Ágora test_source.py 11/11. Asserts del
ensayo comprobaron igualdad de contenido/sellos y rechazo de fuente alterada en los
dos casos. Las dos generaciones de Ágora terminaron candidate: no admisión automática.

Dos incidencias de preparación, antes de llamadas al proveedor: Llavero exigió ruta
absoluta del consumidor; luego el perfil legado entregó SKOPOS_LLM_API_KEY y Ágora
esperaba ZAI_API_KEY. Se adaptó únicamente la variable en memoria del proceso.
El primer resultado fallido, con cero intentos HTTP, se conserva en runs/. No cambió
Llavero, ninguna credencial, ni el producto. No se publican secretos ni reasoning.

result.json publica evidencia sintética y hashes. runs/ conserva respuestas crudas
localmente, excluidas de Git. El informe registra HEADs; Skopos y MemOS tenían cambios
previos no modificados por este ensayo. Ágora estaba limpio antes del nuevo expediente.

## Reproducción local

Desde Ágora, con ambos repositorios en las rutas usadas en compare.py y servidor
MemOS preparado, autorizar dos cubos nuevos y llamadas al proveedor antes de ejecutar:

```bash
python3 -B experiments/memos-skopos-agora-v1/compare.py /tmp/NEW-COMPARISON
python3 /Users/krisnova/www/aria/llavero/llavero.py ejecutar zai -- /usr/bin/python3 -B /Users/krisnova/www/aria/agora/experiments/memos-skopos-agora-v1/generate_agora.py /tmp/NEW-COMPARISON
```

La primera ruta debe ser inexistente. No repetir el mismo laboratorio tras timeout;
inspeccionar el intento conservado. Los cubos se conservan como evidencia. No se
ha ejecutado una segunda reproducción completa. Siguiente prueba útil: documento
reservado largo y mismas preguntas, con verificación humana de citas/omisiones y
contabilidad separada de ingestión y consultas. No ampliar sin cerrar primero
el diagnóstico pendiente de feedback si se pretende usar actualizaciones de MemOS.
