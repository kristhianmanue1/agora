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
