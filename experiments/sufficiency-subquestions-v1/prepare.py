import json,hashlib,sys,time,subprocess
from pathlib import Path
r=Path(__file__).resolve().parents[2];sys.path.insert(0,str(r/'src'))
from agora.subquestions import prepare_subquestions
from agora.source import FileSourceAdapter
b=r/'experiments/sufficiency-subquestions-v1';b.mkdir();(b/'inputs').mkdir();parent=r/'experiments/sufficiency-real-retrieval-v1'
reports=json.loads((parent/'retrieval.json').read_text());cases=json.loads((parent/'inputs/cases.json').read_text())
queries=[['What evaluation tasks and experiments are performed?','Which datasets or corpora are used for each evaluation task?'],['Which languages are used for evaluation?','What evaluation experiments and corpora correspond to those languages?']]
# Written before selection; neither omitted-task names nor reference ranges supplied.
specs=[dict(schema='agora/subquestions-input/v1-experimental',questions=[dict(id=f'q{j+1}',query=q,reference_ranges=[]) for j,q in enumerate(qs)]) for qs in queries]
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
dump(b/'specifications.json',specs)
freeze=dict(code_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip(),budget_bytes=8000,top_k=3,strategy='paragraphs-equal',specifications_sha256=hashlib.sha256((b/'specifications.json').read_bytes()).hexdigest(),criterion='Recover previously absent evaluation while retaining known relevant content; characterize gaps; no claim of exhaustiveness',provider_policy='Only compare reviewers if new context warrants calls; max four calls per provider, 90s, no retries')
dump(b/'protocol.json',freeze)
rows=[];new=[]
for i,d in enumerate(reports):
 source=parent/'inputs'/f"{d['document_id']}.txt";data=source.read_bytes();assert hashlib.sha256(data).hexdigest()==d['source_sha256']
 adapter=FileSourceAdapter(source,'qasper:'+d['document_id']);start=time.monotonic();plan=prepare_subquestions(adapter,d['source_sha256'],specs[i],budget=8000,top_k=3);elapsed=time.monotonic()-start
 dump(b/'inputs'/f"{d['document_id']}-plan.json",plan);env=plan['envelope'];assert env
 for s in env['spans']:assert data[s['start_byte']:s['end_byte']].decode()==s['text']
 evidence='\n\n'.join(s['text'] for s in env['spans']);ranges=[[s['start_byte'],s['end_byte']] for s in env['spans']]
 before=json.loads((parent/'inputs'/f"{d['document_id']}-envelope.json").read_text());oldtext='\n\n'.join(s['text'] for s in before['spans'])
 rows.append(dict(document_id=d['document_id'],source_sha256=d['source_sha256'],before_bytes=d['delivered_bytes'],after_bytes=env['delivered_bytes'],elapsed_seconds=elapsed,ranges=ranges,questions=plan['questions'],global_completeness=plan['global_completeness'],introduced_text_bytes=sum(len(s['text'].encode()) for s in env['spans'] if s['text'] not in oldtext),contains_denoising='denois' in evidence.lower(),contains_entity_evaluation='xie16entitydesc2' in evidence,contains_five_languages=all(x in evidence for x in ['Arabic','Chinese','French','English','German'])))
 for j in (0,1):new.append(dict(id=f's{len(new)+1:02}',task=cases[i*2+j]['task'],summary=cases[i*2+j]['summary'],evidence=evidence))
dump(b/'retrieval.json',rows);dump(b/'inputs/cases.json',new);dump(b/'freeze.json',dict(cases_sha256=hashlib.sha256((b/'inputs/cases.json').read_bytes()).hexdigest(),max_calls_per_provider=4,retries=0,timeout_seconds=90))
(b/'.gitignore').write_text('inputs/\nruns-*/\n');(b/'run.py').write_text((parent/'run.py').read_text());print(json.dumps([{k:v for k,v in d.items() if k not in ['questions','ranges']} for d in rows]))
