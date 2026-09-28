"""Preserve both outcomes and score each against its own supplied evidence."""
import argparse,hashlib,json,runpy
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def score(directories):
 for file in ('freeze.json','parent-hashes.json'):
  for name,h in json.loads((BASE/file).read_text()).items():assert sha((ROOT/name).read_bytes())==h,name
 cases=json.loads((BASE/'inputs/cases.json').read_text());gold=json.loads((BASE/'gold.json').read_text());parents=json.loads((BASE/'originals.json').read_text())
 lineage={r['id']:r for r in json.loads((BASE/'lineage.json').read_text())}
 transport=runpy.run_path(str(BASE.parent/'reviewer-comparison-v2/run.py'))
 result=dict(schema='agora/evidence-expansion/v1-experimental',frozen_inputs_verified=True,parent_artifacts_unchanged=True,providers={})
 for provider,directory in directories.items():
  manifest=json.loads((directory/'manifest.json').read_text());assert manifest['case_sha256']==sha((BASE/'inputs/cases.json').read_bytes()) and manifest['provider']==provider
  scored=[];usage={};seconds=0
  for case in cases:
   path=directory/(case['id']+'.json');r=json.loads(path.read_text()) if path.exists() else {'status':'not_attempted'}
   if path.exists():
    _,payload=transport['payload'](provider,case)
    assert r['request']==payload and r['request_sha256']==sha(json.dumps(payload,ensure_ascii=False).encode())
   predicted=r.get('label') if r['status']=='completed' else 'no_valid_output'
   if r['status']=='completed':assert transport['engine'].label(provider,r['response'])==predicted
   original=next(p for p in parents[provider] if p['case_id']==lineage[case['id']]['parent_case_id'])
   scored.append(dict(id=case['id'],condition=case['condition'],repeat=case['repeat'],status=r['status'],expected=gold[case['id']],predicted=predicted,original_label=original['label'],parent_response_sha256=sha(json.dumps(original['response'],sort_keys=True).encode()),changed_from_original=predicted!='no_valid_output' and predicted!=original['label'],correct=predicted==gold[case['id']]))
   for k,v in (r.get('response',{}).get('usage') or {}).items():
    if type(v) is int:usage[k]=usage.get(k,0)+v
   seconds+=r.get('elapsed_seconds',0)
  conditions={}
  for condition in ('baseline','control','target'):
   items=[r for r in scored if r['condition']==condition]
   pairs=[]
   for index in range(2):
    pair=[r for r in items if r['id'].startswith(f'claim{index}-')]
    pairs.append(len(pair)==2 and all(r['status']=='completed' for r in pair) and pair[0]['predicted']==pair[1]['predicted'])
   conditions[condition]=dict(total=len(items),completed=sum(r['status']=='completed' for r in items),correct=sum(r['correct'] for r in items),false_support=sum(r['predicted']=='supported' and r['expected']!='supported' for r in items),matching_repeat_pairs=sum(pairs),repeat_pairs=2)
  result['providers'][provider]=dict(conditions=conditions,usage=usage,sum_request_seconds=round(seconds,3),cases=scored)
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('glm',type=Path);p.add_argument('jev',type=Path);args=p.parse_args()
 print(json.dumps(score({'glm':args.glm,'jev':args.jev}),ensure_ascii=False,indent=2))
