"""The CTIM v0.2 bridge rejects changed provenance and geometry."""

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from agora.skopos_page_v02_bridge import build, main
from agora.source import SourceError
from agora.source_evidence_exchange import validate_exchange


def fixture():
    original = b"%PDF-1.4\nexample\n"
    sha = hashlib.sha256(original).hexdigest()
    item_id = "b" * 64
    line = {"item_id": item_id, "text": "CTIM revisa el anteproyecto",
            "bbox": [0.1, 0.2, 0.8, 0.3]}
    parent = {"material_id": "ctim", "source_revision": 1, "source_sha256": sha}
    page = {"page_number": 1, "page_width_points": 612.0,
            "page_height_points": 792.0, "page_rotation": 0,
            "native_text": {"status": "extracted", "lines": [line]},
            "ocr_text": {"status": "not_run", "lines": []}}
    manifest = {"schema": "skopos/pdf-document-manifest/v0.1",
                "contract_version": "v0.1", "derivation_id": "c" * 64,
                "parent": parent, "pages": [page]}
    raw = json.dumps(manifest).encode()
    request = {"request_id": "p1", "operation": "read_pdf_page",
               "source_id": "ctim", "page_number": 1}
    request_sha = hashlib.sha256(json.dumps(request, ensure_ascii=False,
                         sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    response = {"schema": "skopos/ctim-source-access/v0.2", "status": "ok",
                "error": None, "request_id": "p1", "request_sha256": request_sha,
                "policy_sha256": "d" * 64,
                "result": {"source_id": "ctim", "source_sha256": sha,
                           "media_type": "application/pdf", "page_count": 1,
                           "fidelity_status": "unreviewed",
                           "line_order": "manifest_extraction_order", **page}}
    return request, response, raw, manifest, original, item_id


class SkoposPageV02BridgeTests(unittest.TestCase):
    def test_cli_writes_valid_exchange_from_pinned_manifest(self):
        request, response, raw, _, original, item_id = fixture()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "request.json").write_text(json.dumps(request))
            (root / "response.json").write_text(json.dumps(response))
            (root / "manifest.json").write_bytes(raw)
            (root / "original.pdf").write_bytes(original)
            out = root / "output"
            args = ["--request", str(root / "request.json"),
                    "--response", str(root / "response.json"),
                    "--producer-manifest", str(root / "manifest.json"),
                    "--manifest-sha256", hashlib.sha256(raw).hexdigest(),
                    "--original", str(root / "original.pdf"),
                    "--item-id", item_id, "--out-dir", str(out)]
            self.assertEqual(main(args), 0)
            exchange = json.loads((out / "exchange.json").read_bytes())
            self.assertEqual(validate_exchange(out / "derived.txt", exchange,
                                               root / "original.pdf")[2],
                             "sha256_verified")

    def test_positive_and_changed_response_controls(self):
        request, response, raw, manifest, original, item_id = fixture()
        expected = hashlib.sha256(raw).hexdigest()
        data, exchange = build(request, response, raw, manifest, original,
                               [item_id], expected)
        self.assertEqual(data.decode(), "CTIM revisa el anteproyecto\n")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "derived.txt").write_bytes(data)
            (root / "original.pdf").write_bytes(original)
            _, _, integrity = validate_exchange(root / "derived.txt", exchange,
                                                root / "original.pdf")
            self.assertEqual(integrity, "sha256_verified")
        for field, value in (("page_number", 2), ("page_rotation", 90),
                             ("page_width_points", 600.0)):
            changed = copy.deepcopy(response)
            changed["result"][field] = value
            with self.subTest(field=field), self.assertRaises(SourceError):
                build(request, changed, raw, manifest, original, [item_id], expected)
        for key, value in (("text", "altered"), ("bbox", [0, 0, 1, 1])):
            changed = copy.deepcopy(response)
            changed["result"]["native_text"]["lines"][0][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(
                    SourceError, "skopos_page_content_mismatch"):
                build(request, changed, raw, manifest, original, [item_id], expected)
        changed = copy.deepcopy(response)
        changed["request_sha256"] = "0" * 64
        with self.assertRaisesRegex(SourceError, "invalid_skopos_page_response"):
            build(request, changed, raw, manifest, original, [item_id], expected)
        with self.assertRaisesRegex(SourceError, "skopos_source_mismatch"):
            build(request, response, raw, manifest, b"different", [item_id], expected)
        with self.assertRaisesRegex(SourceError, "skopos_manifest_hash_mismatch"):
            build(request, response, raw, manifest, original, [item_id], "0" * 64)


if __name__ == "__main__":
    unittest.main()
