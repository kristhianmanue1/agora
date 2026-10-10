"""Create and verify a blinded retrospective adjudication packet; no model calls."""
import argparse
import csv
import hashlib
import json
import secrets
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))
from agora.qasper import render  # noqa: E402

T0 = ROOT / "experiments/evidence-answer-flow-t0-v1/runs/run-2026-10-10-glm-paired-02-llavero"
JEV03 = ROOT / "experiments/jev-case-03-review-v1"
HELDOUT = ROOT / "experiments/jev-heldout-qasper-v1"
SELECTION = [(f"case-{n:02d}", arm) for n, arm in ((1,"A"),(1,"B"),(2,"A"),(2,"B"),(3,"A"),(4,"A"),(4,"B"),(5,"A"),(5,"B"),(6,"A"))]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def data(path):
    raw = path.read_bytes()
    return json.loads(raw), sha(raw)


def limitations(value):
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, list) and all(isinstance(v, str) for v in value):
        return [v for v in value if v.strip()]
    raise ValueError("invalid_limitations")


def inputs():
    t0_freeze, _ = data(ROOT / "experiments/evidence-answer-flow-t0-v1/freeze.json")
    case_specs = {c["id"]: c for c in t0_freeze["cases"]}
    rows = []
    for case_id, arm in SELECTION:
        spec = case_specs[case_id]
        case_dir = T0 / case_id
        source = (case_dir / "source.txt").read_bytes()
        if sha(source) != spec["source_sha256"]:
            raise ValueError("source_mismatch:" + case_id)
        result, result_sha = data(case_dir / arm / "result.json")
        if result["source_sha256"] != spec["source_sha256"]:
            raise ValueError("result_source_mismatch:" + case_id)
        if arm == "A":
            if result["status"] != "candidate":
                raise ValueError("invalid_A:" + case_id)
            answer = result["answer"]
            status = "answered" if answer["status"] == "answered" else "abstained"
            claims = [c["text"] for c in answer["claims"]]
            missing = limitations(answer["missing"])
        else:
            if result["status"] not in ("candidate_reviewed", "review_incomplete"):
                raise ValueError("invalid_B:" + case_id)
            candidate_path = case_dir / arm / "candidate.json"
            candidate, candidate_sha = data(candidate_path)
            if candidate["source_sha256"] != spec["source_sha256"] or len(candidate["parts"]) != 1:
                raise ValueError("candidate_source_mismatch:" + case_id)
            part = candidate["parts"][0]
            if part["status"] not in ("answered", "not_in_passages"):
                raise ValueError("invalid_part_status:" + case_id)
            status = "answered" if part["status"] == "answered" else "abstained"
            claims = [c["text"] for c in part["claims"]]
            missing = limitations(part["missing"])
            result_sha += ":candidate=" + candidate_sha
        rows.append({
            "origin": "T0-" + case_id + "-" + arm,
            "origin_path": str((case_dir / arm / "result.json").relative_to(ROOT)),
            "origin_fingerprint": result_sha,
            "source_key": case_id,
            "source": source,
            "question": spec["question"],
            "requirements": spec["requirements"],
            "response_status": status,
            "claims": claims,
            "stated_limitations": missing,
            "kind": "spontaneous",
        })
    # A prior positive-negative pair tests whether the assessor sees an obvious omission.
    control, control_sha = data(JEV03 / "control-run-2026-10-10-01/control-candidate.json")
    case = case_specs["case-03"]
    source = (T0 / "case-03/source.txt").read_bytes()
    rows.append({
        "origin": "case-03-omission-control",
        "origin_path": "experiments/jev-case-03-review-v1/control-run-2026-10-10-01/control-candidate.json",
        "origin_fingerprint": control_sha,
        "source_key": "case-03",
        "source": source,
        "question": case["question"],
        "requirements": case["requirements"],
        "response_status": "answered",
        "claims": [c["text"] for c in control["claims"]],
        "stated_limitations": limitations(control["missing"]),
        "kind": "prepared_omission",
    })
    heldout, heldout_sha = data(HELDOUT / "freeze.json")
    hcase = next(c for c in heldout["cases"] if c["id"] == "datasets")
    variant = next(v for v in hcase["variants"] if v["id"] == "contradiction")
    dataset_path = ROOT / heldout["dataset"]
    dataset, dataset_sha = data(dataset_path)
    if dataset_sha != heldout["dataset_sha256"]:
        raise ValueError("dataset_mismatch")
    hsource, _ = render(dataset[hcase["document_id"]])
    if sha(hsource) != hcase["source_sha256"]:
        raise ValueError("heldout_source_mismatch")
    rows.append({
        "origin": "heldout-datasets-contradiction-control",
        "origin_path": "experiments/jev-heldout-qasper-v1/freeze.json",
        "origin_fingerprint": heldout_sha,
        "source_key": "heldout-datasets",
        "source": hsource,
        "question": hcase["question"],
        "requirements": hcase["requirements"],
        "response_status": "answered",
        "claims": [variant["answer"]],
        "stated_limitations": [],
        "kind": "prepared_contradiction",
    })
    if len(rows) != 12:
        raise ValueError("selection_count_mismatch")
    return rows


def blind_item(row, item_id, source_id):
    return {
        "schema": "agora/blind-adjudication-item/v1",
        "item_id": item_id,
        "source_file": "../sources/" + source_id + ".txt",
        "source_sha256": sha(row["source"]),
        "question": row["question"],
        "requirements": row["requirements"],
        "response_status": row["response_status"],
        "claims": row["claims"],
        "stated_limitations": row["stated_limitations"],
    }


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def create():
    if (HERE / "blind").exists() or (HERE / "sealed").exists():
        raise ValueError("packet_already_exists")
    rows = inputs()
    blind = HERE / "blind"
    items = blind / "items"
    sources = blind / "sources"
    sealed = HERE / "sealed"
    for path in (items, sources, sealed):
        path.mkdir(parents=True, exist_ok=False)
    rng = secrets.SystemRandom()
    source_ids = {k: "S-" + secrets.token_hex(4) for k in {r["source_key"] for r in rows}}
    entries = []
    for row in rows:
        source_id = source_ids[row["source_key"]]
        source_path = sources / (source_id + ".txt")
        if not source_path.exists():
            source_path.write_bytes(row["source"])
        elif source_path.read_bytes() != row["source"]:
            raise ValueError("source_collision")
        item_id = "J-" + secrets.token_hex(5)
        item = blind_item(row, item_id, source_id)
        item_path = items / (item_id + ".json")
        write_json(item_path, item)
        entries.append({
            "item_id": item_id,
            "source_id": source_id,
            "origin": row["origin"],
            "kind": row["kind"],
            "origin_path": row["origin_path"],
            "origin_fingerprint": row["origin_fingerprint"],
            "item_sha256": sha(item_path.read_bytes()),
            "source_sha256": sha(row["source"]),
        })
    rng.shuffle(entries)
    with (blind / "scorecard-template.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["item_id", "question_clarity", "support", "coverage", "support_evidence", "coverage_evidence", "material_omissions", "notes"])
        for entry in entries:
            writer.writerow([entry["item_id"], "", "", "", "", "", "", ""])
    write_json(sealed / "mapping.json", {
        "schema": "agora/blind-adjudication-mapping/v1",
        "scope": "retrospective; preparer knew earlier Jev results for some controls",
        "entries": entries,
    })
    return len(entries)


def verify():
    rows = {r["origin"]: r for r in inputs()}
    mapping, _ = data(HERE / "sealed/mapping.json")
    entries = mapping["entries"]
    if len(entries) != 12 or len({e["item_id"] for e in entries}) != 12 or len({e["source_id"] for e in entries}) != 7:
        raise ValueError("mapping_shape_mismatch")
    if {p.stem for p in (HERE / "blind/items").glob("*.json")} != {e["item_id"] for e in entries}:
        raise ValueError("item_inventory_mismatch")
    if {p.stem for p in (HERE / "blind/sources").glob("*.txt")} != {e["source_id"] for e in entries}:
        raise ValueError("source_inventory_mismatch")
    for entry in entries:
        row = rows[entry["origin"]]
        item_path = HERE / "blind/items" / (entry["item_id"] + ".json")
        source_path = HERE / "blind/sources" / (entry["source_id"] + ".txt")
        item, item_sha = data(item_path)
        if entry["origin_fingerprint"] != row["origin_fingerprint"] or entry["origin_path"] != row["origin_path"] or entry["kind"] != row["kind"]:
            raise ValueError("origin_mismatch:" + entry["item_id"])
        if item != blind_item(row, entry["item_id"], entry["source_id"]) or item_sha != entry["item_sha256"]:
            raise ValueError("item_mismatch:" + entry["item_id"])
        if source_path.read_bytes() != row["source"] or sha(row["source"]) != entry["source_sha256"]:
            raise ValueError("source_mismatch:" + entry["item_id"])
    with (HERE / "blind/scorecard-template.csv").open(newline="", encoding="utf-8") as stream:
        reader = list(csv.DictReader(stream))
    if [r["item_id"] for r in reader] != [e["item_id"] for e in entries] or any(any(v for k,v in r.items() if k != "item_id") for r in reader):
        raise ValueError("scorecard_mismatch")
    decision, _ = data(HERE / "sealed/decision-lock.json")
    sentinels = {e["item_id"]: e["origin"] for e in entries if e["kind"].startswith("prepared_")}
    if set(decision["sentinels"]) != set(sentinels) or len(sentinels) != 2:
        raise ValueError("sentinel_inventory_mismatch")
    expected = {
        "case-03-omission-control": {"support": "supported", "coverage": "omitted"},
        "heldout-datasets-contradiction-control": {"support": "unsupported", "coverage": "omitted"},
    }
    for item_id, origin in sentinels.items():
        if {k: decision["sentinels"][item_id][k] for k in ("support", "coverage")} != expected[origin]:
            raise ValueError("sentinel_label_mismatch")
    return {"items": len(entries), "sources": len({e["source_id"] for e in entries}), "blind_integrity": "verified"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("create", "verify"))
    args = parser.parse_args()
    print(json.dumps({"created": create()} if args.action == "create" else verify()))
