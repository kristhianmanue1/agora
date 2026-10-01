# Reto de omisiones inducidas: sin éxito completo

Dos documentos nuevos según inventario local, seleccionados por hash antes de
llamadas: QASPER 2004.02105 y 1803.05160. Cada entrada es una respuesta vacía
**sintética**, identificada como tal, con sólo el primer párrafo como contexto.
Esto prueba recuperación desde falta inducida; no mide frecuencia natural de omisión.
La revisión GLM marcó los tres requisitos de cada semilla como missing.

Congelado antes de ejecución: pregunta completa como consulta, presupuesto 12.000
bytes, top-k 3 y hasta tres párrafos siguientes. Generación 4.096 tokens; revisión
2.048, una llamada por fase y caso, sin reintentos ni sustitución de casos.

| Resultado | Modelos preentrenados | Variantes de validación cruzada |
|---|---|---|
| Contexto inicial → propuesto | 58 → 9.548 bytes | 68 → 9.650 bytes |
| Generación | Rejected: invalid_json | Complete, respuesta parcial |
| Cobertura posterior | No ejecutada por rechazo | Failed: generation_incomplete |
| Jev | No ejecutado por rechazo | Tres afirmaciones y declaración de faltante supported |

El primer proveedor reportó finish_reason=stop, pero añadió una nota después del
JSON (el parser detecta Extra data). Ágora rechazó la salida sin extraer el primer
objeto ni repararlo. El segundo revisor consumió 2.048 tokens de razonamiento,
finish_reason=length y contenido vacío: no hay dictamen de cobertura. No se
reinterpretan estos fallos como omisiones etiquetadas ni como aprobación.

Los párrafos exactos anotados por la rúbrica quedaron fuera de ambos contextos.
Esto revela que la recuperación no alcanza esas referencias; por sí solo no prueba
que no haya evidencia equivalente en otros pasajes. El candidato válido distingue
validación aleatoria y por bloques, pero no enumera las tres configuraciones
completas de la referencia (pliegues, estratificación y selección). Esta observación
textual del productor no reemplaza la revisión de cobertura fallida.

Seis llamadas de un máximo de ocho; 17.611 tokens reportados, incluidos fallos.
Sin precio monetario ni latencia total medidos. Las respuestas originales, propuestas,
requests y revisiones se conservan localmente en inputs/runs (excluidos de Git);
`result.json` publica resultados y hashes. `verify.py` reproduce las solicitudes y
resultados, incluidos rechazos, sin red. No hubo cambio de producto ni de defaults.

## C6 anterior

[Contraste técnico](c6-review.md): respaldo contextual disponible para las ideas
centrales, con referente WED/CDA en el párrafo anterior y un ejemplo específico de
BIBREF5 comprimido en la misma afirmación. Hipótesis sobre la discrepancia, no causa
demostrada del voto. Original conservado; aceptación independiente pendiente.

## Decisión y siguiente paso

No promover la estrategia. Separar tres problemas: selección que deja fuera pasajes
anotados, respuesta que incumple JSON y revisión que agota presupuesto. Antes de
cambiar parámetros, comparar offline qué recuperan consulta exacta, términos de la
pregunta y continuidad de sección. Usar anotaciones sólo para puntuar, no para formar
consultas. Congelar después una condición nueva; no reescribir esta ni reintentar
hasta obtener verde. Cualquier reparación de formato debe crear un derivado explícito.
