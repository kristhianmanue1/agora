import contextlib,io,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from agora import evidence_cli
from agora.source import digest

class EvidenceCliTests(unittest.TestCase):
    def test_policy_reaches_prompt_validator_and_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'s';source.write_text('Ada starts. Bruno ends.')
            aspects=root/'a';aspects.write_text('[{"id":"a","question":"Who starts and ends?"}]')
            argv=['evidence_cli','--source',str(source),'--source-id','test','--sha256',digest(source.read_bytes()),'--question','Who starts and ends?','--aspects',str(aspects),'--model','test','--response-language','en','--max-unit-bytes','1024','--max-quotes-per-part','1','--out',str(root/'out')]
            value={'parts':[{'id':'a','status':'answered','claims':[{'text':'Ada starts and Bruno ends.','quotes':['Ada starts.','Bruno ends.']}],'missing':[]}]}
            response={'choices':[{'finish_reason':'stop','message':{'content':json.dumps(value)}}]};requests=[]
            class Opener:
                def open(self,request,timeout):
                    requests.append(json.loads(request.data));return io.BytesIO(json.dumps(response).encode())
            with patch('sys.argv',argv),patch.dict('os.environ',{'ZAI_API_KEY':'test-key'}),patch('urllib.request.build_opener',return_value=Opener()),contextlib.redirect_stdout(io.StringIO()):code=evidence_cli.main()
            r=json.loads((root/'out/result.json').read_text())
            self.assertEqual(code,2);self.assertEqual(len(requests),1)
            self.assertIn('At most 1 quote',requests[0]['messages'][0]['content'])
            self.assertEqual(r['request_config']['response_language'],'en')
            self.assertEqual(r['request_config']['max_unit_bytes'],1024)
            self.assertIn('every claim text and missing item in English',requests[0]['messages'][0]['content'])
            self.assertEqual(r['policy']['max_quotes_per_part'],1)
            self.assertEqual(r['diagnostics'][0]['code'],'quote_count_exceeded')
