import importlib.util
from pathlib import Path
import unittest

p=Path(__file__).resolve().parents[1]/'experiments/review-controls-v1/score.py'
spec=importlib.util.spec_from_file_location('control_scores',p)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class ControlMetricsTests(unittest.TestCase):
    def setUp(self):
        self.pos=dict(support='supported',relevance='relevant',language='match',recommendation='needs_adjudication')
        self.neg=dict(support='supported',relevance='extra',language='match',recommendation='needs_revision')
        self.gold={'p':dict(pair='year',dimension='relevance',positive=True,expected=self.pos),
                   'n':dict(pair='year',dimension='relevance',positive=False,expected=self.neg)}
    def test_always_revision_cannot_pass_positive_or_pair(self):
        r=m.scores(self.gold,{'p':dict(self.pos,recommendation='needs_revision'),'n':self.neg})
        self.assertEqual(r['axis_correct']['support'],2)
        self.assertEqual(r['pairs_correct'],0)
        self.assertEqual(r['positive_correct'],0)
        self.assertEqual(r['negative_correct'],1)
    def test_failures_and_missing_remain_in_denominators(self):
        r=m.scores(self.gold,{'p':'failed'})
        self.assertEqual(r['cases'],2)
        self.assertEqual(r['statuses'],{'failed':1,'not_run':1})
        self.assertEqual(r['pairs_correct'],0)
    def test_support_does_not_substitute_for_relevance(self):
        r=m.scores(self.gold,{'p':self.pos,'n':self.pos})
        self.assertEqual(r['axis_correct']['support'],2)
        self.assertEqual(r['axis_correct']['relevance'],1)
        self.assertEqual(r['pairs_correct'],0)
        self.assertEqual(m.scores(self.gold,{'p':self.pos,'n':self.neg})['pairs_correct'],1)
    def test_unknown_cases_incomplete_pairs_and_invalid_predictions_rejected(self):
        for gold,predictions in [(self.gold,{'x':self.pos}),({'p':self.gold['p']},{}),(self.gold,{'p':{}})]:
            with self.assertRaises(ValueError):m.scores(gold,predictions)
