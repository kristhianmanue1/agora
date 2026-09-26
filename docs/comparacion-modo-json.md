# Comparación del modo JSON: campaña interrumpida

Fecha: 2026-09-23. Implementación local completada; comparación **parcial**.

## Cambio disponible

La CLI `python3 -m agora.routed_cli` admite
`--response-format {default,json_object}`. Por defecto omite el parámetro en la
petición HTTP y conserva el comportamiento anterior. La opción `json_object`
añade únicamente `response_format={"type":"json_object"}`; no cambia prompts,
perfil, modelo ni validación local. La elección queda en `request_config`.
No exige un esquema del proveedor, no repara campos y no reintenta respuestas.
El perfil predeterminado sigue siendo `legacy`.

## Ensayo

Ejecutor: `experiments/provider-format-v1/run_comparison.py`.
Auditoría reproducible: `experiments/provider-format-v1/score_comparison.py`.
Evidencia local excluida de Git: `experiments/provider-format-v1/runs/paired-01`.

Se congelaron código, ocho fixtures de desarrollo ya conocidos y protocolo antes
de ejecutar. Se planificaron 16 solicitudes, una por modo y caso, con orden
alternado, `concise-v1`, `glm-5.3-flash`, temperatura 0, máximo 8192 tokens,
timeout de socket de 90 segundos y de proceso de 110 segundos por llamada.
Los idiomas se mantuvieron según cada fixture. Sin reintentos. Parada ante
fallo de transporte/acceso/configuración/integridad.

Se completaron cuatro respuestas (dos pares). La quinta solicitud, E3/default,
terminó con `timeout` después de 90.492 segundos. Se detuvo la campaña y no se
intentaron las once llamadas restantes. No se conoce el consumo ni el resultado
del lado del proveedor para esa solicitud. El timeout no demuestra que el modo
predeterminado sea menos fiable.

| Sólo pares completos E1/E2 | default | json_object |
|---|---:|---:|
| Respuestas parseables como JSON | 2/2 | 2/2 |
| Campos exactos requeridos presentes | 2/2 | 2/2 |
| Contrato local aceptado | 2/2 | 2/2 |
| Abstenciones esperadas | 2/2 | 2/2 |
| Tokens reportados | 2104 | 2514 |
| Segundos de las llamadas completas | 23.112 | 24.104 |

La campaña consumió **4618 tokens conocidos más el consumo desconocido del
timeout**. Tiempo acumulado de los cinco procesos: 137.708 segundos. Son dos
pares y caché no controlada; no hay base para recomendar un modo por coste o
latencia. `scores.json` conserva conteos por modo incluyendo la llamada fallida;
la tabla anterior restringe ambos denominadores a pares completos.

## Revisión y límites

La autorrevisión semántica contrastó las cuatro respuestas con las fuentes:
E1 distingue una práctica general del método del ensayo Cedar; E2 distingue
resultados de escuelas urbanas de una pregunta sobre escuelas rurales. Ambas
abstenciones son coherentes con el texto. No es revisión independiente.

Las cuatro respuestas llevan `quotes: []` porque se abstienen. **No se obtuvo
ningún caso con citas que permita evaluar su literalidad en esta campaña.**
Tampoco se ejecutaron los controles positivos previstos D2/D4/D6/D8. La
comparación está incompleta, no es un éxito 100% ni evidencia de generalización.

Se verificaron hashes de protocolo, código y fixtures; integridad de cada
resultado; igualdad exacta de prompts y fuentes entre modos; correspondencia
entre código ejecutado y código actual. La suite pasó: **183 tests**. Tres
pruebas nuevas ejercitan el transporte con HTTP simulado: omisión del parámetro
por defecto, cambio exclusivo de formato y rechazo de campo ausente sin
reintento. No acreditan disponibilidad del proveedor. `git diff --check` pasó.

## Recomendación

Mantener `default` y no promover `concise-v1`. La opción JSON queda disponible
para experimentación explícita, sin evidencia suficiente para recomendarla.

Siguiente bloque: comprobar disponibilidad del proveedor con un control pequeño;
si responde, completar en una campaña nueva y separada los seis pares E3/E4 y
D2/D4/D6/D8, preservando este timeout y los mismos prompts/configuración.
Declarar cualquier reejecución de E3 como nueva ejecución, no como corrección
del historial. No gastar aún una nueva muestra QASPER ni cambiar el prompt.

## Cierre posterior

Los seis pares pendientes se ejecutaron en una campaña separada. Véase el
[cierre de comparación](comparacion-modo-json-cierre.md): se mantiene el modo
predeterminado; el timeout de la campaña inicial se conserva.
