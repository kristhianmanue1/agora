import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from fusion import fuse
class Tests(unittest.TestCase):
 def test_both_channels_retained_when_they_fit(self):
  raw=b'Title\n\nAlpha\n\nBeta';r=fuse(raw,[[0,5],[7,12]],[[0,5],[14,18]],18)
  self.assertEqual(r['ranges'],[[0,5],[7,12],[14,18]]);self.assertEqual(r['bytes'],14)
 def test_overlap_is_counted_once(self):
  raw=b'Title\n\nabcdefghij';r=fuse(raw,[[7,14]],[[10,17]],15)
  self.assertEqual(r['bytes'],15);self.assertEqual(r['ranges'],[[0,5],[7,17]])
 def test_budget_preserves_title(self):
  raw=b'Title\n\nAlpha\n\nBeta'
  for budget in (5,6,10,14):
   r=fuse(raw,[[7,12]],[[14,18]],budget);self.assertIn([0,5],r['ranges']);self.assertLessEqual(r['bytes'],budget)
 def test_no_silent_utf8_split(self):
  with self.assertRaises(UnicodeDecodeError):fuse('Title\n\né'.encode(),[[7,8]],[],20)
 def test_reproduction_includes_failed_control(self):
  from run import run,load,B
  r=run();self.assertEqual(r,load(B/'result.json'));rows=[x for x in r['rows'] if x['mode']=='hybrid'];self.assertEqual(sum(x['covered_paragraphs']==x['reference_paragraphs'] for x in rows),3)
if __name__=='__main__':unittest.main()
