import importlib.util
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

base=Path(__file__).resolve().parents[1]/'experiments/split-comparison-v1'
def load(name):
    spec=importlib.util.spec_from_file_location(name,base/(name+'.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
previous=sys.modules.get('audit');sys.modules['audit']=load('audit')
try:metrics=load('score')
finally:
    if previous is None:del sys.modules['audit']
    else:sys.modules['audit']=previous


class SplitComparisonMetricsTests(unittest.TestCase):
    def fixture(self, root):
        def save(name,value):
            p=root/name;p.write_text(json.dumps(value));return hashlib.sha256(p.read_bytes()).hexdigest()
        golden={'1-on':{'support':'supported','relevance':'relevant'},
                '1-off':{'support':'supported','relevance':'extra'}}
        checksum=save('gold.json',golden);save('freeze.json',{'gold.json':checksum})
        save('calls.json',[]);save('summary.json',{})
        result={'execution_status':'complete','assessment':{'claims':[golden['1-on']]}}
        checksum=save('1-on-combined.json',result)
        save('scores.json',[{'case':'1-on','mode':'combined','status':'complete','seconds':1,
              'result_sha256':checksum,'support_correct':True,'relevance_correct':True,'joint_correct':True}])
        return save

    def test_missing_case_is_not_a_successful_pair(self):
        with tempfile.TemporaryDirectory() as d:
            self.fixture(Path(d));r=metrics.score(d)
            self.assertEqual(r['combined']['joint_correct'],1)
            self.assertEqual(r['combined']['correct_pairs'],0)
            self.assertEqual(r['split']['complete'],0)
            self.assertEqual(r['split']['cases'][0]['status'],'not_attempted')

    def test_recorded_score_is_recomputed_not_trusted(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);save=self.fixture(root)
            rows=json.loads((root/'scores.json').read_text());rows[0]['joint_correct']=False
            save('scores.json',rows)
            with self.assertRaisesRegex(ValueError,'recorded_score_mismatch'):metrics.score(d)

    def test_changed_gold_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.fixture(root);(root/'gold.json').write_text('{}')
            with self.assertRaisesRegex(ValueError,'frozen_file_changed'):metrics.score(d)

    def test_unclosed_run_is_not_reported_as_final(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.fixture(root);(root/'summary.json').unlink()
            with self.assertRaisesRegex(ValueError,'run_in_progress_or_unclosed'):metrics.score(d)
