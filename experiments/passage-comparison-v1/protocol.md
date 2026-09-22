# Comparación exploratoria de pasajes v1

Alcance autorizado: consumidor de múltiples pasajes y comparación. Sólo fuente
sintética, sin datos privados ni integración con otros componentes. Protocolo
preparado antes de ejecutar GLM. No es holdout: productor conoce las preguntas.

Tres rutas, mismas cinco preguntas y mismo prompt/parámetros:
- source: fuente completa (control comparativo, no verdad de referencia).
- reference: pasajes de referencia establecidos en cases.json; control diagnóstico.
- retrieve: solapamiento léxico de párrafos, hasta tres semillas y vecinos si caben.

GLM solicitado glm-5.3-flash; temperatura0;2048tokens de salida;90s de timeout por operación de socket;110s máximo de proceso por ruta;
máximo15peticiones,sin retries. Fuente20480bytes máximos enviados como contenido;
reference/retrieve1800bytes;prompt65536bytes (system+user,no transporteJSON/tokens).
Sin candidato de búsqueda: cero llamadas y resultado no_retrieval_candidates.
No existe búsqueda semántica ni fallback; no mejorar prompts después de resultados.

Criterios por pregunta fijados en cases.json. Q1 contradicción12/18, Q2hechos
separados Inés/240, Q3sinónimos sin vocabulario compartido (control de fallo de
recuperación), Q4ausencia de importe y Q5responsable local. Evaluación de soporte
humana/agente contra fuente, nunca JSONválido=corrrecto ni baseline=referencia.
No hay juez automático de fidelidad. Recuperación y respuesta se evalúan aparte.

Conservar fallos, tiempos, prompt completo, contenido/uso/modeloreportado por
proveedor, hashes de módulos, código ejecutado congelado,fuente y criterios.
No almacenar reasoning_content ni credenciales. Latencia paredporruta; no medir
latencia sumada como tiempo de sesión cuando se ejecute en paralelo.

Parar llamadas nuevas si aparece credencial/sensible, alcanceexcedido o fallo
persistente del proveedor. Un fallo semántico no impide controles diagnósticos.
No afirmar estabilidad, robustez general o rendimiento en documentos arbitrarios.
El corpus con distractores repetidos sirve para recorrido acotado, no representa
complejidad real. No visión global/hierarquía en este incremento.

El runner mide tiempo monotónico y ejecuta copia congelada del código.
local_scan_bytes no incluye las otras relecturas/hash del archivo.
