"""Offline guards for two known page-18 citation errors; not semantic adjudication."""

import argparse
import hashlib
import json
from copy import deepcopy
from pathlib import Path

SOURCE_SHA256 = "ae101c1df39c2d7f0cab65b30d4a53c1fc78e1edf25749e61e18d9ff9083bd48"
ACTOR_ROW_16_17 = (822, 827)
REQUIRED = {
    2: [(800, 821), (822, 827), (827, 831), (1043, 1056),
        (1213, 1271), (1319, 1334)],
    3: [(822, 827), (973, 1043), (1043, 1056),
        (1213, 1271), (1319, 1334), (1334, 1477)],
}


def audit(raw, package):
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError("wrong_page18_source")
    if package.get("schema") != "agora/consultation-package/v3-experimental":
        raise ValueError("wrong_package_schema")
    claims = {c["claim_index"]: c for c in package["claims"]}
    if len(claims) != 4 or set(claims) != {0, 1, 2, 3}:
        raise ValueError("wrong_claim_set")
    for index, expected in REQUIRED.items():
        evidence = claims[index]["evidence"]
        for item in evidence:
            start, end = item["start_byte"], item["end_byte"]
            if not 0 <= start < end <= len(raw):
                raise ValueError("invalid_evidence_range")
            if (item["literal_text"] != raw[start:end].decode("utf-8") or
                    item["literal_sha256"] != hashlib.sha256(raw[start:end]).hexdigest()):
                raise ValueError("invalid_evidence_literal")
        for start, end in expected:
            if not any(e["start_byte"] <= start and end <= e["end_byte"]
                       for e in evidence):
                raise ValueError(f"claim_{index}_required_source_span_missing:{start}-{end}")
    actor = [e for e in claims[3]["evidence"]
             if (e["start_byte"], e["end_byte"]) == ACTOR_ROW_16_17]
    if len(actor) != 1 or actor[0].get("segment_id") != "skopos-p18-item-29":
        raise ValueError("activity_17_wrong_actor_row")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--package", required=True, type=Path)
    parser.add_argument("--prior-package", required=True, type=Path)
    args = parser.parse_args()
    raw = args.source.read_bytes()
    package = json.loads(args.package.read_text(encoding="utf-8"))
    prior = json.loads(args.prior_package.read_text(encoding="utf-8"))
    audit(raw, package)
    negative_results = {}
    for index in (2, 3):
        modified = deepcopy(package)
        modified["claims"][index]["evidence"] = prior["claims"][index]["evidence"]
        try:
            audit(raw, modified)
        except ValueError as exc:
            negative_results[str(index)] = str(exc)
        else:
            raise AssertionError(f"negative_control_{index}_accepted")
    print(json.dumps({"status": "known_error_guards_passed",
                      "negative_controls": negative_results}, sort_keys=True))


if __name__ == "__main__":
    main()
