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

La primera petición no demostraba que Jev detectara una omisión: recibió una respuesta
plausiblemente completa, sin control de omisión en esa serie. Tampoco repara el
fallo de generación B del caso 03 ni reemplaza la adjudicación humana ciega.

## Control de omisión posterior

El [congelado](control-freeze.json) fija antes de red una sola mutación: retirar
la tercera afirmación de A, que explicaba el orden descendente. El
[ejecutor](run_control.py) comprueba hashes de fuente, respuesta y petición A,
y conserva pregunta, requisitos, fuente, modelo, criterios e instrucciones.
Registra el intento antes de la única llamada. El control mantiene `answered`
y `missing: ""`, para probar si la revisión detecta la omisión declarada.

En `control-run-2026-10-10-01`, Jev reportó `supported` para las dos afirmaciones
restantes y `omitted` para cobertura, frente a `supported` y `complete` en A.
El modelo reportado fue `jev-1.13.0`; uso reportado: 6.797 tokens de entrada y
79 de salida; duración local: 0,219 s. La [autorrevisión](control-run-2026-10-10-01/adjudication.json)
constata que la fuente explica el orden descendente en la línea 141 y la copia
enviada no lo hace. Una comprobación estructural confirmó que la petición sólo
cambió el contenido de la respuesta candidata.

**Alcance del resultado:** Jev discriminó este par positivo-negativo local.
El productor creó y revisó el control; no hubo adjudicador independiente ni
muestra reservada. No se infiere fiabilidad general, calibración de sus
probabilidades, utilidad en producción ni reparación del B fallido.
