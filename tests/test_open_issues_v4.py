import copy
import importlib.util
import json
from pathlib import Path
import unittest
BASE=Path(__file__).resolve().parents[1]/'experiments/open-issues-v4'
spec=importlib.util.spec_from_file_location('issues_v4',BASE/'protocol.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class IssueV4Tests(unittest.TestCase):
    def setUp(self):
        self.cases=json.loads((BASE/'replay-fixtures.json').read_text())
        self.data=self.cases[0]['input']
        self.out=m.prepare_candidate(self.cases[0]['original_content'],self.data)
    def validate(self):return m.validate(json.dumps(self.out),self.data)
    def test_real_absence_payload_preserved_and_accepted(self):
        original=json.loads(self.cases[0]['original_content'])
        r=self.validate()
        self.assertEqual(r['fields'],original['fields'])
        self.assertEqual(r['reason'],original['reason'])
        self.assertEqual(r['status'],'partial')
        self.assertEqual(r['fields']['date']['evidence'],[])
    def test_real_conflict_preserved_with_citations(self):
        case=self.cases[1];r=m.validate(json.dumps(m.prepare_candidate(case['original_content'],case['input'])),case['input'])
        self.assertEqual(r['fields']['date']['support_status'],'disputed')
        self.assertEqual(len(r['fields']['date']['evidence']),2)
    def test_no_implicit_v3_migration(self):
        with self.assertRaises(ValueError):m.validate(self.cases[0]['original_content'],self.data)
    def test_unsupported_schema_rejected(self):
        self.out['schema']='agora/issue-assessment/v3'
        with self.assertRaisesRegex(ValueError,'schema'):self.validate()
    def test_invented_source_version_locator_and_completeness_rejected(self):
        for key,value in [('source_id','invented'),('source_sha256','0'*64),('original_revision',99),('selection_complete','complete')]:
            with self.subTest(key=key):
                out=copy.deepcopy(self.out);out['reviewed_scope']['sources'][0][key]=value
                with self.assertRaisesRegex(ValueError,'review_scope_mismatch'):m.validate(json.dumps(out),self.data)
        self.out['reviewed_scope']['sources'][0]['units'][0]['locator']['id']='invented'
        with self.assertRaisesRegex(ValueError,'review_scope_mismatch'):self.validate()
    def test_missing_or_empty_scope_rejected(self):
        for scope in ({},dict(basis='supplied_input_only',sources=[])):
            self.out['reviewed_scope']=scope
            with self.assertRaises(ValueError):self.validate()
    def test_changed_source_bytes_rejected(self):
        self.data['sources'][0]['text']+='altered'
        with self.assertRaises(ValueError):self.validate()
    def test_supported_still_requires_quote(self):
        self.out['fields']['owner']['evidence']=[]
        with self.assertRaisesRegex(ValueError,'missing_evidence'):self.validate()
    def test_disputed_and_withdrawn_still_require_quotes(self):
        for support in ('disputed','withdrawn'):
            row=self.out['fields']['date'];row['support_status']=support
            row['relations']=['refutation'] if support=='withdrawn' else ['initial']
            row['change_source_ids']=[self.data['sources'][0]['id']] if support=='withdrawn' else []
            with self.assertRaisesRegex(ValueError,'missing_evidence'):self.validate()
    def test_missing_cannot_assert_value(self):
        self.out['fields']['date']['observed_value']='2026-10-21'
        with self.assertRaisesRegex(ValueError,'unresolved_field'):self.validate()
    def test_metadata_quote_cannot_support_value(self):
        self.out['fields']['owner']['evidence'][0]['quote']='not_established'
        with self.assertRaisesRegex(ValueError,'invalid_reference'):self.validate()
    def test_false_claim_of_full_review_rejected(self):
        self.out['reviewed_scope']['basis']='fully_read'
        with self.assertRaisesRegex(ValueError,'review_scope_mismatch'):self.validate()
    def test_plain_unicode_source_scope_uses_bytes(self):
        import hashlib
        text='Responsable: Lucía.'
        source=dict(id='u',text=text,sha256=hashlib.sha256(text.encode()).hexdigest())
        data=dict(sources=[source],dependents=[])
        scope,units=m.supplied_scope(data)
        self.assertEqual(scope['sources'][0]['units'][0]['end_byte'],len(text.encode()))
        self.assertEqual(units,{'u':[text]})

    def test_type_confusion_in_scope_rejected(self):
        self.out['reviewed_scope']['sources'][0]['original_revision']=True
        with self.assertRaisesRegex(ValueError,'review_scope_mismatch'):self.validate()
    def test_forged_byte_limit_rejected(self):
        self.out['reviewed_scope']['sources'][0]['units'][0]['end_byte']+=1
        with self.assertRaisesRegex(ValueError,'review_scope_mismatch'):self.validate()
    def test_absence_without_any_supplied_source_rejected(self):
        with self.assertRaisesRegex(ValueError,'missing_review_scope'):
            m.supplied_scope(dict(sources=[],dependents=[]))
