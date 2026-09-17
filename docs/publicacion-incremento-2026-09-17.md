# Publicación del incremento local — 2026-09-17

El Operador autorizó commit y push de Ágora y Pinax tras solicitar su estado.
Esta nota registra la preparación; la confirmación de publicación corresponde
al SHA remoto observado al cierre, no a la existencia de este documento.

## Alcance

Código de transformación, consulta directa/por selección/por resumen y revisión
local; ocho módulos de pruebas, seis documentos de uso, organización del piloto
y actualización acotada de estado en AGENTS.md previamente autorizada.
Las menciones «sin commit/publicación» en las notas de incrementos describen
su estado histórico anterior a esta autorización.

No se incluyen `experiments/source-query-pilot/inputs/`, la transcripción médica,
sus extractos, respuestas ni vistas HTML. Permanecen locales e ignorados por Git.
Las referencias a esos archivos describen evidencia local no distribuida.

## Verificación para publicación

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests`:
  76 pruebas, OK; sin llamadas al proveedor.
- `git diff --cached --check`: sin hallazgos en el lote previo a esta nota.
- AN-KLA: integridad OK, revisión 3, usando el entorno propio `.venv`.
  El intento con el entorno de Pinax devolvió `reader_gate_unavailable`;
  no se modificó el store. Plantilla declarada beta.21 frente a beta.26:
  actualización pendiente, separada de esta publicación.
- Revisión final de publicación: alcance, privacidad y límites documentados.
  Los dictámenes se informan en el cierre; esta nota no anticipa su resultado.

## Límites conservados

Fuente máxima 4096 bytes; selección de líneas explícita; citas literales no
certifican soporte semántico. Sin motor jerárquico ni integración contractual
con Skopos/AN-KLA. La revisión HTML tiene pruebas funcionales y de contenido;
la inspección visual renderizada sigue pendiente. El experimento M1-R1 no se
modifica ni se promueve. No se ejecutan nuevas corridas GLM, despliegue ni
escrituras de memoria. Publicar código no adjudica resultados experimentales.
