# Alcance de ausencia, omisión y contradicción; segunda lectura demostrada

Cinco controles sintéticos del productor, fijados antes de llamadas: ausencia en
pasajes → missing; omisión con evidencia leída → missing; afirmación contraria a
fuente → contradicted; respuesta correcta → covered; negación global falsa →
contradicted. Los cinco coincidieron. No son validación estadística independiente.

El caso real previo de modelos de referencia fue revisado sin cambiar candidato,
fuente ni rúbrica. V2 clasificó ambos requisitos missing y Jev respaldó su declaración
limitada al contexto. `reading-route` indicó expand y referencias fuera del contexto.
`coverage-plan` amplió de 7.680 a 14.409 bytes bajo techo 20.000. `generate-recovery`
produjo candidato válido; scoped GLM cubrió 2/2 y Jev dio respaldo. La siguiente ruta
quedó candidate_ready_for_explicit_review, nunca aceptación ni admisión.

Todo el recorrido usó comandos públicos; demo.py sólo los orquesta. Originales
conservados; verify.py reproduce generación, vínculos y decisiones sin red. El
revisor v1 y sus resultados históricos no se modificaron.

Diez llamadas (cinco controles y cinco para la transición), 18.964 tokens reportados.
Una llamada por fase, sin reintentos. La diferencia v1/v2 es una condición nueva,
no una adjudicación por mayoría. Los controles no permiten afirmar fiabilidad general.

Archivos completos en inputs/runs locales excluidos de Git; reportes y hashes
publicados. No escribir secretos en estas carpetas. Reproducción requiere los
artefactos locales anteriores. Los tests de producto no dependen de ellos.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 experiments/scoped-flow-v1/verify.py
```
