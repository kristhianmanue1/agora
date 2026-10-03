# Fórmula faltante: selección enfocada y reparación explícita

## Resultado

Se obtuvo una respuesta candidata que conserva lo conocido y declara desconocido
el rango positivo perdido en la extracción. La inspección del productor acepta
**esta reparación concreta**; no hubo adjudicación independiente ni admisión a
memoria. El consumidor mantiene `candidate_requires_expansion` porque recibió una
selección parcial. No se cambia ese estado mediante la evaluación del productor.

No se modificó código del producto: se ejercitaron `--mode reference`, IDs y límites
ya publicados en `915bd51`. Se seleccionaron manualmente cuatro párrafos originales,
3.224 de 45.557 bytes, con offsets y hashes. La selección cubre la recogida de
etiquetas y la predicción. No es evidencia de recuperación automática ni de ausencia
en el PDF: `INLINEFORM0` identifica un límite del texto extraído disponible.

## Tres intentos conservados

| Etapa | Esfuerzo | Resultado semántico del productor | Tokens |
|---|---|---|---:|
| Pregunta anterior y selección enfocada | Predeterminado | No aceptado: inglés e inferencia «las restantes», aunque declara fórmula faltante | 3.552 |
| Misma pregunta y selección | low | No aceptado: inglés, reconstruye 3–5 y omite faltante | 1.647 |
| Reparación explícita de redacción en español | Predeterminado | Aceptado dentro de este caso: datos conocidos y faltante explícito | 3.591 |
| Total | Tres llamadas | No se eliminan los intentos fallidos | 8.790 |

Todos pasaron la validación estructural. Los dos primeros muestran que procedencia
literal, alcance conservador y JSON válido no bastan para fidelidad o idioma.
No se promovió `low`. Un fallo inicial de importación del ejecutor sucedió antes
de las llamadas; se corrigió mediante una ruta explícita de repositorio.

La reparación conservó fuente, selección y presupuestos, pero cambió la redacción
de la pregunta: pidió español y prohibió deducir valores por eliminación. Es una
intervención después de ver errores, no un ensayo ciego ni una comparación causal
pura. Las preguntas, criterios previos y cada freeze se conservan por separado.
El ahorro de entrada observado en esta selección manual no demuestra ahorro neto
del sistema: hubo trabajo del productor y tres llamadas. No se midieron dólares.

## Qué afirma la respuesta final

- Trabajadores mediante crowdsourcing, valoraciones de 1 a 5.
- La valoración 1 se asigna a insatisfacción; la 2 se descarta.
- El conjunto positivo no puede reconstruirse a partir de `INLINEFORM0`.
- Las notas se solicitan para el entrenamiento inicial, no durante el despliegue.
- La predicción usa contexto codificado con Transformer, cabeza lineal y parámetros
  de satisfacción separados. No se confunde generación de etiquetas con predicción.

La inspección cotejó esas afirmaciones con los cuatro párrafos conservados en
`case.json`. La limitación aparece en `missing`, fuera del texto agregado de
`answer`: un consumidor que sólo muestre `answer` perdería ese aviso. Debe mostrar
ambos, además del alcance, sin interpretar esta aceptación como cierre documental.

## Reproducibilidad

`initial/` y `repair/` conservan casos, congelaciones, ejecutores y receipts. Las
respuestas originales se mantienen, incluidos los errores semánticos. Los scripts
requieren fuente original por hash, ruta de repositorio y salida nueva; Llavero
entrega `SKOPOS_LLM_API_KEY` sólo al proceso. No hay credenciales ni razonamiento
interno en estos archivos.

Comprobación local sin llamadas externas:

```bash
python3 experiments/focused-label-v1/verify.py --source /ruta/1901.05415.txt
python3 scripts/verify_benchmark_evidence.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -p 'test_benchmark_evidence.py' -q
```

El verificador comprueba identidad, rangos, citas, presupuesto configurado y suma
de tokens; **no certifica semántica**. Los totales históricos v1 que imprime el
verificador general no son los de esta ronda; sus hashes sí incluyen este expediente.

## Cierre y próximo paso

Se cierra la reparación asistida de este caso, conservando la revisión humana
pendiente y el alcance parcial del candidato. Antes de otra batería grande, verificar
que el recorrido de consumo muestre `missing` junto a `answer`, y convertir esta
selección manual en un plan explícito reutilizable. No afirmar todavía recuperación
automática fiable, ahorro general ni equivalencia con MemOS. Sin cambios a MemOS,
Skopos, AN-KLA o la configuración predeterminada de Ágora.
