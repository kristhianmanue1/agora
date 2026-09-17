"""Literal query-scoped selection. Groups are declared by the caller, not detected."""
import argparse
import json
from pathlib import Path
from .transform import snapshot, digest, unique_object, TransformError


def select(data, source_hash, question, lines, groups=None, budget=4096, parts=None):
    source = snapshot(data, source_hash, "extract-source", [])
    if type(question) is not str or not question.strip() or len(question) > 2000:
        raise TransformError("invalid_question")
    question.encode("utf-8")
    parts = [question] if parts is None else parts
    if type(parts) is not list or not 1 <= len(parts) <= 8 or any(type(t) is not str or not t.strip() or len(t) > 2000 for t in parts):
        raise TransformError("invalid_question_parts")
    for part in parts:
        part.encode("utf-8")
    if type(budget) is not int or not 1 <= budget <= 16384:
        raise TransformError("invalid_extract_budget")
    def checked(values):
        if type(values) is not list or not values or any(type(n) is not int or not 1 <= n <= len(source["lines"]) for n in values):
            raise TransformError("invalid_extract_lines")
        return sorted(set(values))
    selected = set(checked(lines))
    if groups is None:
        groups = []
    if type(groups) is not list or len(groups) > 64:
        raise TransformError("invalid_evidence_groups")
    groups = [checked(g) for g in groups]
    # Transitive closure prevents partial inclusion of overlapping evidence groups.
    while True:
        expanded = selected | {n for g in groups if selected.intersection(g) for n in g}
        if expanded == selected:
            break
        selected = expanded
    chunks = data.decode("utf-8").splitlines(keepends=True)
    spans = []
    offset = 0
    for number, chunk in enumerate(chunks, 1):
        size = len(chunk.encode("utf-8"))
        if number in selected:
            spans.append({"line": number, "start_byte": offset, "end_byte": offset + size,
                          "text": chunk})
        offset += size
    # Boundaries are explicit; excerpts are never presented as contiguous source.
    document = "\n".join(f"[source line {s['line']}; bytes {s['start_byte']}:{s['end_byte']}]\n{s['text']}" for s in spans)
    if len(document.encode("utf-8")) > budget:
        raise TransformError("extract_budget_exceeded")
    return {"schema": "agora/literal-selection/v0.1", "source_sha256": source_hash,
            "scope": "query", "question": question, "question_parts": parts, "requested_lines": sorted(set(lines)),
            "evidence_groups": groups, "selected_lines": sorted(selected), "spans": spans,
            "budget_bytes": budget, "document": document,
            "document_sha256": digest(document.encode("utf-8")),
            "review_status": "unreviewed", "semantic_support": "not_verified",
            "source_bytes": len(data), "document_bytes": len(document.encode("utf-8"))}


def verify_selection(data, source_hash, artifact_data, artifact_hash, question, parts=None):
    if len(artifact_data) > 1048576 or digest(artifact_data) != artifact_hash:
        raise TransformError("selection_hash_or_size_mismatch")
    try:
        artifact = json.loads(artifact_data, object_pairs_hook=unique_object)
        expected = select(data, source_hash, question, artifact["requested_lines"],
                          artifact["evidence_groups"], artifact["budget_bytes"], parts)
        if artifact != expected:
            raise ValueError()
    except (KeyError, TypeError, ValueError, UnicodeError) as exc:
        raise TransformError("invalid_selection_binding") from exc
    return artifact


def main():
    parser = argparse.ArgumentParser(description="Select literal source lines without model calls.")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--question", required=True)
    parser.add_argument("--part", action="append", default=None)
    parser.add_argument("--line", type=int, action="append", required=True)
    parser.add_argument("--group", action="append", default=[], help="Comma-separated line numbers kept together")
    parser.add_argument("--budget", type=int, default=4096)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        with args.source.open("rb") as stream:
            data = stream.read(4097)
        groups = [[int(n) for n in group.split(",")] for group in args.group]
        result = select(data, args.sha256, args.question, args.line, groups, args.budget, args.part)
        with args.out.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, ensure_ascii=True, indent=2)
            stream.write("\n")
    except (OSError, ValueError, UnicodeError) as exc:
        parser.exit(2, f"{type(exc).__name__}: selection failed\n")
    print(json.dumps({"status": "complete", "selected_lines": result["selected_lines"],
                      "document_bytes": result["document_bytes"], "model_calls": 0}))


if __name__ == "__main__":
    main()
