import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch,Mock,MagicMock
from agora import __main__ as cli
from agora.transform import snapshot,TransformError

class CliTests(unittest.TestCase):
    def run_cli(self, body, expected, opener, summary_limit=None, max_tokens=None, timeout_seconds=None):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'source.txt';source.write_bytes(body)
            out=Path(tmp)/'run'
            argv=['agora','--source',str(source),'--sha256',expected,'--source-id','fixture','--model','fixture','--out',str(out)]
            if summary_limit is not None: argv+=['--summary-max-bytes',str(summary_limit)]
            if max_tokens is not None: argv+=['--max-output-tokens',str(max_tokens)]
            if timeout_seconds is not None: argv+=['--timeout-seconds',str(timeout_seconds)]
            with patch.object(sys,'argv',argv),patch.dict(os.environ,{'ZAI_API_KEY':'synthetic-secret'}),patch('urllib.request.build_opener',return_value=opener),contextlib.redirect_stdout(io.StringIO()):
                code=cli.main()
            if code!=0:
                self.assertFalse((out/'summary.txt').exists())
                self.assertFalse((out/'evidence.json').exists())
            result=json.loads((out/'result.json').read_text())
            if code==0:
                self.assertEqual((out/'source.txt').read_bytes(),body)
                self.assertEqual((out/'reading.txt').read_bytes(),result['views']['reading'].encode('utf-8'))
                self.assertEqual((out/'summary.txt').read_text(),result['views']['summary'])
            else:
                self.assertFalse((out/'reading.txt').exists())
            return code,result
    def test_wrong_hash_makes_no_http_attempt(self):
        opener=Mock()
        code,result=self.run_cli(b'changed','0'*64,opener)
        self.assertEqual(code,2);self.assertEqual(result['http_attempts'],0)
        opener.open.assert_not_called()
    def test_transport_failure_not_retried_or_echoed(self):
        opener=Mock();opener.open.side_effect=RuntimeError('synthetic-secret')
        code,result=self.run_cli(b'source',hashlib.sha256(b'source').hexdigest(),opener)
        self.assertEqual(code,1);self.assertEqual(opener.open.call_count,1)
        self.assertEqual(result['http_attempts'],1)
        self.assertNotIn('synthetic-secret',json.dumps(result))
    def test_valid_response_records_finish_and_both_modules(self):
        reply={'model':'fixture','id':'synthetic','choices':[{'finish_reason':'stop','message':{'content':json.dumps({'claims':[{'text':'source','citations':[{'line':1,'quote':'source'}]}]})}}]}
        opener=Mock();response=MagicMock()
        response.__enter__.return_value.read.return_value=json.dumps(reply).encode();opener.open.return_value=response
        code,result=self.run_cli(b'source',hashlib.sha256(b'source').hexdigest(),opener)
        self.assertEqual(code,0);self.assertEqual(result['producer']['finish_reason'],'stop')
        self.assertEqual(set(result['implementation_hashes']),{'transform.py','__main__.py'})
    def test_truncated_response_emits_no_views(self):
        reply={'model':'fixture','id':'synthetic','choices':[{'finish_reason':'length','message':{'content':''}}]}
        opener=Mock();response=MagicMock()
        response.__enter__.return_value.read.return_value=json.dumps(reply).encode();opener.open.return_value=response
        code,result=self.run_cli(b'source',hashlib.sha256(b'source').hexdigest(),opener,700)
        self.assertEqual(code,2)
        self.assertEqual(result['diagnostic'],'generation_not_confirmed_complete')
        self.assertEqual(result['raw_output'],'')
        self.assertEqual(opener.open.call_count,1)
    def test_budget_override_reaches_request_and_receipt(self):
        reply={'model':'fixture','id':'synthetic','choices':[{'finish_reason':'stop','message':{'content':json.dumps({'claims':[{'text':'source','citations':[{'line':1,'quote':'source'}]}]})}}]}
        opener=Mock();response=MagicMock()
        response.__enter__.return_value.read.return_value=json.dumps(reply).encode();opener.open.return_value=response
        code,result=self.run_cli(b'source',hashlib.sha256(b'source').hexdigest(),opener,max_tokens=8192,timeout_seconds=180)
        self.assertEqual(code,0)
        request=opener.open.call_args.args[0]
        self.assertEqual(json.loads(request.data)['max_tokens'],8192)
        self.assertEqual(result['producer']['max_tokens'],8192)
        self.assertEqual(opener.open.call_args.kwargs['timeout'],180)
        self.assertEqual(result['request_config']['timeout_seconds'],180)
        self.assertEqual(opener.open.call_count,1)
    def test_invalid_token_budget_before_transport(self):
        opener=Mock()
        with contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit) as caught:
            self.run_cli(b'source',hashlib.sha256(b'source').hexdigest(),opener,max_tokens=8193)
        self.assertEqual(caught.exception.code,2)
        opener.open.assert_not_called()
    def test_invalid_timeout_before_transport(self):
        opener=Mock()
        with contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit) as caught:
            self.run_cli(b'source',hashlib.sha256(b'source').hexdigest(),opener,timeout_seconds=181)
        self.assertEqual(caught.exception.code,2)
        opener.open.assert_not_called()
    def test_size_and_encoding_boundaries(self):
        for data in [b'x'*4097,b'\xff']:
            with self.assertRaises(TransformError): snapshot(data,hashlib.sha256(data).hexdigest(),'s',[])
        self.assertEqual(len(snapshot(b'x'*4096,hashlib.sha256(b'x'*4096).hexdigest(),'s',[])['text']),4096)

if __name__=='__main__': unittest.main()
