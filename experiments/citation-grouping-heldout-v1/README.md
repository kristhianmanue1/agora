# Agrupación de citas: dos casos reservados

**Resultado mixto: ambas generaciones válidas y con cobertura; una objeción de
respaldo impide promover todavía la instrucción como comportamiento predeterminado.**

| Caso | Fuente | Citas: usos / bytes | Cobertura de rúbrica | Jev sobre afirmaciones |
|---|---|---|---|---|
| Mecanismo de caché | 1708.07252; 40.528 bytes | 7 / 3.582 | 2 de 2 requisitos | 5 supported |
| Aplicaciones de diálogo | 1912.00342; 37.526 bytes | 6 / 4.503 | 3 de 3 requisitos | 5 supported; C3 insufficient |

## Método y límites

Selección determinista por hash, excluyendo identificadores presentes en el inventario
local de experimentos de hasta 2 MB, sin datasets crudos. Reserva relativa a ese
inventario, no al entrenamiento del proveedor ni a otros sistemas. Casos congelados
antes de generación. Dos fuentes de 30–60 KB, preguntas respondibles y 2–4 fragmentos
de respuesta humana mapeables. Esto sesga la muestra a ese tipo de preguntas; no
cubre preguntas globales, respuestas ausentes o documentos enormes.

Rúbricas extraídas por el productor de la primera anotación QASPER. No se afirma
exhaustividad ni adjudicación independiente. El único arreglo de preparación,
anterior a llamadas, normalizó espacios de los párrafos anotados para mapearlos;
no cambió la selección ni los originales.

Se conservó la instrucción de agrupación exacta del piloto y el límite de 12.000
bytes/12 usos. GLM recibió la fuente completa, no la rúbrica, y produjo respuestas
sin reparación. `review-rubric` evaluó requisitos; Jev `jev-1.13.0` evaluó cada
texto contra sus propias citas, sin ver etiquetas de cobertura. Separación de
proveedor, no adjudicación humana. No hubo brazo con prompt anterior, por lo que
no se atribuye causalmente el resultado a la agrupación.

## Hallazgo localizado

C3 del segundo caso incluye ejemplos “not to swim in an onsen” y “the amount of
today's snowfall”. La cita adjunta es un párrafo general sobre aplicaciones que
remite a los ejemplos por número, pero no contiene esos textos. Los ejemplos sí
están en la fuente, en unidades distintas no citadas:

- `ev_cb2cec6acd09b259de55311e`, bytes [32566, 32643).
- `ev_893fdc5c20fa9511a0264aec`, bytes [33059, 33123).

Jev marcó `insufficient`, con distribución cercana entre insufficient (0,53) y
supported (0,47). La inspección del productor corrobora la brecha concreta de
localizadores; no prueba falsedad de los ejemplos ni conoce la causa interna de
la decisión del revisor. Agrupar no exime de respaldar cada parte de la afirmación.
No se reparó el candidato ni se repitió ninguna llamada.

## Verificación y coste

Seis llamadas: dos generaciones, dos revisiones de rúbrica y dos de fidelidad.
37.408 tokens y 69,744 segundos acumulados de cliente. Coste monetario no informado.
Se leyó toda la fuente; no se mide ahorro frente a lectura selectiva.
`verify.py` reproduce candidatos exactos, hashes, fuentes públicas, offsets,
prompts efectivos y separación de entradas, sin red. Originales completos locales
en carpetas ignoradas; `result.json` conserva respuestas y hashes. Sin cambios de
producto, sin suite general repetida, sin admisión de memoria.

## Estado del plan y continuación

1. **Interfaz utilizable:** CLI existente para preparar, generar, inspeccionar y
   revisar; `review-rubric` ya permite el contraste explícito.
2. **Recorrido comprobado:** generación y revisión funcionaron sin reparación en
   estos dos casos. Fallos anteriores quedan conservados.
3. **Calidad semántica:** parcial. Hay cobertura de la lista, pero una asociación
   afirmación-evidencia requiere atención. No promover defaults todavía.
4. **Leer menos sin perder lo importante:** pendiente de un contraste completo
   que mida omisiones, fidelidad y coste total de lectura selectiva frente a completa.
5. **Memoria integrada:** fuera de este incremento; no se activaron consolidación,
   vigilancia ni admisión automática, ni conexiones nuevas con Skopos/AN-KLA.

Siguiente paso concreto: preparar una reparación candidata que añada los dos
localizadores faltantes, sin cambiar C3, y verificar cobertura de cada subafirmación
y presupuesto. Mantener original y derivado separados. Usar este fallo como control
negativo para la futura opción de agrupación. Después ejecutar la comparación de
lectura selectiva/completa sobre fuentes nuevas; evitar más rondas generales sobre
la rúbrica o declarar un porcentaje de madurez sin criterio.
