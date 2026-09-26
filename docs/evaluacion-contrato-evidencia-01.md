# Tres bloques del plan refinado: implementación y evaluación

2026-09-23. Encargo completado dentro del alcance experimental; no promoción a
producción, admisión en memoria ni publicación. Contrato y uso:
[afirmaciones y evidencia](contrato-afirmaciones-evidencia.md).

## Bloque 1 — Contrato y diagnósticos

Se implementó `EvidencePolicy` con límites efectivos comunicados al modelo y
conservados en el resultado. El contrato nuevo separa forma, literalidad,
cantidad, duplicados y tamaño UTF-8; puede reportar varios errores simultáneos.
No se elimina evidencia para aprobar una salida. La ruta legacy conserva sus
reglas y ahora comunica el máximo de 12 desde la misma constante usada por su
validador. Los rechazos viejos siguen siendo rechazos de aquella versión.

## Bloque 2 — Afirmaciones, respaldo y lagunas

Nueva CLI optativa `agora.evidence_cli`, contrato `agora/claim-evidence-query/v1`.
Cada aspecto solicitado contiene afirmaciones con citas propias y lagunas
propuestas. Estados `answered`, `partial`, `not_in_passages`, consistentes con
el contenido. El sistema conserva revisión pendiente por afirmación y aspecto.
Nunca convierte el estado propuesto por el modelo en respaldo o cobertura
verificada. La nueva estructura facilita inspección; no implementa un juez NLI.

## Bloque 3 — Versión fija y casos nuevos

Campaña `experiments/evidence-contract-v1/runs/glm-01`: seis llamadas, protocolo,
fuentes, criterios y código congelados antes de ejecutar; sin ajustes durante
la campaña, sin reparación ni reintentos. Modelo solicitado y reportado GLM
5.3 Flash, temperatura 0, salida máxima 8192 tokens, socket/proceso 180/200 s.
JSON mode omitido. Se usó el mismo contexto seleccionado de 6965 bytes para G1.

| Caso | Consumidor | Resultado | Tokens | Segundos |
|---|---|---|---:|---:|
| G1 conocido | legacy, límite comunicado | Rechazo por cita no literal | 5366 | 53.554 |
| G1 conocido, seis aspectos | contrato nuevo | Candidato aceptado | 10015 | 104.895 |
| N1, urbano frente a rural | contrato nuevo | Parcial válido | 957 | 9.405 |
| N2, capacidades contradictorias | contrato nuevo | Parcial válido | 903 | 9.830 |
| N3, rechazo de compra y pago desconocido | contrato nuevo | Parcial válido | 746 | 7.425 |
| N4, versiones y prueba cancelada | contrato nuevo | Rechazo por JSON inválido | 1532 | 18.731 |

Total: **19519 tokens**, 203.840 segundos acumulados de procesos. No hubo timeout;
ningún consumo es desconocido en esta campaña. Preparación y autorrevisión no
están incluidas en ese tiempo. No se midió coste monetario. Se cuentan ambos
rechazos. El contrato nuevo entregó candidatos en 4/5 casos, incluidos 3/4 casos
nuevos. No confundir `candidate_partial` coherente con información ausente con
un fallo: en N1/N2/N3 preserva hechos conocidos y deja sin resolver lo desconocido.

### Revisión del contenido

- G1 nuevo conserva los seis criterios: extracción/alineación de nombres,
  plantillas y Maximum Entropy, selección humana frente a automática, resultados
  y limitación de automatización, recursos manuales comunes y futuro multilingüe.
  Tiene 25 citas distribuidas entre seis aspectos, dentro de los presupuestos;
  no se le aplicó retrospectivamente el máximo global de otra interfaz. La frase
  sobre enfoque en inglés es una inferencia explícita desde el objetivo futuro,
  no una afirmación textual independiente de cobertura lingüística.
- N1 conserva el 4% en escuelas urbanas sin transferirlo a rurales; declara la
  ausencia de un resultado rural numérico.
- N2 conserva 24 y 31 con sus fuentes, ambas vigentes, y no inventa precedencia.
- N3 conserva la negativa explícita de compra y no convierte a Nora, coordinadora,
  en autorizadora de pago.
- N4 fue rechazado por un corchete faltante en `missing` antes del aspecto rain.
  No se reconstruye para puntuación ni se cuenta como respuesta semántica válida.
- G1 legacy contiene 12 citas, pero una cambia INLINEFORM1 por INLINEFORM0.
  Se confirma que comunicar el máximo no garantiza literalidad.

Las 30 citas de los cuatro candidatos aceptados fueron verificadas contra bytes
de las fuentes. La revisión semántica fue del productor, no independiente. N1–N4
son casos sintéticos nuevos fijados antes de las llamadas, pero elaborados por
quien implementó el contrato: no son holdout independiente ni QASPER oficial.

## Verificación local

**202 pruebas pasan** (183 anteriores y 19 nuevas). Las nuevas cubren frontera
12/13, política configurable, bytes UTF-8 por aspecto y totales, anclajes con
offsets, duplicados, errores simultáneos, partes omitidas, consistencia de estados,
JSON mal formado, integración CLI y ausencia de llamadas si falla el presupuesto.
Una regresión demuestra que una afirmación falsa con una cita literal puede
pasar estructura y conserva el estado semántico no verificado.

`audit.py` verificó los archivos congelados, hashes de los seis resultados,
código actual contra el ejecutado y anclajes. El producto permaneció sin cambios
durante la campaña. Se añadieron pruebas posteriormente, sin modificar el código
evaluado. `git diff --check` pasó.

## Autorrevisión adversarial final

- No atribuir el resultado favorable de G1 sólo al límite de citas: también
  cambian estructura, prompt y división en seis aspectos. Es prueba de viabilidad
  de una versión, no comparación causal de una variable.
- El control nuevo costó más tokens que el intento legacy rechazado; no hay
  ahorro demostrado a igual calidad ni optimización del número de citas.
- Los presupuestos iniciales no están calibrados empíricamente como óptimos.
  Repetir citas entre afirmaciones se permite con cargo al presupuesto; duplicar
  dentro de una afirmación se diagnostica.
- Las lagunas que el modelo no declara todavía pueden quedar ocultas. Revisión
  pendiente no equivale a detector automático de omisiones.
- La recuperación automática sigue pendiente de mejora: G1 recibió evidencia
  seleccionada por el productor. No se ensayó Skopos ni AN-KLA como recuperadores.
- La transcripción literal sigue a cargo del modelo y puede fallar; un contrato
  posterior con referencias por ID debe evaluarse por separado, sin asumir que
  un ID válido acredita respaldo semántico.

## Decisión y continuación

Conservar el contrato nuevo como interfaz experimental optativa, sin sustituir
los consumidores antiguos ni promover fiabilidad general. Los tres bloques están
terminados; N4 es un resultado negativo de la evaluación, no trabajo oculto.

Próximo incremento recomendado: evaluar referencias a unidades de evidencia por
ID para evitar que el modelo reescriba las citas, y una estrategia explícita para
salidas JSON inválidas (rechazo visible; sin reparación silenciosa). Después,
una muestra nueva sobre fuentes reales con adjudicación separada, antes de
ampliar automatización o integración. No repetir N4 hasta obtener un éxito y
presentarlo como si fuera su único intento.
