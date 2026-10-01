# Recuperación de cobertura: regresión local sin proveedor

Ejecutar desde la raíz:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 experiments/coverage-recovery-v1/verify.py
```

El runner usa la CLI pública y los artefactos locales conservados del caso
`condition-expansion-heldout-v1`. Sus hashes están en `result.json`. Es una regresión
conocida; el diseño de expansión a tres párrafos se informó por la lista omitida.
La consulta `metrics` procede de la pregunta, no de las respuestas ΔG y ΔS.
La rúbrica se usa para activar la propuesta y después para puntuar los rangos;
no alimenta la consulta de recuperación.

Resultado: contexto inicial 5.162 bytes; propuesta 9.439, incremento 4.277,
límite 12.000. Se preservan todos los rangos anteriores y se incorporan las
definiciones R2/ΔG y R3/ΔS. R1 también queda incluido. El pasaje exacto de R4/BLEU
anotado en la rúbrica no está dentro del nuevo contexto; no se declara cobertura
completa. La respuesta anterior mencionaba BLEU con otros pasajes: cobertura de
rangos anotados y cobertura de respuesta son mediciones diferentes.

Se verificaron archivos originales sin cambios y rechazo de sobrescritura. Cero
llamadas a proveedores, cero tokens de API; no se midió latencia ni coste total.
No se generó ni revisó una respuesta nueva. Recuperar evidencia no demuestra que
un modelo la utilice correctamente. La heurística puede añadir párrafos irrelevantes.

Siguiente: consumidor explícito de la propuesta para generar un derivado, revisión
de cobertura y fidelidad separadas; después casos nuevos con parámetros congelados.
