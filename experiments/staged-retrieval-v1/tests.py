import unittest
from run import run,load,B
from stages import accumulate
class Tests(unittest.TestCase):
 def test_monotonic_and_budget(self):
  raw=b'abcdefghij';h=accumulate(raw,[(3,[[0,3]]),(6,[[4,7]]),(10,[[0,10]])])
  for prev,nxt in zip(h,h[1:]):
   self.assertTrue(all(any(x<=a and b<=y for x,y in nxt['ranges']) for a,b in prev['ranges']))
  for step in h:self.assertLessEqual(step['bytes'],step['budget'])
 def test_skipped_candidate_retried_without_new_input(self):
  h=accumulate(b'abcdefghij',[(3,[[0,5]]),(5,[])])
  self.assertEqual(h[0]['stop_reason'],'continue');self.assertEqual(h[1]['ranges'],[[0,5]])
 def test_no_gain_not_stop_when_future_candidate_remains(self):
  h=accumulate(b'abcdefghij',[(3,[[0,2]]),(4,[[0,2]]),(6,[[4,6]])])
  self.assertEqual(h[1]['added_bytes'],0);self.assertEqual(h[1]['stop_reason'],'continue');self.assertEqual(h[-1]['bytes'],4)
 def test_terminal_budget_does_not_claim_complete(self):
  h=accumulate(b'abcdefghij',[(3,[[0,10]])])
  self.assertEqual(h[-1]['stop_reason'],'budget_schedule_exhausted');self.assertEqual(h[-1]['semantic_completeness'],'not_established')
 def test_replay(self):self.assertEqual(run(),load(B/'result.json'))
if __name__=='__main__':unittest.main()
