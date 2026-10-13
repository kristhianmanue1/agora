# Corrida acotada nueva: página física 21 CTIM RS1

**Fecha local:** 2026-10-10. **Alcance autorizado:** sólo el derivado UTF-8 de
582 bytes de la página 21, actividades 25–27; no se envió el PDF completo ni
comentarios del borrador. Esta es una corrida nueva de `answer-v2`, distinta de
`live-answer-v1`. Se usaron la pregunta, requisitos y `budgets.json` del
preflight, `glm-5.3-flash` solicitado y `--skip-omissions`. La `ZAI_API_KEY`
heredada se excluyó del proceso; Llavero suministró el perfil `zai` sin revelar
la credencial. No hubo reintentos automáticos.

## Preflight y transporte

- Fuente: 582 bytes, SHA-256
  `ee7ec9b09e6c171dd4e37ed5c1d155366093b2098f38d060a6170f0eefe200c4`.
- Intercambio: SHA-256
  `2e2faaac027b9bdf2e2de0fa8ce67b39eea497088d6157947dac3379800bf088`;
  13 segmentos; `sha256_verified` contra el PDF local, SHA-256
  `1f8ad5e506b21cbf6b568b68790d2a757ba870524a6ba341f2dff3637d2494f2`.
- Preflight offline: una sola unidad documental cuyo texto era exactamente los
  582 bytes; prompt de generación de 3285 bytes. SHA-256 de petición lógica
  `d901dbb372f40c70e3d781da44e85e4d3d37b5aa208d0d5cdcff556d49aa9f9a`,
  igual al intento durable. El SHA-256 del payload enviado, reconstruido del
  prompt y parámetros, coincide con el recibo:
  `140c7eccae6181c2df372e473beded917578c786dc84c3b76bf296d44eb7c25f`.

## Resultado y costo observable

`live-answer-v2/result.json` tiene SHA-256
`a5a53ce150b6e60ff38384c4e81b04a8e80171d8f1e30ae37c58b477400e122a`,
`status=candidate_reviewed`, cuatro intentos durables y cuatro respuestas
guardadas, todos con `finish_reason=stop`; no hubo archivo de fallo ni etapa de
omisiones. Generación, respaldo, pertinencia y cobertura terminaron. El
identificador de modelo reportado por los recibos fue `glm-5.3-flash`; el
modelo efectivo sigue sin comprobación independiente.

| Etapa | Prompt tokens | Completion tokens | Razonamiento incluido | Total |
| --- | ---: | ---: | ---: | ---: |
| Generación | 865 | 787 | 505 | 1652 |
| Respaldo | 1213 | 763 | 448 | 1976 |
| Pertinencia | 936 | 691 | 369 | 1627 |
| Cobertura | 1280 | 309 | 297 | 1589 |
| **Total reportado** | **4294** | **2550** | **1619** | **6844** |

Hay 128 tokens de prompt reportados como cacheados, incluidos en el total de
prompt. Los recibos no indican importe facturado, por lo que el costo monetario
es desconocido.

El candidato tiene tres afirmaciones y ningún faltante declarado. GLM marcó
las tres como `supported` y `relevant`, y cobertura `complete`; son consejos
del mismo proveedor. El cotejo visual local de la página física 21 encontró:

1. A25: CTIM recibe por oficio de CPSI, OOAD o UMAE la solicitud de revisión
   del anteproyecto conceptual; coincide con la fila 25.
2. A26: CTIM identifica modificaciones e informa a CPSI, OOAD o UMAE hasta
   acordar el anteproyecto, con referencia al Anexo 6; coincide con la fila 26.
3. A27: CTIM firma y envía el anteproyecto con el oficio nombrado a CPSI y
   OOAD o UMAE; coincide con la fila 27.

`package-live-v2/package.json`, SHA-256
`aa651cbb70c21602e9216671d0fe89cdbd7cc85707a9b12fab7e43ba0243f521`,
se exportó y reconstruyó offline contra el mismo derivado, intercambio y PDF.
Sus citas aún abarcan la unidad completa de 582 bytes por afirmación; la
exportación no da respaldo fino. No se verificó la existencia del Anexo 6, la
autoridad institucional, la vigencia del borrador ni la completitud de otras
páginas. El paquete conserva `requires_review` y no admite memoria.
