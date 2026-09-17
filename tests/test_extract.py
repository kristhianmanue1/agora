import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from agora.extract import select, verify_selection
from agora.query import query, sha
from agora.transform import TransformError

SOURCE = "No existe fórmula.\r\nSí se propuso una fórmula.\u2029Actor sin identificar.\nDato ajeno.\n".encode()
QUESTION = "¿Qué consta sobre la fórmula?"


def reply(text="", quotes=None):
    return {"finish_reason": "stop", "content": json.dumps({"parts": [{"id": "P1",
        "status": "answer" if text else "not_in_document", "answer": text,
        "quotes": quotes or []}]})}


class ExtractTests(unittest.TestCase):
    def artifact(self):
        return select(SOURCE, sha(SOURCE), QUESTION, [1], [[1, 2]])

    def query_case(self, response, mode="extract", artifact=None, question=QUESTION):
        value = self.artifact() if artifact is None else artifact
        data = json.dumps(value).encode()
        calls = []
        def provider(system, user):
            calls.append(json.loads(user))
            return response
        result = query(SOURCE, sha(SOURCE), None, None, question, provider, mode=mode,
                       selection_data=data, selection_hash=sha(data))
        return result, calls

    def test_declared_conflict_preserves_both_literal_sides_and_unicode_offsets(self):
        result = self.artifact()
        self.assertEqual(result["selected_lines"], [1, 2])
        for span in result["spans"]:
            self.assertEqual(SOURCE[span["start_byte"]:span["end_byte"]].decode(), span["text"])
        self.assertTrue(result["spans"][0]["text"].endswith("\r\n"))
        self.assertTrue(result["spans"][1]["text"].endswith("\u2029"))
        self.assertNotIn("Dato ajeno.", result["document"])

    def test_group_closure_is_transitive(self):
        result = select(SOURCE, sha(SOURCE), QUESTION, [1], [[2, 3], [1, 2]])
        self.assertEqual(result["selected_lines"], [1, 2, 3])

    def test_budget_rejects_instead_of_dropping_second_side(self):
        with self.assertRaisesRegex(TransformError, "extract_budget_exceeded"):
            select(SOURCE, sha(SOURCE), QUESTION, [1], [[1, 2]], budget=30)

    def test_hash_drift_rejected(self):
        with self.assertRaisesRegex(TransformError, "source_hash_mismatch"):
            select(SOURCE + b"changed", sha(SOURCE), QUESTION, [1])

    def test_invalid_lines_and_groups(self):
        for lines, groups in [([True], []), ([0], []), ([5], []), ([], []), ([1], [[9]]), ([1], [[]])]:
            with self.subTest(lines=lines, groups=groups), self.assertRaises(TransformError):
                select(SOURCE, sha(SOURCE), QUESTION, lines, groups)

    def test_tampered_spans_and_document_rejected_even_with_new_artifact_hash(self):
        for field in ["spans", "document", "selected_lines", "source_sha256", "review_status"]:
            item = self.artifact()
            item[field] = "changed"
            data = json.dumps(item).encode()
            with self.subTest(field=field), self.assertRaises(TransformError):
                verify_selection(SOURCE, sha(SOURCE), data, sha(data), QUESTION)

    def test_other_question_rejected_before_provider(self):
        result, calls = self.query_case(reply(), question="Qui approuve ?")
        self.assertEqual(result["execution_status"], "rejected")
        self.assertEqual(calls, [])

    def test_changed_subquestions_rejected_before_provider(self):
        item = select(SOURCE, sha(SOURCE), QUESTION, [1], [[1, 2]], parts=["Première partie"])
        data = json.dumps(item).encode()
        result = query(SOURCE, sha(SOURCE), None, None, QUESTION,
            lambda *a: self.fail("provider called"), mode="extract", parts=["Different part"],
            selection_data=data, selection_hash=sha(data))
        self.assertEqual(result["execution_status"], "rejected")
        verified = verify_selection(SOURCE, sha(SOURCE), data, sha(data), QUESTION, ["Première partie"])
        self.assertEqual(verified["question_parts"], ["Première partie"])

    def test_direct_source_needs_no_summary_and_calls_once(self):
        result, calls = self.query_case(reply(), mode="source")
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["document"], SOURCE.decode())
        self.assertEqual(result["answer_status"], "not_in_source")

    def test_missing_in_extract_does_not_assert_missing_in_source(self):
        result, calls = self.query_case(reply())
        self.assertEqual(len(calls), 1)
        self.assertEqual(result["answer_status"], "not_in_selection")
        self.assertEqual(result["parts"][0]["answered_from"], "extract")

    def test_quotes_cannot_use_locator_metadata(self):
        result, _ = self.query_case(reply("invented", ["source line 1"]))
        self.assertEqual(result["diagnostic"], "quote_outside_literal_span")

    def test_false_semantics_not_certified_by_literal_quote(self):
        result, _ = self.query_case(reply("No contradiction exists.", ["No existe fórmula."]))
        self.assertEqual(result["execution_status"], "complete")
        self.assertEqual(result["semantic_support"], "not_verified")
        self.assertEqual(result["review_status"], "unreviewed")

    def test_cli_preserves_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)/"source.txt"
            output = Path(directory)/"selection.json"
            source.write_bytes(SOURCE)
            command = [sys.executable, "-B", "-m", "agora.extract", "--source", str(source),
                "--sha256", sha(SOURCE), "--question", QUESTION, "--line", "1", "--group", "1,2", "--out", str(output)]
            first = subprocess.run(command, capture_output=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            saved = output.read_bytes()
            second = subprocess.run(command, capture_output=True)
            self.assertNotEqual(second.returncode, 0)
            self.assertEqual(output.read_bytes(), saved)


if __name__ == "__main__":
    unittest.main()
