import json
import unittest
from agora.transform import digest, snapshot, transform, validate_candidate, TransformError

TEXT='Se autoriza preparar un borrador.\nNo se autoriza publicar.\nFecha pendiente.\n'
DATA=TEXT.encode()

def candidate(text='Se permite preparar, no publicar; la fecha está pendiente.'):
    return json.dumps({'claims':[{'text':text,'citations':[{'line':i+1,'quote':line} for i,line in enumerate(TEXT.splitlines())]}]})

class TransformTests(unittest.TestCase):
    def setUp(self): self.source=snapshot(DATA,digest(DATA),'synthetic-p1',[1,2,3])
    def test_verified_candidate_remains_unreviewed(self):
        calls=[]
        def provider(*args): calls.append(args);return {'finish_reason':'stop','content':candidate()}
        result=transform(DATA,digest(DATA),'synthetic-p1',[1,2,3],provider)
        self.assertEqual(len(calls),1)
        self.assertEqual(result['structural_status'],'valid')
        self.assertEqual(result['semantic_support'],'not_verified')
        self.assertEqual(result['review_status'],'unreviewed')
    def test_changed_source_never_calls_provider(self):
        with self.assertRaisesRegex(TransformError,'hash_mismatch'):
            transform(DATA+b'Alterada',digest(DATA),'s',[],lambda *a:self.fail('provider called'))
    def test_missing_citation_rejected(self):
        with self.assertRaises(TransformError): validate_candidate('{"claims":[{"text":"x","citations":[]}]}',self.source)
    def test_fabricated_quote_rejected(self):
        x=json.loads(candidate());x['claims'][0]['citations'][0]['quote']='Se autoriza publicar.'
        with self.assertRaisesRegex(TransformError,'quote_mismatch'): validate_candidate(json.dumps(x),self.source)
    def test_omitted_required_line_rejected(self):
        x=json.loads(candidate());x['claims'][0]['citations'].pop()
        with self.assertRaisesRegex(TransformError,'required_evidence_missing'): validate_candidate(json.dumps(x),self.source)
    def test_boolean_line_rejected(self):
        x=json.loads(candidate());x['claims'][0]['citations'][0]['line']=True
        with self.assertRaisesRegex(TransformError,'out_of_range'): validate_candidate(json.dumps(x),self.source)
    def test_semantic_lie_is_not_autoapproved(self):
        result=transform(DATA,digest(DATA),'s',[1,2,3],lambda *a:{'finish_reason':'stop','content':candidate('Se autoriza publicar mañana.')})
        self.assertEqual(result['structural_status'],'valid')
        self.assertEqual(result['review_status'],'unreviewed')
        self.assertEqual(result['semantic_support'],'not_verified')
    def test_invalid_output_preserved(self):
        result=transform(DATA,digest(DATA),'s',[],lambda *a:{'finish_reason':'stop','content':'invalid JSON'})
        self.assertEqual(result['raw_output'],'invalid JSON')
        self.assertEqual(result['structural_status'],'rejected')

    def test_truncated_valid_json_not_admitted(self):
        result=transform(DATA,digest(DATA),'s',[],lambda *a:{'content':candidate(),'finish_reason':'length'})
        self.assertEqual(result['structural_status'],'rejected')
        self.assertEqual(result['diagnostic'],'generation_not_confirmed_complete')
    def test_missing_finish_reason_not_admitted(self):
        result=transform(DATA,digest(DATA),'s',[],lambda *a:{'content':candidate()})
        self.assertEqual(result['structural_status'],'rejected')

if __name__=='__main__': unittest.main()
