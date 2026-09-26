"""Frozen paired comparison on new documents; no retry or prompt adaptation."""
from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess,sys,time
from agora.qasper import prepare,verify

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 b=Path(__file__).resolve().parent;root=b.parents[1]
 original=b/'inputs/test.json';provenance=json.loads((b/'inputs/provenance.json').read_text());assert sha(original)==provenance['test.json']['sha256']
 previous=b/'prepared/pilot-01';verify(previous)
 excluded={c['source_id'].split(':',1)[1] for c in json.loads((previous/'model_inputs/cases.json').read_text())}
 excluded.add('1911.10742') # schema example inspected during initial preparation
 data=json.loads(original.read_text());filtered={k:v for k,v in data.items() if k not in excluded}
 filtered_path=b/'inputs/test-excluding-pilot01.json'
 with filtered_path.open('x') as f:json.dump(filtered,f)
 prepared=b/'prepared/pilot-02';prepare(filtered_path,prepared)
 selected=json.loads((prepared/'model_inputs/cases.json').read_text());assert not {c['source_id'].split(':',1)[1] for c in selected}&excluded
 out=b/'runs/glm-paired-01';out.mkdir(exist_ok=False)
 shutil.copytree(root/'src/agora',out/'code/agora',ignore=shutil.ignore_patterns('__pycache__'))
 shutil.copytree(prepared/'model_inputs',out/'model_inputs');shutil.copyfile(__file__,out/'run_comparison.py')
 protocol={'model':'glm-5.3-flash','temperature':0,'language':'en','profiles':['legacy','concise-v1'],'max_calls':24,'output_tokens_per_call':8192,'socket_seconds':90,'process_seconds':110,'full_source_bytes':65536,'prompt_bytes':131072,'retries':0,'order':'alternate first profile by case index','failure_policy':'record timeout/format/generation failures and continue; stop HTTP/access/configuration/integrity errors','excluded_document_ids':sorted(excluded),'original_dataset_sha256':sha(original),'prepared_manifest_sha256':sha(prepared/'freeze.json'),'scope':'12 new-document diagnostic pairs, one draw each; not population estimate','started_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
 manifest={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};(out/'freeze.json').write_text(json.dumps(manifest,indent=2)+'\n')
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(out/'code'));rows=[]
 allowed={'timeout','answer_generation_incomplete','invalid_answer_shape','invalid_concise_answer_shape','answer_quote_mismatch','quote_outside_literal_passage'}
 for i,c in enumerate(selected):
  for profile in (['legacy','concise-v1'] if i%2==0 else ['concise-v1','legacy']):
   assert all(sha(out/n)==h for n,h in manifest.items())
   dest=out/profile/c['id']
   cmd=[sys.executable,'-m','agora.routed_cli','--source',str(out/'model_inputs'/c['source']),'--source-id',c['source_id'],'--sha256',c['sha256'],'--question',c['question'],'--parts',str(out/'model_inputs'/c['parts']),'--response-language','en','--answer-profile',profile,'--model','glm-5.3-flash','--full-source-budget','65536','--prompt-budget','131072','--max-output-tokens','8192','--timeout-seconds','90','--out',str(dest)]
   start=time.monotonic();row={'case':c['id'],'profile':profile}
   try:p=subprocess.run(cmd,env=env,timeout=110);row['exit_code']=p.returncode
   except subprocess.TimeoutExpired:row.update(exit_code=None,diagnostic='process_deadline',provider_outcome='unknown')
   row['seconds']=round(time.monotonic()-start,3);f=dest/'result.json';r=json.loads(f.read_text()) if f.exists() else {}
   row.update(result_sha256=sha(f) if f.exists() else None,status=r.get('execution_status','unknown'),diagnostic=r.get('diagnostic',row.get('diagnostic')),usage=r.get('response',{}).get('usage'))
   rows.append(row);(out/'execution.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps({**row,'usage':(row['usage'] or {}).get('total_tokens')}),flush=True)
   if r and (r.get('route')!='full_source' or (r.get('execution_status')!='complete' and r.get('diagnostic') not in allowed)):return 2
 assert all(sha(out/n)==h for n,h in manifest.items())
 return 0
if __name__=='__main__':raise SystemExit(main())
