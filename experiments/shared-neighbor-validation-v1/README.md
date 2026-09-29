# Validación de redistribución por vecinos

## Conclusión

La regla pasó los controles de integridad, presupuesto y conservación de evidencia. La utilidad adicional en documentos nuevos es modesta: no justifica reemplazar la estrategia predeterminada ni afirmar completitud semántica. No se cambió src/agora ni se incorporó a CLI.

## Selección fijada antes de medir

Doce documentos QASPER test-v0.3, entre 20.000 y 65.000 bytes tras render de Ágora, excluidos de los IDs encontrados en metadatos JSON de pilotos anteriores. Se seleccionó determinísticamente una pregunta respondible por documento; la selección y los parámetros quedaron escritos en protocol.json antes de calcular resultados. El hash del corpus coincide con su procedencia local.

Dos presupuestos (4.000 y 8.000 bytes), top_k=3. Dos consultas por caso: la pregunta original y una expansión mecánica que pide métodos, datos, condiciones y resultados para responderla. No es descomposición autónoma por un modelo. Las anotaciones de evidencia se usaron sólo para puntuar después de recuperar; no llegaron a la selección de pasajes. Los documentos pasan a ser casos de desarrollo tras esta ejecución.

## Resultados de cobertura anotada

| Presupuesto por documento | Antes | Después | Documentos con mejora | Bytes totales recuperados | Aumento |
|---|---:|---:|---:|---:|---:|
| 4000 | 9/29 | 10/29 | 1/12 | 35,712 → 43,555 | +21.96% |
| 8000 | 10/29 | 12/29 | 2/12 | 58,690 → 70,944 | +20.88% |

No hubo retrocesos en esta métrica: la ampliación conserva todos los rangos previos por construcción. Esa propiedad no garantiza que texto adicional irrelevante no distraiga al revisor. A 8.000 bytes siguen sin recuperarse íntegramente 17 de las 29 referencias del benchmark.

La métrica cuenta intervalos de evidencia anotada recuperados íntegramente, no afirmaciones correctamente respondidas ni toda la evidencia posible del documento. El piloto anterior mostró que las anotaciones también pueden omitir pasajes útiles. No se interpreta como fidelidad general ni como precisión clínica.

## Controles ejecutados

- Equivalencia exacta del algoritmo extraído con los rangos de los dos pilotos previos.
- Seis casos límite: UTF-8 multibyte, duplicados, ausencia de coincidencias, presupuesto exacto sin espacio extra, párrafo demasiado grande y separadores CRLF.
- Doscientos casos aleatorios con semilla fija: límites de bytes, conservación de rangos, deduplicación, referencias UTF-8 exactas y determinismo.
- Veinticuatro comparaciones reales (12 documentos × 2 presupuestos), con los mismos controles.
- Repetición local en directorio temporal nuevo: idénticos totales de cobertura y bytes. No constituye revisión independiente.

Cero llamadas a proveedores; consumo API nuevo cero. No se ejecutó la suite del producto porque no se modificó su código. Los controles prueban esta implementación experimental y estos casos, no seguridad o fiabilidad universal.

## Reproducción

`python3 experiments/shared-neighbor-validation-v1/validate.py --out /tmp/una-ruta-nueva --protocol experiments/shared-neighbor-validation-v1/protocol.json`

La salida debe ser nueva; el programa usa la selección congelada, no elige otra muestra. Requiere corpus local ignorado de QASPER y envelopes de los pilotos originales para verificar equivalencia. Resultados originales inmutables en result.json; ver replay-check.json para la repetición. La exploración de elegibilidad sólo comprueba metadatos/estructura: la reserva es local y no acredita ausencia en entrenamiento o usos históricos no registrados.

## Decisión recomendada

Mantener como candidata optativa experimental. Antes de incorporar al producto, contrastar si el texto adicional mejora las respuestas completas y sus omisiones frente al coste de lectura; usar casos nuevos o separar explícitamente desarrollo de evaluación. Los controles técnicos han pasado, pero sólo dos documentos mejoran a 8.000 bytes y la cobertura restante es baja.

No sustituir paragraphs-equal ni aumentar top_k automáticamente. Si se autoriza después la incorporación, conservar versión/estrategia optativa y estos tests de regresión, además de un criterio semántico de aceptación. La suficiencia de fuente y la admisión de resultados siguen siendo decisiones separadas.
