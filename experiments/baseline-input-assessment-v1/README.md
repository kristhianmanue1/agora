# Baseline input: model identity is not experimental input configuration

## Conclusion

Keep `input` unknown in the current v2 candidate. The full-sentence interpretation
is plausible for the **baseline experimental condition**, but should remain a
producer inference rather than an explicitly established field. This is not a
claim that the paper lacks evidence, nor proof that the baseline uses fragments.

## Evidence and counterexample

Six exact spans and their offsets are preserved in assessment.json:

1. Introduction: full-sentence models wait for the end of a sentence.
2. Method: treating a full sentence as an information unit reduces the proposed
   model to a standard translation model.
3. Model settings: baseline is a standard Transformer with big hyperparameters.
4. Crucially, **sub-sentence also uses the baseline model**, after splitting a
   sentence at commas. The same model can therefore receive different inputs.
5. Experiments distinguish baseline and sub-sentence conditions.
6. Whole-talk context in dataset translation describes the human translator;
   it is not evidence of whole-document machine input.

Together, these favor a full-sentence baseline condition, but the correspondence
between model family, named condition and exact input is inferred. The first
three paragraphs alone did not capture the model-reuse counterexample.

The earlier manual three-paragraph chain remains historical, unchanged. Its
usefulness for a qualified explanation must not be inflated into a fully explicit
identity/input proof. Neither Jev support nor repeated generation resolves that.

## Check against original publication

Also inspected [arXiv v2](https://arxiv.org/html/1907.12984) and extracted
[PDF text](https://arxiv.org/pdf/1907.12984): Figure 1 caption, section 4.3,
Table 2, Figure 8 caption and the NIST08 discussion. The figure explains
full-sentence waiting; the table separates experimental conditions and the
NIST08 discussion associates baseline performance with long sentences. This
strengthens the interpretation but does not give an explicit run configuration.
No PDF visual inspection or upstream code execution was performed.

To settle exact experiment input mechanically, inspect a configuration or
inference path tied to that baseline run. Do not claim that all original-paper
evidence is absent, and do not repeat the already-inspected table as a new test.

## Outcome and stop rule

No product changes, candidate mutation, API calls or automatic admission.
Producer inspection and adversarial self-review only. This diagnostic is closed;
the candidate retains input unknown. Do not repeat generations on the same three
paragraphs expecting new evidence. Next useful action is to obtain the exact experiment configuration, or move
to a new case while preserving this one as unresolved. No new schema is needed just to record this uncertainty.

Offline verification:

```sh
python3 experiments/baseline-input-assessment-v1/verify.py
python3 scripts/verify_benchmark_evidence.py
```

Checks establish provenance and preservation, not semantic adjudication.
