"""Convert a verified local Skopos page response into an Ágora exchange."""

import argparse
import json
from pathlib import Path
import sys

from .source import SourceError, digest
from .source_evidence_exchange import EXCHANGE, _read_json, _label, validate_exchange


def build(response, producer_raw, producer_manifest, item_ids):
    if (type(response) is not dict or response.get("status") != "ok" or
            response.get("operation") != "page" or type(response.get("result")) is not dict):
        raise SourceError("invalid_skopos_page_response")
    result = response["result"]
    parent = response.get("source")
    if (type(parent) is not dict or type(producer_manifest) is not dict or
            producer_manifest.get("schema") != "skopos/pdf-document-manifest/v0.1" or
            producer_manifest.get("parent") != parent):
        raise SourceError("skopos_source_mismatch")
    manifest_sha = digest(producer_raw)
    if (result.get("manifest_sha256") != manifest_sha or
            result.get("derivation_id") != producer_manifest.get("derivation_id")):
        raise SourceError("skopos_manifest_mismatch")
    page_number = result.get("page_number")
    modality = result.get("modality")
    if (type(page_number) is not int or page_number < 1 or
            modality not in ("native_text", "ocr_text") or result.get("status") != "extracted"):
        raise SourceError("invalid_skopos_page")
    page = next((page for page in producer_manifest.get("pages", [])
                 if page.get("page_number") == page_number), None)
    if (page is None or page[modality].get("status") != "extracted" or
            result.get("lines") != page[modality].get("lines")):
        raise SourceError("skopos_page_content_mismatch")
    if type(item_ids) is not list or not 1 <= len(item_ids) <= 64 or len(set(item_ids)) != len(item_ids):
        raise SourceError("invalid_item_ids")
    lines = {line["item_id"]: line for line in result["lines"]}
    if len(lines) != len(result["lines"]):
        raise SourceError("duplicate_skopos_item_id")
    data = bytearray()
    segments = []
    for index, item_id in enumerate(item_ids):
        _label(item_id, "invalid_item_id", 100)
        line = lines.get(item_id)
        if line is None:
            raise SourceError("unknown_skopos_item_id")
        text = _label(line.get("text"), "invalid_skopos_text", 8192)
        if index:
            data.extend(b"[omitted]\n")
        start = len(data)
        raw = (text + "\n").encode("utf-8")
        data.extend(raw)
        segments.append({"id": "skopos-item-" + str(index + 1), "start_byte": start,
                         "end_byte": len(data), "sha256": digest(raw),
                         "locator": {"kind": "pdf_page", "value": {
                             "page": page_number, "item_id": item_id, "bbox": line["bbox"]}},
                         "modality": modality, "extraction_status": "unreviewed"})
    if len(data) > 1024 * 1024:
        raise SourceError("derived_budget_exceeded")
    exchange = {"schema": EXCHANGE,
                "source": {"id": parent["material_id"], "sha256": parent["source_sha256"],
                           "media_type": "application/pdf", "revision": str(parent["source_revision"]),
                           "uri": response.get("source_url")},
                "derivative": {"id": "skopos-page-" + str(page_number) + "-selection",
                               "sha256": digest(data), "coverage": "partial",
                               "producer": {"system": "skopos", "version": producer_manifest["contract_version"],
                                            "manifest_sha256": manifest_sha,
                                            "derivation_id": result["derivation_id"]}},
                "segments": segments}
    return bytes(data), exchange


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--response", type=Path, required=True)
    parser.add_argument("--producer-manifest", type=Path, required=True)
    parser.add_argument("--item-id", action="append", required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        _, response = _read_json(args.response, 4 * 1024 * 1024)
        raw, producer_manifest = _read_json(args.producer_manifest, 8 * 1024 * 1024)
        data, exchange = build(response, raw, producer_manifest, args.item_id)
        args.out_dir.mkdir(parents=True, exist_ok=False)
        (args.out_dir / "derived.txt").write_bytes(data)
        manifest_path = args.out_dir / "exchange.json"
        manifest_path.write_text(json.dumps(exchange, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
        validate_exchange(args.out_dir / "derived.txt", exchange)
        print(json.dumps({"status": "created", "derived_sha256": digest(data),
                          "exchange_sha256": digest(manifest_path.read_bytes()),
                          "segments": len(exchange["segments"]), "provider_calls": 0}))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "rejected", "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
