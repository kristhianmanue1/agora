import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from agora.transform import digest, TransformError
from agora.query import query
from agora.extract import select
from agora.review import inspect_run, make_judgment, verify_judgment, render

SOURCE = "Pantalla visible.\r\nEnvío al completar.\u2029Pantalla visible.\n<script>alert(1)</script>\n".encode()
QUESTION = "¿Cuándo es visible?"


def fixture(mode="source", content=None):
    response = {"finish_reason": "stop", "content": content or json.dumps({"parts": [
        {"id": "P1", "status": "answer", "answer": "<img src=x onerror=alert(1)> Visible.",
         "quotes": ["Pantalla visible."]}]})}
    a = json.dumps(select(SOURCE,digest(SOURCE),QUESTION,[1])).encode()
    return query(SOURCE,digest(SOURCE),None,None,QUESTION,lambda *_: response,mode=mode,
                 selection_data=a,selection_hash=digest(a))


def inspected(run=None):
    data=json.dumps(fixture() if run is None else run).encode()
    return inspect_run(SOURCE,digest(SOURCE),data,digest(data)),data


class ReviewTests(unittest.TestCase):
    def test_both_routes_replay_without_provider(self):
        for mode in ["source","extract"]:
            (source,run),data=inspected(fixture(mode))
            self.assertEqual(run["execution_status"],"complete")
            self.assertEqual(source["text"],SOURCE.decode())

    def test_modified_final_rejected_even_if_hash_is_updated(self):
        for field,value in [("answer","Different"),("answer_status","partial_answer"),("parts",[])]:
            run=fixture();run[field]=value
            with self.subTest(field=field),self.assertRaises(TransformError):
                inspected(run)

    def test_modified_prompt_binding_rejected(self):
        run=fixture();prompt=json.loads(run["steps"][0]["prompt"]["user"])
        prompt["document"]="Other source"
        run["steps"][0]["prompt"]["user"]=json.dumps(prompt)
        with self.assertRaises(TransformError):inspected(run)

    def test_raw_response_mismatch_rejected(self):
        run=fixture();run["steps"][0]["response"]["content"]='{"parts": []}'
        with self.assertRaises(TransformError):inspected(run)

    def test_source_drift_rejected(self):
        _,data=inspected()
        with self.assertRaises(TransformError):
            inspect_run(SOURCE+b"changed",digest(SOURCE),data,digest(data))

    def test_report_escapes_source_answer_and_note(self):
        (source,run),data=inspected()
        judgment=make_judgment(digest(SOURCE),digest(data),run,"Agent <b>","uncertain","<script>danger</script>")
        page=render(source,run,digest(data),judgment)
        self.assertNotIn("<script>",page);self.assertNotIn("<img src",page)
        self.assertIn("&lt;script&gt;",page);self.assertIn("Content-Security-Policy",page)
        self.assertIn("Identidad declarada, no autenticada",page)

    def test_repeated_quote_links_to_all_source_occurrences(self):
        (source,run),data=inspected()
        page=render(source,run,digest(data))
        self.assertIn("href='#line-1'",page);self.assertIn("href='#line-3'",page)

    def test_extract_marks_occurrences_not_sent_to_model(self):
        (source,run),data=inspected(fixture("extract"))
        page=render(source,run,digest(data))
        self.assertIn("línea 1, en contexto enviado",page)
        self.assertIn("línea 3, fuera del contexto seleccionado",page)

    def test_rejected_raw_not_rendered_as_answer(self):
        (source,run),data=inspected(fixture(content='{"parts": [], "raw_secret_marker":1}'))
        self.assertEqual(run["execution_status"],"rejected")
        page=render(source,run,digest(data))
        self.assertIn("Sin respuesta utilizable",page)
        self.assertNotIn("raw_secret_marker",page)
        with self.assertRaisesRegex(TransformError,"cannot_review_incomplete_answer"):
            make_judgment(digest(SOURCE),digest(data),run,"Reviewer","supported","ok")

    def test_judgment_bound_to_both_inputs_and_caller_declared(self):
        (_,run),data=inspected()
        j=make_judgment(digest(SOURCE),digest(data),run,"Reviewer","unsupported","Interpretation not established")
        body=json.dumps(j).encode()
        self.assertFalse(verify_judgment(body,digest(body),digest(SOURCE),digest(data),run)["identity_verified"])
        for source_hash,run_hash in [("0"*64,digest(data)),(digest(SOURCE),"0"*64)]:
            with self.assertRaises(TransformError):verify_judgment(body,digest(body),source_hash,run_hash,run)

    def test_judgment_cannot_elevate_identity_or_admission(self):
        (_,run),data=inspected()
        for field,value in [("identity_verified",True),("memory_admission","admitted")]:
            j=make_judgment(digest(SOURCE),digest(data),run,"Reviewer","supported","ok")
            j[field]=value;body=json.dumps(j).encode()
            with self.assertRaises(TransformError):verify_judgment(body,digest(body),digest(SOURCE),digest(data),run)

    def test_duplicate_json_keys_rejected(self):
        data=b'{"schema":1,"schema":2}'
        with self.assertRaises(TransformError):inspect_run(SOURCE,digest(SOURCE),data,digest(data))

    def test_summary_schema_is_not_silently_supported(self):
        run=fixture();run["schema"]="agora/source-query/v0.2"
        with self.assertRaises(TransformError):inspected(run)

    def test_cli_record_render_preserves_inputs_and_output(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);source=p/"source.txt";run=p/"run.json";note=p/"note.txt"
            source.write_bytes(SOURCE);run.write_text(json.dumps(fixture()));note.write_text("Technical review only")
            common=[sys.executable,"-B","-m","agora.review"]
            bindings=["--source",str(source),"--sha256",digest(SOURCE),"--run",str(run),"--run-sha256",digest(run.read_bytes())]
            j=p/"review.json";page=p/"review.html"
            record=common+["record"]+bindings+["--reviewer","test-agent","--decision","uncertain","--note-file",str(note),"--out",str(j)]
            self.assertEqual(subprocess.run(record,capture_output=True).returncode,0)
            command=common+["render"]+bindings+["--judgment",str(j),"--judgment-sha256",digest(j.read_bytes()),"--out",str(page)]
            proc=subprocess.run(command,capture_output=True)
            self.assertEqual(proc.returncode,0,proc.stderr)
            old=page.read_bytes()
            self.assertNotEqual(subprocess.run(command,capture_output=True).returncode,0)
            self.assertEqual(page.read_bytes(),old);self.assertEqual(source.read_bytes(),SOURCE)

    def test_query_cli_defaults_to_source_without_summary(self):
        with tempfile.TemporaryDirectory() as d:
            import os
            p=Path(d);s=p/"s.txt";s.write_bytes(SOURCE)
            env=os.environ.copy();env.pop("ZAI_API_KEY",None)
            proc=subprocess.run([sys.executable,"-B","-m","agora.query","--source",str(s),"--sha256",digest(SOURCE),"--question",QUESTION,"--model","test","--out",str(p/"out")],env=env,capture_output=True)
            self.assertEqual(proc.returncode,2)
            result=json.loads((p/"out/result.json").read_text())
            self.assertEqual(result["retrieval_mode"],"direct_source")
            self.assertEqual(result["http_attempts"],0)


if __name__ == "__main__":unittest.main()
