---
id: agora-skevi-experiment-v1
autor: Mediador, documentado por OpenAI Codex
fecha: 2026-09-07
proyectos: [agora, skevi]
estado: vigente
derivado_de: [agora-baseline-v1, agora-skevi-pilot-v1, decision-identidad-agora, evaluacion-skevi-agora]
---

# agora-skevi-experiment/v1

Contrato documental congelado. Identifica un experimento futuro; no autoriza
construir la vertical slice, activar SKEVI ni ejecutar corridas.

```yaml
experiment_id: agora-skevi-experiment/v1
status: frozen
frozen_at: 2026-09-07T22:30:12-06:00
refrozen_at: 2026-09-08T03:17:18-06:00
amendments:
  - amendment_id: freeze-status-consistency-1
    prior_git_revision: 0a35bf5702023996dd9163a8f3ade3e0754be713
    scope: profile status wording and profile digest
    semantic_change: false

conditions:
  C0:
    instruction_packs: [agora-baseline/v1]
  C1:
    instruction_packs: [agora-baseline/v1, agora-skevi-pilot/v1]

baseline:
  id: agora-baseline/v1
  path: 2026-09-07-agora-baseline-v1.md
  sha256: 6f6eef7f5ccbc6092cbe563bbbabc80919ec45ddb19c7f6265a400f3a59a516b

skevi_profile:
  id: agora-skevi-pilot/v1
  path: 2026-09-07-agora-skevi-pilot-v1.md
  sha256: 0fc5a51a1479804afa890d5ef59f4940ebf633091aa978bcda74de47b8e4c34e
  skevi_commit: b400b85c164827ecfb107363a2194c5c6635a9c7

section_digest_rule:
  encoding: UTF-8
  line_endings: LF
  start: heading line included
  end: byte before next heading matching "### P<number>."

fixture_set:
  id: agora-skevi-fixtures/v1
  source: 2026-09-07-agora-skevi-pilot-v1.md#P3
  sha256: 9a0f91e3fc0a4b1598938b7eca21f64b3cf7c65c009ac8d356b2ef6f9a68a28b

measurement_protocol:
  id: agora-skevi-measurement/v1
  source: 2026-09-07-agora-skevi-pilot-v1.md#P5
  sha256: 60af577c0fd4884a6bc73af60c387978ac91c1167b247de46de85fde35bee683

producer:
  provider: OpenAI
  model: gpt-6-astra
  reasoning_effort: high

tool_manifest:
  id: agora-producer-tools/v1
  allowed:
    - read and write inside assigned isolated workspace
    - shell execution inside assigned isolated workspace
    - local git status, diff, log and object reads
    - preinstalled language runtime and test runner
  denied:
    - network access
    - git remote mutation, commit, push, merge, tag and release
    - AN-KLA retrieval, write and checkpoint
    - files, caches, logs and sessions from other runs
    - GUI and external applications

budget:
  pairs: 3
  producer_runs: 6
  per_producer:
    tokens: 150000
    model_invocations: 20
    active_hours: 4
  reviewer_runs: 6
  per_reviewer:
    tokens: 30000
    active_hours: 1
  coordination_tokens: 70000
  coordination_active_hours: 6
  total_base_tokens: 1150000
  total_active_hours: 36

reviewer_protocol:
  source: 2026-09-07-agora-skevi-pilot-v1.md#P9
  sha256: 46558e17a4c0d0fb76567373fabb9894768e2ca6658f6cfa69fe0768d2337692
  provider: OpenAI
  model: gpt-5.6-sol
  reasoning_effort: high
  target_condition_awareness: blinded

isolation_policy:
  source: 2026-09-07-agora-skevi-pilot-v1.md#P8
  sha256: e4adbd2024d43d98ca4fbb759759e5faf33667741bf73bfbd147714f0364599d

repetition_policy:
  source: 2026-09-07-agora-skevi-pilot-v1.md#P4
  sha256: 8e87aaea9d18fc1626c80eabb073e185426db930d8c3be22e5f07b1ec044380b
  pairs: 3

decision_rules:
  source: 2026-09-07-agora-skevi-pilot-v1.md#P10
  sha256: 4d5aa2a8f6109d99a375e9c53be9a448333ed15813ff963f8a0a54668470798f

analysis:
  primary: intention-to-treat
  secondary: C0 spontaneous SKEVI-equivalent mechanism rate
```

## Contrato de cada corrida

Toda corrida futura debe declarar y validar antes de comenzar:

```yaml
experiment_id: agora-skevi-experiment/v1
run_id: <id único>
pair_id: <par 1..3>
condition: C0 | C1
```

El run manifest añade `agora_base_commit`, digests de los instruction packs,
modelo efectivo, reasoning, tool manifest, presupuesto, orden asignado, ambiente
y timestamps. Cualquier diferencia no preautorizada se trata conforme a
experimental invalidity; no se corrige después de observar el outcome.

## Intention-to-treat y crossover

La condición asignada nunca cambia. Prácticas equivalentes a SKEVI surgidas
espontáneamente en C0 se registran como crossover y cuentan normalmente en C0.
Omisiones metodológicas en C1 permanecen en C1. El análisis secundario calcula la
tasa cerrada definida en P2 del perfil; no sustituye el análisis principal.

## Límite de inferencia

Superar o no los umbrales sólo sustenta conclusiones bajo los artefactos,
modelos, reasoning, herramientas, presupuesto, aislamiento, reviewers y número
de pares congelados aquí. No autoriza inferencias universales sobre SKEVI,
agentes de IA, otros proyectos, proveedores ni modelos presentes o futuros.

## Revisión identificable

`experiment_id` y los digests identifican el contenido lógico. La revisión Git
que incorpore este documento identifica el freeze físico del corpus documental.
No existe actualización in-place: cualquier cambio crea `/v2` o una enmienda
explícita que vuelve a congelar todos los digests afectados.
