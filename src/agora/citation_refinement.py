"""Validate explicit offline subquotes without claiming semantic entailment."""

import hashlib
import re

from .source_evidence_exchange import _read_json

SCHEMA = "agora/citation-refinement/v1-experimental"


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load_refinement(path, source_raw, source_sha256, candidate, candidate_sha256):
    raw, selection = _read_json(path, 65536)
    if (type(selection) is not dict or set(selection) !=
            {"schema", "source_sha256", "candidate_sha256", "claims"} or
            selection["schema"] != SCHEMA or
            selection["source_sha256"] != source_sha256 or
            selection["candidate_sha256"] != candidate_sha256 or
            type(selection["claims"]) is not list):
        raise ValueError("invalid_citation_refinement")
    expected = {(part["id"], index): (claim, [c for c in candidate["citations"]
                if c["part_id"] == part["id"] and c["claim_index"] == index])
                for part in candidate["parts"] for index, claim in enumerate(part["claims"])}
    found = {}
    for row in selection["claims"]:
        if (type(row) is not dict or set(row) !=
                {"part_id", "claim_index", "claim_sha256", "ranges"} or
                type(row["part_id"]) is not str or
                type(row["claim_index"]) is not int or
                type(row["claim_sha256"]) is not str or
                type(row["ranges"]) is not list or not row["ranges"]):
            raise ValueError("invalid_refinement_claim")
        key = row["part_id"], row["claim_index"]
        if key not in expected or key in found:
            raise ValueError("invalid_refinement_claim_set")
        claim, citations = expected[key]
        if _sha(claim["text"].encode("utf-8")) != row["claim_sha256"] or not citations:
            raise ValueError("refinement_claim_mismatch")
        ranges = []
        previous_end = -1
        for item in row["ranges"]:
            if (type(item) is not dict or set(item) !=
                    {"start_byte", "end_byte", "literal_sha256"} or
                    type(item["start_byte"]) is not int or
                    type(item["end_byte"]) is not int or
                    type(item["literal_sha256"]) is not str):
                raise ValueError("invalid_refinement_range")
            start, end = item["start_byte"], item["end_byte"]
            if not 0 <= start < end <= len(source_raw) or start < previous_end:
                raise ValueError("invalid_refinement_range")
            excerpt = source_raw[start:end]
            try:
                excerpt.decode("utf-8")
            except UnicodeError as exc:
                raise ValueError("refinement_splits_utf8") from exc
            if _sha(excerpt) != item["literal_sha256"]:
                raise ValueError("refinement_literal_mismatch")
            matching = [c for c in citations if any(
                match["start_byte"] <= start and end <= match["end_byte"]
                for match in c["matches"])]
            if not matching:
                raise ValueError("refinement_outside_candidate_citation")
            ranges.append((start, end, matching[0].get("evidence_id")))
            previous_end = end
        activity = re.search(r"\bActividad\s+(\d+)\b", claim["text"], re.IGNORECASE)
        if activity and not re.search(
                rb"(?<!\d)" + activity.group(1).encode() + rb"\.",
                b"\n".join(source_raw[start:end] for start, end, _ in ranges)):
            raise ValueError("refinement_activity_mismatch")
        found[key] = ranges
    if set(found) != set(expected):
        raise ValueError("invalid_refinement_claim_set")
    return found, _sha(raw)
