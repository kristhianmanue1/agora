import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import unittest
from unittest import mock
from pathlib import Path

from agora.evidence_answer_flow import PROFILE_SCHEMA, ZaiProvider, run_flow, replay_flow


class FakeProvider:
    def __init__(self, *, fail_stage=None, reported_model=None, abstain=False,
                 coverage="complete", omission="no_omission_found"):
        self.calls = []
        self.fail_stage = fail_stage
        self.reported_model = reported_model
        self.abstain = abstain
        self.coverage = coverage
        self.omission = omission

    def __call__(self, system, user, *, model, max_output_tokens,
                 timeout_seconds, json_object):
        if 'evidence_units' in json.loads(user) and 'aspects' in json.loads(user):
            stage = 'generation'
        elif 'Assess each self-contained claim' in system:
            stage = 'support'
        elif 'Assess whether each claim' in system:
            stage = 'relevance'
        elif 'Criteria:' in system:
            stage = 'coverage'
        else:
            stage = 'omission'
        self.calls.append(stage)
        if stage == self.fail_stage:
            raise TimeoutError('simulated timeout')
        if stage == 'generation':
            evidence_id = json.loads(user)['evidence_units'][0]['id']
            part = {'id': 'P1', 'status': 'not_in_passages' if self.abstain else 'answered',
                    'claims': [] if self.abstain else [
                        {'text': 'Atlas scored 91%.', 'evidence_ids': [evidence_id]}],
                    'missing': ['Answer unavailable.'] if self.abstain else []}
            value = {'parts': [part]}
        elif stage == 'support':
            value = {'claims': [{'id': 0, 'support': 'supported',
                                 'quote_indices': [0], 'reason': 'Exact quote.'}]}
        elif stage == 'relevance':
            value = {'claims': [{'id': 0, 'relevance': 'relevant',
                                 'reason': 'Answers the task.'}]}
        elif stage == 'coverage':
            value = {'coverage': self.coverage}
        else:
            if self.omission == 'proposed_omissions':
                evidence_id = json.loads(user)['evidence_units'][0]['id']
                value = {'status': self.omission,
                         'omissions': [{'missing': 'Atlas score.', 'evidence_ids': [evidence_id]}]}
            else:
                value = {'status': self.omission, 'omissions': []}
        return {'content': json.dumps(value), 'finish_reason': 'stop',
                'requested_model': model,
                'reported_model': self.reported_model or model, 'usage': {'total_tokens': 7}}


class EvidenceAnswerFlowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'source.txt'
        self.source.write_text('Atlas scored 91%.', encoding='utf-8')
        self.sha = hashlib.sha256(self.source.read_bytes()).hexdigest()

    def run_case(self, name, provider, **kwargs):
        return run_flow(self.source, 'source-1', self.sha, 'What was Atlas score?',
                        ['Give the score.'], self.root / name, provider, **kwargs)

    def test_full_flow_and_replay(self):
        provider = FakeProvider()
        result = self.run_case('run', provider)
        self.assertEqual(result['status'], 'candidate_reviewed')
        self.assertEqual(provider.calls, ['generation', 'support', 'relevance',
                                          'coverage', 'omission'])
        self.assertEqual(result['dispatches'], 5)
        self.assertEqual(result['memory_admission'], 'not_performed')
        self.assertEqual(replay_flow(self.root / 'run', self.source,
                                     self.root / 'replay')['stages'], result['stages'])

    def test_agent_entry_replays_recorded_flow_without_provider(self):
        original = self.run_case('recorded', FakeProvider())
        entry = Path(__file__).resolve().parents[1] / 'scripts/agora.py'
        result = subprocess.run([sys.executable, str(entry), 'run', 'answer',
                                 '--source', str(self.source), '--out', str(self.root / 'via-agent'),
                                 '--replay-run', str(self.root / 'recorded')],
                                cwd=self.root, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        replayed = json.loads((self.root / 'via-agent/result.json').read_text())
        self.assertEqual(replayed['stages'], original['stages'])
        self.assertEqual(replayed['provider_id'], 'replay')

    def test_timeout_preserves_attempt_and_never_retries(self):
        provider = FakeProvider(fail_stage='support')
        result = self.run_case('timeout', provider)
        self.assertEqual(result['status'], 'remote_outcome_unknown')
        self.assertEqual(provider.calls, ['generation', 'support'])
        attempt = json.loads((self.root / 'timeout' / '02-support-attempt.json').read_text())
        self.assertEqual(attempt['remote_outcome'], 'unknown')
        self.assertEqual(json.loads((self.root / 'timeout' / 'result.json').read_text())['dispatches'], 2)
        self.assertFalse((self.root / 'timeout' / '03-relevance-attempt.json').exists())

    def test_wrong_source_rejected_before_dispatch_and_replay(self):
        provider = FakeProvider()
        self.source.write_text('Boreal scored 91%.', encoding='utf-8')
        result = self.run_case('changed', provider)
        self.assertEqual(result['status'], 'rejected')
        self.assertEqual(result['dispatches'], 0)
        self.assertFalse(provider.calls)
        self.source.write_text('Atlas scored 91%.', encoding='utf-8')
        self.run_case('original', FakeProvider())
        self.source.write_text('Boreal scored 91%.', encoding='utf-8')
        with self.assertRaises(ValueError):
            replay_flow(self.root / 'original', self.source, self.root / 'replay-bad')

    def test_model_discrepancy_blocks_following_stages(self):
        result = self.run_case('mismatch', FakeProvider(reported_model='other'))
        self.assertEqual(result['status'], 'incomplete')
        self.assertEqual(result['dispatches'], 1)
        self.assertTrue((self.root / 'mismatch' / '01-generation-response.json').exists())
        outcome = json.loads((self.root / 'mismatch' / '01-generation-outcome.json').read_text())
        self.assertEqual(outcome['remote_outcome'], 'received')

    def test_http_401_is_recorded_without_retry_or_body(self):
        class Refused:
            calls = 0

            def __call__(self, *args, **kwargs):
                self.calls += 1
                raise urllib.error.HTTPError('https://example.invalid', 401,
                                             'secret-bearing message', {}, None)

        provider = Refused()
        result = self.run_case('http-401', provider)
        self.assertEqual(result['status'], 'incomplete')
        self.assertEqual(provider.calls, 1)
        outcome = json.loads((self.root / 'http-401' / '01-generation-outcome.json').read_text())
        self.assertEqual((outcome['http_status'], outcome['remote_outcome']),
                         (401, 'http_rejected'))
        self.assertNotIn('secret-bearing', (self.root / 'http-401' / 'result.json').read_text())

    def test_malformed_and_truncated_generation_stop_before_review(self):
        class Bad(FakeProvider):
            def __init__(self, finish):
                super().__init__()
                self.finish = finish

            def __call__(self, *args, **kwargs):
                response = super().__call__(*args, **kwargs)
                response['content'] = '{'
                response['finish_reason'] = self.finish
                return response

        for finish in ('stop', 'length'):
            with self.subTest(finish=finish):
                provider = Bad(finish)
                result = self.run_case('bad-' + finish, provider)
                self.assertEqual(result['status'], 'incomplete')
                self.assertEqual(result['dispatches'], 1)
                self.assertEqual(provider.calls, ['generation'])
                self.assertTrue((self.root / ('bad-' + finish) /
                                 '01-generation-response.json').exists())

    def test_llavero_credential_alias_reaches_transport(self):
        class Opener:
            def open(self, request, timeout):
                self.authorization = request.get_header('Authorization')
                return io.BytesIO(json.dumps({
                    'choices': [{'message': {'content': '{}'}, 'finish_reason': 'stop'}],
                    'model': 'glm-5.3-flash', 'id': 'r1', 'usage': {}}).encode())

        opener = Opener()
        with mock.patch.dict(os.environ, {'ZAI_API_KEY': '',
                                          'SKOPOS_LLM_API_KEY': 'test-placeholder'}):
            with mock.patch('urllib.request.build_opener', return_value=opener):
                result = ZaiProvider()('system', 'user', model='glm-5.3-flash',
                                       max_output_tokens=32, timeout_seconds=30,
                                       json_object=True)
        self.assertEqual(opener.authorization, 'Bearer test-placeholder')
        self.assertEqual(result['reported_model'], 'glm-5.3-flash')
        self.assertIn('sent_payload_sha256', result)

    def test_versioned_profile_changes_recorded_request_and_replays(self):
        profile = {'schema': PROFILE_SCHEMA, 'id': 'failed-slots-v2',
                   'generation_system_suffix': 'Return concise complete JSON.',
                   'support_max_output_tokens': 4096,
                   'relevance_max_output_tokens': 2048}
        result = self.run_case('profile', FakeProvider(), profile=profile)
        self.assertEqual(result['status'], 'candidate_reviewed')
        candidate = json.loads((self.root / 'profile/candidate.json').read_text())
        self.assertIn(profile['generation_system_suffix'], candidate['prompt']['system'])
        support = json.loads((self.root / 'profile/02-support-attempt.json').read_text())
        self.assertEqual(support['max_output_tokens'], 4096)
        self.assertEqual(replay_flow(self.root / 'profile', self.source,
                                     self.root / 'profile-replay')['stages'], result['stages'])
        with self.assertRaises(ValueError):
            self.run_case('invalid-profile', FakeProvider(),
                          profile={**profile, 'support_max_output_tokens': 999999})
        self.assertFalse((self.root / 'invalid-profile').exists())

    def test_abstention_skips_claim_review(self):
        provider = FakeProvider(abstain=True, coverage='justified_abstention')
        result = self.run_case('abstain', provider)
        self.assertEqual(result['status'], 'candidate_reviewed')
        self.assertEqual(result['stages']['claim_review']['status'], 'not_run')
        self.assertEqual(provider.calls, ['generation', 'coverage', 'omission'])

    def test_disagreement_is_visible_and_not_adjudicated(self):
        result = self.run_case('disagree', FakeProvider(omission='proposed_omissions'))
        self.assertEqual(result['status'], 'review_disagreement')
        self.assertEqual(result['stages']['coverage']['coverage'], 'complete')
        self.assertTrue(result['stages']['omission']['review_disagreement'])
        self.assertEqual(result['adjudication'], 'not_performed')

    def test_process_interruption_leaves_durable_attempt(self):
        out = self.root / 'interrupted'
        script = '''import sys,time
from agora.evidence_answer_flow import run_flow
class Slow:
 def __call__(self,*args,**kwargs):time.sleep(30)
run_flow(sys.argv[1],'source-1',sys.argv[2],'What was Atlas score?',
 ['Give the score.'],sys.argv[3],Slow())'''
        env = os.environ.copy()
        env['PYTHONPATH'] = 'src'
        proc = subprocess.Popen([sys.executable, '-c', script, str(self.source),
                                 self.sha, str(out)], cwd=Path(__file__).resolve().parents[1],
                                env=env)
        try:
            deadline = time.monotonic() + 5
            while not (out / '01-generation-attempt.json').exists() and time.monotonic() < deadline:
                time.sleep(.02)
            self.assertTrue((out / '01-generation-attempt.json').exists())
        finally:
            proc.kill()
            proc.wait(timeout=5)
        attempt = json.loads((out / '01-generation-attempt.json').read_text())
        self.assertEqual(attempt['state'], 'attempted')
        self.assertEqual(attempt['remote_outcome'], 'unknown')
        self.assertFalse((out / 'result.json').exists())


if __name__ == '__main__':
    unittest.main()
