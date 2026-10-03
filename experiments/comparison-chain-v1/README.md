# Comparison-chain retrieval v1 — not promoted

2026-10-03. Offline experiment; no provider calls and no default/CLI changes.

## Frozen rule and sample

`selector.py` selects whole UTF-8 paragraphs from three English keyword groups:
baseline/comparison, input granularity, evaluation/results. Within each group it
uses question-token IDF; it interleaves the queues while space remains. The
selector takes only source bytes, question and budget, never gold evidence.
This is a role-keyword heuristic, not entity linking or semantic chain recovery.

The selector was fixed before scoring. `freeze.json` records its hash, corpus
hash and cases. All selections were saved before accessing answer annotations.
Budgets: 5,000 and 12,000 bytes. Comparator: existing IDF with six seeds and
neighbor expansion. Same byte ceiling does not imply the same delivered bytes.

Sample: development case `1907.12984`, plus first three sorted QASPER papers of
25–100 KB with a comparison/baseline/outperform question and IDs absent from
prior experiment freeze files. This is local novelty, not certified global
holdout. The attempted 40–100 KB filter could not supply three cases; it was
relaxed before annotation access. No paper was discarded for its score.

## Results (covered / mapped annotated evidence)

Annotations are scored separately, not merged into a manufactured gold.

| Paper / annotation | IDF 5k | Chain 5k | IDF 12k | Chain 12k |
|---|---:|---:|---:|---:|
| 1602.04341 / first | 1/10 | 3/10 | 2/10 | 4/10 |
| 1602.04341 / second and third, each | 1/1 | 1/1 | 1/1 | 1/1 |
| 1602.07776 / both | unmapped | unmapped | unmapped | unmapped |
| 1603.00957 / first | 1/2 | 0/2 | 1/2 | 0/2 |
| 1603.00957 / second | unmapped | unmapped | unmapped | unmapped |

On development paper 1907.12984, the corrected manual evidence chain remains
**1/3** at both budgets (IDF 0/3). Original annotation A changes from 1/3 at 5k
to 0/3 at 12k; B goes from 0/1 to 1/1. B refers to a different task according to
the previous diagnosis and must not be counted as substantive improvement.
Original annotations remain intact. See `../streaming-diagnosis-v1/README.md`.

## Adversarial self-review and decision

- Regression on a new document refutes a claim of general improvement.
- Greedy budget packing is non-monotonic: a larger paragraph can take space
  previously occupied by a smaller relevant one. More bytes do not imply more
  preserved evidence. Separate calls at different budgets are not a safe
  incremental second-reading implementation.
- Generic role terms retrieve unrelated comparisons and do not establish that
  the baseline, input and results belong to the same system/task.
- Unmapped evidence cannot be scored as absence or zero recall.
- Annotation overlap is not faithfulness or generated-answer accuracy. No
  generated response, latency benchmark or monetary savings claim is made.

**Decision: do not promote.** Keep this code under experiments and preserve the
existing product default. This was producer self-review, not independent QA.

Next candidate should preserve previously selected evidence during expansion
and resolve named-system links across paragraphs. Fix the rule using development
cases, then assess it on a separately frozen sample; do not retune v1 against
these now-inspected test annotations.

## Reproduction

From the repository root:

```sh
PYTHONPATH=src python3 experiments/comparison-chain-v1/check_selector.py
PYTHONPATH=src python3 experiments/comparison-chain-v1/verify.py
python3 scripts/verify_benchmark_evidence.py
```

`run.py REPO NEW_OUTPUT_DIRECTORY` documents original sample discovery. A new
run will see more freeze files and can choose different cases; use `verify.py`
to reproduce the preserved frozen selections instead. Corpus must be present
locally at `experiments/qasper-v1/inputs/test.json`.
