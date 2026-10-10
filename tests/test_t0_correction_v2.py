import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
T0 = ROOT / 'experiments/evidence-answer-flow-t0-v1'
sys.path.insert(0, str(T0))
spec = importlib.util.spec_from_file_location('t0_correction_v2', T0 / 'run_failed_slots_v2.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class AbstainingProvider:
    def __init__(self):
        self.calls = 0

    def __call__(self, system, user, *, model, max_output_tokens,
                 timeout_seconds, json_object):
        self.calls += 1
        if 'aspects' in json.loads(user):
            value = {'parts': [{'id': 'P1', 'status': 'not_in_passages',
                                'claims': [], 'missing': ['No answer.']}]}
        elif 'Criteria:' in system:
            value = {'coverage': 'justified_abstention'}
        else:
            value = {'status': 'no_omission_found', 'omissions': []}
        return {'content': json.dumps(value), 'finish_reason': 'stop',
                'requested_model': model, 'reported_model': model, 'usage': {}}


class T0CorrectionTests(unittest.TestCase):
    def test_only_three_frozen_failed_slots_and_code_hashes(self):
        with tempfile.TemporaryDirectory() as temp:
            provider = AbstainingProvider()
            out = Path(temp) / 'correction'
            result = runner.run(out, provider)
            self.assertEqual(result['status'], 'complete_execution')
            self.assertEqual(result['selected_slots'], ['case-03', 'case-04', 'case-06'])
            self.assertEqual(provider.calls, 9)
            self.assertEqual([r['correction_status'] for r in result['rows']],
                             ['candidate_reviewed'] * 3)
            self.assertEqual(result['base_denominator'], 6)
            self.assertEqual(len(result['implementation_sha256']), 7)
            self.assertEqual(set(p.name for p in out.iterdir()),
                             {'result.json', 'case-03', 'case-04', 'case-06'})
            with self.assertRaises(FileExistsError):
                runner.run(out, provider)
            self.assertEqual(provider.calls, 9)


if __name__ == '__main__':
    unittest.main()
