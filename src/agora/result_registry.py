"""Register and retrieve evidence answer flow results by stable identifier.

The registry is a small append-only index: it never rewrites run directories,
never dispatches providers and never admits candidates. Retrieval revalidates
the recorded result.json hash and fails closed on drift, so a moved or edited
run is reported instead of silently served. Inspection of an incomplete run
stays offline: replay belongs to the flow's own --replay-run contract.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

REGISTRY_SCHEMA = "agora/result-registry/v1"
ENTRY_SCHEMA = "agora/result-registry-entry/v1"
SUPPORTED_RESULT_SCHEMAS = (
    "agora/evidence-answer-flow/v1-experimental",
    "agora/evidence-answer-flow/v2-experimental",
)


class RegistryError(ValueError):
    """Raised with a stable code; never carries file contents."""


def _sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load(path):
    path = Path(path)
    if not path.is_file():
        raise RegistryError("registry_not_found")
    try:
        registry = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError):
        raise RegistryError("invalid_registry_json") from None
    if (type(registry) is not dict or registry.get("schema") != REGISTRY_SCHEMA
            or type(registry.get("entries")) is not list):
        raise RegistryError("invalid_registry_shape")
    for entry in registry["entries"]:
        if (type(entry) is not dict or entry.get("schema") != ENTRY_SCHEMA
                or type(entry.get("id")) is not str
                or type(entry.get("path")) is not str
                or type(entry.get("result_sha256")) is not str
                or entry.get("result_schema") not in SUPPORTED_RESULT_SCHEMAS
                or type(entry.get("status")) is not str):
            raise RegistryError("invalid_registry_entry")
    return registry


def _save(path, registry):
    path = Path(path)
    if path.exists() and not path.is_file():
        raise RegistryError("registry_path_not_a_file")
    path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")


def _next_id(entries):
    highest = 0
    for entry in entries:
        try:
            highest = max(highest, int(entry["id"].rsplit("-", 1)[1]))
        except (IndexError, ValueError):
            raise RegistryError("invalid_registry_entry_id") from None
    return f"r-{highest + 1:04d}"


def register(registry_path, run_dir):
    """Index a finished or interrupted run directory under a fresh id."""
    run_dir = Path(run_dir)
    result_path = run_dir / "result.json"
    if not result_path.is_file():
        raise RegistryError("result_json_not_found")
    try:
        result = json.loads(result_path.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError):
        raise RegistryError("invalid_result_json") from None
    if type(result) is not dict or result.get("schema") not in SUPPORTED_RESULT_SCHEMAS:
        raise RegistryError("unsupported_result_schema")
    for field in ("status", "source_id", "source_sha256", "question", "dispatches"):
        if type(result.get(field)) not in (str, int):
            raise RegistryError("invalid_result_field")
    result_sha = _sha256_file(result_path)
    registry = _load(registry_path) if Path(registry_path).is_file() else {
        "schema": REGISTRY_SCHEMA, "entries": []}
    for entry in registry["entries"]:
        if entry["result_sha256"] == result_sha:
            raise RegistryError("result_already_registered")
    entry = {"schema": ENTRY_SCHEMA, "id": _next_id(registry["entries"]),
             "path": str(run_dir.resolve()), "result_sha256": result_sha,
             "result_schema": result["schema"], "status": result["status"],
             "source_id": result["source_id"],
             "source_sha256": result["source_sha256"],
             "question": result["question"], "dispatches": result["dispatches"],
             "retrieval": "revalidates_result_sha256"}
    registry["entries"].append(entry)
    _save(registry_path, registry)
    return entry


def get(registry_path, result_id):
    """Resolve an id to its manifest, failing closed on any drift."""
    registry = _load(registry_path)
    for entry in registry["entries"]:
        if entry["id"] == result_id:
            result_path = Path(entry["path"]) / "result.json"
            if not result_path.is_file():
                raise RegistryError("result_file_missing")
            if _sha256_file(result_path) != entry["result_sha256"]:
                raise RegistryError("result_drift")
            manifest = json.loads(result_path.read_text(encoding="utf-8"))
            return {"entry": entry, "manifest": manifest,
                    "replay": ["--replay-run", entry["path"]],
                    "admission": "not_performed"}
    raise RegistryError("unknown_result_id")


def list_entries(registry_path):
    registry = _load(registry_path) if Path(registry_path).is_file() else {
        "schema": REGISTRY_SCHEMA, "entries": []}
    return {"schema": REGISTRY_SCHEMA,
            "count": len(registry["entries"]),
            "entries": [{"id": entry["id"], "status": entry["status"],
                         "source_id": entry["source_id"],
                         "dispatches": entry["dispatches"]}
                        for entry in registry["entries"]]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    register_parser = sub.add_parser("register", help="Index a run directory.")
    register_parser.add_argument("--registry", required=True)
    register_parser.add_argument("--run", required=True)
    get_parser = sub.add_parser("get", help="Resolve an id to its manifest.")
    get_parser.add_argument("--registry", required=True)
    get_parser.add_argument("--id", required=True)
    sub.add_parser("list", help="List registered ids.").add_argument("--registry", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "register":
            print(json.dumps(register(args.registry, args.run), ensure_ascii=False))
        elif args.command == "get":
            print(json.dumps(get(args.registry, args.id), ensure_ascii=False))
        else:
            print(json.dumps(list_entries(args.registry), ensure_ascii=False))
    except RegistryError as exc:
        print(json.dumps({"error": str(exc)}))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
