# Piloto persistente de cuestiones abiertas

SQLite local, sin servicios, modelos nuevos ni admisión AN-KLA. Historial por
cuestión con revisiones candidatas enlazadas por hash. Cada revisión conserva
entrada exacta, fuentes y versiones, respuesta recibida, evaluación validada,
procedencia declarada y hash del validador. El estado del candidato no otorga
permiso para ejecutar acuerdos ni acredita verdad.

`append` exige el digest de la revisión padre esperada y usa BEGIN IMMEDIATE.
Un escritor atrasado es rechazado; candidato inválido o inserción fallida no
cambian el historial. La pregunta y requisitos iniciales no pueden sustituirse
silenciosamente bajo el mismo ID. No hay API de borrar o editar revisiones.
`history` comprueba cadena, hashes y revalida con el contrato v3; cambio de
validador exige migración explícita. `expected_head` detecta pérdida de cola
cuando el consumidor conserva ese digest fuera del almacén.

## Resultado local-02, 27 de septiembre de 2026

1. Abierto: fecha y responsable pendientes (fixture manual).
2. Resuelto: fecha 2026-10-21 y Lina (fixture manual).
3. Parcial: fecha retirada, Lina conservada (reproducción de la evaluación GLM
   obtenida en open-issues-v3, no una llamada nueva ni nueva prueba semántica).

Tras cada escritura se cerró la conexión y un proceso Python nuevo recuperó
exactamente todas las revisiones, las entradas, citas y resultados. Tres de tres
comparaciones exactas. Cero llamadas al modelo, cero tokens nuevos. El criterio
final coincide con la evaluación full de v3, no se realizó otra comparación LLM.

329 tests pasan, incluidos ocho nuevos: reapertura, escritor atrasado, candidato
inválido, alteración de payload, pérdida de última revisión con digest externo,
fallo de inserción/rollback, base ajena/sobrescritura e identidad de la pregunta.
La primera corrida local-01 pasó antes de añadir el control de identidad. Se
conservó y se repitió local-02 con el código final y copias del código en runs/.
Resultado compacto: result-local-02.json. Base y detalle: runs/local-02/.

## Uso local

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python experiments/issue-store-v1/run.py experiments/issue-store-v1/runs/NOMBRE_NUEVO
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests
```

El destino debe ser nuevo. Datos sintéticos; runs/ ignorado por Git. El ejecutor
usa umask 077. No publica ni escribe memoria canónica. La base guarda snapshots
completos por revisión: no es una estrategia de escala.

## Límites y autorrevisión

- No se probó corte eléctrico, crash durante commit ni durabilidad de dispositivo.
- El test de dos escritores es secuencial con conexiones separadas, no una
  campaña de carreras. SQLite local no implica coordinación distribuida.
- Hashes detectan inconsistencias; no autentican autor ni impiden que quien
  modifica toda la base recalcule hashes. Sin digest externo, una cola borrada
  puede aparentar una historia válida más corta.
- Provenance y revisiones declaradas de dependientes no son receipts autenticados.
- El historial está disponible para inspección, no es reconocimiento automático
  de nuevas fuentes, detección de pendientes ni reevaluación autónoma.
- Las comprobaciones del contrato verifican referencias/forma, no verdad ni
  suficiencia semántica. La tercera revisión reproduce una salida anterior.
- Sin gestión multiusuario, cifrado propio, política de retención, backup/restore
  verificado ni garantías sobre enormes historiales. Sin migración automática.

Siguiente paso propuesto: un adaptador local explícito que reciba una fuente
nueva, recupere la cuestión y su revisión esperada y prepare una evaluación
candidata. Primero probar preparación y rechazo de revisión atrasada sin red;
después una evaluación real acotada. No watcher ni integración obligatoria.

Git: cambios locales sobre d92ce22; sin commit ni push en esta tarea.
