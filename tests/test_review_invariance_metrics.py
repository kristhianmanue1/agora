import importlib.util,unittest
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'experiments/review-invariance-v1/score.py';s=importlib.util.spec_from_file_location('invariance_scores',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class InvarianceTests(unittest.TestCase):
 def setUp(self):
  self.a=dict(support='insufficient',relevance='relevant',language='match',recommendation='needs_revision');self.b=dict(self.a,relevance='extra')
  self.gold={'a':dict(pair='p',origin='new',expected=self.a),'b':dict(pair='p',origin='new',expected=self.b)}
 def test_stable_wrong_is_not_correct(self):
  r=m.scores(self.gold,{'a':dict(self.a,support='contradicted'),'b':dict(self.b,support='contradicted')})
  self.assertEqual(r['stable_pairs'],1);self.assertEqual(r['correct_pairs'],0)
 def test_same_support_different_relevance_passes(self):
  r=m.scores(self.gold,{'a':self.a,'b':self.b});self.assertEqual(r['correct_pairs'],1)
 def test_failed_or_missing_pair_cannot_pass_invariance(self):
  r=m.scores(self.gold,{'a':'failed'});self.assertEqual(r['failed'],1);self.assertEqual(r['not_run'],1);self.assertEqual(r['stable_pairs'],0)
 def test_stable_support_wrong_relevance_still_fails(self):
  r=m.scores(self.gold,{'a':self.a,'b':self.a});self.assertEqual(r['stable_pairs'],1);self.assertEqual(r['correct_pairs'],0)
