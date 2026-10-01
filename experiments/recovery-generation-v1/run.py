"""Known-case CLI experiment: one generation, one rubric review; no retries."""
import hashlib,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;ROOT=B.parents[1];sys.path.insert(0,str(ROOT/'src'))
from agora.issue_cli import main
BASE=B.parent/'condition-expansion-heldout-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=dict(source=BASE/'inputs/expanded.txt',candidate=BASE/'runs-glm/expanded/candidate.json',rubric=BASE/'expanded-rubric.json',review=BASE/'runs-review-expanded/result.json')
question='What metrics are used to measure bias reduction?'
cli=['--workspace',str(B/'inputs/workspace')]
args=['--part-id','P1','--question',question]
for key,path in files.items():args+=['--'+key,str(path),'--'+key+'-sha256',sha(path)]
if sys.argv[1]=='prepare':
 (B/'inputs').mkdir(exist_ok=False);assert main(cli+['init'])==0
 assert main(cli+['coverage-plan']+args+['--query','metrics','--query-origin','Explicit question term; known-case regression','--budget','12000','--top-k','3','--following','3','--out',str(B/'inputs/proposal.json')])==0
 freeze=dict(inputs={k:sha(p) for k,p in files.items()},proposal_sha256=sha(B/'inputs/proposal.json'),max_generation_calls=1,max_review_calls=1,generation_tokens=4096,review_tokens=2048,retries=0,scope='Known-case regression; no promotion; no prompt addendum',response_language='en')
 with (B/'freeze.json').open('x') as out:json.dump(freeze,out,indent=2);out.write('\n')
elif sys.argv[1]=='live':
 freeze=json.loads((B/'freeze.json').read_text());assert freeze['inputs']=={k:sha(p) for k,p in files.items()}
 code=main(cli+['generate-recovery']+args+['--proposal',str(B/'inputs/proposal.json'),'--proposal-sha256',freeze['proposal_sha256'],'--response-language','en','--live','--out',str(B/'runs-generation')])
 if code:raise SystemExit(code)
 candidate=B/'runs-generation/result.json'
 review_args=['--source',str(files['source']),'--source-sha256',sha(files['source']),'--candidate',str(candidate),'--candidate-sha256',sha(candidate),'--rubric',str(files['rubric']),'--rubric-sha256',sha(files['rubric']),'--part-id','P1','--question',question,'--live','--out',str(B/'runs-review')]
 raise SystemExit(main(cli+['review-rubric']+review_args))
else:raise SystemExit('Unknown mode')
