import json,hashlib,sys,time,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root/'src'))
from agora.qasper import render
from agora.passages import prepare
from agora.source import FileSourceAdapter
b=root/'experiments/sufficiency-real-retrieval-v1';b.mkdir();(b/'inputs').mkdir()
parent=root/'experiments/sufficiency-long-reserved-v1';docs=json.loads((parent/'documents.json').read_text());old=json.loads((parent/'inputs/cases.json').read_text());dataset_path=root/'experiments/qasper-v1/inputs/test.json';raw=dataset_path.read_bytes();assert hashlib.sha256(raw).hexdigest()==json.loads((parent/'selection.json').read_text())['dataset_sha256'];dataset=json.loads(raw)
cases=[];reports=[]
for i,d in enumerate(docs):
 document_id=d['id'];paper=dataset[document_id];data,_=render(paper);source=b/'inputs'/f'{document_id}.txt';source.write_bytes(data);revision=hashlib.sha256(data).hexdigest();adapter=FileSourceAdapter(source,'qasper:'+document_id);question=old[i*4]['task']
 start=time.monotonic();env,meta,_=prepare(adapter,revision,question,'retrieve',content_budget=8000,top_k=3,prompt_budget=65536);elapsed=time.monotonic()-start
 if env is None:raise RuntimeError('no_retrieval_preserve_before_provider')
 for span in env['spans']:assert data[span['start_byte']:span['end_byte']].decode()==span['text']
 (b/'inputs'/f'{document_id}-envelope.json').write_text(json.dumps(env,ensure_ascii=False,indent=2)+'\n')
 evidence='\n\n'.join(s['text'] for s in env['spans'])
 reports.append(dict(document_id=document_id,source_sha256=revision,previous_serialization_sha256=d['source_sha256'],source_bytes=len(data),delivered_bytes=env['delivered_bytes'],retrieval_seconds=round(elapsed,6),retrieval=meta,ranges=[dict(start_byte=s['start_byte'],end_byte=s['end_byte'],sha256=hashlib.sha256(s['text'].encode()).hexdigest()) for s in env['spans']],question=question))
 for j in (0,1):cases.append(dict(id=f'r{len(cases)+1:02}',task=question,evidence=evidence,summary=old[i*4+j]['summary']))
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
dump(b/'inputs/cases.json',cases);dump(b/'retrieval.json',reports)
dump(b/'freeze.json',dict(cases_sha256=hashlib.sha256((b/'inputs/cases.json').read_bytes()).hexdigest(),code_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),retrieval_budget_bytes=8000,top_k=3,max_calls_per_provider=4,retries=0,timeout_seconds=90,selection='source + original question only; no answers/evidence annotations passed to retrieval',source_format='existing agora.qasper.render uses double newlines; different bytes/hash from previous single-newline review serialization',expected_policy='No inherited gold for source sufficiency after context changes; report judgments and evidence audit, not automatic accuracy.'))
(b/'run.py').write_text((parent/'run.py').read_text());(b/'.gitignore').write_text('inputs/\nruns-*/\n')
print(json.dumps([{k:d[k] for k in ('document_id','source_bytes','delivered_bytes','retrieval_seconds')} for d in reports]))
