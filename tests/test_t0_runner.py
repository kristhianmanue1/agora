import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
T0 = ROOT / 'experiments/evidence-answer-flow-t0-v1'
sys.path.insert(0, str(T0))
spec = importlib.util.spec_from_file_location('t0_runner', T0 / 'run.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
audit_spec = importlib.util.spec_from_file_location('t0_audit', T0 / 'audit.py')
auditor = importlib.util.module_from_spec(audit_spec)
audit_spec.loader.exec_module(auditor)


class AbstainingProvider:
    def __init__(self):
        self.calls = 0

    def __call__(self, system, user, *, model, max_output_tokens,
                 timeout_seconds, json_object):
        self.calls += 1
        if user.startswith('Source ID:'):
            value = {'status': 'insufficient', 'claims': [], 'missing': 'No answer.'}
        elif 'aspects' in json.loads(user):
            value = {'parts': [{'id': 'P1', 'status': 'not_in_passages',
                                'claims': [], 'missing': ['No answer.']}]}
        elif 'Criteria:' in system:
            value = {'coverage': 'justified_abstention'}
        else:
            value = {'status': 'no_omission_found', 'omissions': []}
        return {'content': json.dumps(value), 'finish_reason': 'stop',
                'requested_model': model, 'reported_model': model, 'usage': {}}


class T0RunnerTests(unittest.TestCase):
    def test_frozen_six_pairs_and_no_reuse(self):
        with tempfile.TemporaryDirectory() as tmp:
            provider = AbstainingProvider()
            out = Path(tmp) / 'run'
            result = runner.run(out, provider)
            self.assertEqual(result['status'], 'complete_execution')
            self.assertEqual(len(result['pairs']), 6)
            self.assertEqual([row['order'] for row in result['pairs']],
                             ['AB', 'BA', 'AB', 'BA', 'AB', 'BA'])
            self.assertEqual(provider.calls, 24)
            self.assertTrue(all(set(row['arms']) == {'A', 'B'} for row in result['pairs']))
            self.assertTrue(all(row['arms']['A']['dispatches'] == 1 and
                                row['arms']['B']['dispatches'] == 3
                                for row in result['pairs']))
            audited = auditor.audit(out)
            self.assertEqual(audited['denominator'], 6)
            self.assertEqual(audited['dispatches'], 24)
            self.assertEqual(audited['responses'], 24)
            with self.assertRaises(FileExistsError):
                runner.run(out, provider)
            self.assertEqual(provider.calls, 24)


if __name__ == '__main__':
    unittest.main()
