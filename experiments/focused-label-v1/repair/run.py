"""Run two frozen known-case trials; credentials supplied by Llavero environment."""
import argparse,hashlib,json,os,sys,time
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('--repo',type=Path,required=True);parser.add_argument('--source',type=Path,required=True);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
sys.path.insert(0,str(args.repo/'src'))
from agora.passage_cli import main
base=Path(__file__).parent;case=json.loads((base/'case.json').read_text());freeze=json.loads((base/'freeze.json').read_text())
assert hashlib.sha256((base/'case.json').read_bytes()).hexdigest()==freeze['case_sha256']
assert hashlib.sha256(args.source.read_bytes()).hexdigest()==case['source_sha256']
args.out.mkdir(exist_ok=False);os.environ['ZAI_API_KEY']=os.environ['SKOPOS_LLM_API_KEY']
for effort in freeze['efforts']:
 sys.argv=['agora','--source',str(args.source),'--source-id',case['source_id'],'--sha256',case['source_sha256'],'--question',case['question'],'--citation-mode','ids','--mode','reference','--content-budget','5000','--prompt-budget','16000','--model',freeze['model'],'--max-output-tokens','4096','--timeout-seconds','180','--out',str(args.out/effort)]
 for r in case['ranges']:sys.argv+=['--range',f"{r['start_byte']}:{r['end_byte']}"]
 if effort!='default':sys.argv+=['--reasoning-effort',effort]
 start=time.monotonic();code=main();(args.out/(effort+'-timing.json')).write_text(json.dumps(dict(seconds=time.monotonic()-start,exit_code=code)))
