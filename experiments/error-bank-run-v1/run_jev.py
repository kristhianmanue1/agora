#!/usr/bin/env python3
"""error-bank-run-v1: ejecuta Jev sobre el banco de errores controlados.

Reproduce el protocolo congelado de refinement-v1 (systemone, jev-1.13.0,
registros en `state`, dos preguntas de opción por registro) sobre los doce
controles de ../error-bank-v1. Cuatro llamadas: dos mitades en orden directo
(llamadas 0 y 1) y dos mitades en orden inverso (llamadas 2 y 3). Las
etiquetas esperadas y los flags nunca se envían. Cero reintentos.
La clave se lee de la variable de entorno TYPESAFE_API_KEY.
"""
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent
BANK = BASE.parent / "error-bank-v1"
STAGING = Path("/tmp/aria-error-bank-v1")
URL = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-1.13.0"
TIMEOUT = 90
RETRIES = 0

SUPPORT_CRITERIA = "full_source supports every claim in answer; answer does not contradict full_source; facts not established by full_source count as unsupported; comment on the original text in brackets does not change this axis"
SUPPORT_INSTRUCTIONS = "Mark supported only if each claim is supported by full_source. Mark unsupported if the answer attributes to the source anything it does not say (wrong numbers, wrong study, wrong task, wrong scope, overstatement). Answer must not be graded for addressing the question here."
COVERAGE_CRITERIA = "answer addresses the question the user asked; details only present in full_source and requested by the question count as omitted; bracketed original text does not change this axis; justified_abstention only when the answer abstains and full_source does not establish the requested answer"
COVERAGE_INSTRUCTIONS = "Mark complete only if the answer responds to what was asked. Mark omitted when the answer states true facts but does not answer the question, or drops requested details (qualifiers, second study, requested axis). Mark justified_abstention only if full_source truly lacks the answer."


def main():
    controls_blob = (BANK / "controls.json").read_bytes()
    controls = json.loads(controls_blob)
    freeze = json.loads((BANK / "freeze.json").read_text())
    digest = hashlib.sha256(controls_blob).hexdigest()
    assert digest == freeze["controls_sha256"], "controls.json no coincide con freeze.json"
    assert freeze["jev_max_calls"] == 4 and freeze["retries"] == 0

    def record_for(c):
        rec = {
            "id": c["id"],
            "full_source": c["source"],
            "question": c["question"],
            "answer": c["answer"],
        }
        if c.get("retrieved"):
            rec["retrieved_passages"] = c["retrieved"]
        return rec

    def questions_for(c):
        return {
            c["id"] + "_backing": {
                "type": "choice",
                "criteria": SUPPORT_CRITERIA,
                "instructions": SUPPORT_INSTRUCTIONS,
            },
            c["id"] + "_coverage": {
                "type": "choice",
                "criteria": COVERAGE_CRITERIA,
                "instructions": COVERAGE_INSTRUCTIONS,
            },
        }

    forward = list(controls)
    reversed_ = list(reversed(controls))
    dry = os.environ.get("DRY_RUN") == "1"
    batches = [forward[0:6], forward[6:12], reversed_[0:6], reversed_[6:12]]
    if dry:
        for i, batch in enumerate(batches):
            state = [record_for(c) for c in batch]
            questions = {}
            for c in batch:
                questions.update(questions_for(c))
            payload = json.dumps({"state": state, "questions": questions},
                                 ensure_ascii=False)
            assert "expected_support" not in payload and "expected_flags" not in payload
            print(f"llamada {i}: {len(state)} registros, {len(questions)} preguntas, "
                  f"{len(payload)} caracteres")
        print("DRY_RUN OK: 4 lotes, etiquetas fuera del contexto")
        return 0

    key = os.environ.get("TYPESAFE_API_KEY")
    if not key:
        print("FALTA TYPESAFE_API_KEY: entrega la clave mediante Llavero "
              "(security add-generic-password -s typesafe -a $USER -w) y reintenta.",
              file=sys.stderr)
        return 2

    STAGING.mkdir(mode=0o700, parents=True, exist_ok=True)

    for i, batch in enumerate(batches):
        state = [record_for(c) for c in batch]
        questions = {}
        for c in batch:
            questions.update(questions_for(c))
        payload = {
            "model": MODEL,
            "state": json.dumps(state, ensure_ascii=False),
            "questions": questions,
        }
        req = urllib.request.Request(
            URL,
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": "Bearer " + key,
                "Content-Type": "application/json",
            },
        )
        (STAGING / f"jev-{i}-request.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2))
        started = time.time()
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                body = resp.read().decode()
                status = resp.status
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            status = e.code
        except Exception as e:  # network failure: no retry, freeze says 0
            (STAGING / f"jev-{i}-result.json").write_text(json.dumps({
                "status": "network-error", "error": repr(e)}, indent=2))
            print(f"llamada {i}: error de red {e!r}", file=sys.stderr)
            return 1
        result = {"status": status, "seconds": round(time.time() - started, 2)}
        try:
            result["response"] = json.loads(body)
        except json.JSONDecodeError:
            result["response_raw"] = body[:2000]
        (STAGING / f"jev-{i}-result.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2))
        print(f"llamada {i}: HTTP {status}, {result['seconds']}s")

    for p in STAGING.iterdir():
        assert key not in p.read_text(), f"clave presente en {p.name}"
    print("OK: 4 llamadas completadas, recibos en", STAGING)
    return 0


if __name__ == "__main__":
    sys.exit(main())
