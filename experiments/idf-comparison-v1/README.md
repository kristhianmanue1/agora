# Ranking IDF optativo: implementación y comparación

## Resultado

La estrategia nueva `paragraphs-idf` mejora la recuperación con dos subpreguntas y
5.000 bytes: 2/4 párrafos frente a 1/4 del método anterior, con 4.943 bytes entregados.
No supera 2/4 en ninguna condición; arquitectura y mecanismo siguen sin recuperarse.
La consulta española no recupera la fuente inglesa. No se cambia el predeterminado.

A 12.000 bytes/top_k=6 y dos preguntas entrega 8.560 bytes frente a 11.168 con la
misma cobertura. Otras configuraciones entregan más texto sin mejorar cobertura.
No hay ganador general, garantía de fidelidad ni evidencia sobre documentos nuevos.

## Algoritmo y contrato

Filtra una lista explícita de palabras frecuentes inglesas además del filtrado
español existente. Para cada término único coincidente suma
`log((N+1)/(df+1)) + 1`, donde N es el número de párrafos y df el número de párrafos
que contienen el término. Cada palabra cuenta una vez; repetirla no suma puntos.
Desempata por orden de fuente. No aplica traducción, stemming ni normalización por
longitud. No es BM25 ni recuperación semántica. Mantiene cuotas, presupuestos,
selección de semillas y expansión a vecinos del recuperador anterior.

`retrieve-subquestions --strategy paragraphs-idf` genera
`agora/subquestions-plan/v4-idf-experimental`. `generate-plan` reconstruye ese plan;
los contratos anteriores conservan sus estrategias. Los hashes de implementación
incluyen el nuevo módulo. La opción no afecta consultas existentes por defecto.

## Comparación congelada

20 condiciones sin llamadas: las ocho configuraciones anteriores con ambas
estrategias y cuatro controles españoles. No se retocaron queries ni pesos tras
ver resultados. Referencias manuales se usan sólo después de recuperar, nunca como
entrada al ranking. Controles positivo/manual 4/4 y negativo/vacío 0/4. Es un caso
conocido, no evaluación reservada. Las subpreguntas son redactadas por el productor.

| Condición | Bytes entregados | Párrafos manuales completos |
|---|---:|---:|
| single-clean-5000-3-paragraphs-equal | 4708 | 0/4 |
| single-clean-5000-3-paragraphs-idf | 4826 | 0/4 |
| single-clean-5000-6-paragraphs-equal | 4968 | 1/4 |
| single-clean-5000-6-paragraphs-idf | 4952 | 1/4 |
| single-clean-12000-3-paragraphs-equal | 5315 | 0/4 |
| single-clean-12000-3-paragraphs-idf | 6786 | 0/4 |
| single-clean-12000-6-paragraphs-equal | 10897 | 2/4 |
| single-clean-12000-6-paragraphs-idf | 11823 | 2/4 |
| split-two-5000-3-paragraphs-equal | 4748 | 1/4 |
| split-two-5000-3-paragraphs-idf | 4943 | 2/4 |
| split-two-5000-6-paragraphs-equal | 4928 | 1/4 |
| split-two-5000-6-paragraphs-idf | 4943 | 2/4 |
| split-two-12000-3-paragraphs-equal | 9886 | 2/4 |
| split-two-12000-3-paragraphs-idf | 10372 | 2/4 |
| split-two-12000-6-paragraphs-equal | 11168 | 2/4 |
| split-two-12000-6-paragraphs-idf | 8560 | 2/4 |
| es-5000-paragraphs-equal | 0 | 0/4 |
| es-5000-paragraphs-idf | 0 | 0/4 |
| es-12000-paragraphs-equal | 0 | 0/4 |
| es-12000-paragraphs-idf | 0 | 0/4 |

## Validación y límites

560 pruebas pasan, incluidas seis nuevas: ponderación de rareza, palabras frecuentes,
repetición, límite entre idiomas, localizadores literales y reproducción del nuevo
plan. CLI real de preparación: 4.943 bytes, v4, cero llamadas. Estos controles son
sintéticos y no sustituyen documentos reservados ni una revisión independiente.
No se modificaron MemOS, Skopos o AN-KLA ni se generaron respuestas nuevas.

`freeze.json` conserva condiciones y hashes de implementación. Su campo code_commit
fue heredado de la campaña anterior: **no es la revisión probada**; la aclaración y
base correcta figuran en `provenance.json`. El árbol probado es la base más los
cambios identificados por hashes. Se conserva el error de metadatos sin reescribir
la congelación después de conocer los resultados.

La autorrevisión comprobó que la nueva opción no reinterpreta planes antiguos,
que no se introducen datos del resultado esperado al ranking y que se conservan
las configuraciones que no mejoran. Los párrafos fuera de referencia no se declaran
irrelevantes. No hay evidencia nueva de suficiencia semántica.

## Reproducir

```bash
PYTHONDONTWRITEBYTECODE=1 python3 experiments/idf-comparison-v1/run.py \
  --repo "$PWD" --source /ruta/1901.05415.txt --out /tmp/idf-nuevo
```

La salida debe ser nueva. Se generan los 20 planes y métricas; no requiere API.
Antes de promover el ranking: evaluar documentos no usados en su diseño. Para el
caso pendiente, probar selección por secciones o normalización morfológica como
intervención separada, sin seguir aumentando top_k o presupuesto hasta obtener pase.
