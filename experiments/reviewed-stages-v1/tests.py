import unittest
from policy import decide
class Tests(unittest.TestCase):
 def coverage(self,*labels):return dict(status='complete',requirements=[dict(id=str(i),status=v) for i,v in enumerate(labels)])
 def fidelity(self,label='supported'):return dict(status='completed',label=label)
 def test_complete_is_candidate_not_admission(self):self.assertEqual(decide('complete',self.coverage('covered'),self.fidelity(),True),'candidate_ready_for_explicit_review')
 def test_missing_advances_only_with_fidelity(self):
  self.assertEqual(decide('complete',self.coverage('missing'),self.fidelity(),True),'expand')
  self.assertEqual(decide('complete',self.coverage('missing'),self.fidelity('requires_review'),True),'requires_fidelity_inspection')
 def test_budget_exhaustion_remains_insufficient(self):self.assertEqual(decide('complete',self.coverage('missing'),self.fidelity(),False),'insufficient_evidence')
 def test_invalid_generation_stops(self):self.assertEqual(decide('rejected',{}, {},True),'stop_invalid_generation')
 def test_review_failure_stops(self):
  self.assertEqual(decide('complete',dict(status='failed'),self.fidelity(),True),'stop_inconclusive_coverage')
  self.assertEqual(decide('complete',self.coverage('covered'),dict(status='failed'),True),'stop_inconclusive_fidelity')
 def test_contradiction_or_uncertainty_does_not_expand(self):
  for label in ('contradicted','uncertain'):self.assertEqual(decide('complete',self.coverage(label),self.fidelity(),True),'requires_coverage_inspection')
if __name__=='__main__':unittest.main()
