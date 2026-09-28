"""Audit retrieval independent of scoring, then compare saved reviewer outputs."""
import argparse,hashlib,json,runpy
from pathlib import Path
from agora.source import FileSourceAdapter
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('glm',type=Path);p.add_argument('jev',type=Path);args=p.parse_args()
 for name,h in json.loads((BASE/'freeze.json').read_text()).items():assert sha((ROOT/name).read_bytes())==h,name
 cases=json.loads((BASE/'inputs/cases.json').read_text());gold=json.loads((BASE/'gold.json').read_text());selections=json.loads((BASE/'selection.json').read_text())
 recovery=runpy.run_path(str(BASE/'prepare.py'))['recover'];adapter=FileSourceAdapter(BASE/'inputs/source.txt','qasper:1811.00051')
 for row,case in zip(selections,cases):
  query,env,meta=recovery(adapter,row['source_sha256'],case['question'],case['claim'],row['budget'])
  assert query==row['query'] and meta==row['retrieval']
  assert [{k:s[k] for k in ('start_byte','end_byte','sha256')} for s in env['spans']]==row['ranges']
  assert sha(case['evidence'].encode())==row['evidence_sha256']
 transport=runpy.run_path(str(BASE.parent/'reviewer-comparison-v2/run.py'))
 score=runpy.run_path(str(BASE.parent/'reviewer-comparison-v1/score.py'))['score']
 result=dict(schema='agora/retrieved-expansion/v1-experimental',frozen_inputs_verified=True,retrieval_reproduced=True,providers={})
 for provider,directory in [('glm',args.glm),('jev',args.jev)]:
  manifest=json.loads((directory/'manifest.json').read_text());assert manifest['case_sha256']==sha((BASE/'inputs/cases.json').read_bytes())
  for case in cases:
   path=directory/(case['id']+'.json')
   if not path.exists():continue
   record=json.loads(path.read_text());_,request=transport['payload'](provider,case)
   assert record['request']==request and record['request_sha256']==sha(json.dumps(request,ensure_ascii=False).encode())
   if record['status']=='completed':assert record['label']==transport['engine'].label(provider,record['response'])
  result['providers'][provider]=score(directory,cases,gold)
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
