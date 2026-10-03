import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from agora.passage_view import display, main

ROOT = Path(__file__).resolve().parents[1]

class PassageViewTests(unittest.TestCase):
    def test_real_repair_preserves_answer_missing_and_scope_without_network(self):
        path=ROOT/'experiments/focused-label-v1/repair/default-receipt.json'
        result=json.loads(path.read_text());buffer=io.StringIO()
        with patch('sys.argv',['view',str(path)]), patch('urllib.request.build_opener',side_effect=AssertionError('network forbidden')),contextlib.redirect_stdout(buffer):
            self.assertEqual(main(),0)
        view=json.loads(buffer.getvalue())
        self.assertEqual(view['answer'],result['answer'])
        self.assertEqual(view['missing'],result['missing'])
        self.assertIn('INLINEFORM0',view['missing'][0])
        self.assertTrue(view['requires_expansion'])
        self.assertEqual(view['answer_scope'],'selected_passages')
        self.assertFalse(view['document_absence_established'])
        self.assertEqual(view['semantic_support'],'not_verified')
        self.assertNotIn('response',view)
        self.assertIn('result_sha256',view)

    def test_legacy_unknown_is_not_empty_missing_or_full_scope(self):
        view=display({'execution_status':'complete','answer':'Dato.'})
        self.assertIsNone(view['missing'])
        self.assertIsNone(view['requires_expansion'])
        self.assertEqual(view['answer_scope'],'unknown')
        self.assertTrue(any('no declarada' in w for w in view['warnings']))

    def test_declared_empty_missing_does_not_certify_semantics(self):
        view=display({'execution_status':'complete','answer':'Dato.','missing':[]})
        self.assertEqual(view['missing'],[])
        self.assertTrue(any('no verifica' in w for w in view['warnings']))

    def test_rejected_or_failed_content_is_not_salvaged(self):
        for status in ['failed','rejected']:
            with self.subTest(status=status):
                view=display({'execution_status':status,'answer':'Should not show','missing':[],
                              'response':{'content':'incomplete'},'diagnostic':'generation_incomplete'})
                self.assertIsNone(view['answer']);self.assertIsNone(view['missing'])
                self.assertEqual(view['diagnostic'],'generation_incomplete')
                self.assertNotIn('response',view)

    def test_duplicate_keys_and_non_object_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'result.json'
            for payload in ['[]','{"answer":1,"answer":2}']:
                p.write_text(payload)
                with patch('sys.argv',['view',str(p)]),contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(main(),2)

class EvidenceViewTests(unittest.TestCase):
    def test_claim_parts_keep_missing_and_aspect_identity(self):
        result={'schema':'agora/claim-evidence-query/v2','execution_status':'complete',
                'requires_expansion':True,'parts':[
                    {'id':'P1','status':'partial','claims':[{'text':'Dato conocido.'}], 'missing':['Fórmula ausente.']},
                    {'id':'P2','status':'not_in_passages','claims':[], 'missing':['Responsable desconocido.']}]}
        view=display(result)
        self.assertEqual(view['missing'],['Fórmula ausente.','Responsable desconocido.'])
        self.assertIn('Dato conocido.',view['answer'])
        self.assertEqual(view['parts'][1]['id'],'P2')
        self.assertEqual(view['parts'][1]['missing'],['Responsable desconocido.'])
        self.assertTrue(view['requires_expansion'])
    def test_invalid_claim_parts_are_not_shown_as_success(self):
        with self.assertRaisesRegex(ValueError,'invalid_display_parts'):
            display({'schema':'agora/claim-evidence-query/v2','execution_status':'complete','parts':[{'id':'P1','claims':[]}]})
    def test_rejected_claim_parts_are_not_salvaged(self):
        view=display({'schema':'agora/claim-evidence-query/v2','execution_status':'rejected','parts':[{'claims':[{'text':'Raw'}]}]})
        self.assertIsNone(view['answer']);self.assertEqual(view['parts'],[])
