# Resultado: transferencia a cuatro tipos de omisión

**Criterio principal no cumplido.** Jev coincide con 11/12 etiquetas de suficiencia y 24/24 etiquetas de unidades. Cuatro omisiones detectadas y cuatro controles descriptivos aceptados; un falso rechazo frente al gold del productor en quantity-full. Doce llamadas, sin errores ni reintentos. Modelo reportado jev-1.13.0.

## Hallazgo conservado

quantity-full incluye literalmente todo el contenido del fixture: módulo de importación por lotes y máximo de 25 archivos. La tarea pide resumir cómo preparar y transferir los archivos mediante ese módulo. El gold congelado es sufficient. Jev devuelve insufficient pero marca e1 y e2 covered. No identifica ninguna unidad missing_required.

La salida es inconsistente con la rúbrica del piloto: insufficient requiere información necesaria disponible en evidencia que el resumen omita. No se observa tal omisión aquí. Es posible que la amplitud de «cómo preparar y transferir» induzca a pedir pasos ausentes de la fuente; eso es una hipótesis, no una explicación producida por Jev. La respuesta tipada no permite conocer su motivo. No se cambia el gold ni se reintenta para obtener un pase.

## Verificación y límites

Inputs y gold conservan hashes congelados. Requests comprobados contra task/evidence/summary/units; gold no enviado. Unidades cotejadas con subcadenas exactas y vinculadas por hash/offsets de caracteres locales. Resultados saneados: [result.json](result.json).

Consumo: 10599 tokens de entrada y 1760 de salida; suma de latencias 3.846 s. No representa coste monetario ni tiempo total de preparación.

Casos sintéticos de desarrollo redactados y etiquetados por el productor, sin adjudicación independiente. Cuatro familias dependientes, textos breves, dos unidades explícitas y una corrida. No son documentos reales, corpus reservado ni una tasa de error generalizable. El criterio falló aunque la mayoría coincida. Se conserva modelo, prompt y etiquetas; no se promociona ni integra automáticamente.

## Decisión técnica recomendada

Conservar un estado de revisión requerida para respuestas incoherentes; no convertirlas silenciosamente en suficiente ni repararlas por mayoría. Antes de implementar ese control en producto, delimitar la diferencia entre **fuente insuficiente para la tarea** y **resumen que omite información presente**. Este lote aporta un contraejemplo que merece comparación pareada y adjudicación, no más casos fáciles del mismo patrón.

## Etapa y dirección

Ágora está validando componentes del revisor con evidencia experimental. El generador y la trazabilidad existen como prototipo; el eje de suficiencia del resumen todavía es experimental y separado de la CLI de producto. El objetivo sigue siendo leer menos sin perder información importante ni perder el acceso a la fuente.

Ruta restante: (1) resolver semántica y tratamiento de inconsistencias; (2) contraste con otro revisor y etiquetas independientes; (3) documentos/casos reservados más largos, requisitos dispersos y medición de ahorro total, omisiones y coste; (4) integrar el control explícito en la CLI si la evidencia lo sostiene. La integración Skopos/AN-KLA permanece por contratos opcionales; no soluciona por sí sola estos errores de revisión.
