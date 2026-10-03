import copy,json,subprocess,sys,tempfile,unittest
from pathlib import Path
from agora.relation_candidates import evidence,template,validate,FIELDS

class RelationTests(unittest.TestCase):
    raw='Atlas: traducción de oraciones.\n\nAtlas obtuvo BLEU 25.'.encode()
    def complete(self):
        value=template(self.raw,'doc');uid=evidence(self.raw,'doc')['units'][0]['id']
        for field in FIELDS:value['fields'][field]={'text':'declared '+field,'evidence_ids':[uid]}
        value['relation_evidence_ids']=[uid]
        return value
    def test_empty_and_partial_gap(self):
        c=template(self.raw,'doc');r=validate(self.raw,'doc',c)
        self.assertEqual(r['status'],'needs_more_evidence');self.assertEqual(len(r['gaps']),6)
        c['fields']['system']['text']='Atlas'
        self.assertIn({'field':'system','reason':'missing_evidence'},validate(self.raw,'doc',c)['gaps'])
    def test_complete_is_not_semantically_validated(self):
        c=self.complete();c['fields']['system']['text']='Wrong system'
        r=validate(self.raw,'doc',c)
        self.assertEqual(r['status'],'requires_semantic_review');self.assertFalse(r['admitted'])
        self.assertEqual(r['semantic_support'],'not_verified')
        anchor=r['anchors']['system'][0]
        self.assertEqual(self.raw[anchor['start_byte']:anchor['end_byte']].decode(),anchor['text'])
    def test_stale_source_and_foreign_id(self):
        c=self.complete()
        with self.assertRaisesRegex(ValueError,'source_identity'):validate(self.raw+b'x','doc',c)
        c['fields']['system']['evidence_ids']=[evidence(self.raw,'foreign')['units'][0]['id']]
        with self.assertRaisesRegex(ValueError,'unknown_evidence'):validate(self.raw,'doc',c)
    def test_duplicates_and_missing_link(self):
        c=self.complete();c['relation_evidence_ids']=[]
        self.assertEqual(validate(self.raw,'doc',c)['gaps'],[{'field':'relation','reason':'missing_link_evidence'}])
        c=self.complete();c['fields']['system']['evidence_ids']*=2
        with self.assertRaisesRegex(ValueError,'duplicate'):validate(self.raw,'doc',c)
    def test_no_injected_admission_or_null_evidence(self):
        c=self.complete();c['admitted']=True
        with self.assertRaisesRegex(ValueError,'shape'):validate(self.raw,'doc',c)
        del c['admitted'];c['fields']['system']['text']=None
        with self.assertRaisesRegex(ValueError,'evidence_without'):validate(self.raw,'doc',c)
    def test_cli_roundtrip_and_bad_revision(self):
        script=Path(__file__).resolve().parents[1]/'scripts/agora_relations.py'
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder);source=p/'source.txt';source.write_bytes(self.raw)
            base=[sys.executable,str(script),'--source',str(source),'--source-id','doc']
            created=subprocess.run(base+['template'],capture_output=True,text=True,check=True)
            candidate=p/'candidate.json';candidate.write_text(created.stdout)
            result=subprocess.run(base+['validate','--candidate',str(candidate)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0);self.assertEqual(json.loads(result.stdout)['status'],'needs_more_evidence')
            source.write_bytes(self.raw+b' changed')
            self.assertEqual(subprocess.run(base+['validate','--candidate',str(candidate)],capture_output=True).returncode,2)
