"""Local review packets and separately recorded, caller-declared judgments."""
import argparse
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from .transform import digest, snapshot, unique_object, TransformError
from .query import query, read_limited

DECISIONS = {"supported": "Apoyada por la fuente", "unsupported": "No apoyada por la fuente",
             "uncertain": "Requiere aclaración"}


def load_bound(data, expected_hash):
    if type(data) is not bytes or len(data) > 1048576 or digest(data) != expected_hash:
        raise TransformError("review_input_hash_or_size_mismatch")
    try:
        return json.loads(data, object_pairs_hook=unique_object)
    except (ValueError, UnicodeError) as exc:
        raise TransformError("invalid_review_json") from exc


def inspect_run(source_data, source_hash, run_data, run_hash):
    source = snapshot(source_data, source_hash, "review-source", [])
    run = load_bound(run_data, run_hash)
    try:
        if run["schema"] != "agora/source-query/v0.3" or run["source_sha256"] != source_hash:
            raise ValueError()
        mode = {"direct_source": "source", "literal_selection": "extract"}[run["retrieval_mode"]]
        status = run["execution_status"]
        if status not in ("complete", "rejected", "failed"):
            raise ValueError()
        if type(run["question"]) is not str:
            raise ValueError()
        # Reproduce validation with stored responses only; this never calls a model.
        if status == "complete":
            steps = run["steps"]
            if len(steps) != 1:
                raise ValueError()
            step = steps[0]
            parts = [p["question"] for p in run["requested_parts"]]
            selection_data = json.dumps(run.get("selection"), ensure_ascii=True).encode()
            replay = query(source_data, source_hash, None, None, run["question"],
                lambda *_: step["response"], parts=parts, mode=mode,
                selection_data=selection_data, selection_hash=digest(selection_data))
            for field in ("execution_status", "requested_parts", "parts", "answer_status",
                          "answer", "quotes", "answered_from"):
                if run[field] != replay.get(field):
                    raise ValueError()
            if step["stage"] != mode or step["document_sha256"] != replay["steps"][0]["document_sha256"]:
                raise ValueError()
            original_prompt = json.loads(step["prompt"]["user"], object_pairs_hook=unique_object)
            rebuilt_prompt = json.loads(replay["steps"][0]["prompt"]["user"])
            if original_prompt != rebuilt_prompt:
                raise ValueError()
    except (KeyError, TypeError, ValueError, IndexError, UnicodeError) as exc:
        raise TransformError("invalid_review_run_binding") from exc
    return source, run


def make_judgment(source_hash, run_hash, run, reviewer, decision, note):
    if run["execution_status"] != "complete":
        raise TransformError("cannot_review_incomplete_answer")
    if decision not in DECISIONS:
        raise TransformError("invalid_review_decision")
    for value, limit in ((reviewer, 200), (note, 8000)):
        if type(value) is not str or not value.strip() or len(value) > limit:
            raise TransformError("invalid_review_text")
        value.encode("utf-8")
    return {"schema": "agora/review-judgment/v0.1", "source_sha256": source_hash,
            "run_sha256": run_hash, "reviewer": reviewer, "decision": decision,
            "note": note, "recorded_at": datetime.now(timezone.utc).isoformat(),
            "provenance": "caller_declared", "identity_verified": False,
            "memory_admission": "not_performed"}


def verify_judgment(data, expected_hash, source_hash, run_hash, run):
    value = load_bound(data, expected_hash)
    try:
        canonical = make_judgment(source_hash, run_hash, run, value["reviewer"], value["decision"], value["note"])
        moment = datetime.fromisoformat(value["recorded_at"])
        if moment.tzinfo is None:
            raise ValueError()
        canonical["recorded_at"] = value["recorded_at"]
        if value != canonical:
            raise ValueError()
    except (KeyError, TypeError, ValueError) as exc:
        raise TransformError("invalid_or_stale_judgment") from exc
    return value


def render(source, run, run_hash, judgment=None):
    esc = lambda value: html.escape(str(value), quote=True)
    status = run["execution_status"]
    state = "Candidata pendiente de revisión" if status == "complete" else "Sin respuesta utilizable: ejecución " + status
    if judgment:
        state = "Dictamen declarado: " + DECISIONS[judgment["decision"]]
    chunks = ["<!doctype html><html lang='es'><meta charset='utf-8'>",
        "<meta name='viewport' content='width=device-width, initial-scale=1'>",
        """<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">""",
        "<title>Ágora · Revisión de respuesta</title><style>body{font:17px/1.55 system-ui;max-width:1000px;margin:40px auto;padding:0 24px;color:#192834;background:#f7f8fa}h1,h2{line-height:1.2}section,details{background:white;border:1px solid #d5dde4;border-radius:10px;padding:20px;margin:18px 0}pre{white-space:pre-wrap;overflow-wrap:anywhere}blockquote{border-left:4px solid #558197;padding-left:16px;margin-left:0}code{overflow-wrap:anywhere}a{color:#155c83}.state{font-weight:700;color:#604411}small{color:#495967}li:target{background:#fff0bb}</style>",
        "<h1>Ágora · Revisión de respuesta</h1><p class='state'>" + esc(state) + "</p>",
        "<p>Las citas se comprueban contra la fuente. Esa coincidencia no demuestra que la interpretación sea correcta. El dictamen no autoriza acciones ni incorpora memoria.</p>",
        "<section><h2>Pregunta</h2><p>" + esc(run["question"]) + "</p></section>"]
    if judgment:
        chunks += ["<section><h2>Dictamen separado</h2><p>" + esc(judgment["reviewer"]) +
            " · Identidad declarada, no autenticada.</p><pre>" + esc(judgment["note"]) +
            "</pre><small>" + esc(judgment["recorded_at"]) + "</small></section>"]
    if status == "complete":
        labels = {p["id"]: p["question"] for p in run["requested_parts"]}
        for part in run["parts"]:
            chunks += ["<section><h2>" + esc(labels[part["id"]]) + "</h2><p>" +
                esc(part["answer"]) + "</p><small>Procedencia: " + esc(part["answered_from"]) + "</small>"]
            for quote in part["quotes"]:
                # Link to the first occurrence, making repeated occurrences explicit.
                starts = []; pos = 0
                while True:
                    pos = source["text"].find(quote, pos)
                    if pos < 0:
                        break
                    offset = 0
                    for line, chunk in enumerate(source["text"].splitlines(keepends=True), 1):
                        offset += len(chunk)
                        if pos < offset:
                            starts.append((line, pos))
                            break
                    pos += 1
                links = []
                for i, (line, start) in enumerate(starts):
                    byte_start = len(source["text"][:start].encode("utf-8"))
                    byte_end = byte_start + len(quote.encode("utf-8"))
                    supplied = run["retrieval_mode"] == "direct_source" or any(
                        span["start_byte"] <= byte_start and byte_end <= span["end_byte"]
                        for span in run["selection"]["spans"])
                    label = "en contexto enviado" if supplied else "fuera del contexto seleccionado"
                    links.append(f"<a href='#line-{line}'>Aparición {i+1}, línea {line}, {label}</a>")
                chunks.append("<blockquote><pre>" + esc(quote) + "</pre>" + " · ".join(links) + "</blockquote>")
            chunks.append("</section>")
        document = json.loads(run["steps"][0]["prompt"]["user"])["document"]
        chunks += ["<details><summary>Contexto entregado al modelo y tamaños</summary><p>Fuente: " +
            str(len(source["text"].encode())) + " bytes. Documento enviado: " + str(len(document.encode())) +
            " bytes. No incluye instrucciones/preguntas ni representa coste total.</p><pre>" + esc(document) + "</pre></details>"]
    else:
        chunks += ["<section><h2>Ejecución no completada</h2><p>" + esc(run.get("diagnostic", "Sin diagnóstico")) +
                   "</p><p>No se presenta contenido rechazado como respuesta candidata.</p></section>"]
    chunks += ["<section><h2>Fuente original</h2><ol>" + "".join(f"<li id='line-{i}'><pre>{esc(line)}</pre></li>" for i,line in enumerate(source["lines"],1)) + "</ol></section>",
        "<details><summary>Identidad de artefactos</summary><p>Fuente SHA-256: <code>" + esc(source["sha256"]) +
        "</code></p><p>Resultado SHA-256: <code>" + esc(run_hash) +
        "</code></p><p>Hashes e integridad no autentican al productor ni al revisor. La comprobación reproduce validación estructural con el código actual; no demuestra la ejecución histórica del modelo ni autentica su prompt. En extractos se reconstruye el contenido; no se verifica el hash del archivo de selección original sin ese archivo. Vista estática local; regenerar con los archivos actuales para detectar cambios posteriores.</p></details></html>"]
    return "\n".join(chunks)


def main():
    parser = argparse.ArgumentParser(description="Local review; no model calls or memory writes.")
    parser.add_argument("action", choices=["render", "record"])
    parser.add_argument("--source", type=Path, required=True); parser.add_argument("--sha256", required=True)
    parser.add_argument("--run", type=Path, required=True); parser.add_argument("--run-sha256", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--judgment", type=Path); parser.add_argument("--judgment-sha256")
    parser.add_argument("--reviewer"); parser.add_argument("--decision", choices=list(DECISIONS))
    parser.add_argument("--note-file", type=Path)
    args = parser.parse_args()
    if args.action == "record" and (not args.reviewer or not args.decision or not args.note_file or args.judgment or args.judgment_sha256):
        parser.error("record requires reviewer, decision and note-file; no prior judgment")
    if args.action == "render" and (args.reviewer or args.decision or args.note_file or bool(args.judgment) != bool(args.judgment_sha256)):
        parser.error("render uses optional judgment plus judgment-sha256; no record fields")
    try:
        source, run = inspect_run(read_limited(args.source,4096), args.sha256,
                                  read_limited(args.run,1048576), args.run_sha256)
        if args.action == "record":
            note = read_limited(args.note_file,32000).decode("utf-8")
            output = json.dumps(make_judgment(args.sha256, args.run_sha256, run, args.reviewer, args.decision, note),ensure_ascii=True,indent=2)+"\n"
        else:
            judgment = verify_judgment(read_limited(args.judgment,1048576), args.judgment_sha256,
                args.sha256, args.run_sha256, run) if args.judgment else None
            output = render(source, run, args.run_sha256, judgment)
        with args.out.open("x", encoding="utf-8") as stream:
            stream.write(output)
    except (OSError, ValueError, TypeError, UnicodeError) as exc:
        parser.exit(2, "Review failed: " + (str(exc) if isinstance(exc,TransformError) else type(exc).__name__) + "\n")
    print(json.dumps({"status":"complete", "action":args.action, "model_calls":0, "memory_writes":0}))


if __name__ == "__main__":
    main()
