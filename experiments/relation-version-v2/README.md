# Relation v2: software release versus configuration

Known development chain from paper 1907.12984, manually selected and preserved
from ../relation-real-v1/. Same derived source identity and offsets; not retrieval.
One new GLM call and one Jev call, no retries or format repairs.

GLM reports glm-5.3-flash and 3,045 total tokens. It leaves software_version null,
places “big version of hyper parameters” in model_configuration and also leaves
input null. Jev reports jev-1.13.0, 3,794 input + 298 output tokens; both missing
fields are insufficient, other fields and relation supported. No structural
inconsistencies, but the candidate remains needs_more_evidence. Total observed:
7,137 tokens, not monetary cost; reasoning tokens are already included.

The intended version/configuration distinction appeared in this run. This is
not general semantic reliability. Input was filled in the v1 run and is missing
here: that change must not be described as an unqualified improvement. Jev marking
the partial relation supported does not fill missing fields or admit the result.

V1 interpretation and artifacts remain intact; v2 is explicit and optional.
No automatic conversion was used. Labels and interpretation are from the producer;
no independent adjudication. The initial source selection is still manual.

Offline check: python3 experiments/relation-version-v2/verify.py
