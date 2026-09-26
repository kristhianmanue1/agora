# Evaluación de revisión por detalles — 01

## Cambio evaluado

Contrato optativo `agora/evidence-review/v2`: el modelo juzga fragmentos literales
de cada afirmación y el código calcula la etiqueta global. Una porción omitida
provoca rechazo por cobertura; una porción `insufficient` impide marcar el conjunto
como `supported`. Los detalles contradichos tienen prioridad en la agregación.

La versión v1 se conserva como opción predeterminada y los expedientes anteriores
siguen intactos. La salida sigue siendo consultiva y requiere adjudicación: no
actualiza el candidato ni escribe memoria.

## Protocolo y muestra

Cuatro llamadas iniciales a GLM-5.3-flash, temperatura 0, máximo 8192 tokens de
salida, timeout HTTP 180 s y proceso 200 s. Sin reparaciones ni reintentos. Código,
entradas, expectativas y protocolo congelados antes de ejecutar; expectativas
fuera del prompt. Los resultados del proveedor reportan ese identificador de
modelo, sin verificación independiente de los pesos.

Una regresión conocida de QASPER N2/1024 (seis afirmaciones, incluida A1–C1)
y tres controles sintéticos nuevos, cada uno con afirmación correcta e incorrecta:
población urbana/rural, rechazo/autorización y condición leve/grave. Los controles
son deliberadamente simples; no son documentos reales nuevos ni holdout independiente.
Las fixtures no fueron generadas por GLM; sus citas se validaron localmente.

## Primera tanda: `runs/glm-01`

| Caso | Resultado operativo | Expectativas | Tokens | Segundos |
|---|---|---|---:|---:|
| Regresión real, seis afirmaciones | Rechazado: generación incompleta | No evaluables | 9813 | 121.959 |
| Población | Completo | Correcta respaldada; rural insuficiente | 3187 | 40.454 |
| Negación | Completo | Correcta respaldada; aprobación contradicha | 2080 | 20.487 |
| Condición | Completo | Correcta respaldada; universalización contradicha | 3328 | 40.925 |

**18408 tokens, 223.825 s**, cuatro llamadas con uso conocido. Los tres controles
cumplen las seis etiquetas esperadas. En el denominador completo de la tanda:
tres de cuatro casos cumplen todas sus expectativas; seis de ocho comprobaciones
predefinidas pasan. Las otras dos correspondían a soporte y pertinencia en la
regresión real y no obtuvieron dictamen válido; no se omiten del denominador.

La revisión real terminó con `finish_reason: length`, sin contenido final.
El proveedor reportó 8192 tokens de completado, de ellos 8191 de razonamiento.
Se conserva únicamente esa telemetría y el contenido final recibido, no contenido
de razonamiento. Esto no demuestra que un presupuesto superior la hubiera resuelto.

## Autorrevisión adversarial del incremento

- **No desaparecer el detalle incómodo:** omitir A1–C1 del desglose genera un
  hueco literal y se rechaza. Cambiar, reordenar o parafrasear porciones también.
- **No sobreescribir el juicio global:** el modelo no envía `support` global;
  si lo envía, se rechaza. El código deriva el resultado de todas las etiquetas.
- **No confundir cobertura textual y juicio correcto:** un detalle con todo el
  texto pero etiqueta equivocada puede pasar. Una prueba local conserva este
  contraejemplo y comprueba que el resultado siga requiriendo adjudicación.
- **Costo de descomponer:** la revisión real completa agotó salida. El cambio no
  acredita escalabilidad ni ahorro de coste; incrementa trabajo del revisor.
- **Controles positivos:** las tres afirmaciones correctas permanecieron
  respaldadas. Detectar errores rechazando todo no contaría como éxito.
- **Independencia:** implementación, fixtures y autorrevisión pertenecen al mismo
  productor. Un modelo externo en otra llamada no acredita adjudicación independiente.

## Verificación local

247 pruebas pasaron. Se preserva compatibilidad de uso de v1 y se comprueban
omisiones, referencias inválidas, inversión de orden, paráfrasis, detalles vacíos,
prioridad de contradicción, ausencia de mutación y rechazo de etiquetas globales.

`experiments/evidence-details-v2/audit.py` verifica código congelado frente al
actual, hashes de entradas/salidas, citas contra fuente original, y reproduce
localmente la validación de cada respuesta guardada. No hace nuevas llamadas ni
certifica verdad semántica. Los directorios `inputs/` y `runs/` permanecen fuera
de Git; para reproducción íntegra hay que conservar también los artefactos locales.

## Comprobación aislada: `runs/projected-01`

Después de conservar el fallo de la revisión completa, se autorizó dentro del
incremento una única llamada diagnóstica sobre la afirmación problemática. Se
copiaron **sin cambios su texto y sus dos citas**. Se conservó la pregunta original,
se remapeó índice 2→0 y se marcó la respuesta como proyección parcial diagnóstica;
no se presentó como una respuesta nueva ni como revisión completa del documento.
El artefacto conserva hash y posición de origen. Las expectativas no se enviaron
al revisor. El presupuesto fue el mismo, sin reintento ni reparación.

**Resultado: completo, 3629 tokens, 44.985 s.** El modelo dividió la afirmación en:

1. Entrenar/probar modelos a nivel de oración: `supported`.
2. Misma metodología y características que a nivel documental: `supported`.
3. Cinco clases: `supported`.
4. “(niveles A1-C1).”: `insufficient`, porque ninguna cita identifica esos niveles.

El código calculó `support: insufficient`, `unsupported_details: [3]` y
`recommendation: needs_revision`. La etiqueta global no fue una decisión del
modelo. La auditoría verificó linaje, identidad del texto/citas, referencias contra
la fuente y reproducción local del resultado.

Esto demuestra detección del fallo conocido **en la afirmación aislada, en esta
llamada**. No acredita estabilidad con repeticiones, otros documentos, cobertura de
omisiones ni adjudicación independiente. Tampoco convierte la revisión completa
fallida en un éxito. El cambio de cantidad de afirmaciones impide atribuir el
resultado exclusivamente al nuevo prompt o contrato.

## Balance y decisión

Cinco llamadas en total: cuatro completas y una rechazada por generación
incompleta. **22037 tokens, 268.810 s** de procesos medidos, incluyendo el fallo.
No hubo uso desconocido, reintentos automáticos, reparación de respuestas ni
publicación. Se excluyen de ese tiempo preparación y autorrevisión.

Se mantiene **v2 como opción experimental**. Los controles y la afirmación aislada
justifican continuar, pero el fallo de la revisión de seis afirmaciones impide
presentarla como solución operativa completa para respuestas grandes.

Siguiente incremento recomendado: planificador explícito de revisiones por
una afirmación o lotes pequeños, con vínculo a índices/hash de la respuesta
original, presupuesto total y resumen de cobertura. Si una revisión falta, agota
presupuesto o falla, el resultado global debe permanecer incompleto. La agregación
no podrá convertir ausencia de dictamen en aprobación. Después se necesita una
muestra real nueva y revisión separada antes de promover el modo.
