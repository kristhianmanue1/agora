import json
import tempfile
import unittest
from pathlib import Path
from agora.plan_generation import generate
from agora.source import FileSourceAdapter, digest
from agora.subquestions import prepare_subquestions

class PlanScopeTests(unittest.TestCase):
    def test_both_citation_modes_require_expansion_without_extra_calls(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'source.txt';raw=b'Approve standards.\n\n'+b'Other information. '*100
            p.write_bytes(raw)
            spec=dict(schema='agora/subquestions-input/v1-experimental',questions=[dict(id='a',query='Approve',reference_ranges=[])])
            plan=prepare_subquestions(FileSourceAdapter(p,'fixture'),digest(raw),spec,100,1)
            data=json.dumps(plan).encode()
            for mode in ['literal','ids']:
                calls=[]
                def provider(system,user):
                    calls.append(user)
                    if mode=='literal':
                        part=dict(id='P1',status='answer',answer='Approve standards.',quotes=['Approve standards.'])
                    else:
                        unit=json.loads(user)['evidence_units'][0]['id']
                        part=dict(id='P1',status='answered',claims=[dict(text='Approve standards.',evidence_ids=[unit])],missing=[])
                    return dict(finish_reason='stop',content=json.dumps({'parts':[part]}))
                r=generate(p,data,digest(data),'What is approved?',provider,mode,scope_guard=True)
                self.assertEqual(r['execution_status'],'complete')
                self.assertEqual(r['answer_status'],'candidate_requires_expansion')
                self.assertTrue(r['requires_expansion'])
                self.assertEqual(r['reading_budget_bytes'],100)
                self.assertEqual(r['scope_contract'],'agora/reading-scope/v1')
                self.assertFalse(r['document_absence_established'])
                self.assertEqual(len(calls),1)
                self.assertEqual(r['expansion_policy'],'explicit_review_and_budget_required')

    def test_empty_retrieval_requires_expansion_without_provider(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'source';raw=b'Only apples.';p.write_bytes(raw)
            spec=dict(schema='agora/subquestions-input/v1-experimental',questions=[dict(id='a',query='zebra',reference_ranges=[])])
            plan=prepare_subquestions(FileSourceAdapter(p,'fixture'),digest(raw),spec,100,1)
            data=json.dumps(plan).encode()
            def provider(*args):raise AssertionError('Unexpected provider call')
            r=generate(p,data,digest(data),'zebra',provider,scope_guard=True)
            self.assertEqual(r['answer_status'],'no_supplied_evidence')
            self.assertTrue(r['requires_expansion'])
            self.assertEqual(r['provider_calls'],0)

if __name__=='__main__':unittest.main()
