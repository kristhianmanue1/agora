# First-use agent test

Tested fbda48da77b70aca40be46045adcd255a7b13da4 with a separate agent launched
without conversation history. Task: discover capabilities, run offline example,
create/validate a synthetic v2 candidate, locate provider review without running
it. Public README/guides/help only; no source/tests/experiments inspection.
These access restrictions and 23 commands are agent-reported; a raw transcript
is not included. Producer independently revalidated the resulting candidate and
assessment. This is same-environment usability evidence, not certification.
The producer freeze was recorded shortly after dispatch, before the result.

All four task criteria completed. Agent recovered from system Python 3.9.6
(doctor attention/exit 1) using .venv Python 3.12.12 (ok/exit 0). The synthetic
candidate retains unknown software_version, needs_more_evidence and admitted=false.
No provider call was requested or reported. The documented live command was
identified but not executed. Unknown version was not filled from configuration.

Two usability fixes follow this run: remove stale pending-generator language and
clarify --contract-version scope in native help. The initial README now includes
a more direct instruction for doctor attention. Changes were not retested by a
second fresh agent; local help checks and regression tests cover them.

Artifact outcomes can be checked by validate through the public CLI; source ID
is first-use-translation. The original tested documentation hashes are in freeze.
No claim of complete first-time usability across agents/providers is made.
