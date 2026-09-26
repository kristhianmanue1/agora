import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from agora import routed_cli
from agora.source import digest


class RoutedTransportTests(unittest.TestCase):
    def run_cli(self, mode=None, missing=False):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'source.txt'; source.write_text('Ada starts.')
            parts = root / 'parts.json'; parts.write_text('[{"id":"p","question":"Who starts?"}]')
            args = ['routed_cli', '--source', str(source), '--source-id', 'test', '--sha256', digest(source.read_bytes()), '--parts', str(parts), '--question', 'Who starts?', '--model', 'test', '--out', str(root / 'out')]
            if mode: args += ['--response-format', mode]
            answer = {'id': 'p', 'status': 'answer', 'answer': 'Ada', 'quotes': ['Ada starts.']}
            if missing: del answer['quotes']
            response = {'choices': [{'finish_reason': 'stop', 'message': {'content': json.dumps({'parts': [answer]})}}]}
            captured = []
            class Opener:
                def open(self, request, timeout):
                    captured.append(json.loads(request.data))
                    return io.BytesIO(json.dumps(response).encode())
            with patch('sys.argv', args), patch.dict('os.environ', {'ZAI_API_KEY': 'fake-test-key'}), patch('urllib.request.build_opener', return_value=Opener()), contextlib.redirect_stdout(io.StringIO()):
                code = routed_cli.main()
            return code, captured, json.loads((root / 'out/result.json').read_text())

    def test_default_omits_wire_parameter(self):
        code, requests, result = self.run_cli()
        self.assertEqual(code, 0)
        self.assertNotIn('response_format', requests[0])
        self.assertEqual(result['request_config']['response_format'], 'default')

    def test_json_mode_changes_only_wire_format(self):
        _, baseline, _ = self.run_cli()
        code, requests, result = self.run_cli('json_object')
        self.assertEqual(code, 0)
        self.assertEqual(requests[0].pop('response_format'), {'type': 'json_object'})
        self.assertEqual(requests, baseline)
        self.assertEqual(result['request_config']['response_format'], 'json_object')

    def test_json_mode_does_not_repair_missing_fields(self):
        code, requests, result = self.run_cli('json_object', missing=True)
        self.assertEqual(code, 2)
        self.assertEqual(len(requests), 1)
        self.assertEqual(result['execution_status'], 'rejected')
