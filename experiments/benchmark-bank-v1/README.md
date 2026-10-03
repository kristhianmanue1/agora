# Banco comparativo ARIA / MemOS: base verificable

## Qué queda operativo

```bash
python3 scripts/verify_benchmark_evidence.py
```

El verificador comprueba hashes de los artefactos seleccionados, identidad del
conjunto de casos y contabilidad de tokens del bloque largo. Rechaza recibos
repetidos, subtotales inconsistentes y exclusión de casos con etiqueta. Incluye
los dos rechazos de Ágora en los cuatro casos y en el consumo. No llama modelos,
no accede a credenciales y no certifica que una respuesta sea verdadera.

El manifiesto también incluye las evidencias históricas de AN-KLA (transiciones)
y Skopos (captura), que no se reejecutaron en este bloque.

El manifiesto congela el conjunto local de evidencia actual; no está firmado ni
protege frente a quien modifica simultáneamente datos y manifiesto. No garantiza
que todos los costes posibles estén registrados. Congelar evidencia histórica no
convierte esos casos vistos en nuevos documentos reservados.

## Integración real de Ágora

`generate-plan --scope-guard` incorpora el control al recorrido de la CLI de
pendientes, en modos de citas literal e ids. Conserva el esquema de citas por ID
y añade scope_contract agora/reading-scope/v1. Marca candidate_requires_expansion
si una respuesta candidata sólo cubre fragmentos. El caso vacío conserva
no_supplied_evidence y también exige ampliar. No cambia los contratos sin el flag.

La salida de CLI muestra requires_expansion, reading_budget_bytes y
expansion_policy=explicit_review_and_budget_required. El presupuesto procede del
plan reconstruido y verificado; no se permite aumentarlo silenciosamente. La revisión
y ampliación usan los comandos existentes reading-route, coverage-plan y
generate-recovery con sus propios artefactos/presupuestos; no se saltan sus validaciones.
El flag no crea revisiones ni conecta esos comandos automáticamente.

Dos invocaciones CLI reales con respuestas conservadas comprobaron los modos literal
e ids, presupuesto de 100 bytes, estado pendiente y cero HTTP. Se verificaron también
planes modificados, fuentes cambiadas y recuperación vacía con pruebas locales.
No se hicieron nuevas llamadas LLM en este bloque. El estado es una condición para
consumidores, no una garantía de que un consumidor externo lo respete.

## Herramientas y validación MemOS

Con autorización explícita del Operador se instaló un entorno temporal
/tmp/aria-bench-tools: Poetry 2.5.1, Ruff 0.11.13, pytest 8.4.2 y plugins declarados.
validation-tools.txt conserva todas las versiones resueltas. No se modificaron
pyproject.toml, uv.lock ni el entorno del servicio. El entorno temporal puede
reconstruirse desde esas versiones; no se afirma reproducción multiplataforma.

Se copió el checkout actual a /tmp/memos-validation-worktree sin secretos/stores y
se ejecutó make format mediante Poetry: OK, dos avisos corregidos, tres archivos
reformateados. Se transfirió sólo el formato de nuestros tres archivos al checkout.
Las cuatro piezas candidatas coinciden byte a byte con las probadas; hashes en
memos-validation.json. Configuración previa y trabajo ajeno preservados.

Pytest sobre tests/mem_feedback y los tests seleccionados del adaptador Neo4j:
55 passed, 3 skipped. Las tres omisiones son integración Neo4j no habilitada.
Se desactivó autoload de plugins; quedó un warning de configuración asyncio_mode,
sin tests async ejecutados en este conjunto. Los tests no equivalen a toda la suite
MemOS ni a revisión independiente. Las pruebas HTTP de actualización y filtrado
se conservan en los expedientes previos. Ningún servicio fue reiniciado en este bloque.

Parches MemOS continúan locales, sin commit/push ni promoción. Los gates disponibles
ya se ejecutaron, pero habilitar esas pruebas de integración exige primero comprobar
que su fixture no toca una base compartida. No se habilitaron a ciegas.

## Protocolo para el siguiente bloque

1. Reservar documentos no usados y fijar preguntas/configuración antes de ejecutar.
2. Comparar captura, recuperación y respuesta como funciones separadas. Skopos no
   debe recibir una nota de generación si sólo se prueba su parser; AN-KLA no debe
   medirse como compresor si se prueban transiciones explícitas.
3. Separar versión upstream, parches locales, configuración y código realmente cargado.
4. Registrar ingestión una vez y consultas posteriores, fallos, recibos, tokens y
   tiempos; no sustituir coste no observado por cero. No reajustar la campaña tras
   ver las respuestas. Cualquier reparación abre una campaña de regresión distinta.
5. Usar anotaciones externas, conservar discrepancias y realizar adjudicación
   independiente antes de afirmar una tasa general de fidelidad o elegir sustituto.

Esto es una base de control ejecutable para la evidencia acumulada, no una batería
universal terminada ni un ranking de las herramientas. El siguiente bloque debe
incorporar independencia de evaluación y más documentos, con presupuesto fijado.

Validación final Ágora: 533 tests, OK. El verificador del banco pasó sobre los
artefactos incluidos. Sin revisión independiente ni afirmación de madurez general.

## Continuación: integración Neo4j ejecutada

Se repitió el conjunto seleccionado con Neo4j 5.26.6 desechable: **58 passed,
0 skipped**, con un aviso de cierre del driver. Se habilitaron las tres pruebas
antes omitidas. El contenedor sólo expuso Bolt en localhost:17687, usó datos
temporales y fue eliminado con salida 0. No se reinició el servicio habitual.
Los cuatro archivos candidatos coinciden con los hashes de la validación anterior.
Evidencia y ejecutor: `neo4j-integration/`. Esto prueba el adaptador Neo4j nativo,
no toda la ruta Community + Qdrant ni todo MemOS. Cero llamadas a modelos.

La campaña `../memos-long-reserved-v2/` se ejecutó después de congelarse. Su
resultado contiene cuatro preguntas, ingestión vacía en MemOS y omisiones en ambos.
Los nuevos hashes están incorporados; la contabilidad expected_accounting del
verificador sigue correspondiendo al bloque histórico v1. V2 conserva recibos y
subtotales separados: no deben sumarse como si fueran el mismo conjunto.
