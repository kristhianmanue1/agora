import json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from agora.agent_cli import doctor,example,ENTRIES,describe

ROOT=Path(__file__).resolve().parents[1]
ENTRY=ROOT/'scripts/agora.py'
class AgentCliTests(unittest.TestCase):
    def call(self,*args,cwd=None):
        return subprocess.run([sys.executable,str(ENTRY),*args],cwd=cwd,capture_output=True,text=True,timeout=20)
    def test_catalog_has_runnable_entrypoints_and_effects(self):
        r=self.call('capabilities','--json');self.assertEqual(r.returncode,0)
        catalog=json.loads(r.stdout)
        self.assertEqual(catalog['schema'],'agora/capabilities/v1')
        self.assertEqual({c['id'] for c in catalog['capabilities']},set(ENTRIES))
        for c in catalog['capabilities']:
            self.assertTrue(Path(c['entrypoint']).is_file());self.assertTrue(Path(c['guide']).is_file())
            self.assertIn('network_effects',c);self.assertIn('filesystem_effects',c)
    def test_every_native_help_runs_from_unrelated_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            # An unrelated package must not replace the checkout's module entrypoint.
            shadow=Path(tmp)/'agora';shadow.mkdir();(shadow/'__init__.py').write_text('raise RuntimeError("wrong checkout")')
            for name in ENTRIES:
                with self.subTest(name=name):
                    r=self.call('run',name,'--help',cwd=tmp)
                    self.assertEqual(r.returncode,0,r.stderr);self.assertIn('usage:',r.stdout)
    def test_example_is_offline_preserves_unknowns_and_writes_nothing(self):
        with patch('socket.create_connection',side_effect=AssertionError('network forbidden')):
            report=example();self.assertFalse(report['result']['admitted'])
            self.assertEqual(report['result']['status'],'needs_more_evidence')
        with tempfile.TemporaryDirectory() as tmp:
            r=self.call('example','relations-offline','--json',cwd=tmp)
            self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(list(Path(tmp).iterdir()),[])
            self.assertEqual(json.loads(r.stdout)['network_calls'],0)
    def test_doctor_never_prints_secret_values(self):
        with patch.dict(os.environ,{'ZAI_API_KEY':'DO_NOT_DISPLAY_TEST_KEY'}):
            result=doctor();self.assertNotIn('DO_NOT_DISPLAY_TEST_KEY',json.dumps(result))
        self.assertEqual(result['network_calls'],0)
        with patch('agora.agent_cli.sys.version_info',(3,9,6)):
            self.assertEqual(doctor()['status'],'attention')
    def test_dispatch_preserves_native_failure(self):
        r=self.call('run','relations','validate')
        self.assertEqual(r.returncode,2);self.assertIn('required',r.stderr)
        self.assertEqual(self.call('run','unknown').returncode,2)
    def test_describe_and_example_discovery(self):
        r=self.call('describe','relation-run','--json');self.assertEqual(r.returncode,0)
        self.assertEqual(json.loads(r.stdout)['network_effects'],'explicit_live_only')
        commands=json.loads(self.call('examples','--json').stdout)['examples']
        self.assertEqual(commands[0]['id'],'relations-offline')
