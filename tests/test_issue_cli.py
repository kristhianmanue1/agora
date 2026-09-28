import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
EX=ROOT/'examples/issues-v4'
class IssueCliTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.ws=self.root/'workspace';self.prepared=self.root/'prepared.json'
        self.env=dict(os.environ,PYTHONPATH=str(ROOT/'src'),PYTHONDONTWRITEBYTECODE='1')
        self.env.pop('ZAI_API_KEY',None)
    def cli(self,*args,code=0):
        proc=subprocess.run([sys.executable,'-m','agora.issue_cli','--workspace',str(self.ws),*map(str,args)],env=self.env,capture_output=True,text=True,timeout=15)
        self.assertEqual(proc.returncode,code,proc.stderr+proc.stdout)
        return json.loads(proc.stdout)
    def prepare(self):
        self.cli('init')
        seed=self.cli('seed','--issue','nube','--input',EX/'initial-input.json','--response',EX/'initial-response.json');self.head=seed['head']
        self.cli('prepare','--issue','nube','--expected-head',self.head,'--source',EX/'new-source.json','--as-of','2026-10-09','--out',self.prepared)
    def test_cli_valid_replay_recovery_preserves_origin(self):
        self.prepare()
        result=self.cli('evaluate','--operation','one','--prepared',self.prepared,'--response',EX/'response-simulated.json')
        self.assertEqual(result['execution_origin'],'supplied_response_replay')
        recovered=self.cli('recover','--operation','one')
        self.assertEqual(result['revision_sha256'],recovered['revision_sha256'])
        self.assertEqual(self.cli('inspect','--issue','nube')['revisions'],2)
    def test_cli_bad_json_repair_and_idempotent_apply(self):
        self.prepare();plan=self.root/'repair.json'
        self.cli('evaluate','--operation','bad','--prepared',self.prepared,'--response',EX/'response-format-error.json',code=2)
        self.assertEqual(self.cli('inspect','--operation','bad')['operation_state'],'response_ready')
        self.cli('recover','--operation','bad',code=2)
        proposal=self.cli('repair-propose','--operation','bad','--expected-head',self.head,'--out',plan)
        args=('repair-apply','--derivation','repair','--plan',plan,'--expected-plan-sha256',proposal['plan_sha256'])
        first=self.cli(*args);self.assertEqual(first,self.cli(*args))
        self.assertEqual(first['kind'],'host_format_repair')
        self.assertEqual(self.cli('inspect','--issue','nube')['revisions'],1)
        self.assertEqual(self.cli('inspect','--operation','bad')['operation_state'],'response_ready')
        self.assertEqual(self.cli('inspect','--derivation','repair')['derivation']['digest'],first['digest'])
    def test_no_workspace_or_output_overwrite(self):
        self.prepare();self.cli('init',code=2)
        before=self.prepared.read_bytes()
        self.cli('prepare','--issue','nube','--expected-head',self.head,'--source',EX/'new-source.json','--as-of','2026-10-09','--out',self.prepared,code=2)
        self.assertEqual(before,self.prepared.read_bytes())
    def test_live_without_key_does_not_reserve_operation(self):
        self.prepare()
        r=self.cli('evaluate','--operation','absent','--prepared',self.prepared,'--live',code=2)
        self.assertEqual(r['diagnostic'],'provider_key_missing')
        self.assertEqual(self.cli('inspect','--operation','absent',code=2)['diagnostic'],'unknown_operation')
    def test_wrong_plan_digest_does_not_incorporate(self):
        self.prepare();plan=self.root/'repair.json'
        self.cli('evaluate','--operation','bad','--prepared',self.prepared,'--response',EX/'response-format-error.json',code=2)
        self.cli('repair-propose','--operation','bad','--expected-head',self.head,'--out',plan)
        self.cli('repair-apply','--derivation','repair','--plan',plan,'--expected-plan-sha256','0'*64,code=2)
        self.cli('inspect','--derivation','repair',code=2)
    def test_replay_cannot_replace_saved_response(self):
        self.prepare()
        self.cli('evaluate','--operation','one','--prepared',self.prepared,'--response',EX/'response-simulated.json')
        r=self.cli('evaluate','--operation','one','--prepared',self.prepared,'--response',EX/'response-format-error.json',code=2)
        self.assertEqual(r['diagnostic'],'replay_response_conflict')
