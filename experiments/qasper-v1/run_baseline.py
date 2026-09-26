"""One sequential baseline campaign; no automatic retries or reference access."""
from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess,sys,time

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 base=Path(__file__).resolve().parent;root=base.parents[1];prepared=base/'prepared/pilot-01'
 # Verify sealed files without parsing reference labels.
 for name,h in json.loads((prepared/'freeze.json').read_text()).items():
  assert digest(prepared/name)==h,name
 out=base/'runs/glm-baseline-01';out.mkdir(exist_ok=False)
 shutil.copytree(root/'src/agora',out/'code/agora',ignore=shutil.ignore_patterns('__pycache__'))
 shutil.copytree(prepared/'model_inputs',out/'model_inputs')
 shutil.copyfile(__file__,out/'run_baseline.py')
 protocol={'model':'glm-5.3-flash','temperature':0,'language':'en','max_calls':12,'output_tokens_per_call':8192,'socket_seconds':90,'process_seconds':110,'full_source_bytes':65536,'prompt_bytes':131072,'retries':0,'timeout_policy':'record and continue next case','stop_policy':'any non-timeout operational failure or integrity/configuration failure','prepared_manifest_sha256':digest(prepared/'freeze.json'),'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
 manifest={str(p.relative_to(out)):digest(p) for p in out.rglob('*') if p.is_file()}
 (out/'freeze.json').write_text(json.dumps(manifest,indent=2)+'\n')
 env=dict(os.environ,PYTHONPATH=str(out/'code'),PYTHONDONTWRITEBYTECODE='1');rows=[]
 for c in json.loads((out/'model_inputs/cases.json').read_text()):
  assert all(digest(out/n)==h for n,h in manifest.items())
  cmd=[sys.executable,'-m','agora.routed_cli','--source',str(out/'model_inputs'/c['source']),'--source-id',c['source_id'],'--sha256',c['sha256'],'--question',c['question'],'--parts',str(out/'model_inputs'/c['parts']),'--response-language','en','--model','glm-5.3-flash','--full-source-budget','65536','--prompt-budget','131072','--max-output-tokens','8192','--timeout-seconds','90','--out',str(out/c['id'])]
  start=time.monotonic();row={'case':c['id'],'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  try:
   p=subprocess.run(cmd,env=env,timeout=110);row['exit_code']=p.returncode
  except subprocess.TimeoutExpired:row.update(exit_code=None,diagnostic='process_deadline',provider_outcome='unknown')
  row['seconds']=round(time.monotonic()-start,3)
  f=out/c['id']/'result.json'
  r=json.loads(f.read_text()) if f.exists() else {}
  row.update(result_sha256=digest(f) if f.exists() else None,execution_status=r.get('execution_status','unknown'),answer_status=r.get('answer_status'),diagnostic=r.get('diagnostic',row.get('diagnostic')),usage=r.get('response',{}).get('usage'))
  rows.append(row);(out/'execution.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
  if r and r.get('execution_status')!='complete' and r.get('diagnostic')!='timeout':break
  if r and r.get('route')!='full_source':break
 assert all(digest(out/n)==h for n,h in manifest.items())
 return 0 if len(rows)==12 else 2
if __name__=='__main__':raise SystemExit(main())
