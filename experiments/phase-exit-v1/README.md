# Cierre técnico de la fase de iteración de lectura revisada

Alcance fijado: una comparación offline en ocho documentos ya conocidos y una
llamada Jev con cuatro controles temporales. Sin reintentos ni ajuste posterior
para conseguir aprobación. Este cierre no es aceptación del Operador, certificación
de fiabilidad general ni conclusión del motor de memoria completo.

## Comparación y paso a código

El contraste congelado conservó el baseline histórico exact-paragraphs y agregó
rangos del selector headings-lists existente hasta 20.000 bytes. Mejoró referencias
en tres casos sin perder rangos; dos casos siguieron sin todas sus referencias.
No cumplió el criterio de promoción a predeterminado. result.json conserva todo.

Por instrucción del Operador se incorporó una opción productiva experimental:
`retrieve-structured` y contrato `agora/subquestions-plan/v3-structured-experimental`.
La estructura QASPER debe reproducir exactamente la fuente. Se rechazan anotaciones
qas en la estructura, se conserva la selección léxica del producto, se añaden rangos
dentro del presupuesto y `generate-plan` reconstruye el plan antes de invocar al
proveedor. Contratos v1/v2 y defaults permanecen. No depende de scripts de experiments.

El baseline del producto no es idéntico al comparador histórico: product-result.json
los distingue. Contra el baseline del producto, la opción mejora rangos anotados en
cuatro de ocho casos, conserva los demás y todos los rangos previos; en seis casos
recupera todos los párrafos anotados. Son casos conocidos y métricas de rangos, no
una tasa de exactitud de respuestas. La ausencia de un párrafo anotado tampoco
excluye evidencia equivalente. No se ejecutó nueva generación live con esta opción;
el consumidor se verificó mediante respuesta conservada en la CLI y pruebas.

## Alcance temporal: límite conservado

Jev devolvió insufficient en los cuatro controles: coincide con dos etiquetas
previstas, falla el positivo y la contradicción según etiquetas del productor.
Una llamada, 1.250 tokens reportados. No hay adjudicación independiente ni evidencia
para cambiar prompts/defaults o automatizar decisiones temporales. Este fallo se
conserva y no abre automáticamente otra iteración.

## Criterio de salida y horizonte

La fase termina técnicamente con: capacidad experimental invocable y conectada al
generador, pruebas de reproducción/conservación/presupuesto, resultados positivos y
negativos preservados, guía de uso y límites publicados. No exige convertir todos
los resultados en éxitos. La aceptación o una fase nueva corresponden al Operador.

Recomendación al cerrar: usar la CLI en piloto supervisado. Mantener sin promoción
la selección predeterminada y la adjudicación temporal. No abrir más rondas de ajuste
de este benchmark salvo defecto reproducible o una nueva fase explícita con objetivo,
presupuesto y criterio de salida. El proyecto completo aún requiere priorizar catálogo,
consolidación, admisión e integración contractual; no tiene fecha de finalización
acordada y no se deduce de estas pruebas.

## Reproducción

`run.py` reproduce comparación congelada. `product_check.py` verifica código actual
y controles temporales guardados; requiere dataset/artefactos locales anteriores.
Los hashes en los resultados identifican implementación. `tests/test_structured_plan.py`
no requiere dataset ni red y recorre CLI → generación replay, además de rechazos.
