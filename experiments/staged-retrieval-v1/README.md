# Ampliación por etapas: conservación demostrada en el ensayo offline

Protocolo congelado: candidatos híbridos a 8.000, 12.000, 20.000 y 32.000 bytes,
conservando todos los rangos acumulados. Se reconsideran rangos descartados por
presupuesto, se deduplican y no se recortan fragmentos. No se usan respuestas ni
anotaciones para seleccionar. Se puntúa después de acumular.

Cuatro documentos conocidos y dos reservados mediante inventario local antes de
medir: 1709.06365 (aumento de datos) y 1909.09070 (baselines supervisados). No se
presume ausencia de exposición fuera del inventario o en entrenamiento. Rúbricas
derivadas de la primera anotación humana de QASPER; no revisión independiente nueva.

| Caso | Primer techo con párrafos anotados completos | Parada por candidatos agotados | Bytes finales |
|---|---:|---:|---:|
| Modelos preentrenados, conocido | 8.000 | 20.000 | 12.216 |
| Validación cruzada, conocido | 8.000 | 20.000 | 12.101 |
| Modelos de referencia, conocido | 20.000 | 20.000 | 15.116 |
| Mitigación de sesgo, conocido | 12.000 | 12.000 | 10.983 |
| Aumento de datos, reservado local | 8.000 | 12.000 | 9.348 |
| Baselines supervisados, reservado local | 8.000 | 12.000 | 10.512 |

La primera columna de presupuestos es una medición posterior contra anotaciones,
no un criterio de parada del selector. Los dos casos nuevos no demuestran reparación
de una omisión inicial: sus referencias ya estaban presentes a 8.000. No se escogieron
otros casos para forzar una mejora.

## Qué prueba y qué no

Se preservan rangos, límites y referencias anotadas al ampliar. El método puede
retener pasajes inútiles y consumir más presupuesto. La rúbrica de modelos conocida
sigue incompleta: coincidencia de rangos no equivale a respuesta completa y fiel.

La parada consulta los conjuntos de candidatos de todos los presupuestos, calculados
previamente de forma offline. No hay ejecución interactiva ni ahorro demostrado de
recuperación local. Sólo se detiene antes del techo final si ningún candidato
programado pendiente añade bytes. Una etapa sin ganancia no basta si quedan
candidatos posteriores. Agotar candidatos **no significa suficiencia semántica**.

Cinco tests y reproducción: conservación/presupuesto, reintento de rangos locales
sin nueva entrada, etapa sin ganancia con candidatos futuros, techo insuficiente
sin falsa completitud, replay. Cero proveedores; sin respuestas nuevas ni evaluación
semántica, sin cambios productivos/defaults.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 experiments/staged-retrieval-v1/tests.py
PYTHONDONTWRITEBYTECODE=1 python3 experiments/staged-retrieval-v1/run.py
```

Fuentes y dataset previos requeridos localmente; hashes en freeze.json. La selección
reservada original está en selection-freeze.json. Los originales no se modificaron.

## Continuación propuesta

Antes de integración, evaluar un recorrido por etapas que use revisión explícita de
cobertura y fidelidad para decidir continuar, no el agotamiento de candidatos como
aceptación. Congelar costes máximos acumulados y conservar todos los intentos.
Mantener una salida de evidencia insuficiente cuando no aparezcan nuevos pasajes.
La decisión de suficiencia requiere una rúbrica adecuada y comprobación de citas;
no se deriva del tamaño del contexto ni de la estabilidad del selector.
