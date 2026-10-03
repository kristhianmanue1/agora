# Real-paper relation workflow with explicit syntax repair

2026-10-03T23:37:43.742962+00:00 freeze; development paper QASPER 1907.12984. Product
revision used: 1120ca7e08c1c3bd72f8123c1332ff5bffac5c29.

## Scope and provenance

Three manually selected original paragraphs, 715 bytes plus four separator bytes,
were supplied as a **derived source** of 719 bytes. Its ID and SHA differ from
the original paper. `freeze.json` maps every derived span to the original source
revision. IDs in the generated candidate refer to the derived source; they must
not be mistaken for offsets into the full paper. This does not test automatic
retrieval: the current retrievers still fail to recover the complete chain.

## Execution

1. One GLM call produced a candidate followed by an extra backtick. Strict JSON
   parsing rejected it (`Extra data`), despite finish_reason=stop. Original
   response remains in generation/result.json; no original candidate was emitted.
2. An explicit local repair removed only the final backtick, leaving the JSON
   content and every field unchanged. `repair-receipt.json` records both hashes.
   The derived response passed through the same CLI in replay mode. This was
   neither a new generation nor a hidden correction of the original response.
3. One Jev call reviewed the repaired candidate: all five fields and their link
   were marked supported; no structural inconsistencies. The result remains
   admitted=false and semantic_support=not_verified.

Observed GLM model glm-5.3-flash: 3,481 tokens. Jev model jev-1.13.0:
3,239 input + 249 output = 3,488. Total **6,969**, with no additional tokens
attributed to replay. One generator call and one reviewer call, no retries.

## Producer assessment and unresolved scope

The candidate preserves sentence scope, does not claim whole-document input and
does not invent a numerical result or metric name. It links the three supplied
paragraphs. These are producer observations, not independent adjudication.

A remaining ambiguity is material: `version` contains the literal phrase
“big version of hyper parameters”. That describes a configuration/variant, not a
software release identity. Jev marks it supported because the words are present.
The v1 field contract does not specify which meaning of version applies. The
source has not established a software version. Preserve this ambiguity; do not
silently rewrite the field or count this as semantic closure.

This run demonstrates a real-paper workflow **with explicit repair**, not clean
first-pass generation, reliable retrieval or reliable entity/version resolution.
Next bounded change: define identity/version separately from configuration, with
explicit unknown values and tests where literal text is placed in the wrong field.
Do not launch a larger benchmark before settling that representation.

## Offline verification

```sh
python3 experiments/relation-real-v1/verify.py
python3 scripts/verify_benchmark_evidence.py
```

The verifier checks provenance mapping, the exact one-character repair,
source/candidate/reviewer binding and observed usage. It does not certify truth.
`prepare.py` is an archived preparation script; rerunning in this directory would
overwrite the freeze, so use a new directory if repeating the experiment.
