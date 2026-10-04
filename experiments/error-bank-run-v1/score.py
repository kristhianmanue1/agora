#!/usr/bin/env python3
"""error-bank-run-v1: puntúa los recibos de Jev contra las etiquetas esperadas.

Umbral de promoción (README de error-bank-v1):
  1. >= 23/24 etiquetas de eje correctas en cada orden (12 controles x 2 ejes).
  2. Cero fallos en la celda supported+omitted en ambos órdenes.
  3. Los cinco gemelos supported+complete aceptados en ambos órdenes.
Superar el umbral no promociona a Jev automáticamente.
"""
import hashlib
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
BANK = BASE.parent / "error-bank-v1"
STAGING = Path("/tmp/aria-error-bank-v1")
ORDERS = {"directo": [0, 1], "inverso": [2, 3]}


def main():
    controls_blob = (BANK / "controls.json").read_bytes()
    controls = json.loads(controls_blob)
    freeze = json.loads((BANK / "freeze.json").read_text())
    assert hashlib.sha256(controls_blob).hexdigest() == freeze["controls_sha256"]
    by_id = {c["id"]: c for c in controls}

    per_order = {}
    detail = []
    for order, call_ids in ORDERS.items():
        labels = {}
        for i in call_ids:
            result = json.loads((STAGING / f"jev-{i}-result.json").read_text())
            assert result.get("status") == 200, f"llamada {i} sin HTTP 200"
            for key_axis, verdict in result["response"]["answers"].items():
                cid, axis = key_axis.rsplit("_", 1)
                labels.setdefault(cid, {})[axis] = verdict.get("choice")
        per_order[order] = labels
        for cid, got in labels.items():
            detail.append({
                "id": cid,
                "family": by_id[cid]["family"],
                "variant": by_id[cid]["variant"],
                "order": order,
                "expected_support": by_id[cid]["expected_support"],
                "got_support": got.get("backing"),
                "expected_coverage": by_id[cid]["expected_coverage"],
                "got_coverage": got.get("coverage"),
                "support_ok": got.get("backing") == by_id[cid]["expected_support"],
                "coverage_ok": got.get("coverage") == by_id[cid]["expected_coverage"],
            })

    summary = {}
    gate_all = True
    for order, labels in per_order.items():
        rows = [d for d in detail if d["order"] == order]
        axis_ok = sum(r["support_ok"] for r in rows) + sum(r["coverage_ok"] for r in rows)
        cell_ok = all(
            r["support_ok"] and r["coverage_ok"]
            for r in rows
            if r["expected_support"] == "supported" and r["expected_coverage"] == "omitted"
        )
        twins_ok = all(
            r["support_ok"] and r["coverage_ok"] and r["got_support"] == "supported"
            and r["got_coverage"] == "complete"
            for r in rows
            if r["variant"] == "control" and r["expected_support"] == "supported"
            and r["expected_coverage"] == "complete"
        )
        g1, g2, g3 = axis_ok >= 23, cell_ok, twins_ok
        gate_all = gate_all and g1 and g2 and g3
        summary[order] = {
            "axis_labels_correct": f"{axis_ok}/24",
            "supported_omitted_cell_clean": cell_ok,
            "complete_twins_accepted": twins_ok,
            "gate_pass": g1 and g2 and g3,
        }

    out = {"summary": summary, "gate_overall": gate_all, "detail": detail}
    (BASE / "result.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("gate_overall:", gate_all)
    return 0


if __name__ == "__main__":
    sys.exit(main())
