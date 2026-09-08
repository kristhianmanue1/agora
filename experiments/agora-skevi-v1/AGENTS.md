# AGENTS.md — controlador experimental

Esta carpeta contiene infraestructura neutral de preparación y verificación.

- No implementes aquí la vertical slice de Ágora.
- No ejecutes productores, reviewers, fixtures ni corridas sin autorización
  humana vigente y separada.
- No instales ni copies SKEVI; C1 consume el perfil documental fijado.
- C0 y C1 deben conservar el mismo baseline, recursos, herramientas y oráculos.
- Un cambio de lock, fixture, measurement o regla de decisión requiere una nueva
  versión o enmienda explícita con digests recalculados.
- Los outputs de preparación deben escribirse fuera del repositorio y fuera del
  alcance de otras corridas.
- Todo resultado material sometido a mecanismos SKEVI requiere una ronda
  adversarial fresca sobre el artefacto final. La revisión registra sus ejes de
  independencia y un veredicto `PROCEED` o `FIX-AND-RETRY`; si causa cambios,
  se repite sobre el nuevo resultado. Una autorrevisión no se declara
  independiente.
