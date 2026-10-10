"""Build a page-local Ágora exchange from a verified Skopos CTIM v0.2 reply."""

import argparse
import json
from pathlib import Path
import sys

from .source import SourceError, digest
from .source_evidence_exchange import EXCHANGE, _label, _read_json, validate_exchange


def _canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def build(request, response, manifest_raw, manifest, original_raw, item_ids,
          expected_manifest_sha256):
    if (type(expected_manifest_sha256) is not str or
            digest(manifest_raw) != expected_manifest_sha256):
        raise SourceError("skopos_manifest_hash_mismatch")
    if (type(request) is not dict or set(request) !=
            {"request_id", "operation", "source_id", "page_number"} or
            request.get("operation") != "read_pdf_page" or
            type(request.get("page_number")) is not int or request["page_number"] < 1):
        raise SourceError("invalid_skopos_request")
    if (type(response) is not dict or response.get("schema") !=
            "skopos/ctim-source-access/v0.2" or response.get("status") != "ok" or
            response.get("error") is not None or type(response.get("result")) is not dict or
            response.get("request_id") != request["request_id"] or
            response.get("request_sha256") != digest(_canonical(request)) or
            type(response.get("policy_sha256")) is not str or
            len(response["policy_sha256"]) != 64):
        raise SourceError("invalid_skopos_page_response")
    if (type(manifest) is not dict or manifest.get("schema") !=
            "skopos/pdf-document-manifest/v0.1" or type(manifest.get("parent")) is not dict):
        raise SourceError("invalid_skopos_manifest")
    parent = manifest["parent"]
    result = response["result"]
    if (parent.get("material_id") != request["source_id"] or
            parent.get("source_sha256") != digest(original_raw) or
            result.get("source_id") != request["source_id"] or
            result.get("source_sha256") != digest(original_raw) or
            result.get("media_type") != "application/pdf" or
            result.get("page_number") != request["page_number"] or
            result.get("line_order") != "manifest_extraction_order" or
            result.get("fidelity_status") != "unreviewed"):
        raise SourceError("skopos_source_mismatch")
    pages = manifest.get("pages")
    if (type(pages) is not list or not 1 <= request["page_number"] <= len(pages) or
            result.get("page_count") != len(pages)):
        raise SourceError("skopos_page_mismatch")
    page = pages[request["page_number"] - 1]
    compared = ("page_number", "page_width_points", "page_height_points",
                "page_rotation", "native_text", "ocr_text")
    if any(result.get(key) != page.get(key) for key in compared):
        raise SourceError("skopos_page_content_mismatch")
    modality = "native_text"
    block = result[modality]
    lines = block.get("lines") if type(block) is dict else None
    if type(block) is not dict or block.get("status") != "extracted" or type(lines) is not list:
        raise SourceError("skopos_native_text_unavailable")
    if (type(item_ids) is not list or not 1 <= len(item_ids) <= 64 or
            len(set(item_ids)) != len(item_ids)):
        raise SourceError("invalid_item_ids")
    by_id = {line["item_id"]: line for line in lines}
    if len(by_id) != len(lines):
        raise SourceError("duplicate_skopos_item_id")
    data = bytearray()
    segments = []
    for index, item_id in enumerate(item_ids):
        _label(item_id, "invalid_item_id", 100)
        line = by_id.get(item_id)
        if line is None:
            raise SourceError("unknown_skopos_item_id")
        if index:
            data.extend(b"[omitted]\n")
        start = len(data)
        raw = (_label(line.get("text"), "invalid_skopos_text", 8192) + "\n").encode()
        data.extend(raw)
        segments.append({"id": "skopos-item-" + str(index + 1),
                         "start_byte": start, "end_byte": len(data), "sha256": digest(raw),
                         "locator": {"kind": "pdf_page", "value": {
                             "page": request["page_number"], "item_id": item_id,
                             "bbox": line["bbox"]}}, "modality": modality,
                         "extraction_status": "unreviewed"})
    if len(data) > 1024 * 1024:
        raise SourceError("derived_budget_exceeded")
    exchange = {"schema": EXCHANGE,
                "source": {"id": request["source_id"], "sha256": digest(original_raw),
                           "media_type": "application/pdf",
                           "revision": str(parent["source_revision"]), "uri": None},
                "derivative": {"id": "skopos-v02-page-" + str(request["page_number"]),
                               "sha256": digest(data), "coverage": "partial",
                               "producer": {"system": "skopos", "version": "v0.2",
                                            "manifest_sha256": digest(manifest_raw),
                                            "derivation_id": manifest["derivation_id"]}},
                "segments": segments}
    return bytes(data), exchange


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--response", required=True, type=Path)
    parser.add_argument("--producer-manifest", required=True, type=Path)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--original", required=True, type=Path)
    parser.add_argument("--item-id", required=True, action="append")
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        _, request = _read_json(args.request, 4096)
        _, response = _read_json(args.response, 65536)
        manifest_raw, manifest = _read_json(args.producer_manifest, 8 * 1024 * 1024)
        if args.original.stat().st_size > 64 * 1024 * 1024:
            raise SourceError("original_budget_exceeded")
        original_raw = args.original.read_bytes()
        data, exchange = build(request, response, manifest_raw, manifest,
                               original_raw, args.item_id, args.manifest_sha256)
        args.out_dir.mkdir(mode=0o700, parents=False, exist_ok=False)
        derived = args.out_dir / "derived.txt"
        derived.write_bytes(data)
        manifest_path = args.out_dir / "exchange.json"
        manifest_path.write_text(json.dumps(exchange, ensure_ascii=False,
                                            sort_keys=True, indent=2) + "\n")
        validate_exchange(derived, exchange, args.original)
        print(json.dumps({"status": "created", "derived_sha256": digest(data),
                          "exchange_sha256": digest(manifest_path.read_bytes()),
                          "segments": len(exchange["segments"]), "provider_calls": 0}))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "rejected", "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
