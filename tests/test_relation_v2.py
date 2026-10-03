import hashlib,json,unittest
from agora.relation_candidates import template,evidence,validate,FIELDS_V2
from agora.relation_workflow import run

class RelationV2Tests(unittest.TestCase):
    raw=b'baseline: a Transformer with big hyperparameters.'
    def candidate(self):
        c=template(self.raw,'doc',contract_version='v2')
        c['fields']['model_configuration']={'text':'big hyperparameters','evidence_ids':[evidence(self.raw,'doc')['units'][0]['id']]}
        return c
    def test_configuration_does_not_fill_software_version(self):
        c=self.candidate();r=validate(self.raw,'doc',c)
        self.assertEqual(r['schema'],'agora/relation-assessment/v2')
        self.assertIn({'field':'software_version','reason':'missing_text'},r['gaps'])
        self.assertEqual(c['fields']['software_version'],{'text':None,'evidence_ids':[]})
    def test_v1_unchanged_and_no_silent_upgrade(self):
        old=template(self.raw,'doc');self.assertIn('version',old['fields'])
        self.assertNotIn('model_configuration',old['fields'])
        self.assertEqual(validate(self.raw,'doc',old)['schema'],'agora/relation-assessment/v1')
        old['schema']='agora/relation-candidate/v2'
        with self.assertRaisesRegex(ValueError,'invalid_fields'):validate(self.raw,'doc',old)
    def test_generation_contract_and_prompt(self):
        seen=[]
        def provider(system,user):
            seen.append(system)
            return {'finish_reason':'stop','content':json.dumps(self.candidate())}
        r=run(self.raw,'doc',hashlib.sha256(self.raw).hexdigest(),provider,question='baseline?',contract_version='v2')
        self.assertEqual(r['execution_status'],'complete');self.assertIn('software release',seen[0])
        self.assertEqual(r['schema'],'agora/relation-workflow/v2')
        r=run(self.raw,'doc',hashlib.sha256(self.raw).hexdigest(),provider,question='baseline?')
        self.assertEqual(r['diagnostics'],['generated_contract_mismatch'])
    def test_review_preserves_unknown_and_flags_overclaim(self):
        def provider(system,user):
            self.assertIn('model_configuration',system)
            self.assertNotIn('"version":',system)
            return {'finish_reason':'stop','content':json.dumps(dict.fromkeys((*FIELDS_V2,'relation'),'supported'))}
        r=run(self.raw,'doc',hashlib.sha256(self.raw).hexdigest(),provider,candidate=self.candidate())
        self.assertIn('software_version',r['review_inconsistencies']);self.assertFalse(r['admitted'])
    def test_literal_wrong_field_is_not_certified(self):
        c=self.candidate();c['fields']['software_version']=dict(c['fields']['model_configuration'])
        r=validate(self.raw,'doc',c)
        self.assertEqual(r['semantic_support'],'not_verified');self.assertFalse(r['admitted'])
