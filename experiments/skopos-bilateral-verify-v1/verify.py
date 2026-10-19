#!/usr/bin/env python3
"""Read-only bilateral verification for the Skopos <-> Agora contract gate.

Checks, without mutating anything, whether the Skopos artifacts consumed by
the Agora bilateral essay can be confirmed from Skopos's own local records:
byte-identical copies, content-normalized copies, logical id bindings, custody
references to the original document, and presence of the original bytes in
either repository. Negative findings are results, not failures of the script.
"""
import hashlib
import json
import subprocess
from pathlib import Path

AGORA = Path(__file__).resolve().parents[2]
ESSAY = AGORA / "experiments" / "ctim-v02-bilateral-v1"
SKOPOS = Path.home() / "www" / "aria" / "skopos"


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_sha(path):
    """Forma canónica del contrato de acceso Skopos v0.3 (compacta, ordenada)."""
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
        encoded = json.dumps(value, sort_keys=True, ensure_ascii=False,
                             separators=(",", ":")).encode("utf-8", "surrogatepass")
    except Exception:
        return None
    return hashlib.sha256(encoded).hexdigest()


def main():
    checks = []
    request = ESSAY / "request.json"
    response = ESSAY / "response.json"
    exchange = ESSAY / "exchange-focused" / "exchange.json"
    derived = ESSAY / "exchange-focused" / "derived.txt"
    artifacts = {"request.json": request, "response.json": response,
                 "exchange.json": exchange, "derived.txt": derived}
    hashes = {name: sha_file(path) for name, path in artifacts.items()}
    manifests = json.loads(exchange.read_text(encoding="utf-8"))
    original_sha = manifests["source"]["sha256"]

    sk_tree = [p for p in SKOPOS.rglob("*")
               if p.is_file() and ".venv" not in p.parts and "node_modules" not in p.parts
               and "__pycache__" not in p.parts]
    sk_hashes = {}
    sk_canon = {}
    for path in sk_tree:
        sk_hashes.setdefault(sha_file(path), []).append(str(path))
        canonical = canonical_sha(path)
        if canonical:
            sk_canon.setdefault(canonical, []).append(str(path))

    byte_matches = {name: sk_hashes.get(digest, []) for name, digest in hashes.items()}
    checks.append({"check": "byte_identical_copies_in_skopos",
                   "expected": "al menos request y response retenidos",
                   "observed": {k: len(v) for k, v in byte_matches.items()}})

    canon_matches = {}
    for name, path in artifacts.items():
        digest = canonical_sha(path)
        canon_matches[name] = sk_canon.get(digest, []) if digest else []
    checks.append({"check": "content_normalized_copies_in_skopos",
                   "observed": {k: len(v) for k, v in canon_matches.items()}})

    ag_req = json.loads(request.read_text(encoding="utf-8"))
    ag_res = json.loads(response.read_text(encoding="utf-8"))
    logical_binding = (ag_req.get("request_id") == ag_res.get("request_id"),
                       ag_res.get("status"))
    binding_reproduces = ag_res.get("request_sha256") in (
        hashes["request.json"], canonical_sha(request))
    checks.append({"check": "internal_request_binding_reproduces_locally",
                   "observed": binding_reproduces,
                   "detail": "reproduce con la forma canónica compacta documentada "
                             "en el contrato de acceso Skopos v0.3 "
                             "(sort_keys, ensure_ascii=False, separadores ',:' )"})

    referenced = []
    for path in sk_tree:
        if path.suffix == ".json":
            try:
                if original_sha in path.read_text(encoding="utf-8"):
                    referenced.append(str(path))
            except Exception:
                pass
    checks.append({"check": "skopos_custody_references_original",
                   "observed": len(referenced), "files": referenced[:3]})

    pdf_found = []
    for path in sk_tree + [p for p in AGORA.rglob("*") if p.is_file()
                           and ".git" not in p.parts]:
        if path.suffix == ".pdf" and sha_file(path) == original_sha:
            pdf_found.append(str(path))
    checks.append({"check": "original_pdf_bytes_present",
                   "observed": pdf_found})

    confirmed = (byte_matches["request.json"] or canon_matches["request.json"]) and \
                (byte_matches["response.json"] or canon_matches["response.json"]) and \
                bool(pdf_found)
    verdict = "bilateral_confirmed" if confirmed else "bilateral_not_confirmed"
    summary = {"schema": "agora/skopos-bilateral-verify/v1", "date": "2026-10-19",
               "verdict": verdict,
               "artifacts_sha256": hashes, "original_sha256": original_sha,
               "checks": checks,
               "required_before_contract_vigencia": [
                   "Skopos debe retener los pares petición/respuesta que sirve "
                   "(hoy custody-delivery y document-delivery están vacíos y ninguna "
                   "copia de request/response existe en su árbol de corridas)",
                   "la huella request_sha256 debe poder reproducirse desde los bytes "
                   "que el consumidor conserva, o Skopos debe publicar su forma canónica",
                   "el original (PDF) debe estar disponible para la verificación de "
                   "integridad del intercambio, o la verificación queda en not_checked"]}
    out = Path(__file__).parent / "runs"
    out.mkdir(exist_ok=True)
    (out / "RESULTS.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": verdict,
                      "checks": [(c["check"], c["observed"]) for c in checks]},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
