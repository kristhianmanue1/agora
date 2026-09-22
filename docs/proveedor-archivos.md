# Proveedor local de fuentes — incremento 1

Implementado localmente el 2026-09-22, tras autorización del Operador sobre el
plan afinado. Es transporte verificable de texto UTF-8, sin búsqueda automática,
modelo, transformación, Skopos ni AN-KLA. No modifica los formatos anteriores.

## Uso

Calcular SHA-256 sobre los bytes exactos de una fuente autorizada; usar ese mismo
hash en inventario y lecturas. Desde la raíz del repositorio:

```bash
PYTHONPATH=src python3 -m agora.source inventory \
  --source fuente.txt --source-id documento-1 --sha256 HASH \
  --unit-bytes 4096 --out inventario.json

PYTHONPATH=src python3 -m agora.source fetch \
  --source fuente.txt --source-id documento-1 --sha256 HASH \
  --range 0:100 --range 8000:8100 --content-budget 200 \
  --envelope-budget 4096 --out fragmentos.json
```

Los rangos del ejemplo son ilustrativos: deben existir y terminar en límites
UTF-8. Usar los localizadores del inventario cuando corresponda. Inicio inclusivo,
fin exclusivo, en **bytes**, no caracteres. Varios rangos deben ir ordenados,
sin solapamientos ni duplicados. Ampliar contexto consiste en pedir rangos más
amplios con el mismo hash, dentro del presupuesto. No se expande automáticamente.

`FileSourceAdapter(path, source_id).inventory(revision)` y
`.fetch(revision, [(start, end), ...])` ofrecen la misma superficie Python.
El ID es declarado por el llamador; la revisión es SHA-256 hexadecimal sin prefijo.
El adaptador no carga rutas ni ejecuta instrucciones desde el texto de la fuente.
No es un control de acceso: quien lo invoca debe estar autorizado a leer el archivo.

## Contratos provisionales

- `agora/source-inventory/v0.1`: identidad/revisión, tamaño total e inventario de
  unidades con rangos y hashes. `inventory_complete` significa partición completa
  de la copia inspeccionada; `content_delivered: false` indica que no se entregó
  su contenido. No acredita que el agente haya leído las unidades.
- `agora/source-envelope/v0.1`: identidad/revisión, fragmentos exactos, rangos,
  hashes y bytes entregados. `coverage: full|partial` describe sólo los rangos de
  esta respuesta; no acumula lecturas de peticiones anteriores.
- `integrity: matches_requested_revision` identifica la copia recibida; no prueba
  autenticidad ni vigencia externa. `evidence_sufficiency: unknown` siempre:
  tampoco una cobertura completa certifica comprensión o suficiencia semántica.
- `truncated: false` y `redacted: false` describen operaciones de este adaptador:
  no recorta para hacer caber resultados ni sanea datos. No afirman que el archivo
  original nunca haya sido recortado o redactado por su productor.

No incluye campos ni dependencias de proveedores particulares. No es un estándar
adoptado del ecosistema; su segundo proveedor y consumidores siguen pendientes.
No se emite TransformationRecord porque aquí no ocurre una transformación.

## Límites independientes

| Límite | Valor |
|---|---|
| Fuente completa local | Máximo 16 MiB; configurable hacia abajo |
| Unidad del inventario | 4096 bytes por defecto; entre 4 y 65536 |
| Inventario | Máximo 16384 unidades; sin truncamiento silencioso |
| Rangos por lectura | Entre 1 y 256 |
| Contenido entregado | 65536 bytes por defecto; máximo 16 MiB |
| Envoltorio JSON | Máximo 8 MiB; configurable hacia abajo |

El presupuesto JSON incluye metadatos, escapes y salto final con la codificación
`encode_record`. No es un presupuesto en tokens ni incluye un futuro prompt.
Una fuente permitida puede no caber en una sola respuesta: pedir rangos menores.
Presupuesto insuficiente causa error; no devuelve una selección recortada.

Las unidades respetan caracteres UTF-8, pero pueden cortar oraciones, negaciones,
tablas o secciones. No son fragmentos semánticamente autosuficientes. Se conservan
separadores originales, incluidos CRLF, sin normalización.
Cada operación relee y verifica la fuente completa localmente: no demuestra ahorro
de I/O ni indexación incremental. Usa una copia acotada en memoria durante la
operación; no mantiene versiones históricas. Si cambia el archivo, la revisión
anterior se rechaza y no se recupera automáticamente. Un cambio posterior a la
lectura no invalida los bytes ya devueltos, pero exige nueva comprobación al releer.

La CLI crea destinos nuevos exclusivamente. Rechazos previos a la escritura no
crean resultado. Un fallo de almacenamiento durante la escritura puede dejar un
archivo parcial: aceptar salida sólo con código 0 y JSON válido. No hay escritura
atómica ni garantía de durabilidad frente a corte eléctrico.
Los resultados pueden contener datos privados; no se publican ni admiten en memoria.

## Compatibilidad y verificación

Los comandos previos `agora`, `agora.query`, `agora.extract` y `agora.review`
conservan su límite de 4096 bytes. **Todavía no consumen este nuevo envelope.**
El incremento habilita recuperar fuentes grandes, no responder sobre ellas.
No se modifica M1-R1 ni su configuración experimental.

Suite ejecutada: 87 pruebas OK (76 previas y 11 nuevas). Las nuevas cubren
reconstrucción exacta UTF-8/CRLF, pasajes distantes y expansión, revisión modificada,
presupuestos independientes, rangos inválidos/solapados, límites de unidades,
compatibilidad anterior y CLI con rechazo y creación exclusiva.

Piloto reproducible sin modelos:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 experiments/source-provider-v1/pilot.py \
  --out experiments/source-provider-v1/runs/nueva-corrida
```

Ejecución `runs/local-01`: 2.385.085 bytes sintéticos, inventario de 583 unidades,
85 bytes recuperados en dos pasajes distantes, envelope de 806 bytes. Se verificó
cada rango/hash del inventario; rechazo por presupuesto y por modificación de
fuente. Cero llamadas a modelos. No es prueba de fidelidad, búsqueda ni ahorro de
tokens: los pasajes se indicaron explícitamente y el contenido es repetitivo.
El reporte local incluye hashes del código y del piloto; runs está excluido de Git.

Revisión separada por review_large_source_plan: PROCEED para el incremento local,
basado en lectura de código y pruebas, sin ejecución adicional por ese revisor.
No es auditoría externa. Se incorporaron sus límites sobre lectura completa local,
unidades mecánicas, ausencia de histórico y posible salida parcial por fallo de disco.
