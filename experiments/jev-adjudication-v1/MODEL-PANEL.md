# Enmienda para panel de modelos, 2026-10-10

El Operador designó a **Codex y OpenCode** como los dos adjudicadores de este
paquete. Esta decisión sustituye **sólo para esta ronda** la exigencia de dos
adjudicadores humanos del `PROTOCOL.md`. El protocolo y su llave histórica se
conservan para no presentar la nueva ronda como una adjudicación humana.

Cada programa recibirá una copia extraída del ZIP ciego en un directorio local
distinto. Se solicita una revisión completa sin acceso al origen, brazo,
controles, expectativas ni salidas del otro revisor. Codex CLI usa el modelo
solicitado `gpt-6-sol`; OpenCode usa `zai-coding-plan/glm-5.3-flash` según
configuración local comprobada. El identificador reportado por cada CLI o API
se registrará por separado; la identidad efectiva del ejecutor puede seguir
desconocida.

La separación es de contexto y distribución, no aislamiento del sistema
operativo: ambos procesos pueden tener otras rutas legibles según sus propios
permisos. Las instrucciones les limitan a la carpeta ciega; el registro de
herramientas se revisará cuando esté disponible. OpenCode/GLM comparte familia
con el generador de los candidatos T0, y la instancia que preparó el paquete
también pertenece a Codex. Sus juicios son revisiones por modelos con posible
dependencia, no referencia humana independiente.

La petición y el modelo solicitado se congelan en `model-panel-freeze.json`.
Habrá **un intento por programa, sin reintentos**. Los resultados se fijarán
por hash antes de abrir `sealed/`. Si un proceso falla, queda registrada la
salida incompleta y no se inventa una hoja. Los criterios de respaldo y
cobertura de `blind/INSTRUCTIONS.md` permanecen; las reglas de promoción del
protocolo humano no se satisfacen por reemplazar a sus adjudicadores.

## Resultado observado

Ambos programas devolvieron 12 juicios válidos en su primer intento, en
directorios separados que contenían sólo `blind/`. Las hojas y hashes se
fijaron antes de comparar con `sealed/`. El [resultado cotejado](model-panel-results/comparison.json)
registra acuerdo en claridad 12/12, respaldo 11/12 y cobertura 12/12. Los dos
controles preparados tuvieron las etiquetas esperadas en ambos revisores.

El único desacuerdo es `J-f119f8f68a`: Codex marcó `unsupported` y OpenCode
`supported`. La respuesta presenta un corpus como el único disponible para la
tarea; la fuente condiciona esa exclusividad a «to the best of our knowledge».
La pérdida de esa salvedad puede ser material para respaldo. Se conserva el
desacuerdo sin decidirlo por mayoría.

Las hojas, locks y comparación están en `model-panel-results/`. Los logs crudos
quedan locales en `exports/model-panel/` y no se publican. Los registros de
herramientas visibles mostraron lectura de las fichas y fuentes de `blind/`;
esto no prueba aislamiento a nivel de sistema operativo. OpenCode añadió 227
bytes de prosa después del JSON; el validador extrajo el primer objeto sin
corregir sus etiquetas. El modelo efectivo permanece `unknown`.

Los dos controles del paquete original **no eran** las dos omisiones exactas
que Jev había marcado `unsupported`. Para probar ese desacuerdo específico se
ejecutó un [suplemento ciego separado](supplement-v1/README.md), sin modificar
las doce fichas originales. El acuerdo del panel es evidencia experimental,
no aceptación humana independiente ni habilitación del revisor como puerta de
admisión.
