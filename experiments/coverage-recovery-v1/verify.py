"""Offline CLI regression; oracle ranges used only after retrieval for scoring."""
import hashlib,json,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from agora.issue_cli import main
BASE=ROOT/'experiments/condition-expansion-heldout-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 source=BASE/'inputs/expanded.txt';candidate=BASE/'runs-glm/expanded/candidate.json'
 rubric=BASE/'expanded-rubric.json';review=BASE/'runs-review-expanded/result.json'
 files=dict(source=source,candidate=candidate,rubric=rubric,review=review)
 before={k:sha(v) for k,v in files.items()}
 with tempfile.TemporaryDirectory() as temp:
  workspace=str(Path(temp)/'workspace');out=Path(temp)/'proposal.json'
  assert main(['--workspace',workspace,'init'])==0
  args=['--workspace',workspace,'coverage-plan','--part-id','P1','--question','What metrics are used to measure bias reduction?','--query','metrics','--query-origin','Explicit term copied from original question; regression design informed by known gap','--budget','12000','--top-k','3','--following','3','--out',str(out)]
  for key,path in files.items():args.extend(['--'+key,str(path),'--'+key+'-sha256',before[key]])
  assert main(args)==0
  proposal=json.loads(out.read_text());ranges=proposal['ranges']
  assert proposal['status']=='proposed' and proposal['delivered_bytes']<=12000
  assert proposal['provider_calls']==0
  assert all(any(a<=x and y<=b for a,b in ranges) for x,y in proposal['initial_ranges'])
  coverage={r['id']:any(a<=r['evidence']['start_byte'] and r['evidence']['end_byte']<=b for a,b in ranges) for r in json.loads(rubric.read_text())['requirements']}
  assert coverage['R2'] and coverage['R3'],coverage
  original=out.read_bytes();assert main(args)==2;assert out.read_bytes()==original
  assert before=={k:sha(v) for k,v in files.items()}
  return dict(status='pass',scope='known regression; retrieved evidence only, no new answer',hashes=before,missing_ids=proposal['missing_requirement_ids'],initial_bytes=proposal['initial_bytes'],delivered_bytes=proposal['delivered_bytes'],new_bytes=proposal['new_bytes'],budget=12000,queries=proposal['queries'],following_paragraphs=3,evidence_in_context=coverage,provider_calls=0,original_files_unchanged=True,exclusive_output=True,implementation_sha256=proposal['implementation_sha256'])
if __name__=='__main__':
 result=verify();print(json.dumps(result,indent=2))
 if len(sys.argv)==2:
  with Path(sys.argv[1]).open('x') as out:json.dump(result,out,indent=2);out.write('\n')
