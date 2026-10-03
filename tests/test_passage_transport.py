import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from agora.passage_cli import main
from agora.source import digest

class PassageTransportTests(unittest.TestCase):
    def check_effort(self, effort):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);source=root/'source.txt';source.write_text('La nota 2 se excluye.')
            argv=['agora','--source',str(source),'--source-id','test','--sha256',digest(source.read_bytes()),
                  '--question','¿Qué se excluye?','--mode','source','--model','glm-5.3-flash','--out',str(root/'out')]
            if effort:argv+=['--reasoning-effort',effort]
            response={'model':'glm-5.3-flash','choices':[{'finish_reason':'stop','message':{'content':json.dumps({'parts':[{'id':'P1','status':'answer','answer':'Se excluye 2.','quotes':['La nota 2 se excluye.']}]})}}]}
            opener=MagicMock();opener.open.return_value.__enter__.return_value.read.return_value=json.dumps(response).encode()
            output=io.StringIO()
            with patch('sys.argv',argv),patch.dict(os.environ,{'ZAI_API_KEY':'fixture-secret'}),patch('urllib.request.build_opener',return_value=opener),contextlib.redirect_stdout(output):
                self.assertEqual(main(),0)
            shown=json.loads(output.getvalue())
            self.assertEqual(shown['answer'],'Se excluye 2.')
            self.assertIn('missing',shown)
            self.assertIsNone(shown['missing'])
            self.assertIn('answer_scope',shown)
            self.assertEqual(shown['semantic_support'],'not_verified')
            sent=json.loads(opener.open.call_args.args[0].data)
            config=json.loads((root/'out/result.json').read_text())['request_config']
            if effort:
                self.assertEqual(sent['reasoning_effort'],effort);self.assertEqual(config['reasoning_effort'],effort)
            else:
                self.assertNotIn('reasoning_effort',sent);self.assertNotIn('reasoning_effort',config)
            self.assertNotIn('thinking',sent)
            self.assertEqual(opener.open.call_count,1)
    def test_explicit_low_is_sent_and_recorded(self):self.check_effort('low')
    def test_omission_preserves_provider_default(self):self.check_effort(None)
