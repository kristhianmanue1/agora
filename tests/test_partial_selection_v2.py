import importlib.util
from pathlib import Path
import unittest
P=Path(__file__).resolve().parents[1]/'experiments/partial-selection-v2/run.py'
spec=importlib.util.spec_from_file_location('partial_selection_v2',P)
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)

class PartialSelectionScoringTests(unittest.TestCase):
    def assessment(self,support,ids):
        return {'status':'partial','fields':{'date':{'observed_value':None,'support_status':support,'evidence':[{'source_id':i} for i in ids]},'owner':{'observed_value':'Lina'}}}
    def test_missing_is_not_a_detected_contradiction(self):
        result=runner.checks(self.assessment('missing',['a','b']),'disputed',{'a':{},'b':{}})
        self.assertTrue(result['values'])
        self.assertFalse(result['support'])
    def test_dispute_requires_both_sources(self):
        result=runner.checks(self.assessment('disputed',['a']),'disputed',{'a':{},'b':{}})
        self.assertTrue(result['support'])
        self.assertFalse(result['both_conflicting_sources'])
    def test_cited_dispute_passes_bounded_rubric(self):
        self.assertTrue(all(runner.checks(self.assessment('disputed',['a','b']),'disputed',{'a':{},'b':{}}).values()))

class CurrentContractBoundaryTests(unittest.TestCase):
    def test_literal_absence_without_supporting_quote_is_currently_rejected(self):
        import hashlib
        import json
        protocol=runner.load('absence_contract',P.parent.parent/'open-issues-v3/protocol.py')
        text='Lina es responsable de Nube.'
        data={'requirements':{'date':['date_confirmed'],'owner':['owner_confirmed']},'sources':[{'id':'s','text':text,'sha256':hashlib.sha256(text.encode()).hexdigest()}],'dependents':[]}
        def field(value,support,missing,evidence):
            return {'observed_value':value,'support_status':support,'missing_requirements':missing,'relations':['initial'],'change_source_ids':[],'evidence':evidence}
        raw=json.dumps({'fields':{'date':field(None,'missing',['date_confirmed'],[]),'owner':field('Lina','supported',[],[{'source_id':'s','quote':text}])},'reason':'La selección no contiene fecha; no se infiere ausencia en la fuente completa.'})
        with self.assertRaisesRegex(ValueError,'missing_evidence'):
            protocol.validate(raw,data)
