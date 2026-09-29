# GLM y Jev como revisores intercambiables: piloto 01

## Pregunta y alcance

¿Puede Jev clasificar el respaldo de una afirmación en lugar de GLM, con la
misma evidencia suministrada? No se cambia el generador ni se autoriza admisión
automática. Es una comparación de dos configuraciones de API, no un aislamiento
experimental del modelo frente a todos los efectos del proveedor.

24 controles sintéticos: 4 situaciones (cifra, sustitución temporal, responsable
con fecha ausente, fuentes contradictorias sin autoridad establecida), 3 clases
y 2 idiomas. Son 12 situaciones traducidas, no 24 observaciones independientes.
`prepare.py` creó `cases.json` y `gold.json` antes de las llamadas. Las etiquetas
son authored gold del agente, sin adjudicación humana independiente. Cada clase
tiene 8 casos. No son un benchmark externo ni documentos grandes reservados.
El runner no lee gold. Cada petición recibe exclusivamente evidencia y afirmación
del mismo caso. No usa la respuesta de un modelo para juzgar al otro.

## Configuraciones y límites

- GLM: `glm-5.3-flash`, temperatura 0, `json_object`, máximo 2048 tokens de salida.
- Jev: `jev-1.13.0`, pregunta `choice` con los mismos tres criterios.
- Una llamada por caso y proveedor, 24 como máximo por proveedor; 90 segundos
  por llamada, sin reintentos. Parada ante 401/402/403/429 o tres errores.
- Claves inyectadas por Llavero; sólo se transmiten controles sintéticos.
- Ambas tandas se ejecutan concurrentemente, cada una secuencial internamente.
  Esta toma única no controla variabilidad de carga, caché ni red.
- Se guardan petición, identidad, modelo reportado, salida final, uso y duración.
  Se excluye reasoning interno. Una reserva `attempted` no demuestra recepción
  del proveedor; el runner no reanuda ni repite automáticamente un directorio.
- `insufficient` es una clase semántica, distinta de error o abstención técnica.
  Fallos y casos no ejecutados permanecen en el denominador de 24.

La interfaz Jev sigue el contrato oficial de
[TypeSafe Quick start](https://docs.typesafe.ai/introduction/quickstart), consultado
el 2026-09-28. Su confidence no se usa como umbral de aceptación ni como garantía.

## Reproducción

Desde la raíz, sin llamadas para puntuar evidencia ya conservada:

```bash
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
python3 experiments/reviewer-comparison-v1/score.py RUTA_RESULTADOS_GLM RUTA_RESULTADOS_JEV
```

Los directorios contienen manifest.json y un JSON por id de caso. Los archivos
`records-glm.jsonl` y `records-jev.jsonl` conservan esos registros y su manifiesto
como primera línea (`manifest`). Para rehidratar, escribir manifest.json desde
esa primera línea y cada registro como `<case_id>.json` en directorios nuevos.

Nueva ejecución, con consumo real y rutas de salida inexistentes:

```bash
python3 /Users/krisnova/www/aria/llavero/llavero.py ejecutar zai -- /usr/bin/python3 /Users/krisnova/www/aria/agora/experiments/reviewer-comparison-v1/run.py glm --out /tmp/agora-comparison-glm-new
python3 /Users/krisnova/www/aria/llavero/llavero.py ejecutar agora.dev.typesafe -- /usr/bin/python3 /Users/krisnova/www/aria/agora/experiments/reviewer-comparison-v1/run.py jev --out /tmp/agora-comparison-jev-new
```

## Autorrevisión adversarial

- Acertar controles simples no prueba detección de omisiones: ambos ven únicamente
  la evidencia entregada y podrían aceptar una afirmación sin conocer una excepción.
- Traducciones y variantes están relacionadas; no usar 24 como muestra independiente
  para intervalos o superioridad estadística. Se necesita un conjunto reservado mayor.
- Un acierto no demuestra buen criterio de aceptación. Mantener los resultados
  candidatos, fuentes originales y adjudicación separada.
- La taxonomía puede afectar errores: falta de autoridad no equivale a evidencia de
  que una fuente sea falsa. Analizar ese desacuerdo antes de cambiar instrucciones.
- Jev tiene salida tipada y GLM JSON solicitado: se compara la configuración
  utilizable de cada proveedor, incluyendo su formato, no sólo razonamiento puro.
- Tokens de tokenizadores distintos no equivalen a coste. No se obtuvo cargo por
  llamada ni tarifa verificada: coste monetario pendiente, sin estimación inventada.
- No hay repetición por caso: no se ha medido estabilidad. No cambiar el revisor
  predeterminado con esta evidencia sola.
