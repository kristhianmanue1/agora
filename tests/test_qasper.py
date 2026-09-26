import copy
import json
from pathlib import Path
import tempfile
import unittest
from agora.qasper import eligible, render, prepare, verify, export_predictions


def paper(qid, absent=False):
    a={'unanswerable':absent,'extractive_spans':[] if absent else ['Ada'],
       'free_form_answer':'','yes_no':None,'evidence':[] if absent else ['Ada leads.']}
    return {'title':'Title','abstract':'Résumé.',
            'full_text':[{'section_name':'Method','paragraphs':['Ada leads.']}],
            'qas':[{'question_id':qid,'question':'Who leads?', 'answers':[{'answer':a}]}]}


class QasperTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);self.root=Path(tmp.name)
        self.dataset=self.root/'data.json';self.out=self.root/'prepared'
        self.dataset.write_text(json.dumps({'p1':paper('q1'),'p2':paper('q2',True)}))
    def prepare(self):
        return prepare(self.dataset,self.out,answerable=1,unanswerable=1)
    def test_unicode_offsets(self):
        raw,ps=render(paper('q'))
        for p in ps:self.assertEqual(raw[p['start_byte']:p['end_byte']].decode(),p['text'])
    def test_reject_visual_disagreement_and_unmapped(self):
        p=paper('q');qa=p['qas'][0];_,ps=render(p)
        qa['answers'][0]['answer']['evidence']=['FLOAT SELECTED x']
        self.assertEqual(eligible(qa,ps)[1],'visual_evidence')
        qa['answers'][0]['answer']['evidence']=['invented']
        self.assertEqual(eligible(qa,ps)[1],'unmapped_or_ambiguous_evidence')
        qa['answers'].append({'answer':{'unanswerable':True}})
        self.assertEqual(eligible(qa,ps)[1],'answerability_disagreement')
    def test_separation_and_freeze(self):
        self.prepare();verify(self.out)
        cases=json.loads((self.out/'model_inputs/cases.json').read_text())
        self.assertEqual(len(cases),2)
        for c in cases:self.assertFalse(set(c)&{'answers','evidence','stratum'})
        self.assertTrue((self.out/'references/gold.json').exists())
        (self.out/'model_inputs/case-01.txt').write_text('modified')
        with self.assertRaisesRegex(ValueError,'freeze_mismatch'):verify(self.out)
    def test_reproducible_and_no_overwrite(self):
        self.prepare();other=self.root/'second'
        prepare(self.dataset,other,answerable=1,unanswerable=1)
        self.assertEqual((self.out/'freeze.json').read_bytes(),(other/'freeze.json').read_bytes())
        with self.assertRaises(FileExistsError):self.prepare()
    def test_insufficient_data_leaves_no_output(self):
        with self.assertRaisesRegex(ValueError,'insufficient'):prepare(self.dataset,self.out)
        self.assertFalse(self.out.exists())
    def test_missing_predictions_not_converted_to_abstentions(self):
        self.prepare();results=self.root/'results';results.mkdir()
        exported=self.root/'predictions.jsonl'
        r=export_predictions(self.out,results,exported)
        self.assertEqual(len(r['missing_or_failed']),2);self.assertEqual(exported.read_text(),'')
    def test_abstention_and_wrong_case(self):
        self.prepare();cases=json.loads((self.out/'model_inputs/cases.json').read_text());c=cases[1]
        results=self.root/'results';p=results/c['id'];p.mkdir(parents=True)
        r={'execution_status':'complete','answer_status':'candidate_partial','source_id':c['source_id'],
           'source_sha256':c['sha256'],'question':c['question'],'response_language':'en',
           'parts':[{'id':'answer','status':'not_in_document','answer':'','quotes':[]}],'citations':[]}
        (p/'result.json').write_text(json.dumps(r))
        dest=self.root/'predictions.jsonl';export_predictions(self.out,results,dest)
        self.assertEqual(json.loads(dest.read_text())['predicted_answer'],'Unanswerable')
        r['source_sha256']='wrong';(p/'result.json').write_text(json.dumps(r))
        with self.assertRaisesRegex(ValueError,'result_case_mismatch'):export_predictions(self.out,results,self.root/'bad.jsonl')

    def test_citation_export_to_original_paragraph(self):
        self.prepare();c=json.loads((self.out/'model_inputs/cases.json').read_text())[0]
        source=(self.out/'model_inputs'/c['source']).read_bytes();start=source.index(b'Ada')
        results=self.root/'results';p=results/c['id'];p.mkdir(parents=True)
        r={'execution_status':'complete','answer_status':'candidate','source_id':c['source_id'],
           'source_sha256':c['sha256'],'question':c['question'],'response_language':'en',
           'parts':[{'id':'answer','status':'answer','answer':'Ada','explanation':'Explanation must not enter the scored answer.','quotes':['Ada']}],
           'citations':[{'part_id':'answer','quote':'Ada','matches':[{'start_byte':start,'end_byte':start+3}]}]}
        (p/'result.json').write_text(json.dumps(r));dest=self.root/'prediction.jsonl'
        export_predictions(self.out,results,dest)
        self.assertEqual(json.loads(dest.read_text())['predicted_evidence'],['Ada leads.'])
        self.assertEqual(json.loads(dest.read_text())['predicted_answer'],'Ada')
        r['citations'][0]['matches'][0]['end_byte']+=1
        (p/'result.json').write_text(json.dumps(r))
        with self.assertRaisesRegex(ValueError,'citation_mismatch'):export_predictions(self.out,results,self.root/'bad.jsonl')

if __name__=='__main__':unittest.main()
