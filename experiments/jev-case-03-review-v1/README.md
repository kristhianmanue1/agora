# Jev: revisión separada del caso 03 de T0

Esta prueba toma la fuente completa QASPER `2002.03056` y la respuesta candidata A
de `run-2026-10-10-glm-paired-02-llavero`. Una sola petición a Jev 1.13.0 evalúa
respaldo y cobertura con opciones congeladas en `run.py`. La petición se registra
antes del envío. No hay reintentos, admisión ni cambio en el denominador T0.

Jev es aquí un revisor de opciones estructuradas, no un generador de la respuesta
B que faltó en la corrección v2. Sus etiquetas son asesoría experimental y no
adjudicación semántica independiente. La fuente y la respuesta están en el árbol
de Ágora; el proveedor recibe ambos textos. No se envía el corpus CTIM.

Ejecución con credencial inyectada, sin imprimirla:

```sh
python3 /Users/krisnova/www/aria/llavero/llavero.py ejecutar agora.dev.typesafe -- \
  /Users/krisnova/www/aria/agora/.venv/bin/python \
  /Users/krisnova/www/aria/agora/experiments/jev-case-03-review-v1/run.py
```

## Resultado, 2026-10-10

`run-2026-10-10-01/attempt.json` se escribió antes del despacho y
`result.json` conserva la respuesta. Hubo una petición, sin reintento, de 29.700
bytes. El proveedor reportó `jev-1.13.0`, 6.888 tokens de entrada y 78 de salida;
esto identifica lo reportado por la API, no verifica facturación ni hardware
ejecutor. Jev etiquetó el respaldo `supported` y la cobertura `complete`;
duración local de la petición: 0,33 s.

El cotejo manual de la fuente en las líneas 121–141 respalda la proximidad
promedio entre aplicaciones, la matriz de similitud, la relevancia de funciones
y su orden descendente. Las dos anotaciones QASPER recuperadas mencionan la
comparación con aplicaciones conocidas y el orden de recomendación. La fuente
también describe adaptación posterior a elecciones del usuario, no incluida en
los dos requisitos congelados; por eso `complete` sólo vale para este contrato
de pregunta. Las probabilidades devueltas por Jev son su salida, no una medida
calibrada de corrección.

Esta prueba no demuestra que Jev detecte una omisión: recibió una respuesta
plausiblemente completa, sin control de omisión en esta serie. Tampoco repara el
fallo de generación B del caso 03 ni reemplaza la adjudicación humana ciega.
