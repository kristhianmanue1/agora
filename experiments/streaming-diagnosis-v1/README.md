# Streaming comparison: retrieval and annotation diagnosis

Observed 2026-10-03. QASPER paper `1907.12984`, question
`ea6edf45f094586caf4684463287254d44b00e95`. Diagnostic follow-up to
`../section-comparison-v1/`; no product code or original annotations changed.

## Findings

The source supports a comparison with a **full-sentence translation baseline**.
It does not establish that the baseline receives an entire document. Three
manually identified paragraphs connect full-sentence input, the standard
Transformer baseline, and the actual comparison: 715 bytes from 47,134 source
bytes. This is a manual evidence plan, not automatic retrieval or demonstrated
end-to-end savings. No answer was generated from this plan.

Against this post-hoc evidence chain, prior overlap, IDF and headings selections
recover 0/3 whole paragraphs at both 5,000 and 12,000 bytes. Headings-lists
recovers 1/3 at both budgets. This confirms a retrieval gap under this diagnostic
criterion; the three selected paragraphs are not an independently adjudicated
exhaustiveness standard. The case is now development data, no longer held out.

## Separate-provider review

One call to Jev, response model `jev-1.13.0`, with the complete source,
anonymized annotation evidence A/B and two scope controls. Original yes/no gold
labels, annotation authors and producer expectations were not sent. The prompt
explicitly asks to distinguish sentence/document and translation/detection:
this framing is disclosed, and is not a blind independent adjudication.

- Both controls matched expectations (unsupported document expansion; supported
  sentence claim).
- Jev classifies B as another task (boundary detection), matching the producer.
- Jev limits full-paper support to sentence scope, matching the producer.
- **Disagreement retained:** A is `supports` for Jev, `partial` for the producer.
  No annotation is relabeled and no automatic acceptance follows.

Observed usage: 11,591 input + 220 output = **11,811 tokens**; one HTTP attempt,
no retries. No GLM call in this experiment. Tokens do not establish monetary or
infrastructure cost. Provider probabilities are not calibrated accuracy.

## Evidence and reproduction

`freeze.json` fixes the request/source hashes, expectations and call limits;
`request.json` preserves exact inputs; `review.json` preserves the response;
`diagnosis.json` records manual spans and prior-selection coverage;
`manual-plan.json` uses the existing explicit-plan contract. `prepare.py` and
`review.py` are archived execution scripts: **do not rerun them in this folder**;
the former overwrites the freeze and the latter can incur a provider call.

Offline integrity check (no API):

```sh
python3 experiments/streaming-diagnosis-v1/verify.py
python3 scripts/verify_benchmark_evidence.py
```

These checks validate preservation and literal ranges, not semantic truth.
Original selection ranges remain in `../section-comparison-v1/result.json`.
The historical accounting totals printed by the bank verifier exclude this
additional review; its tokens are reported separately above.

## Next bounded step

Evaluate comparison-oriented retrieval that connects baseline identity, input
granularity and evaluation results. Freeze its selection rule before scoring new
papers; retain the existing default until generalization is demonstrated.
Use this case for development, separately adjudicate the A disagreement, and do
not optimize against B as if boundary detection were translation evidence.
