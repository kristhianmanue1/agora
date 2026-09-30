# Diagnóstico CLI: evidencia localizable, validación parcial

Par conocido QASPER 1803.08419, mismos candidatos y revisiones conservadas de coverage-cli-long-v1. Dos llamadas GLM, sin regeneración ni reintentos. Expectativa congelada antes de enviar: localizar limitaciones de BLEU/embeddings en equal; no proponer faltantes materiales en shared. El modelo no recibió esas expectativas ni las etiquetas anteriores.

## Resultado

- **Equal:** cuatro propuestas. Las dos primeras coinciden con las omisiones conocidas: diversidad de respuestas para BLEU y composicionalidad insuficiente de promedios de embeddings. Ambas citan el párrafo bytes [39327,39909).
- **Adicional 1:** múltiples respuestas correctas dificultan evaluación cuantitativa, bytes [14385,15677). Esta idea figura en una anotación QASPER alternativa; queda como propuesta con atribución al texto, no ley universal sobre evaluación.
- **Adicional 2:** ausencia de método perfecto y préstamo de métricas de traducción, bytes [4504,4899). Está en la fuente, pero su necesidad adicional frente a las afirmaciones existentes queda pendiente; no se cuenta como verdadero positivo por contener cita válida.
- **Shared, control suficiente:** finish_reason=length; 2.048 tokens de salida, 2.043 reportados como reasoning. Respuesta rechazada, sin diagnóstico semántico válido. No equivale a no_omission_found ni prueba de ausencia de falsos positivos. No se repitió.

Consumo total conocido: **25.437 tokens** (12.500 y 12.937). Modelo reportado glm-5.3-flash. No coste monetario verificado. Los hashes de fuente, candidatos y revisiones permanecen idénticos. audit.py comprueba todos los offsets y recompone result.json.

## Verificación y autorrevisión

Diez pruebas específicas verifican localización UTF-8, IDs inventados/duplicados, cardinalidad/estado, truncamiento, vinculación al informe original, replay sin mutación, timeout sin retry, reserva y discrepancias. Suite final: 480 pruebas aprobadas. Ninguna de ellas sustituye validación semántica.

Después de la prueba real se mejoró únicamente el diagnóstico local de error: la CLI final muestra generation_incomplete en vez del genérico ValueError. Los registros reales permanecen intactos; no se reejecutó por ese cambio de presentación. La reproducción y regresión final comprueban el cambio offline.

Autorrevisión: citas verificables no prueban omisión; cuatro propuestas no son cuatro aciertos; controles de desarrollo y productor común no establecen independencia; el control positivo fallido impide declarar completa la validación semántica. Candidato original y revisión anterior no se sustituyen.

## Pendiente concreto

Probar el control suficiente bajo una nueva condición explícita con presupuesto de salida adecuado al diagnóstico, conservando el intento truncado. Antes de más casos, fijar el presupuesto y comprobar tanto control suficiente como incompleto, sin editar expectativas para acomodar resultados. No activar reparación automática. La limitación observada es generación incompleta con este presupuesto, no un timeout ni fallo de red.

La implementación y publicación experimental están completas; el contraste semántico de ambos lados del par está parcial. Uso: [diagnose-omissions](../../docs/diagnostico-omisiones-cli.md). run.py rechaza repetir el lote; audit.py no usa API. Entradas y journals completos permanecen ignorados.
