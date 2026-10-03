# Selección automática frente al plan manual — 2026-10-03

## Resultado

En este documento conocido, el recuperador léxico no alcanza el plan manual de
cuatro párrafos. Con pregunta en español no recupera candidatos sobre la fuente
inglesa. Con traducción inglesa, la mejor configuración recupera dos párrafos,
pero deja fuera los dos que describen la arquitectura y predicción.

| Pregunta | Presupuesto bytes | top_k | Entregado bytes | Párrafos manuales completos | Bytes manuales recuperados |
|---|---:|---:|---:|---:|---:|
| Español | 5.000 | 3 | 0 | 0/4 | 0 |
| Español | 5.000 | 6 | 0 | 0/4 | 0 |
| Español | 12.000 | 3 | 0 | 0/4 | 0 |
| Español | 12.000 | 6 | 0 | 0/4 | 0 |
| Inglés | 5.000 | 3 | 4.708 | 0/4 | 0 |
| Inglés | 5.000 | 6 | 4.961 | 1/4 | 585 |
| Inglés | 12.000 | 3 | 5.315 | 0/4 | 0 |
| Inglés | 12.000 | 6 | 11.010 | 2/4 | 1.162 |

El plan manual conserva 3.224 bytes de una fuente de 45.557. Sus párrafos son:
objetivo de satisfacción, recogida/mapeo de etiquetas, componentes del modelo y
mecanismo Transformer/cabeza lineal. La mejor selección automática cubre los dos
primeros. A 5.000/top_k=6 cubre sólo recogida/mapeo. Bytes fuera de la referencia
**no significan texto irrelevante**; pueden contener evidencia alternativa.
No se evaluó aquí la semántica de todo lo recuperado ni respuestas generadas.

## Método y controles

Ocho condiciones congeladas antes de ejecutar: dos idiomas, dos presupuestos y
dos valores top_k. Mismo documento, método `paragraphs-equal` existente; se conserva
la expansión a vecinos que ese método ya implementa. top_k limita semillas, no el
número final de párrafos tras la expansión. La pregunta incluye las instrucciones
para responder del caso previo: así funciona hoy este recorrido. La traducción es
del productor, no independiente, y no convierte el experimento en prueba reservada.

Los rangos manuales **no se pasaron al selector** (`reference_ranges=[]`). Se usan
sólo después, para intersección de intervalos y cobertura de los cuatro párrafos.
Control positivo: los rangos manuales recuperan 4/4. Control negativo: selección
vacía recupera 0/4. Se verificaron hashes, presupuesto, literalidad UTF-8 y suma de
bytes. Cada condición escaneó localmente la fuente completa de 45.557 bytes: menos
bytes entregados no significa menos lectura local por el programa.

Cero llamadas de modelo, cero tokens nuevos y sin cambio de código del producto.
Los tiempos en result.json son observaciones locales individuales, no un benchmark
de rendimiento. Esta ronda no volvió a probar MemOS, Skopos ni AN-KLA.

## Diagnóstico y siguiente paso acotado

El algoritmo puntúa coincidencias de palabras; no traduce ni usa embeddings. En
español hubo cero párrafos con coincidencias; no es evidencia de ausencia en fuente.
La traducción mejora el solapamiento, pero no garantiza todos los aspectos. Subir
el presupuesto por sí solo no resolvió la cobertura.

Probar primero una especificación explícita de subpreguntas en el idioma de la
fuente, separando etiquetas y mecanismo de predicción de las instrucciones de
formato/idioma. Reutilizar el recuperador de subpreguntas existente. Medir contra
estos rangos sin pasárselos como guía de selección. No hacer nuevas llamadas de
generación hasta que los pasajes necesarios estén disponibles. No se propone aún
cambiar el valor predeterminado ni introducir traducción automática silenciosa.

## Reproducibilidad

```bash
PYTHONDONTWRITEBYTECODE=1 python3 experiments/selection-comparison-v1/run.py \
  --repo "$PWD" --source /ruta/1901.05415.txt --out /tmp/seleccion-nueva
```

La salida debe ser nueva. `freeze.json` fija fuente, plan manual, condiciones y
commit inicial; `result.json` registra métricas y hashes de código. La ejecución
genera además los ocho planes completos, útiles para inspeccionar texto y rangos.
El banco conserva este resultado y verifica su integridad. No certifica fidelidad.
