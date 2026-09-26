# Consulta explícita sobre evidencia de un recorrido

## Resultado

Existe una CLI `python3 -m agora.traversal_cli` y una API
`agora.traversal_query.query_traversal` que consumen un recorrido conservado.
Devuelven `agora/traversal-query/v0.1`: evidencia, rangos pendientes, estado de
recorrido y respuesta candidata con citas, sin admitir memoria ni publicar.

Antes de llamar al modelo se comprueban hash del registro, revisión e identidad
de fuente y coincidencia exacta de pregunta. Se reconstruyen unidades, ventanas,
extracciones y evidencia utilizando los receipts guardados, sin volver a consultar
al proveedor. Una modificación aislada de citas, estado completo o pendientes
no supera esta comprobación. No equivale a autenticar receipts: son datos aportados
por el llamante, y un registro coherente fabricado no acredita una ejecución real.
Cambios incompatibles del algoritmo requieren migración explícita del registro.

Un recorrido parcial devuelve `blocked_partial_traversal`, con pendientes y evidencia,
sin generación. Sin citas retenidas devuelve `no_retained_evidence`, que no demuestra
ausencia en la fuente. Con recorrido completo permite una llamada de respuesta, bajo
presupuesto de prompt. Conserva `global_completeness: not_established`,
`semantic_support: not_verified` y `review_status: unreviewed`: recorrer todas las
unidades no demuestra que se haya preservado todo lo relevante.

## Uso

Desde la raíz de Ágora, con la credencial existente disponible sólo en entorno:

```bash
PYTHONPATH=src python3 -m agora.traversal_cli   --source /ruta/fuente.txt --source-id identidad   --sha256 SHA256_DE_FUENTE   --traversal /ruta/recorrido.json --traversal-sha256 SHA256_DE_RECORRIDO   --question 'La misma pregunta del recorrido'   --model glm-5.3-flash --out /ruta/salida-nueva
```

Salida persistida: `result.json`. `evidence` conserva cinco fragmentos en el ensayo;
`pending_ranges` indica lo pendiente; `answer_result.answer` contiene la respuesta;
`answer_result.citations` vincula citas a posiciones originales. Revisar los estados
antes de consumir la respuesta. El directorio de salida debe ser nuevo. Máximo una
llamada, sin reintentos; salida por defecto 2048 tokens, timeout socket 90 segundos.
El registro de recorrido se limita a 8 MiB. El replay puede releer repetidamente la
fuente localmente: evitar llamadas externas no significa eliminar coste de lectura.

## Ensayo del 22 de septiembre de 2026

Fuente sintética de 144 748 bytes y recorrido anterior completo de nueve unidades.
Se reutilizaron cinco fragmentos, 323 bytes; cuatro describen las fases de Vela y
uno alude a Eloy en Risco. Código, entradas y referencia congelados antes de llamar.
Modelo solicitado y reportado por proveedor: `glm-5.3-flash`, sin acreditación externa.

La respuesta incluyó correctamente:

1. Preparar el almacén — Aina.
2. Probar las herramientas — Berto.
3. Formar al personal — Cora.
4. Revisar los resultados — Darío.

Citó los cuatro fragmentos correspondientes, con anclajes verificados contra el
original. No incorporó a Eloy. Una llamada nueva, **918 tokens reportados**,
**13,197 segundos** de proceso. Coste acumulado observado de recorrido más respuesta:
**96 008 tokens**, diez llamadas en dos ejecuciones. No hay ahorro demostrado frente
a lectura completa directa ni coste monetario calculado.

Evidencia local: `experiments/traversal-query-v1/runs/glm-01/`, ignorada por Git.
La suite pasó **145 pruebas**, ocho nuevas sobre candidato completo, bloqueo parcial,
evidencia alterada, falsa cobertura, pregunta cambiada, extracción vacía, fuente
cambiada y hash incorrecto. CLI comprobada mediante help y ejecución real desde la
copia de código congelada. Autorrevisión adversarial del productor, no independiente.

## Siguiente paso

Hay una ruta funcional de lectura → evidencia conservada → respuesta candidata.
Falta evaluarla con documentos reales autorizados y preguntas nuevas, y comparar
coste total con un baseline de fuente completa. Optimizar tamaño de ventanas y
solapamiento sólo después de fijar el criterio de omisiones aceptable. Las CLI
anteriores y los contratos de cobertura siguen separados; este consumidor no se
activa automáticamente ni cambia las integraciones opcionales con Skopos y AN-KLA.

Sin commit, push, escritura de memoria ni cambio de contexto canónico.
