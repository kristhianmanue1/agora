import json,unittest
from agora.query import query,sha
from test_query import fixture,SOURCE

def response(known,ids=('P1','P2')):
    return {'finish_reason':'stop','content':json.dumps({'parts':[{'id':i,'status':'answer' if i in known else 'not_in_document','answer':known[i][0] if i in known else '', 'quotes':known[i][1] if i in known else []} for i in ids]})}

class PartsTests(unittest.TestCase):
    def run_case(self,replies):
        run=fixture();calls=[]
        def provider(s,u):calls.append(json.loads(u));return replies[len(calls)-1]
        r=query(SOURCE,sha(SOURCE),run,sha(run),'What is allowed and its cost?',provider,parts=['What is allowed?','What is its cost?'])
        return r,calls
    def test_partial_known_answer_survives_missing_cost(self):
        r,c=self.run_case([response({'P1':('Synthetic only',['Only synthetic files'])}),response({'P1':('Synthetic only',['Only synthetic files.'])})])
        self.assertEqual(r['answer_status'],'partial_answer');self.assertEqual(len(c),2)
        self.assertEqual(r['parts'][0]['answer'],'Synthetic only')
        self.assertEqual(r['parts'][1]['status'],'not_in_source')
        self.assertEqual(r['parts'][0]['answered_from'],'source')
    def test_missing_source_part_retains_prior_known_with_provenance(self):
        r,c=self.run_case([response({'P1':('Synthetic only',['Only synthetic files'])}),response({})])
        self.assertEqual(r['answer_status'],'partial_answer')
        self.assertEqual(r['parts'][0]['answered_from'],'summary')
        self.assertEqual(r['answered_from'],'mixed')
    def test_multipart_source_confirmation_even_if_model_claims_all_known(self):
        known={'P1':('Synthetic only',['Only synthetic files']),'P2':('No deployment',['no deployment permission.'])}
        r,c=self.run_case([response(known),response({'P1':('Synthetic only',['Only synthetic files.']),'P2':('No deployment',['No deployment permission.'])})])
        self.assertEqual(len(c),2);self.assertEqual(r['answer_status'],'answer')
        self.assertEqual(r['steps'][0]['retrieval_reason'],'multipart_source_confirmation')
    def test_source_overrides_summary_and_restores_requested_order(self):
        r,c=self.run_case([response({'P1':('Initial',['Only synthetic files'])}),response({'P1':('Final',['Only synthetic files.']),'P2':('No deployment',['No deployment permission.'])},('P2','P1'))])
        self.assertEqual([p['id'] for p in r['parts']],['P1','P2'])
        self.assertEqual(r['parts'][0]['answer'],'Final')
        self.assertEqual(r['parts'][0]['answered_from'],'source')
    def test_missing_duplicate_and_foreign_ids_rejected(self):
        for ids in [('P1',),('P1','P1'),('P1','P3')]:
            r,c=self.run_case([response({},ids)])
            self.assertEqual(r['execution_status'],'rejected');self.assertEqual(len(c),1)
    def test_metadata_quote_cannot_support_claim(self):
        r,c=self.run_case([response({'P1':('Not approved',['Borrador pendiente de revisión.'])})])
        self.assertEqual(r['diagnostic'],'answer_quote_mismatch')
    def test_empty_or_excess_parts_do_not_call_provider(self):
        run=fixture()
        for parts in [[],['x']*9,['']]:
            r=query(SOURCE,sha(SOURCE),run,sha(run),'x',lambda *a:self.fail('provider called'),parts=parts)
            self.assertEqual(r['diagnostic'],'invalid_question_parts')

if __name__=='__main__':unittest.main()
