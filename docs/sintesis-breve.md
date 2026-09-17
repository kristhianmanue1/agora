# Síntesis breve y evidencia separada — incremento local

Encargo del Operador: continuar tras lote de cinco fuentes que preservó hechos
pero amplió texto. Una fuente más larga, síntesis breve y citas separadas.
No es una nueva fase del experimento congelado M1 ni una publicación.

## Implementación

Flag opcional `--summary-max-bytes N` (128..4096; int exacto en API). El modo
anterior sigue disponible sin el flag. Se usa prompt-v0.2-compact y conserva
el prompt efectivo en el resultado. No cambió el máximo de generación:1200.

Se producen dos vistas sólo si pasan estructura, citas, finish_reason=stop y
límite de bytes: summary.txt incluye «Borrador pendiente de revisión» y IDs Cn;
evidence.json vincula esos IDs a líneas/citas y hash de fuente. El presupuesto
cuenta UTF-8 del render entero, incluido encabezado, IDs y LF. Son vistas de un
candidato sin revisión semántica automática. result.json conserva procedencia.

El tamaño separado de síntesis no representa tamaño total ni ahorro de tokens.
El registro de evidencia puede seguir siendo mayor que la fuente. No modifica
fuentes, no autentica contenido ni publica o incorpora memoria.

## Ensayo autorizado y resultado

Fuente sintética Nerea nueva:2623bytes,14líneas,seis hechos críticos señalados.
Una petición glm-5.3-flash, síntesis<=700bytes,1200tokens de salida,45s,sin retry.
Fuente, oráculo y código congelados antes de generar; copias de código anterior
y ejecutado conservadas. No se enviaron hechos de referencia al productor.

Resultado NO_USABLE_OUTPUT. Proveedor reportó finish_reason=length, contenido
vacío,981tokens de entrada+1200salida=2181total; dentro de la salida reportó1198
reasoning_tokens. La CLI rechazó con generation_not_confirmed_complete y exit2.
No se generaron summary.txt/evidence.json. No se reintentó ni se corrigió salida.
El contador de razonamiento es metadato de uso; no se persistió su contenido.

No hay evidencia de preservación de seis hechos, cumplimiento de700bytes,
compresión o utilidad. Tampoco prueba que el límite de700bytes sea imposible:
el proveedor agotó otro presupuesto, el de generación, sin devolver texto final.
No se atribuye causa más específica al prompt o al proveedor.

## Pruebas y siguiente decisión

19 tests core/CLI pasan. Casos nuevos: enlace de vistas, bytes UTF-8, frontera
exacta, presupuesto inválido antes del proveedor, rechazo length sin emitir
vistas ni reintentar. No se han probado escrituras atómicas del conjunto de
archivos ni concurrencia de exportación; es una CLI local de un solo proceso.

Antes de otro ensayo, elegir una configuración de generación con presupuesto
suficiente para obtener texto final y fijarla de nuevo. No aumentar a ciegas
la fuente o reducir restricciones semánticas para hacer pasar la prueba.
Cualquier ensayo adicional debe tener identidad propia; este fallo permanece.
No se hizo otra llamada en este incremento.

Evidencia externa al repositorio:
`/Users/krisnova/www/aria/pinax/docs/design/agora-sintesis-breve-v1/`.
El código anterior preservado coincide con hashes del lote de cinco fuentes;
esos resultados anteriores no se modificaron. La implementación actual es otra
versión local, no debe verificarse contra hashes de código anteriores.

## Segundo ensayo: presupuesto4096 y timeout

En el incremento siguiente se añadió `--max-output-tokens` (128..4096;
default1200). El valor pasa a la petición y al recibo de respuesta cuando existe.
21tests pasan, incluidos paso de4096 al transporte y rechazo de4097 antes de red.
El control de síntesis700bytes y el core no cambiaron.

Se ejecutó una sola solicitud con presupuesto4096, misma fuente, prompt, ID,
líneas requeridas y timeout45s. Resultado: TimeoutError,exit1. Sin respuesta
conservada ni recibo de uso. No sabemos cuántos tokens consumió el servidor ni
si completó el trabajo después de que el cliente dejara de esperar. No inferir
uso cero ni terminación remota a partir de ese error.

Este intento no produjo summary.txt/evidence.json. Sus seis hechos siguen sin
poder evaluarse. El fallo original por finish_reason=length permanece intacto.
Evidencia del segundo intento:
`/Users/krisnova/www/aria/pinax/docs/design/agora-sintesis-breve-v2/`.

Antes de otra llamada, fijar conjuntamente presupuesto de tokens y espera del
cliente, dejando un máximo de solicitudes y preservando resultados incompletos.
No hubo reintento ni llamada adicional en este segundo ensayo.

## Tercer intento autorizado:8192tokens y180s

El Operador ordenó duplicar tokens y cuadruplicar tiempo frente al segundo
intento. CLI ahora admite --max-output-tokens128..8192 y --timeout-seconds1..180,
con defaults1200/45. El timeout es por operación urllib, no deadline global.
También registra request_config en los fallos sin respuesta.22tests pasan.

Un intento con fuente/core/prompt iguales y límite700bytes respondió en26,07s.
Proveedor reportó stop,981tokens entrada+1365salida=2346total (906de razonamiento
incluidos en la salida). El presupuesto8192 es máximo, no consumo observado.

La generación completa produjo seis claims, pero su render mide838bytes:138más
del límite. Ágora rechazó con summary_budget_exceeded/exit2 y no emitió las vistas.
Revisión separada del raw_output encontró los seis hechos respaldados; es un
análisis auxiliar del candidato rechazado, no una salida aceptada. El dictamen
global sigue NO_USABLE_OUTPUT por el contrato de tamaño. No hubo corrección,
relajación del límite ni otra llamada automática.

El nuevo problema observable es concisión, no falta de texto final. Antes de un
siguiente ensayo, ajustar formulación para quitar redundancia manteniendo700bytes
y los seis hechos; no aumentar límites después de ver la salida para aprobarla.
Evidencia: `/Users/krisnova/www/aria/pinax/docs/design/agora-sintesis-breve-v3/`.
