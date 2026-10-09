"""No-runtime checks for the optional Skopos page response bridge."""

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from agora.source import SourceError
from agora.skopos_page_bridge import build
from agora.source_evidence_exchange import validate_exchange


def fixture():
    parent = {"material_id": "example-document", "source_revision": 1,
              "source_sha256": "a" * 64}
    line = {"item_id": "b" * 64, "text": "Área de prueba",
            "bbox": [0.1, 0.2, 0.8, 0.3]}
    producer = {"schema": "skopos/pdf-document-manifest/v0.1",
                "contract_version": "v0.1", "derivation_id": "c" * 64,
                "parent": parent, "pages": [{"page_number": 3,
                "native_text": {"status": "extracted", "lines": [line]}}]}
    raw = json.dumps(producer, sort_keys=True).encode()
    response = {"status": "ok", "operation": "page", "source": parent,
                "source_url": "https://example.invalid/document.pdf",
                "result": {"page_number": 3, "modality": "native_text", "status": "extracted",
                           "lines": [line], "derivation_id": "c" * 64,
                           "manifest_sha256": hashlib.sha256(raw).hexdigest()}}
    return response, raw, producer, line


class SkoposPageBridgeTests(unittest.TestCase):
    def test_selected_real_shape_preserves_item_page_bbox_and_producer(self):
        response, raw, producer, line = fixture()
        data, exchange = build(response, raw, producer, [line["item_id"]])
        self.assertEqual(data.decode(), "Área de prueba\n")
        self.assertEqual(exchange["source"]["sha256"], "a" * 64)
        self.assertEqual(exchange["derivative"]["producer"]["manifest_sha256"],
                         hashlib.sha256(raw).hexdigest())
        segment = exchange["segments"][0]
        self.assertEqual(segment["locator"]["value"],
                         {"page": 3, "item_id": "b" * 64, "bbox": [0.1, 0.2, 0.8, 0.3]})
        self.assertEqual(segment["modality"], "native_text")
        self.assertEqual(segment["extraction_status"], "unreviewed")

    def test_changed_page_and_manifest_are_rejected(self):
        response, raw, producer, line = fixture()
        wrong = copy.deepcopy(response)
        wrong["result"]["lines"][0]["text"] = "cambiado"
        with self.assertRaisesRegex(SourceError, "skopos_page_content_mismatch"):
            build(wrong, raw, producer, [line["item_id"]])
        wrong = copy.deepcopy(response)
        wrong["result"]["manifest_sha256"] = "0" * 64
        with self.assertRaisesRegex(SourceError, "skopos_manifest_mismatch"):
            build(wrong, raw, producer, [line["item_id"]])

    def test_cli_writes_new_exchange_that_validates(self):
        response, raw, _, line = fixture()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "response.json").write_text(json.dumps(response))
            (root / "producer.json").write_bytes(raw)
            out = root / "exchange"
            command = [sys.executable, "-m", "agora.skopos_page_bridge",
                       "--response", str(root / "response.json"),
                       "--producer-manifest", str(root / "producer.json"),
                       "--item-id", line["item_id"], "--out-dir", str(out)]
            run = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            exchange = json.loads((out / "exchange.json").read_bytes())
            segments, _, integrity = validate_exchange(out / "derived.txt", exchange)
            self.assertEqual(len(segments), 1)
            self.assertEqual(integrity, "not_checked")
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)


if __name__ == "__main__":
    unittest.main()
