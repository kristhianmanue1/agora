"""Controles negativos del piloto; no certifican resolución semántica."""
import importlib.util
import json
from pathlib import Path
import unittest
P=Path(__file__).resolve().parents[1]/'experiments/open-issues-v1'
spec=importlib.util.spec_from_file_location('open_issue_protocol',P/'protocol.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)

class OpenIssueTests(unittest.TestCase):
    def setUp(self):
        self.case=json.loads((P/'cases.json').read_text())[0]
        self.data=p.payload(self.case,0)
        self.valid=dict(status='open',relation='initial',values={'date':None},evidence=[dict(source_id='a1',quote='falta definir la fecha')],affected=[],reason='Falta fecha.')
    def test_literal_reference_and_future_evidence(self):
        self.assertEqual(p.validate(json.dumps(self.valid),self.data),self.valid)
        for ref in [dict(source_id='a2',quote='confirmo'),dict(source_id='a1',quote='fecha confirmada')]:
            bad=dict(self.valid,evidence=[ref])
            with self.assertRaises(ValueError):p.validate(json.dumps(bad),self.data)
    def test_unknown_dependent_and_incomplete_closure(self):
        for bad in [dict(self.valid,affected=['invented']),dict(self.valid,status='resolved')]:
            with self.assertRaises(ValueError):p.validate(json.dumps(bad),self.data)
    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(ValueError):p.validate('{"status":"open","status":"resolved"}',self.data)
    def test_previous_assessment_is_not_mutated_or_gold(self):
        previous=dict(self.valid)
        data=p.payload(self.case,1,previous)
        self.assertEqual(data['previous_assessment'],self.valid)
        self.assertEqual(len(data['sources']),2)
        self.assertNotIn('gold',data)
        self.assertIsNone(p.payload(self.case,1)['previous_assessment'])
    def test_literal_integrity_is_not_semantic_support(self):
        # Un valor falso puede superar la forma: la evaluación semántica es aparte.
        wrong=dict(self.valid,status='resolved',values={'date':'2099-01-01'})
        validated=p.validate(json.dumps(wrong),self.data)
        gold=json.loads((P/'gold.json').read_text())['clarification'][0]
        self.assertFalse(all(p.score(validated,gold).values()))
if __name__=='__main__':unittest.main()
