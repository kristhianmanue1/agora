import copy
import json
import unittest
from agora.split_review import review_split


def candidate(question='What did Maren carry?'):
    return {'schema':'agora/claim-evidence-query/v2','execution_status':'complete',
            'prompt':{'user':json.dumps({'question':question})},
            'requested_aspects':[{'id':'a','question':question}],
            'parts':[{'id':'a','claims':[{'text':'Maren carried a brass key.',
                        'quotes':['Maren carried a brass key.']}],'missing':[]}]}


def response(axis, label):
    row={'id':0,axis:label,'reason':'Synthetic reviewer control.'}
    if axis=='support':row['quote_indices']=[0]
    return {'finish_reason':'stop','content':json.dumps({'claims':[row]})}


class SplitReviewTests(unittest.TestCase):
    def test_question_changes_only_relevance_payload(self):
        captured=[]
        for question in ('What did Maren carry?', 'What was the weather?'):
            def support(s,u):
                captured.append((s,u));return response('support','supported')
            def relevance(s,u):
                p=json.loads(u)
                self.assertNotIn('quotes',p['claims'][0])
                self.assertNotIn('support',p['claims'][0])
                return response('relevance','relevant' if question.startswith('What did') else 'extra')
            result=review_split(candidate(question),support,relevance)
            self.assertEqual(result['execution_status'],'complete')
        self.assertEqual(captured[0],captured[1])
        self.assertNotIn('question',json.loads(captured[0][1]))

    def test_no_mutation_and_no_approval(self):
        c=candidate();before=copy.deepcopy(c)
        r=review_split(c,lambda s,u:response('support','supported'),lambda s,u:response('relevance','relevant'))
        self.assertEqual(c,before);self.assertEqual(r['recommendation'],'needs_adjudication')
        self.assertEqual(r['memory_admission'],'not_performed')

    def test_insufficient_can_be_relevant(self):
        r=review_split(candidate(),lambda s,u:response('support','insufficient'),lambda s,u:response('relevance','relevant'))
        self.assertEqual(r['recommendation'],'needs_revision')
        self.assertEqual(r['assessment'][0]['relevance'],'relevant')

    def test_first_stage_failure_stops_second(self):
        r=review_split(candidate(),lambda s,u:{'finish_reason':'length'},lambda s,u:self.fail('second call'))
        self.assertEqual(r['provider_calls'],1);self.assertNotIn('recommendation',r)

    def test_second_stage_failure_preserves_support(self):
        def fail(s,u):raise TimeoutError()
        r=review_split(candidate(),lambda s,u:response('support','supported'),fail)
        self.assertEqual(r['execution_status'],'failed')
        self.assertEqual(r['stages']['support']['execution_status'],'complete')
        self.assertNotIn('recommendation',r)

    def test_total_budget_checked_before_any_call(self):
        r=review_split(candidate(),lambda s,u:self.fail(),lambda s,u:self.fail(),prompt_budget=1)
        self.assertEqual(r['provider_calls'],0)

    def test_malformed_judgments_cannot_pass(self):
        for mutation in ('duplicate','missing','boolean','badquote','injected_axis'):
            with self.subTest(mutation=mutation):
                value=json.loads(response('support','supported')['content'])
                if mutation=='duplicate':value['claims']*=2
                if mutation=='missing':value['claims']=[]
                if mutation=='boolean':value['claims'][0]['id']=False
                if mutation=='badquote':value['claims'][0]['quote_indices']=[99]
                if mutation=='injected_axis':value['claims'][0]['relevance']='relevant'
                r=review_split(candidate(),lambda s,u:{'finish_reason':'stop','content':json.dumps(value)},lambda s,u:self.fail())
                self.assertEqual(r['execution_status'],'rejected')

    def test_provider_mutation_cannot_change_second_payload(self):
        c=candidate()
        def support(s,u):
            c['requested_aspects'][0]['question']='injected'
            return response('support','supported')
        def relevance(s,u):
            self.assertNotIn('injected',u)
            return response('relevance','relevant')
        self.assertEqual(review_split(c,support,relevance)['execution_status'],'complete')
