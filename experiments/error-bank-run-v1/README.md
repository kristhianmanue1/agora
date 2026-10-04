# Ejecutor del banco de errores — preparación

Scripts de trabajo preservados para el banco `../error-bank-v1`. Su incorporación
a Git no acredita una ejecución Jev ni valida los resultados de esa campaña.

- `run_jev.py`: prepara cuatro lotes; con `DRY_RUN=1` no llama al proveedor.
  Sin ese modo requiere credencial por entorno y puede realizar cuatro llamadas.
- `score.py`: lee recibos de `/tmp/aria-error-bank-v1` y escribe `result.json`.

Comprobación realizada al publicar: sintaxis Python, JSON del banco, coincidencia
del hash congelado y preparación offline de cuatro lotes. No se ejecutaron
llamadas Jev ni puntuación de recibos en esta revisión de publicación.

Antes de usar como ejecución validada, revisar reserva de un directorio nuevo
(el actual es fijo y permite reutilización), preservación de intentos y resultados
inciertos, validación exacta de IDs/ejes de respuesta y límites del transporte.
El scorer actual no verifica explícitamente unicidad y conjunto completo de
respuestas antes de calcular sus umbrales. No tratar estos scripts como una
calibración aprobada ni como autorización automática para una nueva corrida.
