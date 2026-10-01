# Generación desde recuperación: recorrido real de CLI

Regresión conocida sobre QASPER 2004.04498. `run.py prepare` fijó los hashes y
límites antes de `run.py live`: un candidato con `generate-recovery`, una revisión
`review-rubric`, ambos GLM. Revisión adicional Jev por afirmación y sus citas,
con etiquetas de cobertura ocultas. El runner Jev procede sin cambios de
`reading-paired-grouping-v1/run_jev.py`. No reintentos ni reparaciones.

## Resultado

- Contexto: 9.439 bytes. Los originales se conservan y el nuevo candidato enlaza
  hashes del padre, revisión y propuesta.
- Generación estructuralmente válida, siete afirmaciones. Incluye Accuracy, ΔG,
  ΔS y BLEU como control de calidad de traducción, no como medida directa de sesgo.
- GLM considera cubiertos R1–R4; la revisión previa tenía R2/R3 ausentes.
- Jev clasifica las siete afirmaciones como `supported`. C7 es limítrofe:
  probabilidades devueltas 0,53 supported y 0,46 insufficient; C5 también recibe
  menor confianza. Son salidas del proveedor, no probabilidades calibradas de verdad.
- Tres llamadas, 10.260 tokens reportados en conjunto; sin medición de precio
  monetario ni latencia total. No comparación controlada de ahorro en este paso.

El pasaje exacto de BLEU anotado en la rúbrica sigue fuera del contexto. La nueva
respuesta lo respalda con otros pasajes: coincidencia con un rango anotado,
cobertura de la respuesta y fidelidad de las citas son comprobaciones distintas.
GLM productor y revisor no son adjudicación independiente. Jev es otro proveedor,
pero su dictamen tampoco equivale a aceptación humana ni cobertura global.

`verify.py` reproduce solicitud y resultado con la respuesta conservada, verifica
linaje, hashes y etiquetas. Los artefactos completos se conservan localmente en
`inputs/` y `runs-*/`, excluidos de Git; el reporte publicado fija sus hashes.
La reproducción del caso real requiere esos archivos locales. Los tests sintéticos
del producto se ejecutan desde un checkout sin ellos.

Siguiente: casos nuevos con selección y parámetros congelados, controles sin
omisión y fuera de presupuesto, y revisión humana de afirmaciones limítrofes antes
de promover una estrategia predeterminada. No hay admisión ni vigilancia automática.
