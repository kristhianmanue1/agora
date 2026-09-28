"""Audit frozen requests, then report external and producer-control cohorts apart."""
import argparse,hashlib,json,runpy
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1]
shared=runpy.run_path(str(BASE.parent/'reviewer-comparison-v1/score.py'))['score']
transport=runpy.run_path(str(BASE/'run.py'))

def enrich(result):
 matrix=result['confusion_matrix'];f1=[]
 for label in ('supported','contradicted','insufficient'):
  tp=matrix[label][label];fn=sum(matrix[label].values())-tp
  fp=sum(row[label] for expected,row in matrix.items() if expected!=label)
  f1.append(2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0)
 result['macro_f1_fixed_three_classes']=sum(f1)/3
 result['no_valid_output']=result['total']-result['completed']
 return result

def audit(directory,cases):
 manifest=json.loads((directory/'manifest.json').read_text())
 assert manifest['case_sha256']==hashlib.sha256((BASE/'inputs/cases.json').read_bytes()).hexdigest()
 provider=manifest['provider']
 for case in cases:
  path=directory/(case['id']+'.json')
  if not path.exists():continue
  record=json.loads(path.read_text());_,payload=transport['payload'](provider,case)
  request_hash=hashlib.sha256(json.dumps(payload,ensure_ascii=False).encode()).hexdigest()
  assert record['case_id']==case['id'] and record['request']==payload and record['request_sha256']==request_hash
  if record['status']=='completed':assert transport['engine'].label(provider,record['response'])==record['label']

def main():
 p=argparse.ArgumentParser();p.add_argument('glm',type=Path);p.add_argument('jev',type=Path);args=p.parse_args()
 for name,digest in json.loads((BASE/'freeze.json').read_text()).items():
  assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest, name
 cases=json.loads((BASE/'inputs/cases.json').read_text());gold=json.loads((BASE/'gold.json').read_text())
 for directory in (args.glm,args.jev):audit(directory,cases)
 output={'schema':'agora/reviewer-comparison/v2-experimental','freeze_verified':True,'groups':{}}
 for group in ('attrscore','large_full','large_abstract'):
  selected=[c for c in cases if c['group']==group];subset={c['id']:gold[c['id']] for c in selected}
  results={provider:enrich(shared(directory,selected,subset)) for provider,directory in [('glm',args.glm),('jev',args.jev)]}
  pairs={'both_match_gold':0,'only_glm_matches':0,'only_jev_matches':0,'neither_matches':0}
  for g,j in zip(results['glm']['cases'],results['jev']['cases']):
   assert g['case_id']==j['case_id']
   yesg=g['predicted']==g['expected'];yesj=j['predicted']==j['expected']
   key='both_match_gold' if yesg and yesj else 'only_glm_matches' if yesg else 'only_jev_matches' if yesj else 'neither_matches'
   pairs[key]+=1
  results['paired']=pairs;output['groups'][group]=results
 print(json.dumps(output,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
