# Plan reproducible de selección explícita

El contrato `agora/explicit-passage-plan/v1` fija pregunta, fuente por SHA-256,
rangos UTF-8, presupuesto y el envelope reproducible. La CLI `plan-passages`
lo prepara sin proveedor; `generate-plan` verifica el hash, reconstruye su contenido
y sólo entonces permite una respuesta conservada o la llamada expresamente pedida.
Cambiar de pregunta requiere otro plan. Selección manual no significa cobertura
semántica verificada: `selection_verified` permanece false.

Este expediente aplica el contrato a los cuatro párrafos del caso de fórmula
faltante: 3.224 bytes seleccionados de 45.557; presupuesto 5.000. La reproducción
usó la respuesta conservada, mantuvo exactamente `answer` y `missing`, y quedó
`candidate_requires_expansion`. La vista conjunta permite ver la fórmula desconocida.
No hubo llamadas API ni una nueva aceptación semántica. El usage dentro de response
pertenece a la generación histórica; no debe contabilizarse como gasto del replay.

## Reproducir sin proveedor

Desde la raíz, con la fuente original fijada por el hash del plan:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 experiments/explicit-plan-v1/replay.py \
  --source /ruta/1901.05415.txt --out /tmp/agora-replay-nuevo
```

El directorio de salida debe ser nuevo. El script utiliza el Python de `.venv`,
crea un workspace temporal y ejecuta `plan-passages`, `generate-plan --response`
y `agora.passage_view`. Conserva comandos y salidas. No utiliza credenciales.
El ejemplo se apoya en el caso y respuesta históricos fijados en focused-label-v1.

## Evidencia y límites

- `plan.json`: plan generado mediante la CLI.
- `response.json`: respuesta histórica suministrada al replay.
- `result.json`: resultado del consumidor con origen `supplied_response_replay`.
- `verification.json`: comprobaciones y conteo de tests de esta ejecución.
- 554 tests pasan: seis nuevos verifican pregunta, fuente, plan, presupuesto y
  límites UTF-8, con rechazo antes de invocar al proveedor.

Planes automáticos anteriores conservan sus contratos y pruebas. Este contrato
nuevo aplica siempre control de alcance, sin relajar límites de citas ni de texto.
Un hash asegura reproducción relativa al archivo esperado; no prueba autoridad,
verdad ni autenticidad frente a quien pueda sustituir plan y hash juntos.

La autorrevisión comprobó separación entre selección manual y automática, coste
histórico frente a llamadas nuevas y conservación de los faltantes. No hubo revisor
independiente. No se cambió MemOS, Skopos ni AN-KLA.

## Siguiente paso

Comparar una selección automática contra este plan manual conservado, primero sin
llamadas: medir qué párrafos recupera, qué omite y cuánto texto entrega. No volver
a generar respuestas hasta saber si la evidencia necesaria llega al consumidor.
