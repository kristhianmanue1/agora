# Piloto v2 — resultado parcial, 27 de septiembre de 2026

Se implementó un contrato experimental por campo (valor, soporte, requisitos,
relaciones y citas). El programa deriva estado global y campos reabiertos;
propaga la señal de revisión sólo a dependencias declaradas del campo afectado.
No modifica documentos reales ni constituye motor persistente de pendientes.

## Ejecución glm-01

Ocho llamadas previstas a glm-5.3-flash; tres intentadas, dos completadas.
En el caso wrong_history ambos brazos devolvieron fecha 2026-10-21 y responsable
Lina, de acuerdo con w1. El brazo tracked recibió como antecedente 2026-11-30 y
Marco y corrigió ambos valores. Las dos evaluaciones coinciden con los seis ejes
del gold: valores, soporte, requisitos, estado, campos reabiertos y afectados.
Las citas se verificaron literalmente; el productor contrastó valores y razones
con w1. No hubo adjudicación independiente.

| Solicitud | Resultado | Tokens reportados | Segundos |
|---|---|---:|---:|
| wrong_history / full | completa | 1369 | 12.832 |
| wrong_history / tracked | completa | 2145 | 26.445 |
| late_source / tracked | TimeoutError de transporte | desconocidos | 90.192 |

Se conservan 3514 tokens conocidos y una llamada de consumo desconocido.
No presentar 3514 como coste total. No se calculó coste monetario.
Timeout no demuestra que el proveedor no procesara la petición.
Se aplicó parada del protocolo: no hubo reintentos ni ejecución de las restantes
cinco solicitudes. Ninguna conclusión semántica sobre late_source es válida.

## Evidencia local

315 tests pasan, incluidos cinco controles nuevos: reapertura parcial sin
invalidar responsable, referencias y requisitos inventados, intento de
sobrescribir estado calculado, separación del antecedente y contradicciones de
forma en una retirada de fecha. Estos tests no prueban que GLM clasifique bien.
Manifiesto congelado verificado. En el par completado sólo cambia la evaluación
previa. Se preserva v1 intacto. No se modificaron src/agora ni AGENTS.md.

## Autorrevisión y límites

- El antecedente falso no incluía citas: es un control inicial fácil. No demuestra
  resistencia a antecedentes erróneos con citas plausibles o múltiples copias.
- La señal affected depende de relaciones propuestas por el modelo. El cálculo
  determinista no convierte esa propuesta en un juicio semántico verificado.
- La llegada tardía, refutación parcial y dependencia no afectada no cuentan con
  resultados reales del proveedor; existen sólo fixtures y controles locales.
- Requisitos, identidad, autoridad declarada y dependencias se suministran. No se
  evalúa su descubrimiento, autenticación, concurrencia ni corpus grandes.
- Casos y gold del productor, una repetición, sin holdout independiente.
- El sobre JSON no constituye adopción de contrato estable ni integración AN-KLA.

## Continuación propuesta

Conservar glm-01. Para completar la comparación, preparar una ejecución nueva
con presupuesto separado y timeout HTTP 180 s/proceso 190 s para los tres casos
pendientes (seis llamadas como máximo), manteniendo modelo, prompt y gold.
Registrar que cambia el límite temporal; no mezclar silenciosamente costes o
latencias entre ejecuciones. No se ha ejecutado esta continuación.
Después, sólo si esos casos pasan, probar antecedentes falsos con citas
existentes pero que no respaldan el valor y fuentes con autoridad insuficiente.

Archivos: `protocol.py`, `cases.json`, `gold.json`, `build_cases.py`, `run.py`,
`README.md`, `result-glm-01.json`; evidencias crudas congeladas en runs/glm-01,
ignoradas por Git. Los archivos nuevos permanecen locales, sin commit ni push.
