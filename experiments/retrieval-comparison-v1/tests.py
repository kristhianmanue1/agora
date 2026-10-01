import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from retrieval_variants import select,VARIANTS,cost
class Tests(unittest.TestCase):
 def test_preserves_utf8_and_budget(self):
  raw='Title\n\nCafé models described.\n\nModels compared.\n\nOther data.'.encode();env=dict(spans=[dict(text=raw.decode())],source=dict(source_bytes=len(raw)))
  for v in VARIANTS:
   r=select(env,'Which models are used?',[[0,7],[7,len(raw)]],v,35)
   self.assertLessEqual(r['bytes'],35);self.assertEqual(r['bytes'],cost(r['ranges']));self.assertTrue(any(a==0 and b>=5 for a,b in r['ranges']))
   for a,b in r['ranges']:raw[a:b].decode()
 def test_no_matching_terms_never_implies_complete(self):
  raw=b'Title\n\nUnrelated prose.';env=dict(spans=[dict(text=raw.decode())],source=dict(source_bytes=len(raw)))
  for v in VARIANTS:
   r=select(env,'zzzz?',[[0,len(raw)]],v,100)
   self.assertEqual(r['ranges'],[[0,5]]);self.assertFalse(r['retrieval']['search_exhaustive_for_meaning'])
 def test_positive_control_recovers_list_tail(self):
  raw=b'Title\n\nMetrics described here.\n\nDetails follow.\n\nAlpha and Beta.';env=dict(spans=[dict(text=raw.decode())],source=dict(source_bytes=len(raw)))
  for v in VARIANTS:
   r=select(env,'Which metrics?',[[0,7],[7,len(raw)]],v,100)
   self.assertTrue(any(b'Alpha and Beta.' in raw[a:b] for a,b in r['ranges']))
 def test_reproduction(self):
  from run import run,load,B
  self.assertEqual(run(),load(B/'result.json'))
if __name__=='__main__':unittest.main()
