import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('bank',Path(__file__).resolve().parents[1]/'scripts/verify_benchmark_evidence.py')
bank=importlib.util.module_from_spec(spec);spec.loader.exec_module(bank)

class BenchmarkEvidenceTests(unittest.TestCase):
    def test_tampered_artifact_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'result';p.write_bytes(b'original')
            records=[dict(path='result',sha256=hashlib.sha256(p.read_bytes()).hexdigest())]
            bank.verify_files(d,records)
            p.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'artifact_hash_mismatch'):bank.verify_files(d,records)
    def test_outside_path_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,'invalid_or_duplicate_artifact_path'):
                bank.verify_files(d,[dict(path='../outside',sha256='0'*64)])
    def test_failed_cases_remain_in_denominator(self):
        rows=[dict(id='q1',agora_status='rejected',agora_usage=dict(total_tokens=7))]
        r=bank.accounting(rows,[],{'q1':{}})
        self.assertEqual(r['cases'],1);self.assertEqual(r['agora_rejected'],1)
        self.assertEqual(r['agora_observed_tokens'],7)
        with self.assertRaisesRegex(ValueError,'case_denominator_mismatch'):bank.accounting(rows,[],{})
    def test_invented_token_total_rejected(self):
        row=dict(file='call',usage_events=[dict(id='receipt',usage=dict(total_tokens=5))],reported_total_tokens=0)
        with self.assertRaisesRegex(ValueError,'usage_subtotal_mismatch'):bank.accounting([], [row], {})

if __name__=='__main__':unittest.main()
