# Entrega del plan estructurado al generador y vista

## Resultado

El plan estructurado existente conserva y entrega **los cuatro párrafos** de la
referencia manual al consumidor por IDs. Entrega **11.990 bytes**, dentro del
presupuesto de 12.000. El resultado mantiene `candidate_requires_expansion`,
`semantic_support: not_verified` y la ausencia documental no establecida.

No son los ~6 KB del selector estructural aislado: el plan v3 preserva primero la
selección léxica y añade después la estructural. No se cambió esa política ni se
usaron los rangos de respuesta como guía del plan (`reference_ranges=[]`).

## Fallo encontrado y corregido

El recorrido `generate-plan` con IDs emite `agora/claim-evidence-query/v2`, donde
las afirmaciones y los faltantes viven dentro de `parts`. La vista de pasajes sólo
buscaba `answer` y `missing` en la raíz y los mostraba como null. Ahora proyecta
esos formatos v1/v2 y presenta texto, faltantes y detalle por ID de aspecto.

El archivo original no cambia. Las ejecuciones rechazadas no se rescatan; datos
por aspecto mal formados se rechazan en la vista. No se adjudica respaldo por
convertir el formato. Los formatos que ya tenían answer/missing conservan su lectura.

## Prueba realizada

Se reconstruye el plan desde la estructura QASPER fijada por hash, se verifica su
reproducción mediante `generate`, y un proveedor local simulado inspecciona el prompt.
La prueba exige que los cuatro párrafos estén presentes en sus unidades. Devuelve
una afirmación sintética y un faltante explícito; la vista debe preservar ambos y
el alcance parcial. **No es una respuesta nueva de GLM ni replay de un modelo.**
No evalúa fidelidad general o calidad de generación. Cero HTTP y cero tokens nuevos.

563 tests pasan, incluyendo tres regresiones nuevas de la vista por aspectos.
El ejecutor completo pasó con la fuente real, su nueva representación canónica y
sus offsets; no se reutilizaron IDs de la fuente histórica distinta. La revisión
fue del productor, sin adjudicación independiente.

## Reproducir

```bash
PYTHONDONTWRITEBYTECODE=1 python3 experiments/structured-handoff-v1/run.py \
  --repo "$PWD" --out /tmp/entrega-estructurada-nueva
```

Requiere el dataset local fijado por hash en section-comparison-v1. La salida debe
ser nueva. Produce fuente, plan, fixture, resultado y vista, sin proveedor externo.
Este expediente conserva comprobaciones y vista; el ejecutor reconstruye el resto.

## Próximo paso

El recorrido de entrega queda comprobado. Corresponde una generación real acotada
con este plan, preservando la fórmula faltante y coste completo. Ese siguiente paso
no debe confundirse con lo probado aquí. El fallo de recuperación streaming/texto
completo en otro documento permanece pendiente y no queda resuelto por esta prueba.
