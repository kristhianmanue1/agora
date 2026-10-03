import json,hashlib,subprocess,sys,os,argparse
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,required=True);parser.add_argument('--out',type=Path,required=True);options=parser.parse_args()
root=Path(__file__).resolve().parents[2];out=options.out.resolve();out.mkdir(exist_ok=False)
c=json.loads((root/'experiments/focused-label-v1/repair/case.json').read_text());receipt=json.loads((root/'experiments/focused-label-v1/repair/default-receipt.json').read_text());(out/'response.json').write_text(json.dumps(receipt['response'],ensure_ascii=False,indent=2)+'\n')
entry=[str(root/'.venv/bin/python'),str(root/'scripts/agora_issues.py'),'--workspace',str(out/'workspace')]
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');history=[]
def run(args):
 p=subprocess.run(args,capture_output=True,text=True,env=env,cwd=root);history.append(dict(args=args,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0,p.stderr+p.stdout
run(entry+['init'])
args=entry+['plan-passages','--source',str(options.source.resolve()),'--source-id',c['source_id'],'--source-sha256',c['source_sha256'],'--question',c['question'],'--budget','5000','--out',str(out/'plan.json')]
for r in c['ranges']:args+=['--range',f"{r['start_byte']}:{r['end_byte']}"]
run(args)
sha=hashlib.sha256((out/'plan.json').read_bytes()).hexdigest()
run(entry+['generate-plan','--source',str(options.source.resolve()),'--plan',str(out/'plan.json'),'--expected-plan-sha256',sha,'--question',c['question'],'--response',str(out/'response.json'),'--citation-mode','ids','--out',str(out/'replay')])
env['PYTHONPATH']=str(root/'src')
run([str(root/'.venv/bin/python'),'-m','agora.passage_view',str(out/'replay/result.json')])
(out/'commands.json').write_text(json.dumps(history,ensure_ascii=False,indent=2)+'\n')
r=json.loads((out/'replay/result.json').read_text());assert r['http_attempts']==0 and r['execution_origin']=='supplied_response_replay';assert r['missing']==receipt['missing'] and r['answer']==receipt['answer'];assert r['requires_expansion'] and not r['selection_verified'];print(json.dumps({'replay':'passed','http_attempts':0,'delivered_bytes':3224,'answer_status':r['answer_status'],'plan_sha256':sha}))
