import json
from pathlib import Path
import tempfile
import unittest
from agora.source import FileSourceAdapter, digest, encode_record
from agora.sufficiency import assess


class SufficiencyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)/'source.txt'
        self.path.write_bytes('La coordinadora es Iria.\n\nEl presupuesto es 42 euros.\n'.encode())
        self.sha = digest(self.path.read_bytes())
        self.adapter = FileSourceAdapter(self.path, 'fixture')
        self.envelope = self.adapter.fetch(self.sha, [(0, 24)])
        self.data = encode_record(self.envelope)
        self.calls = 0

    def call(self, judgment, **kwargs):
        def provider(*args):
            self.calls += 1
            return {'finish_reason': 'stop', 'content': json.dumps(judgment)}
        return assess(self.adapter,self.sha,'¿Quién coordina?',self.data,digest(self.data),provider,**kwargs)

    def sufficient(self):
        return {'decision':'sufficient','explanation':'La fuente nombra la coordinadora.',
                'quotes':['La coordinadora es Iria.'],'missing':[]}

    def test_sufficient_is_only_a_model_judgment(self):
        r=self.call(self.sufficient())
        self.assertEqual(r['execution_status'],'complete')
        self.assertEqual(r['assessment_status'],'model_judgment_unverified')
        self.assertEqual(r['action_taken'],'none')
        self.assertEqual(r['semantic_verification'],'not_performed')
        self.assertEqual(self.calls,1)

    def test_partial_evidence_allows_missing_fact(self):
        r=self.call({'decision':'insufficient','explanation':'Falta importe.',
                     'quotes':['La coordinadora es Iria.'],'missing':['Presupuesto']})
        self.assertEqual(r['execution_status'],'complete')
        self.assertEqual(r['action_taken'],'none')

    def test_uncertain_is_allowed_without_citations(self):
        r=self.call({'decision':'uncertain','explanation':'No identifica sujeto.',
                     'quotes':[],'missing':['Identidad']})
        self.assertEqual(r['execution_status'],'complete')

    def test_missing_quote_or_contradictory_shape_rejected(self):
        for change in ({'quotes':[]},{'missing':['Presupuesto']},{'decision':'verified'},
                       {'extra':True},{'explanation':''}):
            j=self.sufficient();j.update(change)
            self.assertEqual(self.call(j)['execution_status'],'rejected')

    def test_translated_or_decorated_enum_is_rejected_without_repair(self):
        for value in ('suficiente', 'Sufficient', 'sufficient ', True, None):
            with self.subTest(value=value):
                judgment = self.sufficient()
                judgment['decision'] = value
                result = self.call(judgment)
                self.assertEqual(result['diagnostic'], 'invalid_assessment_shape')
                self.assertNotIn('judgment', result)

    def test_quote_outside_selected_material_rejected(self):
        j=self.sufficient();j['quotes']=['El presupuesto es 42 euros.']
        self.assertEqual(self.call(j)['execution_status'],'rejected')

    def test_tampered_envelope_never_calls_provider(self):
        self.envelope['spans'][0]['text']='La coordinadora es otra persona.'
        self.data=encode_record(self.envelope)
        r=self.call(self.sufficient())
        self.assertEqual(r['diagnostic'],'invalid_envelope_binding')
        self.assertEqual(self.calls,0)

    def test_tampered_boolean_type_never_calls_provider(self):
        self.envelope['truncated'] = 0
        self.data = encode_record(self.envelope)
        r = self.call(self.sufficient())
        self.assertEqual(r['diagnostic'], 'invalid_envelope_binding')
        self.assertEqual(self.calls, 0)

    def test_changed_revision_never_calls_provider(self):
        self.path.write_bytes(b'changed')
        r=self.call(self.sufficient())
        self.assertEqual(r['execution_status'],'rejected')
        self.assertEqual(self.calls,0)

    def test_prompt_budget_never_calls_provider(self):
        r=self.call(self.sufficient(),prompt_budget=1)
        self.assertEqual(r['diagnostic'],'assessment_prompt_budget_exceeded')
        self.assertEqual(self.calls,0)

    def test_hash_mismatch_never_calls_provider(self):
        r=assess(self.adapter,self.sha,'Question',self.data,'0'*64,lambda *args:self.fail('called'))
        self.assertEqual(r['diagnostic'],'envelope_hash_or_size_mismatch')

    def test_false_semantic_claim_is_not_certified(self):
        j=self.sufficient();j['explanation']='Iria también aprueba gastos.'
        r=self.call(j)
        self.assertEqual(r['execution_status'],'complete')
        self.assertEqual(r['semantic_verification'],'not_performed')
        self.assertEqual(r['action_taken'],'none')


if __name__=='__main__':unittest.main()
