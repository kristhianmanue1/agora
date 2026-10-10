"""Export only the verified blind packet; never include sealed mapping."""
import hashlib
import json
import zipfile
from pathlib import Path

import build


HERE = Path(__file__).resolve().parent
BLIND = HERE / "blind"
EXPORTS = HERE / "exports"
ARCHIVE = EXPORTS / "jev-adjudication-v1-blind.zip"
RECEIPT = EXPORTS / "jev-adjudication-v1-blind-receipt.json"


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    verified = build.verify()
    files = sorted(p for p in BLIND.rglob("*") if p.is_file())
    expected = {BLIND / "INSTRUCTIONS.md", BLIND / "scorecard-template.csv"}
    expected.update((BLIND / "items").glob("*.json"))
    expected.update((BLIND / "sources").glob("*.txt"))
    if set(files) != expected or len(files) != 21:
        raise ValueError("unexpected_blind_inventory")
    if any(p.is_symlink() or not p.resolve().is_relative_to(BLIND.resolve()) for p in files):
        raise ValueError("unsafe_blind_file")
    EXPORTS.mkdir(exist_ok=True)
    if ARCHIVE.exists() or RECEIPT.exists():
        raise ValueError("export_already_exists")
    entries = {}
    with zipfile.ZipFile(ARCHIVE, mode="x", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            name = "blind/" + str(path.relative_to(BLIND))
            raw = path.read_bytes()
            entries[name] = digest(raw)
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 10, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, raw)
    with zipfile.ZipFile(ARCHIVE) as archive:
        if set(archive.namelist()) != set(entries):
            raise ValueError("archive_inventory_mismatch")
        if any(digest(archive.read(name)) != expected_sha for name, expected_sha in entries.items()):
            raise ValueError("archive_content_mismatch")
    receipt = {
        "schema": "agora/blind-packet-export/v1",
        "archive": str(ARCHIVE.relative_to(HERE)),
        "archive_sha256": digest(ARCHIVE.read_bytes()),
        "files": len(entries),
        "items": verified["items"],
        "sources": verified["sources"],
        "entry_sha256": entries,
        "contains_sealed_material": False,
        "delivery": "not_performed",
    }
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: receipt[k] for k in ("archive", "archive_sha256", "files", "items", "sources", "delivery")}))


if __name__ == "__main__":
    main()
