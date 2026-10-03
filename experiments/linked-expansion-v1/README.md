# Linked additive expansion — development experiment

2026-10-03. Implements expansion in `selector.py`; no product or CLI change.
No API calls. Four previously inspected papers, explicitly development data.

## Rule

Start with frozen IDF selections at 5,000 bytes; expand to at most 12,000.
Verify source SHA, question and exact whole-paragraph ranges. Preserve every
selected range, rejecting insufficient budgets rather than deleting content.
Find literal labels defined at paragraph starts (`label: description`), then
add paragraphs sharing an active label, ranked by shared labels, IDF and order.
Repeat until no linked paragraph fits. Every addition records its matching
labels. Matching strings are clues, not verified system identity or relations.

The source hash protects against accidentally reusing offsets in another source;
it is not authenticity or authorization. Independently starting at two budgets
is not guaranteed monotonic; preservation applies to expansion from prior state.

## Observations

| Paper | Initial bytes | Expanded bytes | Added paragraphs | Annotated coverage |
|---|---:|---:|---:|---|
| 1907.12984 | 4,981 | 11,997 | 14 | unchanged: 0/3 and 0/1 |
| 1602.04341 | 4,911 | 4,911 | 0 | unchanged: 1/10, 1/1, 1/1 |
| 1602.07776 | 4,914 | 4,914 | 0 | annotations unmapped |
| 1603.00957 | 4,636 | 4,636 | 0 | unchanged: 1/2; second unmapped |

The corrected manual chain for 1907.12984 improves from 0/3 to 1/3 (the
paragraph at bytes 22731–22937), still insufficient. Original annotations remain
unchanged; the prior annotation scope disagreement is not adjudicated here.

## Adversarial self-review

Preservation passes on four development transitions and synthetic controls;
it does not prove all-input correctness. No coverage gains against mapped gold.
A broad definition pattern admits `good` as a label, so definitions are not
reliable system names. Repeated labels can refer to different tasks; no semantic
identity resolution exists. English colon labels omit unnamed systems and
pronouns. Added context can consume budget without completing a comparison.

**Do not promote this retrieval heuristic.** The additive-state mechanism is a
useful candidate, but link quality is insufficient. No new held-out validation
or provider generation is warranted for this unchanged heuristic. Next work
should separately validate identifying a system and linking its input/evaluation
statements, with a control where identical labels refer to different tasks.
Avoid spending another campaign merely varying keyword weights.

## Reproduction

From repository root:

```sh
PYTHONPATH=src python3 experiments/linked-expansion-v1/check_selector.py
PYTHONPATH=src python3 experiments/linked-expansion-v1/verify.py
python3 scripts/verify_benchmark_evidence.py
```

`run.py REPO NEW_OUTPUT_DIRECTORY` reproduces development selections and scoring.
`freeze.json` stores source/corpus/selector identities before annotation scoring.
`selections.json` preserves outputs before scores; `result.json` adds annotations.
Four tests check preservation, literal links, UTF-8, no inferred links, and
rejection of changed source/question, invalid ranges and insufficient budgets.
The initial test mistakenly compared per-step addition receipts with a direct
expansion receipt; fixed to compare final ranges, since receipt histories differ.
