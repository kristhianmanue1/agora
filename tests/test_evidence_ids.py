import json,tempfile,unittest
from pathlib import Path
from agora.evidence import EvidencePolicy,query_evidence
from agora.evidence_ids import build_units,validate_ids
from agora.source import FileSourceAdapter,digest

class EvidenceIdTests(unittest.TestCase):
    def setUp(self):self.env={'spans':[{'text':'Árbol INLINEFORM1.\n\nAtlas scored 91%.','start_byte':10}]};self.units=build_units(self.env,'doc','rev')
    def response(self,ids,text='Árbol INLINEFORM1.'):
        return {'finish_reason':'stop','content':json.dumps({'parts':[{'id':'a','status':'answered','claims':[{'text':text,'evidence_ids':ids}],'missing':[]}]})}
    def test_roundtrip_literal_with_utf8(self):
        parts,errors,anchors=validate_ids(self.response([self.units[0]['id']]),self.units,['a'],EvidencePolicy())
        self.assertEqual(errors,[]);self.assertEqual(parts[0]['claims'][0]['quotes'],['Árbol INLINEFORM1.']);self.assertEqual(anchors[0]['matches'][0]['start_byte'],10)
    def test_identity_changes_with_source_revision_offset(self):
        self.assertNotEqual(self.units[0]['id'],build_units(self.env,'doc','rev2')[0]['id'])
        self.assertNotEqual(self.units[0]['id'],build_units(self.env,'other','rev')[0]['id'])
        self.assertEqual(self.units,build_units(self.env,'doc','rev'))
    def test_unknown_and_foreign_ids(self):
        _,errors,_=validate_ids(self.response(['ev_not_present']),self.units,['a'],EvidencePolicy())
        self.assertEqual(errors[0]['code'],'unknown_evidence_id')
    def test_duplicate_id(self):
        _,errors,_=validate_ids(self.response([self.units[0]['id']]*2),self.units,['a'],EvidencePolicy())
        self.assertEqual(errors[0]['code'],'duplicate_evidence_id')
    def test_resolved_bytes_not_id_length(self):
        _,errors,_=validate_ids(self.response([self.units[0]['id']]),self.units,['a'],EvidencePolicy(12,1,1))
        self.assertIn('part_quote_bytes_exceeded',[e['code'] for e in errors])
    def test_no_model_supplied_quotes(self):
        r=self.response([self.units[0]['id']]);v=json.loads(r['content']);v['parts'][0]['claims'][0]['quotes']=['tampered'];r['content']=json.dumps(v)
        self.assertEqual(validate_ids(r,self.units,['a'],EvidencePolicy())[1][0]['code'],'invalid_claim_id_shape')
    def test_same_text_binds_selected_occurrence(self):
        units=build_units({'spans':[{'text':'Same.','start_byte':0},{'text':'Same.','start_byte':100}]},'d','r')
        _,e,a=validate_ids(self.response([units[1]['id']]),units,['a'],EvidencePolicy())
        self.assertFalse(e);self.assertEqual(a[0]['matches'],[{'start_byte':100,'end_byte':105}])
    def test_utf8_chunk_boundaries(self):
        text='é'*100;units=build_units({'spans':[{'text':text,'start_byte':0}]},'d','r',7)
        self.assertEqual(''.join(u['text'] for u in units),text)
        self.assertTrue(all(u['quote_bytes']<=7 for u in units))
    def test_wrong_claim_with_valid_id_stays_unverified(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'s';p.write_text('Atlas scored 91%.');adapter=FileSourceAdapter(p,'d')
            def provider(s,u):return self.response([json.loads(u)['evidence_units'][0]['id']],text='Boreal scored 91%.')
            r=query_evidence(adapter,digest(p.read_bytes()),'Boreal?',[{'id':'a','question':'Boreal?'}],provider,citation_mode='ids')
            self.assertEqual(r['execution_status'],'complete');self.assertEqual(r['semantic_support'],'not_verified');self.assertEqual(r['schema'],'agora/claim-evidence-query/v2')
    def test_invalid_json_not_repaired(self):
        self.assertEqual(validate_ids({'finish_reason':'stop','content':'{}junk'},self.units,['a'],EvidencePolicy())[1][0]['code'],'invalid_json')

    def test_id_from_another_revision_is_not_accepted(self):
        stale=build_units(self.env,'doc','old')[0]['id']
        self.assertEqual(validate_ids(self.response([stale]),self.units,['a'],EvidencePolicy())[1][0]['code'],'unknown_evidence_id')

    def test_absent_part_still_rejected_with_valid_id(self):
        _,errors,_=validate_ids(self.response([self.units[0]['id']]),self.units,['a','b'],EvidencePolicy())
        self.assertEqual(errors[0]['code'],'invalid_part_ids')

    def test_oversized_policy_unit_rejected(self):
        with self.assertRaises(ValueError):build_units(self.env,'doc','rev',3)

    def test_abstention_does_not_require_fake_reference(self):
        r={'finish_reason':'stop','content':json.dumps({'parts':[{'id':'a','status':'not_in_passages','claims':[],'missing':['Unknown result.']}]})}
        parts,errors,anchors=validate_ids(r,self.units,['a'],EvidencePolicy())
        self.assertFalse(errors);self.assertFalse(anchors);self.assertEqual(parts[0]['claims'],[])
