# T0: lote de calibración para respuesta con evidencia

**Estado:** diseño congelado antes de nuevas llamadas a modelos. Este lote prepara la comparación entre una respuesta directa y el recorrido compuesto propuesto en `docs/plan-consulta-con-modelos-y-evidencia-2026-10-10.md`. No hay resultados de los dos brazos ni decisión de promoción.

## Fuentes y selección

`freeze.json` fija seis preguntas de seis artículos del `test.json` local de QASPER v0.3: cuatro respondibles y dos anotadas como no respondibles. El dataset y cada representación UTF-8 producida por `agora.qasper.render` están fijados por SHA-256. Las preguntas y requisitos de tarea visibles para ambos brazos son idénticos por caso. Los requisitos describen **qué debe cubrirse**, sin entregar la respuesta anotada. La respuesta y los pasajes de referencia se leen del dataset sólo para adjudicar, nunca para construir el prompt.

Antes de congelar, una búsqueda local en `experiments/`, `docs/`, `src/` y `tests/`, excluyendo datasets crudos, no encontró esos seis IDs; se revisaron las anotaciones elegidas para evitar un caso con una sola anotación y otro cuyos anotadores enumeraban métricas discordantes. Esto es reserva relativa a ese inventario y revisión del productor; no prueba ausencia en todos los historiales ni independencia de la referencia. Los casos quedan visibles al publicar este protocolo y **no servirán como evaluación reservada T5**.

Los artículos QASPER son fuentes de investigación sobre NLP, no sustitutos de procedimientos institucionales. El caso CTIM previo sigue como desarrollo y no entra en el denominador de este lote.

## Comparación congelada

1. **Entrada compartida:** fuente textual completa reconstruida por `agora.qasper.render`, pregunta exacta, requisitos de tarea y mismo modelo solicitado `glm-5.3-flash`; fuente y pregunta se verifican contra `freeze.json` antes de cada despacho. La etiqueta QASPER y los criterios de adjudicación quedan fuera del prompt. No se usa recuperación ni PDF.
2. **A, línea base:** una llamada de generación directa con la fuente y lista explícita de requisitos. `baseline-prompt.json` fija el texto exacto y su SHA-256 consta en `freeze.json`. Debe devolver estado de respuesta o abstención, afirmaciones y citas literales. Límite de salida: 4.096 tokens; timeout: 120 segundos; temperatura 0; cero reintentos. La forma se valida por separado de la calidad semántica.
3. **B, recorrido:** la misma fuente, pregunta, requisitos, modelo y límite de generación; luego revisión de respaldo, cobertura y, si se solicita, diagnóstico. Hasta cinco despachos totales: uno de generación, dos ejes de `split_review`, uno de cobertura y uno de diagnóstico. Si una etapa falla o supera presupuesto, se registra y no se sustituye por una conclusión. Esta descripción es el perfil a implementar; no afirma que el recorrido exista hoy.
4. **Orden y costo:** alternar AB/BA por ID de caso; ejecutar cada par en una ventana temporal próxima y registrar tiempos, bytes, llamadas, uso reportado y costo monetario sólo si hay recibo. El techo de llamadas es explícito para ambos; la línea base usa una por diseño. No equiparar presupuesto disponible con costo efectivo.
5. **Seguridad de ejecución:** antes de cada llamada, registrar en un archivo nuevo y durable identidad del caso/brazo/etapa, hashes de entrada/petición, presupuesto y estado `attempted`; el resultado remoto tras timeout o interrupción es `unknown`. No repetir automáticamente. No llamar a un proveedor si la política de envío de esa fuente no está autorizada para el contexto.

## Adjudicación y puertas

- Mantener seis pares en el denominador aunque un brazo produzca salida inválida, abstención o timeout. Puntuar por separado: omisión material, atribución errónea o afirmación sin respaldo, falso faltante, fidelidad de cita, abstención, cobertura de requisitos, trazabilidad y costo. Las anotaciones QASPER son referencias, no verdad por declaración; cotejar discrepancias con pasajes exactos y conservar la diferencia entre anotadores.
- Cegar al adjudicador respecto del brazo y de las revisiones automáticas hasta registrar su juicio de contenido. Si el productor adjudica, declararlo como autorrevisión; una segunda persona o proceso independiente sólo se atribuye si participa y queda verificable.
- El congelado y su verificador permiten iniciar T1–T4; **no** se exige un resultado del brazo B antes de construirlo. Después de T4 y antes de T5, ejecutar los seis pares: exigir recibos interpretables, cero atribuciones materiales equivocadas o citas que no pertenezcan a su fuente, y ninguna omisión de caso del denominador. Un fallo conserva el lote y exige revisar el diseño en otro incremento. Este umbral sólo controla viabilidad en seis casos: no demuestra mejora, fiabilidad general ni utilidad.
- La comparación de utilidad y cualquier decisión de ofrecer la operación pertenecen a T5, con **otros documentos**, criterios de mejora y límites de regresión fijados antes de ver sus respuestas. Una ventaja de trazabilidad no compensa errores materiales fuera del límite fijado.

`verify.py` reconstruye fuentes y verifica hashes, preguntas, anotaciones y sus pasajes, sin modelos ni red. El proveedor efectivo y la facturación quedan `unknown` cuando el recibo no los acredite.

**Comprobación local del congelado:** `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python experiments/evidence-answer-flow-t0-v1/verify.py` devolvió seis casos verificados (4/2). Controles con el hash de la primera fuente alterado y con el prompt sustituido en copias temporales fueron rechazados; no se modificó el congelado. Esto verifica el enlace mecánico de la muestra y el prompt, no sus etiquetas semánticas.
