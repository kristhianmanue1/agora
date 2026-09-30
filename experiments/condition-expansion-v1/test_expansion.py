import unittest
from expansion import expand
class ExpansionTests(unittest.TestCase):
 def test_subject_and_cue_required(self):
  s=b'Datasets A and B.\n\nDataset B is excluded under configuration X.\n\nFootball is excluded.\n\nDatasets have labels.'
  r=expand(s,'Which datasets?',[[0,17]]);self.assertEqual(len(r['added']),1);self.assertIn(b'configuration X',s[r['added'][0]['start_byte']:r['added'][0]['end_byte']])
 def test_budget_preserves_initial(self):
  s=b'Dataset A.\n\nDataset B is excluded.';r=expand(s,'Which datasets?',[[0,10]],10);self.assertEqual(r['ranges'],[[0,10]]);self.assertTrue(r['skipped'])
 def test_utf8_and_repeat(self):
  s='Datasets café.\n\nDataset café is excluded.\n\nDataset café is excluded.'.encode();n=len('Datasets café.'.encode());r=expand(s,'Which datasets?',[[0,n]]);self.assertEqual(len(r['added']),2)
  for c in r['added']:self.assertEqual(s[c['start_byte']:c['end_byte']].decode(),'Dataset café is excluded.')
 def test_no_cues_not_completeness(self):
  r=expand(b'Datasets A and B.','Which datasets?',[[0,17]]);self.assertEqual(r['added'],[]);self.assertEqual(r['semantic_completeness'],'not_established')
 def test_invalid_byte_boundary(self):
  with self.assertRaises(UnicodeDecodeError):expand('é'.encode(),'Q?',[[0,1]])
 def test_over_budget(self):
  with self.assertRaises(ValueError):expand(b'Dataset A.','Datasets?',[[0,10]],9)
if __name__=='__main__':unittest.main()
