#!/usr/bin/env python3
"""Synthetic trial for the AN-KLA <-> Agora governed admission contract.

Promotes the draft contract by executing its validation gates in a
disposable lab: an Agora answer run is produced with a simulated provider,
registered under a stable id, referenced by hash, and admitted into a fresh
synthetic AN-KLA store through its governed write flow only. Supersede is
exercised and a forged authority is expected to fail closed. Zero live
providers; the production .an-kla store of the repository is never touched.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from agora.consultation_package import build_package  # noqa: E402
from agora.evidence_answer_flow import run_flow  # noqa: E402
from agora.result_registry import register  # noqa: E402

ENV = dict(os.environ, AN_KLA_NO_UPDATE_CHECK="1")
ANKLA = "an-kla"


class SimulatedProvider:
    def __call__(self, system, user, *, model, max_output_tokens,
                 timeout_seconds, json_object):
        payload = json.loads(user)
        if "evidence_units" in payload and "aspects" in payload:
            stage, evidence_id = "generation", payload["evidence_units"][0]["id"]
            value = {"parts": [{"id": "P1", "status": "answered",
                                "claims": [{"text": "Atlas scored 91%.",
                                            "evidence_ids": [evidence_id]}],
                                "missing": []}]}
        elif "Assess each self-contained claim" in system:
            stage = "support"
            value = {"claims": [{"id": 0, "support": "supported",
                                 "quote_indices": [0], "reason": "Exact quote."}]}
        elif "Assess whether each claim" in system:
            stage = "relevance"
            value = {"claims": [{"id": 0, "relevance": "relevant",
                                 "reason": "Answers the task."}]}
        elif "Criteria:" in system:
            stage = "coverage"
            value = {"coverage": "complete"}
        else:
            stage = "omission"
            value = {"status": "no_omission_found", "omissions": []}
        return {"content": json.dumps(value), "finish_reason": "stop",
                "requested_model": model, "reported_model": model,
                "usage": {"total_tokens": 7}}


def run_ankla(store, *args, check=True):
    result = subprocess.run([ANKLA, "--project-root", str(store), *args],
                            capture_output=True, text=True, env=ENV)
    if check and result.returncode != 0:
        raise RuntimeError(f"an-kla {' '.join(args[:1])} failed: {result.stdout}{result.stderr}")
    return result


def revision(store):
    out = run_ankla(store, "status").stdout
    return json.loads(out)["revision"]


def write_fact(store, lab, name, proposal, expect_committed=True):
    proposal_path = lab / f"{name}-proposal.json"
    authority_path = lab / f"{name}-authority.json"
    plan_path = lab / f"{name}-plan.json"
    proposal_path.write_text(json.dumps(proposal, ensure_ascii=False), encoding="utf-8")
    template = run_ankla(store, "plan-write", "--proposal", str(proposal_path),
                         "--emit-authority-template").stdout
    if name == "forged-authority":
        forged = json.loads(template)
        forged["authority_class"] = "tool_observed"
        authority_path.write_text(json.dumps(forged, ensure_ascii=False), encoding="utf-8")
    else:
        authority_path.write_text(template, encoding="utf-8")
    plan_out = run_ankla(store, "plan-write", "--proposal", str(proposal_path),
                         "--authority", str(authority_path), check=False)
    plan_path.write_text(plan_out.stdout, encoding="utf-8")
    if not expect_committed:
        error = re.search(r"an-kla error: (\S+)", plan_out.stderr)
        return {"error": error.group(1) if error else "unexpected_success",
                "returncode": plan_out.returncode}
    plan = json.loads(plan_out.stdout or "{}")
    if plan.get("decision", {}).get("decision") != "write-summary":
        raise RuntimeError(f"{name}: unexpected plan decision {plan}")
    commit = run_ankla(store, "commit-write-plan",
                       "--expected-current", revision(store),
                       "--proposal", str(proposal_path),
                       "--authority", str(authority_path),
                       "--planning-result", str(plan_path), check=False)
    return {"commit": json.loads(commit.stdout or "{}"), "returncode": commit.returncode}


def main():
    steps = []
    with tempfile.TemporaryDirectory(prefix="ankla-admission-") as tmp:
        lab = Path(tmp)
        # 1. Agora side: real flow with simulated provider, then registry id.
        source = lab / "source.txt"
        source.write_text("Atlas scored 91%.", encoding="utf-8")
        import hashlib
        source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
        run_dir = lab / "agora-run"
        flow = run_flow(source, "admission-trial", source_sha,
                        "What was the Atlas score?", ["Give the Atlas score."],
                        run_dir, SimulatedProvider())
        registry = lab / "registry.json"
        entry = register(registry, run_dir)
        result_sha = entry["result_sha256"]
        package = build_package(source, run_dir)
        package_path = lab / "package.json"
        package_path.write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n",
                                encoding="utf-8")
        package_sha = hashlib.sha256(package_path.read_bytes()).hexdigest()
        reference = {"kind": "agora-result-ref/v1", "result_id": entry["id"],
                     "result_sha256": result_sha,
                     "package_schema": package["schema"],
                     "package_sha256": package_sha,
                     "source_sha256": source_sha,
                     "question": flow["question"], "status": flow["status"],
                     "requires_review": True}
        steps.append({"step": "agora_run_and_registry",
                      "flow_status": flow["status"], "result_id": entry["id"],
                      "result_sha256": result_sha,
                      "package_schema": package["schema"],
                      "package_sha256": package_sha,
                      "package_claims": len(package.get("claims", []))})

        # 2. Fresh synthetic AN-KLA store: init then governed admission.
        store = lab / "ankla-store"
        store.mkdir()
        init = run_ankla(store, "init", "--transaction-id", str(uuid.uuid4()))
        steps.append({"step": "store_initialized",
                      "genesis": json.loads(init.stdout).get("status", "ok")})
        base = revision(store)
        text = ("Resultado de consulta de Agora admitido por referencia: "
                + json.dumps(reference, ensure_ascii=False, sort_keys=True)
                + ". La referencia no eleva autoridad; requires_review viaja con ella.")
        first = write_fact(store, lab, "admission", {
            "schema": "an-kla/write-proposal-v1", "base_revision": base,
            "stream": "facts", "operation": "add",
            "requested_representation": "summary",
            "record": {"id": "f-agora-ref-trial-1", "text": text},
            "lineage": {"derived_from_retrieval": False,
                        "refs": [{"kind": "external", "id": entry["id"]}]}})
        committed = first["commit"].get("committed")
        steps.append({"step": "admission_committed", "committed": committed})

        # 3. Governed supersede of the reference fact.
        after_first = revision(store)
        second = write_fact(store, lab, "supersede", {
            "schema": "an-kla/write-proposal-v1", "base_revision": after_first,
            "stream": "facts", "operation": "supersede",
            "requested_representation": "summary",
            "supersedes": "f-agora-ref-trial-1",
            "record": {"id": "f-agora-ref-trial-2",
                       "text": text + " Sustituido para probar supersede gobernado."},
            "lineage": {"derived_from_retrieval": False,
                        "refs": [{"kind": "external", "id": entry["id"]}]}})
        inventory = json.loads(run_ankla(store, "inventory",
                                         "--revision", revision(store)).stdout)
        facts = {r["id"]: r["status"] for r in inventory.get("records", [])
                 if r.get("stream") == "facts"}
        steps.append({"step": "supersede_committed",
                      "committed": second["commit"].get("committed"),
                      "fact_states": facts})

        # 4. Negative control A: forged privileged authority must fail closed.
        forged = write_fact(store, lab, "forged-authority", {
            "schema": "an-kla/write-proposal-v1", "base_revision": revision(store),
            "stream": "facts", "operation": "add",
            "requested_representation": "full",
            "record": {"id": "f-forged", "text": "Intento de autoridad falsificada."},
            "lineage": {"derived_from_retrieval": False, "refs": []}},
            expect_committed=False)
        steps.append({"step": "forged_authority_outcome",
                      "error": forged["error"],
                      "returncode": forged["returncode"],
                      "not_committed": True})

        # 5. Negative control B: no direct-write path exists in Agora sources.
        grep = subprocess.run(["grep", "-rli", "an.kla", str(REPO / "src" / "agora")],
                              capture_output=True, text=True)
        steps.append({"step": "no_direct_write_path",
                      "src_matches": len(grep.stdout.split())})

        verify = json.loads(run_ankla(store, "verify").stdout)
        steps.append({"step": "store_verify", "ok": verify.get("ok"),
                      "identity": verify.get("identity_status")})

    summary = {"schema": "agora/ankla-admission-trial/v1", "steps": steps}
    out = Path(__file__).parent / "runs"
    out.mkdir(exist_ok=True)
    (out / "RESULTS.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
