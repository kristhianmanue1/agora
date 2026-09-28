# Ampliación explícita de evidencia — ensayo 01

2026-09-28. Seguimiento de dos fallos conocidos de reviewer-comparison-v2.
No es holdout ni recuperación automática: el productor selecciona el pasaje.
Se conserva el resultado original por proveedor, con su hash y request_sha256.

Por cada afirmación y revisor: abstract solo, abstract más párrafo general,
abstract más párrafo decisivo. Dos repeticiones por condición: 12 llamadas por
proveedor, 24 máximas; 2048 tokens de salida GLM, 90 segundos, sin reintentos.
Mismos criterios/payload/transportes que v2; no se pasa etiqueta anterior, gold,
nombre de condición o repetición al modelo. Orden intercalado por hash fijo.
El párrafo decisivo tiene 1375 bytes; el control general 1383 bytes. Ambos son
literales de la misma revisión de fuente, con rangos UTF-8 y hashes comprobados.
No se sintetiza ni corrige el original; las expansiones son candidatos separados.

Criterios fijados antes de llamar: baseline/control → insufficient para ambas
frases. Target → supported para dependencia externa y contradicted para operación
interna. Evaluar corrección por condición, cambios respecto del resultado original,
repeticiones coincidentes y conservación de fuentes/afirmación/pregunta. Fallos
permanecen en el denominador. Parada heredada por 401/402/403/429 o tres errores.

Un acierto con el pasaje elegido no prueba detección automática de insuficiencia,
recuperación relevante, cobertura global, causalidad general ni estabilidad con
sólo dos repeticiones. Cambiar de etiqueta es necesario cuando cambia la evidencia;
no equivale por sí solo a acertar. No se promueve Jev ni se cambia GLM generador.
La señal de confianza no decide cuándo expandir: este ensayo tiene disparo explícito.

Preparar: PYTHONPATH=src python3 experiments/evidence-expansion-v1/prepare.py.
Ejecutar mediante Llavero como v2, con run.py glm/jev --out RUTA_NUEVA.
Inputs completos permanecen locales ignorados; originales, linaje, gold, resultados
y recibos sin texto documental completo se publican. freeze.json fija entradas,
código y contrato antes de las llamadas. Puntuación posterior no cambia gold.
