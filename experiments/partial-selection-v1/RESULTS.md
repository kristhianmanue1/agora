# Resultado GLM-01 — 2026-09-28

Dos llamadas reales, ambas completas, 13 612 tokens reportados y 221,184 segundos
sumados de transporte. Modelo solicitado: glm-5.3-flash; identificadores reportados
y uso completo por llamada en result-glm-01.json. Sin reintentos.

1. Selección parcial: fecha null, responsable Lina, estado partial. La explicación
   limita expresamente la ausencia a la selección y no afirma que toda la reunión
   carezca de fecha. El request inspeccionado no contenía la fecha retenida.
2. Selección ampliada: fecha 2026-10-21, responsable Lina, estado resolved. La cita
   apunta al segmento Calendario. Reconoce que ambos paquetes comparten origen y
   que la repetición no es corroboración independiente.

Tres revisiones SQLite recuperadas tras cerrar y reabrir la conexión; ambos
paquetes recuperados exactamente. El texto y hash de sistema quedan dentro de
la identidad persistida de cada operación. Tres referencias a paquetes Skopos
resuelven a localizadores nativos; las restantes citan el antecedente q1.

## Autorrevisión adversarial

- El antecedente dice explícitamente que la fecha estaba pendiente: caso más
  fácil que ausencia sin antecedente. No generalizar a ese segundo caso.
- No hay contradicción nueva ni selección engañosa; falta probar esas variantes.
- Las etiquetas de relación agrupan fuentes sin vinculación individual; la
  explicación aclara el caso, pero la estructura aún pierde esa distinción.
- Guardar dos paquetes no demuestra que se haya leído toda la fuente. Incluso
  ampliado, selection_complete sigue siendo not_established.
- El evaluador y la revisión de fidelidad son del productor. No hay adjudicación
  independiente, evaluación estadística, admisión ni despliegue.
- Los hashes congelados identifican código local; no son firma ni aprobación.

351 pruebas existentes pasan. La evidencia nueva de comportamiento procede de
estas dos llamadas reales, no de ese conteo de regresión.

Siguiente incremento propuesto: ausencia sin antecedente y evidencia contradictoria,
con expectativas fijadas antes de ejecutar. Después, convertir sólo el mecanismo
estable en una API reutilizable; evitar acumular demos equivalentes.
