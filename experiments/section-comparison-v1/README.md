# Selección por secciones: caso conocido y dos documentos nuevos

## Resultado

Se evaluaron los selectores estructurales **ya existentes**, sin cambiar código
ni llamar a modelos. Cuatro métodos, dos presupuestos, cinco preguntas: 40
condiciones. Los casos y parámetros se congelaron antes de seleccionar; las
anotaciones se consultaron después de completar todas las selecciones.

### Caso conocido: 1901.05415

| Método | Bytes con límite 5.000 | Párrafos /4 | Bytes con límite 12.000 | Párrafos /4 |
|---|---:|---:|---:|---:|
| Solapamiento | 4.966 | 1 | 8.985 | 2 |
| IDF | 4.951 | 1 | 11.004 | 2 |
| Encabezados | 3.981 | 3 | 5.952 | 4 |
| Encabezados y cuerpo/listas | 4.101 | 3 | 5.991 | 4 |

La estructura permite localizar los párrafos de arquitectura/predicción que el
ranking de palabras dejaba fuera. Esto establece cobertura de la referencia manual,
no fidelidad de una respuesta que no se generó ni suficiencia general.

### Documentos nuevos en los expedientes revisados

Selección determinista: primeros dos IDs ordenados no hallados en archivos de
experimentos escaneados, 40–100 KB, primeras dos preguntas. No se usaron etiquetas
para elegir casos. «Nuevos» no significa garantía universal de que ningún agente
los haya visto fuera de esos archivos. No hubo ajustes tras observarlos.

- **1907.12984 — conjuntos de datos:** con 12.000 bytes, encabezados/cuerpo-listas
  entrega 9.290 bytes y cubre ambas anotaciones (1/1 y 4/4). IDF cubre 1/1 y 3/4;
  solapamiento 1/1 y 2/4. Encabezados solos entrega sólo el título y no recupera
  evidencia, aun con mayor presupuesto.
- **1907.12984 — sistema con texto completo frente a streaming:** ningún método
  recupera los pasajes anotados (0/3 y 0/1) en ambos presupuestos. No equivale a
  declarar que no hay respuesta en el documento.
- **2003.04707 — interpretación del modelo:** una anotación declara no respondible;
  otra aporta dos evidencias, no recuperadas. Se conserva el desacuerdo; no se
  fabrica una etiqueta única ni se trata el vacío de la primera como acierto.
- **2003.04707 — comparación con métodos basados sólo en datos:** una anotación
  apunta a Table 4, ausente del texto renderizado; otra no adjunta evidencia. La
  cobertura no es evaluable con esas referencias. No se suma al denominador como
  una omisión demostrada del recuperador.

## Controles de representación y evaluación

Se usó `agora.qasper.render` para todos los métodos: separa encabezados con doble
salto de línea, requisito del selector estructural. El caso conocido pasó de
45.557 a 45.571 bytes; tiene otra revisión SHA-256. Se remapearon los cuatro textos
manuales a la fuente canónica. Nunca se copiaron offsets de la revisión anterior.
Por ello estas cifras sólo se comparan dentro de esta campaña, no como una mejora
causal sobre cifras históricas que usaban otro render.

Los selectores reciben estructura/pregunta, nunca anotaciones. Las evidencias se
localizan por su primera aparición literal en el render; la cobertura exige
contención completa. Es una métrica de localización, no de entailment. Las
anotaciones se puntúan por separado y no se mezclan en un único porcentaje global.

La política no es idéntica: léxicos usan seis semillas y vecinos; estructurales
hasta tres secciones. Comparten presupuesto, no algoritmo ni número de candidatos.
Ambos selectores estructurales conservan el título incluso sin coincidencias:
**devolver algunos bytes no demuestra haber encontrado evidencia**.

## Reproducir y verificar

```bash
PYTHONDONTWRITEBYTECODE=1 python3 experiments/section-comparison-v1/run.py \
  --repo "$PWD" --out /tmp/secciones-nuevo
python3 scripts/verify_benchmark_evidence.py
```

La salida debe ser nueva. Dataset local fijado por hash en freeze.json; el script
verifica render y offsets y guarda las selecciones antes de puntuar anotaciones.
`result.json` conserva 40 resultados y detalles; `references.json`, rangos,
referencias no localizables y estado de cada anotación. No se copia el dataset.
Cero llamadas API, cero tokens nuevos, sin cambio de código de producto ni pruebas
nuevas de MemOS. La inspección corresponde al productor, sin revisión independiente.

## Decisión propuesta

La estructura merece conservarse como alternativa explícita, no promoverse como
solución universal. Para el caso conocido, comprobar ahora que el plan estructurado
existente entrega los mismos cuatro párrafos al generador. Para evaluación amplia,
separar preguntas textuales, discrepancias de anotación y fuentes con tablas. El
próximo fallo prioritario de recuperación es la comparación streaming/texto completo,
con referencia localizable: no gastar en generación hasta recuperar su evidencia.
