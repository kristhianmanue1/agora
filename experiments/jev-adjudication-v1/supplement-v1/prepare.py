"""Create a four-item blind supplement for Jev's two disputed omissions."""
import csv
import hashlib
import json
import secrets
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "src"))
from agora.qasper import render  # noqa: E402


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def write(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def source_rows():
    heldout = json.loads((ROOT / "experiments/jev-heldout-qasper-v1/freeze.json").read_text())
    raw = (ROOT / heldout["dataset"]).read_bytes()
    if sha(raw) != heldout["dataset_sha256"]:
        raise ValueError("dataset_changed")
    dataset = json.loads(raw)
    rows = []
    for case in heldout["cases"]:
        source, _ = render(dataset[case["document_id"]])
        if sha(source) != case["source_sha256"]:
            raise ValueError("source_changed")
        for variant in case["variants"]:
            if variant["id"] not in ("complete", "omission"):
                continue
            rows.append((case, variant, source))
    if len(rows) != 4:
        raise ValueError("case_count")
    return rows


def create():
    if (HERE / "blind").exists() or (HERE / "sealed").exists() or (HERE / "blind.zip").exists():
        raise ValueError("already_created")
    rows = source_rows()
    items = HERE / "blind/items"
    sources = HERE / "blind/sources"
    sealed = HERE / "sealed"
    for path in (items, sources, sealed):
        path.mkdir(parents=True, exist_ok=False)
    (HERE / "blind/INSTRUCTIONS.md").write_text((HERE.parent / "blind/INSTRUCTIONS.md").read_text().replace("12 fichas", "4 fichas"))
    source_ids = {c["id"]: "S-" + secrets.token_hex(4) for c, _, _ in rows}
    mapping = []
    for case, variant, source in rows:
        sid = source_ids[case["id"]]
        source_path = sources / (sid + ".txt")
        if not source_path.exists():
            source_path.write_bytes(source)
        iid = "J-" + secrets.token_hex(5)
        item = {
            "schema": "agora/blind-adjudication-item/v1",
            "item_id": iid,
            "source_file": "../sources/" + sid + ".txt",
            "source_sha256": sha(source),
            "question": case["question"],
            "requirements": case["requirements"],
            "response_status": "answered",
            "claims": [variant["answer"]],
            "stated_limitations": [],
        }
        item_path = items / (iid + ".json")
        write(item_path, item)
        mapping.append({"item_id": iid, "source_id": sid, "case": case["id"], "variant": variant["id"], "expected": variant["expected"], "item_sha256": sha(item_path.read_bytes()), "source_sha256": sha(source)})
    secrets.SystemRandom().shuffle(mapping)
    with (HERE / "blind/scorecard-template.csv").open("w", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["item_id", "question_clarity", "support", "coverage", "support_evidence", "coverage_evidence", "material_omissions", "notes"])
        for row in mapping:
            writer.writerow([row["item_id"], "", "", "", "", "", "", ""])
    write(sealed / "mapping.json", {"schema": "agora/jev-disputed-omission-supplement/v1", "entries": mapping})
    with zipfile.ZipFile(HERE / "blind.zip", "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted((HERE / "blind").rglob("*")):
            if path.is_file():
                archive.write(path, "blind/" + str(path.relative_to(HERE / "blind")))
    return verify()


def verify():
    rows = source_rows()
    mapping = json.loads((HERE / "sealed/mapping.json").read_text())["entries"]
    if len(mapping) != 4 or len({r["item_id"] for r in mapping}) != 4:
        raise ValueError("mapping_mismatch")
    originals = {(c["id"], v["id"]): (c, v, source) for c, v, source in rows}
    for row in mapping:
        c, v, source = originals[(row["case"], row["variant"])]
        item_path = HERE / "blind/items" / (row["item_id"] + ".json")
        item = json.loads(item_path.read_text())
        if sha(item_path.read_bytes()) != row["item_sha256"] or item["claims"] != [v["answer"]] or item["source_sha256"] != sha(source):
            raise ValueError("item_changed")
        if (HERE / "blind/sources" / (row["source_id"] + ".txt")).read_bytes() != source:
            raise ValueError("source_changed")
    with zipfile.ZipFile(HERE / "blind.zip") as archive:
        actual = {n: sha(archive.read(n)) for n in archive.namelist()}
    expected = {"blind/" + str(p.relative_to(HERE / "blind")): sha(p.read_bytes()) for p in (HERE / "blind").rglob("*") if p.is_file()}
    if actual != expected or len(actual) != 8 or any("sealed" in n for n in actual):
        raise ValueError("archive_mismatch")
    return {"items": 4, "sources": 2, "archive_sha256": sha((HERE / "blind.zip").read_bytes()), "files": 8}


if __name__ == "__main__":
    print(json.dumps(create() if len(sys.argv) > 1 and sys.argv[1] == "create" else verify()))
