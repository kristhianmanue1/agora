# Referencias de evidencia por ID

Interfaz experimental optativa: `agora/claim-evidence-query/v2`.
El modo literal v1 sigue siendo el predeterminado; no hay migración automática.

## Qué cambia

`python -m agora.evidence_cli --citation-mode ids` permite que el modelo devuelva
`evidence_ids` en cada afirmación en lugar de copiar `quotes`. El sistema resuelve
cada ID contra las unidades que realmente entregó en esa petición y reconstruye
texto y anclajes desde la fuente. La respuesta original del proveedor se conserva.
La resolución es parte declarada del contrato, no reparación de la respuesta.

Cada ID deriva de identidad de fuente, revisión SHA-256, inicio/fin en bytes y
texto de la unidad; usa un prefijo `ev_` y 24 dígitos hexadecimales. Se comprueban
colisiones durante la construcción, sin afirmar inmunidad criptográfica absoluta.
Un ID de otra revisión o no suministrado se rechaza. No se buscan coincidencias
aproximadas ni se corrigen IDs mal escritos.

## Unidades y límites

Los pasajes se dividen por párrafos/líneas en unidades literales de hasta 4096
bytes UTF-8, con fragmentación adicional si un párrafo supera ese tamaño. Las
fronteras respetan UTF-8 y los offsets del original. Se omiten separadores en
blanco; no se afirma cobertura semántica ni equivalencia con una lectura humana.
Máximo de 4096 unidades por petición. La identidad depende también del recorte:
no es una identidad semántica permanente que sobreviva a cualquier segmentación.

Los límites de cantidad y bytes se aplican a las citas **reconstruidas completas**,
no al tamaño del ID. Un párrafo largo puede agotar el presupuesto. Seleccionar
IDs no acredita ahorro de tokens; añade metadatos al prompt y puede aumentar el
tamaño del paquete de evidencia. La contabilidad de las pruebas distingue esto.

IDs repetidos dentro de una afirmación se rechazan; los presupuestos siguen
contando las repeticiones entre afirmaciones. Dos ubicaciones con el mismo texto
tienen IDs distintos; la cita resuelta se ancla sólo a la ubicación seleccionada.
El contrato heredado de evidencia tampoco acepta duplicación del mismo texto
dentro de una afirmación, aunque proceda de IDs distintos.

## Forma de salida

Proveedor:

```json
{"parts":[{"id":"aspecto","status":"answered","claims":[{"text":"Afirmación","evidence_ids":["ev_ID_SUMINISTRADO"]}],"missing":[]}]}
```

El resultado aceptado conserva `evidence_ids`, añade `quotes` mediante resolución
local y contiene anclajes por afirmación e ID. Los consumidores deben reconocer
v2; no se debe hacer pasar esta forma por v1. `--citation-mode literal` conserva
la forma y validación anteriores.

## Qué no resuelve

Un ID válido puede apuntar a un párrafo que no respalda la afirmación. Permanece
`semantic_support: not_verified` y `coverage: not_verified`. La prueba de una
atribución falsa con ID válido confirma esta limitación. Las lagunas declaradas
son del modelo; no hay detección automática de todas las omisiones.

El modo tampoco garantiza JSON bien formado, selección relevante, citas mínimas,
calidad de resúmenes ni revisión independiente. No emplea las referencias de
QASPER para alimentar al modelo en los casos reales. El control G1 sí utiliza
contexto seleccionado por el productor y se identifica como tal.

## Verificación

Pruebas de ida y vuelta, UTF-8, IDs desconocidos/de otra revisión, duplicados,
presupuesto sobre texto resuelto, rechazo de citas suministradas por el modelo,
ubicaciones con texto idéntico, aspectos ausentes, abstención y límite semántico.
La campaña `experiments/evidence-ids-v1` compara ambos modos en una versión
congelada, con el mismo contexto y aspectos por par; el esquema, instrucciones
de referencia y metadatos cambian necesariamente. No se atribuye causalidad a
una sola modificación ni rendimiento poblacional con esta muestra.
