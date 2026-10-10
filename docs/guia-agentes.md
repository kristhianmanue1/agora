# Empezar a usar Ágora como agente

Ágora transforma y consulta fuentes con evidencia trazable. Produce candidatos:
no certifica verdad, exhaustividad ni autoriza acciones. Funciona de forma
independiente de Skopos y AN-KLA. La entrada de descubrimiento es
`scripts/agora.py`; no es un servidor ni requiere instalar un plugin.

## Primer minuto

Desde el checkout, usar Python 3.10 o superior. Si el entorno local está instalado:

```sh
.venv/bin/python scripts/agora.py doctor --json
.venv/bin/python scripts/agora.py capabilities --json
.venv/bin/python scripts/agora.py examples --json
.venv/bin/python scripts/agora.py example relations-offline --json
```

El entorno `.venv` no se distribuye con Git. En otro equipo sustituir su ruta por
un intérprete Python 3.10+ disponible. Desde otro directorio, pasar la ruta absoluta
a `scripts/agora.py`; no hace falta configurar PYTHONPATH. Las rutas de entradas
y salidas se interpretan desde el directorio de trabajo del llamador.

Descubrimiento, doctor y el ejemplo anterior no usan proveedores ni guardan
archivos. El ejemplo resuelve referencias reales de un texto sintético, conserva
versión/configuración desconocidas y termina con `needs_more_evidence`. Ése es el
resultado esperado: no intentar “repararlo” inventando datos.

## Elegir capacidad

| Necesidad | Identificador |
|---|---|
| Pendientes, recuperación por pasajes/subpreguntas, generación desde planes y reparación | `issues` |
| IDs de evidencia, plantilla y validación de una relación | `relations` |
| Generar o revisar relaciones con GLM/Jev o replay | `relation-run` |
| Consultar fuente por aspectos con citas/IDs | `evidence` |
| Responder una pregunta con generación y revisión GLM sobre una fuente UTF-8 | `answer` |
| Responder con presupuestos de salida explícitos por etapa | `answer-v2` |
| Revisar con Jev las citas de una ejecución `answer` ya terminada | `jev-review` |
| Exportar offline un paquete de consulta para un consumidor | `export-answer` |
| Construir intercambio PDF desde una respuesta Skopos CTIM v0.2 | `skopos-page-v02` |
| Elegir fuente completa o representación previa | `route` |
| Recorrer una fuente en unidades | `traverse` |
| Resumen inicial | `summarize` |
| Inspeccionar resultado guardado | `view` |

```sh
.venv/bin/python scripts/agora.py describe relations --json
.venv/bin/python scripts/agora.py run relations --help
.venv/bin/python scripts/agora.py run relations template --contract-version v2 --source /ruta/fuente.txt --source-id documento
```

`run` conserva argumentos, salidas y códigos de la CLI existente; no añade una
operación implícita. Acepta un separador `--` antes de argumentos nativos.
No necesita migrar archivos anteriores. Las ayudas nativas pueden ser texto,
aunque descubrimiento y diagnóstico devuelven JSON también sin `--json`.

`issues` requiere un workspace explícito para sus subcomandos. Su ayuda general
lista operaciones; [el recorrido de pendientes](pendientes-cli.md) especifica
entradas y ejemplos completos. Para generación/revisión de relaciones consultar
[la guía correspondiente](relaciones-candidatas.md). Para `answer`, Jev y el
paquete de salida, leer el [contrato de consulta](contrato-consulta-evidencia-v1.md).
Los demás enlaces aparecen en `describe`. El catálogo cubre trece capacidades,
no cada módulo interno
ni todos los experimentos históricos.

## Leer los contratos y efectos antes de ejecutar

`capabilities` y `describe` indican propósito, madurez, entradas, salidas, efectos
en disco, uso de red y documentación. Son metadatos de descubrimiento, **no una
barrera de permisos**. `run` puede escribir o transmitir al proveedor según la
operación solicitada. Primero confirmar que la fuente puede enviarse y fijar
presupuestos. Usar respuestas conservadas cuando el comando ofrezca replay.
No incluir credenciales en archivos, argumentos o resultados; usar Llavero.

La interfaz de descubrimiento fija schemas v1 propios. No impone a todas las CLI
un mismo esquema de errores ni convierte sus distintos códigos en equivalentes.
Un proceso exitoso puede devolver candidato parcial o evidencia insuficiente.
En relaciones, `admitted` permanece false incluso cuando el revisor diga supported.
Si un archivo o resultado está rechazado, no rescatar su texto como una respuesta
aceptada ni repetir una llamada incierta sin inspección previa.

## Qué comprueba doctor

Versión del intérprete y presencia de entradas/documentación. Devuelve código 0
con `status: ok`; 1 con `status: attention`. Por ejemplo, Python 3.9 puede ejecutar
estas utilidades, pero está por debajo del mínimo documentado y genera atención.
Doctor no instala, no lee claves y no llama a proveedores. Tampoco comprueba
salud de servicios, datasets, almacenes, integridad de workspaces o calidad semántica.
Consultar sus `not_checked` y `next_step`; no interpretar OK como validación global.

## Prueba del recorrido de descubrimiento

Las pruebas ejecutan las ayudas reales desde un directorio ajeno al proyecto,
verifican propagación de errores, ausencia de archivos creados por el ejemplo y
conservación de huecos. Una [prueba posterior con agente de contexto nuevo](../experiments/agent-first-use-v1/README.md)
completó el recorrido sin inspeccionar código y detectó ambigüedades documentales
corregidas. Fue una instancia separada en el mismo entorno/proveedor; no una
certificación independiente ni validación para todos los agentes.
