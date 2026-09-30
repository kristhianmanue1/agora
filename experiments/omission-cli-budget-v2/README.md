# Diagnóstico con 4.096 tokens: truncamiento resuelto, validación aún parcial

Dos nuevas llamadas sobre los mismos candidatos, fuentes, preguntas y revisiones del [lote anterior](../omission-cli-v1/README.md). Presupuesto fijado en 4.096 tokens de salida, timeout 90 s, sin reintentos. Prompts system/user exactamente iguales a los anteriores, cotejados por audit.py. La CLI incorpora --max-output-tokens con opciones 2048/4096; default 2048 preservado. No cambió el contrato de respuesta.

## Resultados

| Candidato | Resultado local | Salida reportada | Consumo total |
|---|---|---:|---:|
| Equal, incompleto | Diagnóstico válido: cuatro propuestas | 2.450 tokens, stop | 13.208 tokens |
| Shared, control esperado suficiente | Rechazado: JSONDecodeError | 2.849 tokens, stop | 13.738 tokens |

**26.946 tokens** conocidos en total; modelo reportado glm-5.3-flash. No coste monetario verificado ni medición de eficiencia general. Ningún truncamiento en esta condición. No se repitieron las llamadas dentro del lote ni se sobrescribieron intentos previos.

Equal vuelve a localizar las dos limitaciones conocidas (BLEU y composicionalidad de embeddings), junto con las dos propuestas adicionales de la ronda anterior. Los offsets apuntan literalmente al archivo fijado por hash; cuatro propuestas no se cuentan como cuatro aciertos.

Shared devuelve un objeto JSON seguido de un carácter backtick sobrante. El parser estricto lo rechaza; finish_reason=stop no garantiza formato válido. Se conserva el original y no se recorta, repara ni admite automáticamente. La ausencia de una lista validada no equivale a no_omission_found.

## Lectura adversarial del control

La inspección humana del texto bruto permite ver dos propuestas, pero no convierte la respuesta rechazada en resultado validado:

1. Múltiples respuestas correctas para una misma entrada dificultan la evaluación cuantitativa. Está en el fragmento [14385,15677) y en una anotación QASPER alternativa. La respuesta shared no lo dice de forma explícita, aunque sí aborda diversidad para BLEU. Puede ser una omisión adicional o una explicación parcialmente solapada: requiere adjudicar materialidad.
2. No existe un método perfecto y se usan métricas prestadas de traducción. Está en [4504,4899), pero puede ser contexto redundante respecto de debilidad de correlación y demás limitaciones ya incluidas.

La expectativa previa “ninguna omisión material” queda **cuestionada**, no corregida retrospectivamente. El fallo de formato y la incertidumbre de esa expectativa son problemas distintos. La fuente respalda que los autores dicen esas frases; no las convierte en hechos universales sobre toda evaluación de diálogo.

## Conclusión

La nueva condición elimina el truncamiento observado y conserva las dos omisiones conocidas, pero no completa el control suficiente. No hay fundamento para aumentar otra vez tokens ni promover el diagnóstico. El cierre de validación semántica sigue parcial.

Siguiente paso recomendado: conservar el rechazo original; si se evalúa una reparación de formato, producir un derivado explícito ligado a su hash, sin reenvío al proveedor ni aceptación automática. Después adjudicar la materialidad de las dos propuestas contra pregunta, candidato y referencias, manteniendo la expectativa original en el registro. Crear también un control verdaderamente suficiente, construido con cobertura explícita de todas las obligaciones de la pregunta. No se realizó esa reparación ni se cambió el control en este lote.

## Verificación

483 pruebas aprobadas: se añaden controles del presupuesto optativo, conservación del default y rechazo de valores no permitidos antes de reservar salida. audit.py verifica igualdad de ambos prompts con el lote previo, hashes de entradas y revisión, y offsets de todas las propuestas válidas. Evidencia y originales preservados; no escritura en AN-KLA, reparación automática ni modificación de candidatos. No hubo revisión independiente.
