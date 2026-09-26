# Consulta sobre recorrido conservado

Ensayo sintético, una llamada máxima GLM, sin reintento; mismos pregunta, fuente y
resultado de `traversal-v1/runs/glm-01`, verificados antes de generar. Referencia:
cuatro fases Aina, Berto, Cora y Darío; Eloy es un distractor. Conjunto conocido,
no holdout. Detalles y contratos en `docs/consulta-recorrido.md`.

`runs/glm-01/` conserva código, entrada y protocolo congelados antes de ejecutar,
respuesta, tiempo, hashes y revisión posterior. Resultados ignorados por Git.
Entrada pública: `PYTHONPATH=src python3 -m agora.traversal_cli --help`.
