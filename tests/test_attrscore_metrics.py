import importlib.util,unittest
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'experiments/attrscore-v1/score.py'
spec=importlib.util.spec_from_file_location('attrscore_metrics',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class AttrScoreMetricsTests(unittest.TestCase):
    def test_failures_remain_in_denominator(self):
        r=m.classification_scores({'a':'supported','b':'contradicted','c':'insufficient'},{'a':'supported','b':'failed'})
        self.assertEqual(r['correct'],1);self.assertEqual(r['accuracy_all_cases'],1/3);self.assertEqual(r['coverage'],1/3);self.assertEqual(r['failed'],1);self.assertEqual(r['not_run'],1);self.assertEqual(r['macro_f1'],1/3)
    def test_wrong_support_not_mixed_with_output_failure(self):
        r=m.classification_scores({'a':'supported','b':'contradicted','c':'insufficient'},{'a':'failed','b':'supported','c':'insufficient'})
        self.assertEqual(r['unsupported_accepted'],{'count':1,'denominator':2});self.assertEqual(r['supported_rejected']['count'],0);self.assertEqual(r['supported_failed_or_not_run'],1)
    def test_contradiction_vs_insufficiency_counts_as_error(self):
        r=m.classification_scores({'a':'supported','b':'contradicted','c':'insufficient'},{'a':'supported','b':'insufficient','c':'contradicted'})
        self.assertEqual(r['accuracy_all_cases'],1/3);self.assertEqual(r['coverage'],1);self.assertEqual(r['macro_f1'],1/3)
    def test_unknown_label_or_case_not_silently_mapped(self):
        with self.assertRaises(ValueError):m.classification_scores({'a':'supported'},{'a':'extra'})
        with self.assertRaises(ValueError):m.classification_scores({'a':'supported'},{'b':'supported'})
