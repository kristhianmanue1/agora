# Candidate relation verification — Jev pilot

2026-10-03. One live call; response model `jev-1.13.0`. No product/CLI change.

## What was tested

Can a reviewer verify a proposed relation between a system, its input and its
evaluation, while preserving task, version and input granularity? Eight synthetic
controls and two claims on the existing manually selected QASPER development
chain. Includes reused names across tasks, explicit aliases, missing evaluation,
version swaps and sentence/document scope. Positive and negative controls use
producer labels frozen before the call; labels were not sent to Jev.

This is **candidate verification**, not autonomous entity extraction, automatic
retrieval, independent annotation adjudication or a held-out accuracy estimate.
All ten records share one request; instructions isolate records but leakage and
order sensitivity were not independently tested. Synthetic cases are small and
explicit. An external provider does not make producer labels independent.

## Observed result

- Exact label agreement: **7/10**.
- Supported versus other: **10/10**, including three supported cases.
- Three disagreements: C02 (evaluation from another task), C08 (evaluation from
  another version), D02 (whole-document input inferred from sentence evidence).
  Producer: `insufficient`; Jev: `contradicted`.
- D01, the full-sentence baseline comparison, is marked supported.
- One HTTP attempt, no retries; **2,921 input + 454 output = 3,375 tokens**.
  Monetary/infrastructure cost not measured. No GLM call.

The broad accept/reject distinction agrees with the producer in this small set,
but the reasons for rejection are unreliable. Absence of evidence is not itself
an explicit contrary statement. D02 extends the known failure mode from earlier
review experiments. No original QASPER labels or documents were changed.

## Decision and adversarial self-review

Do not use these classifications for automatic contradiction assertions or
admission. A reviewer may flag `needs_more_evidence` as a candidate signal;
claiming contradiction should require an identifiable contrary source span and
human or separately validated adjudication. That is a recommendation, not a
newly activated product policy.

The main retrieval bottleneck remains: relevant relations were supplied here,
not discovered. The next useful implementation should return a candidate
relation with source-span IDs and a separate evidence-gap state, while retaining
the existing manual review boundary. Do not spend another broad retrieval
campaign until this relation representation and its failure behavior are tested.

## Files and checks

`request.json`, `freeze.json`, `review.json` preserve exact request, limits,
producer expectations and raw response. `assessment.json` preserves all three
disagreements. `assess.py` validates identity/keys and computes counts offline.
`prepare.py` / `review.py` are archived execution scripts; do not rerun in place:
preparation overwrites the freeze and review consumes a provider call.

```sh
python3 experiments/relation-review-v1/assess.py
python3 experiments/relation-review-v1/check_assess.py
python3 scripts/verify_benchmark_evidence.py
```

Historical totals printed by the bank verifier exclude this new call; its usage
is reported separately above. Hash integrity is not semantic correctness.
