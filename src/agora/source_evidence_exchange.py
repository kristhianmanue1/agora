"""Offline, source-neutral resolution of candidate claims to local evidence."""

import argparse
import hashlib
import json
from pathlib import Path
import sys

from .source import FileSourceAdapter, SourceError, digest
from .transform import unique_object

EXCHANGE = "agora/source-evidence-exchange/v1"
CANDIDATE = "agora/source-evidence-candidate/v1"
RESOLUTION = "agora/source-evidence-resolution/v1"
BUNDLE_CANDIDATE = "agora/source-evidence-bundle-candidate/v1"
BUNDLE_RESOLUTION = "agora/source-evidence-bundle-resolution/v1"
MAX_MANIFEST = 1024 * 1024
MAX_CANDIDATE = 1024 * 1024
MAX_ORIGINAL = 64 * 1024 * 1024
SUPPORTED_MEDIA_TYPES = {
    "application/pdf",
    "text/plain; charset=utf-8",
    "text/markdown; charset=utf-8",
    "text/html; charset=utf-8",
    "text/html; charset=iso-8859-1",
}


def _object(value, keys, error):
    if type(value) is not dict or set(value) != set(keys):
        raise SourceError(error)
    return value


def _object_variant(value, key_sets, error):
    if type(value) is not dict or set(value) not in key_sets:
        raise SourceError(error)
    return value


def _label(value, error, maximum=200):
    if type(value) is not str or not value.strip() or len(value) > maximum:
        raise SourceError(error)
    value.encode("utf-8")
    return value


def _hash(value, error):
    if (type(value) is not str or len(value) != 64 or
            any(c not in "0123456789abcdef" for c in value)):
        raise SourceError(error)
    return value


def _positive_int(value, error):
    if type(value) is not int or value < 0:
        raise SourceError(error)
    return value


def _typed_anchor(value, error):
    if type(value) is int:
        return _positive_int(value, error)
    return _label(value, error, 200)


def _temporal(value):
    _object(value, ("document_date", "status"), "invalid_temporal_status")
    if value["document_date"] is not None:
        _label(value["document_date"], "invalid_document_date", 40)
    if value["status"] != "not_assessed":
        raise SourceError("invalid_temporal_status")
    return value


def _normalization(value):
    _object(value, ("status", "description"), "invalid_normalization")
    if value["status"] not in ("not_applied", "applied"):
        raise SourceError("invalid_normalization")
    if value["description"] is not None:
        _label(value["description"], "invalid_normalization", 500)
    if value["status"] == "not_applied" and value["description"] is not None:
        raise SourceError("invalid_normalization")
    return value


def _source(value):
    _object_variant(value,
                    ({"id", "sha256", "media_type", "revision", "uri"},
                     {"id", "sha256", "media_type", "revision", "uri", "temporal"}),
                    "invalid_source_shape")
    _label(value["id"], "invalid_source_id")
    _hash(value["sha256"], "invalid_source_sha256")
    _label(value["media_type"], "invalid_source_media_type")
    _label(value["revision"], "invalid_source_revision")
    if value["uri"] is not None:
        _label(value["uri"], "invalid_source_uri", 1000)
    if "temporal" in value:
        _temporal(value["temporal"])
    return value


def _derivative(value):
    _object_variant(value,
                    ({"id", "sha256", "coverage", "producer"},
                     {"id", "sha256", "coverage", "producer", "normalization"}),
                    "invalid_derivative_shape")
    _label(value["id"], "invalid_derivative_id")
    _hash(value["sha256"], "invalid_derivative_sha256")
    if value["coverage"] not in ("full", "partial", "unknown"):
        raise SourceError("invalid_coverage")
    producer = _object(value["producer"],
                       ("system", "version", "manifest_sha256", "derivation_id"),
                       "invalid_producer_shape")
    _label(producer["system"], "invalid_producer_system")
    _label(producer["version"], "invalid_producer_version")
    if producer["manifest_sha256"] is not None:
        _hash(producer["manifest_sha256"], "invalid_producer_manifest_sha256")
    if producer["derivation_id"] is not None:
        _label(producer["derivation_id"], "invalid_derivation_id", 200)
    if "normalization" in value:
        _normalization(value["normalization"])
    return value


def _read_json(path, limit):
    with Path(path).open("rb") as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise SourceError("json_budget_exceeded")
    try:
        obj = json.loads(raw, object_pairs_hook=unique_object)
    except (ValueError, UnicodeError) as exc:
        raise SourceError("invalid_json") from exc
    return raw, obj


def _check_original(path, expected):
    if path is None:
        return "not_checked"
    count = 0
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        while chunk := stream.read(65536):
            count += len(chunk)
            if count > MAX_ORIGINAL:
                raise SourceError("original_budget_exceeded")
            digest.update(chunk)
    if digest.hexdigest() != expected:
        raise SourceError("original_sha256_mismatch")
    return "sha256_verified"


def _locator(value, profiled):
    _object(value, ("kind", "value"), "invalid_locator")
    kind = value["kind"]
    coordinates = value["value"]
    if type(coordinates) is not dict or not coordinates or len(coordinates) > 8:
        raise SourceError("invalid_locator_value")
    if not profiled:
        _label(kind, "invalid_locator_kind", 80)
        for key, item in coordinates.items():
            _label(key, "invalid_locator_key", 80)
            if key == "bbox":
                if (type(item) is not list or len(item) != 4 or
                        any(type(number) not in (int, float) or not 0 <= number <= 1
                            for number in item) or item[0] > item[2] or item[1] > item[3]):
                    raise SourceError("invalid_bbox")
            elif type(item) is str:
                _label(item, "invalid_locator_value", 500)
            elif type(item) is int:
                _positive_int(item, "invalid_locator_value")
            else:
                raise SourceError("invalid_locator_value")
        if kind == "pdf_page" and (
                type(coordinates.get("page")) is not int or coordinates["page"] < 1):
            raise SourceError("invalid_pdf_page")
        return value
    if kind not in ("pdf_page", "text_range", "html_fragment"):
        raise SourceError("unsupported_locator_kind")
    common = {"section", "activity", "article"}
    if kind == "pdf_page":
        allowed = common | {"page", "function", "item_id", "bbox"}
        if type(coordinates.get("page")) is not int or coordinates["page"] < 1:
            raise SourceError("invalid_pdf_page")
    elif kind == "text_range":
        allowed = common | {"start_byte", "end_byte"}
        if (type(coordinates.get("start_byte")) is not int or
                type(coordinates.get("end_byte")) is not int or
                not 0 <= coordinates["start_byte"] < coordinates["end_byte"]):
            raise SourceError("invalid_text_range")
    else:
        allowed = common | {"selector", "start_byte", "end_byte", "item_id"}
        has_range = "start_byte" in coordinates or "end_byte" in coordinates
        if "selector" in coordinates:
            _label(coordinates["selector"], "invalid_html_selector", 500)
        if has_range and (type(coordinates.get("start_byte")) is not int or
                          type(coordinates.get("end_byte")) is not int or
                          not 0 <= coordinates["start_byte"] < coordinates["end_byte"]):
            raise SourceError("invalid_html_byte_range")
        if not has_range and "selector" not in coordinates:
            raise SourceError("missing_html_anchor")
    if not set(coordinates) <= allowed:
        raise SourceError("invalid_locator_key")
    for key in common & set(coordinates):
        _typed_anchor(coordinates[key], "invalid_typed_anchor")
    if "function" in coordinates:
        _typed_anchor(coordinates["function"], "invalid_locator_value")
    if "item_id" in coordinates:
        _label(coordinates["item_id"], "invalid_locator_value", 200)
    if "bbox" in coordinates:
        item = coordinates["bbox"]
        if (type(item) is not list or len(item) != 4 or
                any(type(number) not in (int, float) or not 0 <= number <= 1
                    for number in item) or item[0] > item[2] or item[1] > item[3]):
            raise SourceError("invalid_bbox")
    return value


def validate_exchange(derived_path, manifest, original_path=None):
    """Validate every segment before making any candidate available."""
    _object(manifest, ("schema", "source", "derivative", "segments"), "invalid_exchange_shape")
    if manifest["schema"] != EXCHANGE:
        raise SourceError("unsupported_exchange_schema")
    source = _source(manifest["source"])
    derivative = _derivative(manifest["derivative"])
    profiled = "temporal" in source or "normalization" in derivative
    if profiled and source["media_type"] not in SUPPORTED_MEDIA_TYPES:
        raise SourceError("unsupported_source_media_type")
    data = FileSourceAdapter(derived_path, derivative["id"])._read(derivative["sha256"])
    size = len(data)
    segments = manifest["segments"]
    if type(segments) is not list or not 1 <= len(segments) <= 4096:
        raise SourceError("invalid_segments")
    by_id = {}
    previous = 0
    for segment in segments:
        _object(segment, ("id", "start_byte", "end_byte", "sha256", "locator", "modality", "extraction_status"),
                "invalid_segment_shape")
        ident = _label(segment["id"], "invalid_segment_id", 100)
        if ident in by_id:
            raise SourceError("duplicate_segment_id")
        start = _positive_int(segment["start_byte"], "invalid_segment_range")
        end = _positive_int(segment["end_byte"], "invalid_segment_range")
        if start < previous or not start < end <= size:
            raise SourceError("invalid_segment_range")
        previous = end
        _hash(segment["sha256"], "invalid_segment_sha256")
        _locator(segment["locator"], profiled)
        _label(segment["modality"], "invalid_modality", 80)
        if segment["extraction_status"] not in ("unreviewed", "visually_checked"):
            raise SourceError("invalid_extraction_status")
        try:
            data[start:end].decode("utf-8")
        except UnicodeError as exc:
            raise SourceError("segment_splits_utf8") from exc
        if digest(data[start:end]) != segment["sha256"]:
            raise SourceError("segment_sha256_mismatch")
        by_id[ident] = segment
    return by_id, data, _check_original(original_path, source["sha256"])


def _resolved_evidence(manifest, segment, start, end, raw, manifest_sha=None):
    """Carry byte literal and declared metadata without interpreting either."""
    try:
        literal = raw.decode("utf-8")
    except UnicodeError as exc:
        raise SourceError("evidence_splits_utf8") from exc
    result = {"source_sha256": manifest["source"]["sha256"],
              "derivative_sha256": manifest["derivative"]["sha256"],
              "segment_id": segment["id"], "start_byte": start, "end_byte": end,
              "literal_text": literal, "literal_sha256": digest(raw),
              "locator": segment["locator"], "modality": segment["modality"],
              "extraction_status": segment["extraction_status"],
              "extraction_status_provenance": "caller_declared",
              "derivative_normalization": manifest["derivative"].get(
                  "normalization", {"status": "not_declared", "description": None}),
              "source_temporal_status": manifest["source"].get(
                  "temporal", {"document_date": None, "status": "not_declared"})}
    if manifest_sha is not None:
        result["manifest_sha256"] = manifest_sha
    return result


def _relation(value, manifests, evidence):
    _object_variant(value,
                    ({"kind", "temporal_status", "identity_status", "normalization"},
                     {"kind", "temporal_status", "identity_status", "normalization", "version_relation"}),
                    "invalid_relation")
    if value["kind"] not in ("cross_source_candidate", "temporal_conflict_candidate",
                              "identity_unresolved_candidate", "version_relation_candidate"):
        raise SourceError("invalid_relation_kind")
    if value["temporal_status"] != "not_assessed":
        raise SourceError("invalid_relation_temporal_status")
    if value["identity_status"] != "not_assessed":
        raise SourceError("invalid_relation_identity_status")
    _normalization(value["normalization"])
    if value["kind"] == "temporal_conflict_candidate":
        dates = {manifests[item["manifest_sha256"]]["source"].get("temporal", {}).get("document_date")
                 for item in evidence}
        if None in dates or len(dates) < 2:
            raise SourceError("temporal_conflict_requires_distinct_declared_dates")
    if value["kind"] == "version_relation_candidate":
        if value.get("version_relation") not in ("amends", "amended_by", "supersedes",
                                                  "superseded_by"):
            raise SourceError("invalid_version_relation")
    elif "version_relation" in value:
        raise SourceError("unexpected_version_relation")
    return value


def resolve(derived_path, manifest_raw, manifest, candidate, original_path=None):
    by_id, data, original_integrity = validate_exchange(derived_path, manifest, original_path)
    _object(candidate, ("schema", "manifest_sha256", "source_sha256", "derivative_sha256", "claims"),
            "invalid_candidate_shape")
    if candidate["schema"] != CANDIDATE:
        raise SourceError("unsupported_candidate_schema")
    if candidate["manifest_sha256"] != hashlib.sha256(manifest_raw).hexdigest():
        raise SourceError("manifest_sha256_mismatch")
    if (candidate["source_sha256"] != manifest["source"]["sha256"] or
            candidate["derivative_sha256"] != manifest["derivative"]["sha256"]):
        raise SourceError("candidate_source_mismatch")
    claims = candidate["claims"]
    if type(claims) is not list or not 1 <= len(claims) <= 64:
        raise SourceError("invalid_claims")
    resolved = []
    seen = set()
    for claim in claims:
        _object(claim, ("id", "kind", "text", "evidence_refs"), "invalid_claim_shape")
        ident = _label(claim["id"], "invalid_claim_id", 100)
        if ident in seen:
            raise SourceError("duplicate_claim_id")
        seen.add(ident)
        if claim["kind"] not in ("interpretation_candidate", "relation_candidate"):
            raise SourceError("invalid_claim_kind")
        _label(claim["text"], "invalid_claim_text", 4000)
        refs = claim["evidence_refs"]
        if type(refs) is not list or not 1 <= len(refs) <= 16:
            raise SourceError("invalid_evidence_refs")
        evidence = []
        ref_seen = set()
        for ref in refs:
            _object(ref, ("segment_id", "start_byte", "end_byte"), "invalid_evidence_ref")
            _label(ref["segment_id"], "invalid_segment_id", 100)
            segment = by_id.get(ref["segment_id"])
            if segment is None:
                raise SourceError("unknown_segment_id")
            start = _positive_int(ref["start_byte"], "invalid_evidence_range")
            end = _positive_int(ref["end_byte"], "invalid_evidence_range")
            if not segment["start_byte"] <= start < end <= segment["end_byte"]:
                raise SourceError("evidence_outside_segment")
            key = (ref["segment_id"], start, end)
            if key in ref_seen:
                raise SourceError("duplicate_evidence_ref")
            ref_seen.add(key)
            evidence.append(_resolved_evidence(manifest, segment, start, end, data[start:end]))
        resolved.append({"id": ident, "kind": claim["kind"], "text": claim["text"],
                         "evidence": evidence, "semantic_support": "not_verified"})
    return {"schema": RESOLUTION, "status": "candidate_unreviewed", "source": manifest["source"],
            "derivative": manifest["derivative"], "original_integrity": original_integrity,
            "claims": resolved, "admitted": False, "provider_calls": 0}


def resolve_bundle(exchanges, candidate):
    """Resolve a relation over independently pinned sources, without adjudication."""
    if type(exchanges) is not list or not 2 <= len(exchanges) <= 8:
        raise SourceError("invalid_exchange_count")
    indexed = {}
    sources = []
    for derived_path, manifest_raw, manifest, original_path in exchanges:
        manifest_sha = digest(manifest_raw)
        if manifest_sha in indexed:
            raise SourceError("duplicate_manifest")
        segments, data, integrity = validate_exchange(derived_path, manifest, original_path)
        indexed[manifest_sha] = (manifest, segments, data)
        sources.append({"manifest_sha256": manifest_sha, "source": manifest["source"],
                        "derivative": manifest["derivative"], "original_integrity": integrity})
    _object(candidate, ("schema", "manifest_sha256s", "claims"), "invalid_bundle_candidate_shape")
    if candidate["schema"] != BUNDLE_CANDIDATE:
        raise SourceError("unsupported_bundle_candidate_schema")
    if candidate["manifest_sha256s"] != list(indexed):
        raise SourceError("bundle_manifest_mismatch")
    claims = candidate["claims"]
    if type(claims) is not list or not 1 <= len(claims) <= 64:
        raise SourceError("invalid_claims")
    resolved = []
    seen = set()
    for claim in claims:
        _object_variant(claim,
                        ({"id", "kind", "text", "evidence_refs"},
                         {"id", "kind", "text", "evidence_refs", "relation"}),
                        "invalid_claim_shape")
        ident = _label(claim["id"], "invalid_claim_id", 100)
        if ident in seen:
            raise SourceError("duplicate_claim_id")
        seen.add(ident)
        if claim["kind"] != "relation_candidate":
            raise SourceError("invalid_bundle_claim_kind")
        _label(claim["text"], "invalid_claim_text", 4000)
        refs = claim["evidence_refs"]
        if type(refs) is not list or not 2 <= len(refs) <= 16:
            raise SourceError("invalid_evidence_refs")
        evidence = []
        used = set()
        used_sources = set()
        for ref in refs:
            _object(ref, ("manifest_sha256", "segment_id", "start_byte", "end_byte"),
                    "invalid_evidence_ref")
            _hash(ref["manifest_sha256"], "invalid_manifest_sha256")
            _label(ref["segment_id"], "invalid_segment_id", 100)
            entry = indexed.get(ref["manifest_sha256"])
            if entry is None:
                raise SourceError("unknown_manifest_sha256")
            manifest, segments, data = entry
            segment = segments.get(ref["segment_id"])
            if segment is None:
                raise SourceError("unknown_segment_id")
            start = _positive_int(ref["start_byte"], "invalid_evidence_range")
            end = _positive_int(ref["end_byte"], "invalid_evidence_range")
            if not segment["start_byte"] <= start < end <= segment["end_byte"]:
                raise SourceError("evidence_outside_segment")
            key = (ref["manifest_sha256"], ref["segment_id"], start, end)
            if key in used:
                raise SourceError("duplicate_evidence_ref")
            used.add(key)
            used_sources.add(manifest["source"]["sha256"])
            evidence.append(_resolved_evidence(manifest, segment, start, end, data[start:end],
                                               ref["manifest_sha256"]))
        if len(used_sources) < 2:
            raise SourceError("relation_requires_multiple_sources")
        relation = claim.get("relation")
        if relation is not None:
            relation = _relation(relation, {key: value[0] for key, value in indexed.items()}, evidence)
        resolved_claim = {"id": ident, "kind": "relation_candidate", "text": claim["text"],
                          "evidence": evidence, "semantic_support": "not_verified"}
        if relation is not None:
            resolved_claim["relation"] = relation
        resolved.append(resolved_claim)
    return {"schema": BUNDLE_RESOLUTION, "status": "candidate_unreviewed",
            "sources": sources, "claims": resolved, "admitted": False, "provider_calls": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("validate", "resolve", "resolve-bundle"))
    parser.add_argument("--derived", type=Path, action="append", required=True)
    parser.add_argument("--manifest", type=Path, action="append", required=True)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--original", type=Path, action="append")
    args = parser.parse_args()
    if (args.action != "validate") != (args.candidate is not None):
        parser.error("--candidate is required for resolve actions only")
    count = len(args.derived)
    if len(args.manifest) != count or (args.original and len(args.original) != count):
        parser.error("--derived, --manifest and supplied --original counts must match")
    if (args.action == "resolve-bundle" and not 2 <= count <= 8) or (
            args.action != "resolve-bundle" and count != 1):
        parser.error("resolve-bundle requires 2-8 exchanges; other actions require one")
    try:
        exchanges = []
        for index in range(count):
            manifest_raw, manifest = _read_json(args.manifest[index], MAX_MANIFEST)
            original = args.original[index] if args.original else None
            exchanges.append((args.derived[index], manifest_raw, manifest, original))
        if args.action == "validate":
            by_id, _, integrity = validate_exchange(exchanges[0][0], exchanges[0][2], exchanges[0][3])
            result = {"schema": EXCHANGE, "status": "valid", "segments": len(by_id),
                      "original_integrity": integrity, "provider_calls": 0}
        else:
            _, candidate = _read_json(args.candidate, MAX_CANDIDATE)
            result = (resolve_bundle(exchanges, candidate) if args.action == "resolve-bundle" else
                      resolve(*exchanges[0][:3], candidate, exchanges[0][3]))
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, SourceError) as exc:
        print(json.dumps({"status": "rejected", "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
