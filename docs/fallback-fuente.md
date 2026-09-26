# Recuperación adicional acotada — 2026-09-22

Incremento local autorizado después de glm-02. Activa una alternativa opcional
cuando el recuperador léxico encuentra cero coincidencias: entregar fuente completa
si cabe en el presupuesto declarado. No constituye búsqueda semántica ni memoria
jerárquica, no conecta Skopos/AN-KLA y no usa TypeSafe.

## Uso y alcance

La CLI `agora.passage_cli --mode retrieve` admite:

```bash
--content-budget 256 --fallback-source-budget 8192 --prompt-budget 65536
```

Sin `--fallback-source-budget`, comportamiento y esquema v0.1 anteriores.
Con el flag: `agora/passage-query/v0.2`, con política, límite y decisión en
`retrieval.fallback`. Un consumidor de v0.1 no debe asumir compatibilidad.
Sólo se admite con retrieve. Presupuesto entre1y4194304bytes, adicional al límite
de prompt; no son tokens. Los límites de lectura/inventario previos siguen vigentes.

Antes de usar esta opción con datos reales, el alcance debe permitir transmitir
la fuente completa, no sólo fragmentos. Declarar presupuesto no concede permiso.
El ensayo de esta entrega usó exclusivamente fuentes sintéticas.

- Cero coincidencias y fuente dentro del presupuesto: `used`, fuente completa
  sin truncamiento, máximo una llamada al modelo.
- Fuente demasiado grande: `fallback_budget_exhausted`, cero llamadas.
- Hay coincidencias que no caben en la selección: `not_applicable_matching_candidates`;
  conserva `retrieval_budget_exhausted`, no elude el límite.
- Hay pasajes seleccionados: `not_needed` significa sólo que la política no se
  activó; no afirma suficiencia. Puede haber evidencia insuficiente o irrelevante.

No se reintenta tras abstención, error HTTP o JSON inválido. No se invoca otro
modelo para reformular la pregunta. La cobertura completa no certifica fidelidad:
revisión semántica y admisión permanecen separadas. La versión nueva no corrige
retrospectivamente respuestas de experimentos anteriores.

## Pruebas y evaluación

107pruebas locales OK (99previas+8). Verifican opt-in, rutas anteriores, fuente
completa exacta, límite de fallback y prompt, coincidencias sobredimensionadas,
revisión cambiada y opciones incompatibles.

`experiments/fallback-v1/`: cinco fuentes/preguntas/criterios nuevos, conocidos
por el productor. Sin holdout. Código/criterios/protocolo congelados antes de GLM;
no se cambiaron tras observar resultados. Modelo solicitado/reportado:
glm-5.3-flash; máximo2048tokens; socket90s, proceso110s; sin reintentos.

| Caso | Léxico | Con alternativa |
|---|---|---|
| N1 vocabulario diferente | Sin candidatos | Responde73créditos con cita válida |
| N2 coincidencia irrelevante | No encuentra respuesta en selección | Igual; no activa fallback |
| N3 duración ausente | Sin candidatos | Abstención después de leer fuente completa |
| N4 fuente11323bytes, límite8192 | Sin candidatos | Presupuesto agotado; no transmite |
| N5 coincidencia útil | Responde27días | Igual; no activa fallback |

N2contiene la respuesta Mara en otra parte: la pregunta sigue incumplida en ambas
rutas. N4demuestra respeto del presupuesto, no respuesta a la pregunta. N3permite
abstención sobre material completo; no certificación automática de ausencia global.
No convertir los estados operativos correctos en cinco respuestas correctas.

10rutas,6solicitudes reales. El fallback trata el vacío de coincidencias; la
insuficiencia de evidencia cuando hay coincidencias sigue abierta. Los resultados
no demuestran robustez general ni mejor rendimiento por el mero aumento de lectura.
Credencial del laboratorio inyectada sólo al proceso; ninguna clave guardada.
Evidencia local ignorada: experiments/fallback-v1/runs/glm-01/ con freeze.json,
resultados, execution.json y metrics.json. No incluye datos médicos ni privados.

Revisión separada review_large_source_plan antes del ensayo: PROCEED acotado;
se corrigió source_id para distinguir los cinco documentos. Revisión semántica
final se conserva separada de resultados. No es auditoría externa.

## Continuación propuesta

Mantener esta alternativa opcional. El siguiente problema es detectar que los
pasajes recuperados no bastan, incluso cuando hay coincidencias. Separar evaluación
de suficiencia y decisión de ampliar con presupuesto; probar primero con casos
nuevos en español. No hacer de un juicio de modelo autoridad automática.
La investigación paralela sobre TypeSafe informa esa decisión, sin instalar SDK
ni activar un servicio nuevo en este incremento.

Recursos observados: léxico2solicitudes/1057tokens/8,480s; alternativa4solicitudes/5336tokens/17,116s. Más llamadas aportaron cobertura, no ahorro. Uso reportado por proveedor, sin estimación monetaria.
