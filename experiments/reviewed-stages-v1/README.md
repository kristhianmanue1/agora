# Revisiones entre etapas: rutas observadas y límite semántico

Tres casos fijados antes de llamadas: un control conocido con evidencia fuera del
contexto inicial y dos fuentes del ensayo offline anterior. Lectura monotónica
preparada a 8/12/20 KB según caso. Cada etapa puede generar, revisar rúbrica con GLM
y revisar fidelidad con Jev. No se admiten memorias ni se alteran originales.

Regla congelada: fallo de generación/revisión detiene; contradicción/incertidumbre
o fidelidad insuficiente exige inspección; cobertura missing con citas respaldadas
y otro contexto permite ampliar; covered con respaldo produce candidato para
revisión explícita. Nunca aceptación automática.

## Resultado real

| Caso | Lectura inicial | Resultado de etapa | Decisión |
|---|---:|---|---|
| Modelos de referencia | 7.680 bytes | GLM contradicted en ambos requisitos; Jev respalda declaración de falta en pasajes | Inspección de cobertura |
| Aumento de datos | 7.154 bytes | Generación invalid_json con finish_reason stop | Detener, conservar rechazo |
| Baselines supervisados | 7.937 bytes | GLM 2/2 covered; Jev 5/5 supported | Candidato para revisión explícita |

Siete llamadas, 18.930 tokens reportados; sin reintentos. **Ningún caso avanzó a la
segunda etapa en esta ejecución.** La ruta expand pasó tests sintéticos, no quedó
validada en vivo aquí. No se sustituyeron casos ni etiquetas para forzarla.

El primer candidato dice no encontrar el baseline en los pasajes suministrados;
no niega su existencia en la fuente completa. Jev evalúa esa ausencia sólo frente
al contexto leído. El revisor de rúbrica la etiqueta contradicted frente a la tarea.
No es prueba de una falsedad global del candidato. Es una discrepancia de alcance
que requiere inspección: pudo haberse clasificado missing y activar más lectura.
Esta es interpretación técnica, no explicación verificada del razonamiento de GLM.

## Límites y verificación

Máximo 21 llamadas para los tres recorridos, tres etapas por caso, 4.096 tokens de
salida por generación y 2.048 por revisión GLM; máximo teórico 18.432 tokens de salida
GLM por caso. No existe un techo único de tokens totales entre proveedores: entrada
acotada por bytes, Jev usa choice, y se contabiliza el consumo observado. Precio
monetario no medido. Timeout 90 segundos por llamada; cero reintentos.

Seis tests de decisión y replay de solicitudes/resultados/linaje pasaron. La
conservación de rangos entre etapas no se ejercitó en vivo porque todos se detuvieron
en la primera; su evidencia está en el ensayo offline anterior. Archivos completos
locales en inputs/runs excluidos de Git; resultados, respuestas y hashes publicados.
Los scripts requieren esas fuentes locales para reproducir. No hay integración en
la CLI productiva, cambio de defaults ni adjudicación independiente.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 experiments/reviewed-stages-v1/tests.py
PYTHONDONTWRITEBYTECODE=1 python3 experiments/reviewed-stages-v1/score.py
```

## Siguiente paso prioritario

Precisar y probar la distinción entre falta en pasajes, omisión de respuesta y
contradicción con la fuente. Usar el primer caso como regresión y controles con
contradicciones reales; no convertir todo contradicted en missing. Mantener original
y registrar una nueva condición explícita si se modifica el revisor. Después probar
una transición real a la segunda lectura. Integrar en CLI sólo tras esa evidencia.
