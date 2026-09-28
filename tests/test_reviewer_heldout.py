import json,runpy,unittest
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]/'experiments/reviewer-comparison-v2'
class HeldoutReviewerTests(unittest.TestCase):
 def test_question_and_evidence_match_without_gold(self):
  module=runpy.run_path(str(BASE/'run.py'))
  case=dict(question='When?',claim='Friday',evidence='No date was given.',gold='secret-label')
  _,g=module['payload']('glm',case);_,j=module['payload']('jev',case)
  self.assertEqual(g['messages'][1]['content'],j['state'])
  self.assertEqual(set(json.loads(j['state'])),{'question','claim','evidence'})
  self.assertNotIn('secret-label',json.dumps(g)+json.dumps(j))
 def test_frozen_groups_are_separate_and_external_labels_balanced(self):
  meta=json.loads((BASE/'cases-metadata.json').read_text());gold=json.loads((BASE/'gold.json').read_text())
  external=[m for m in meta if m['id'].startswith('attr-')]
  self.assertEqual(len(external),24);self.assertEqual(len(meta),36)
  self.assertEqual([sum(gold[m['id']]==label for m in external) for label in ('supported','contradicted','insufficient')],[8,8,8])
  for paper in ('1811.00051','1911.03977'):
   self.assertEqual(gold[f'long-{paper}-0-abstract'],'insufficient')
   self.assertNotEqual(gold[f'long-{paper}-0-full'],'insufficient')
 def test_no_output_reduces_f1(self):
  enrich=runpy.run_path(str(BASE/'score.py'))['enrich']
  labels=('supported','contradicted','insufficient')
  matrix={l:{p:0 for p in (*labels,'no_valid_output')} for l in labels}
  for l in labels:matrix[l]['no_valid_output']=1
  result=enrich(dict(confusion_matrix=matrix,total=3,completed=0))
  self.assertEqual(result['macro_f1_fixed_three_classes'],0)
  self.assertEqual(result['no_valid_output'],3)
