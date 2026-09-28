import json,runpy,tempfile,unittest
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]/'experiments/reviewer-comparison-v1'
class ReviewerComparisonTests(unittest.TestCase):
 def test_balanced_controls_and_request_evidence_identity(self):
  cases,gold=runpy.run_path(str(BASE/'prepare.py'))['build']()
  self.assertEqual(len(cases),24)
  self.assertEqual([list(gold.values()).count(label) for label in ('supported','contradicted','insufficient')],[8,8,8])
  self.assertEqual(cases,json.loads((BASE/'cases.json').read_text()))
  payload=runpy.run_path(str(BASE/'run.py'))['payload']
  for case in cases:
   _,glm=payload('glm',case);_,jev=payload('jev',case)
   self.assertEqual(glm['messages'][1]['content'],jev['state'])
 def test_incomplete_and_invalid_outputs_rejected(self):
  label=runpy.run_path(str(BASE/'run.py'))['label']
  with self.assertRaises(ValueError):label('glm',{'choices':[{'finish_reason':'length','message':{'content':'{"support":"supported"}'}}]})
  with self.assertRaises(ValueError):label('jev',{'answers':{'support':{'choice':'unknown'}}})
 def test_missing_responses_are_not_dropped_and_false_support_is_counted(self):
  score=runpy.run_path(str(BASE/'score.py'))['score']
  cases=[dict(id='a',language='es'),dict(id='b',language='en')];gold={'a':'insufficient','b':'supported'}
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp);(path/'a.json').write_text(json.dumps(dict(status='completed',label='supported')))
   result=score(path,cases,gold)
   self.assertEqual(result['total'],2);self.assertEqual(result['completed'],1)
   self.assertEqual(result['correct'],0);self.assertEqual(result['false_support'],1)
   self.assertEqual(result['confusion_matrix']['supported']['no_valid_output'],1)
