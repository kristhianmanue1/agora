import csv,json,hashlib,runpy
from pathlib import Path
root=Path(__file__).resolve().parents[2];b=root/'experiments/plan-ids-review-v1';assert not (b/'freeze.json').exists();b.mkdir(exist_ok=True);(b/'inputs').mkdir(exist_ok=True);(b/'.gitignore').write_text('inputs/\nruns/\n')
m=root/'experiments/manual-dpm-v1';r=json.loads((m/'runs/functions-generation-ids/result.json').read_text());raw_source=(m/'inputs/source.txt').read_bytes();units={u['id']:u for u in r['evidence_units']};cases=[];gold={};meta=[]
for i,c in enumerate(r['parts'][0]['claims'],1):
 for uid,q in zip(c['evidence_ids'],c['quotes']):
  u=units[uid];assert raw_source[u['start_byte']:u['end_byte']].decode()==q
 cid=f'manual-{i}';evidence='\n\n'.join(c['quotes']);cases.append(dict(id=cid,group='manual',question='¿La afirmación está respaldada por estos fragmentos, sin inferir exhaustividad ni vigencia externa?',claim=c['text'],evidence=evidence));gold[cid]='supported';meta.append(dict(id=cid,gold_origin='producer source review, not independent',evidence_ids=c['evidence_ids'],evidence_sha256=hashlib.sha256(evidence.encode()).hexdigest()))
old=root/'experiments/attrscore-v1/inputs';raw=(old/'AttrEval-GenSearch.csv').read_bytes();download=json.loads((old/'download.json').read_text());assert hashlib.sha256(raw).hexdigest()==download['files']['AttrEval-GenSearch.csv']['sha256'];rows=list(csv.DictReader(raw.decode().splitlines()));previous=[]
for f in [old/'pilot-01/cases.json',root/'experiments/attrscore-v2/inputs/pilot-02/cases.json']:
 previous.extend(rows[c['source_row_index']] for c in json.loads(f.read_text()))
previous.extend(rows[c['source_row_index']] for c in json.loads((root/'experiments/reviewer-comparison-v2/cases-metadata.json').read_text()) if c['id'].startswith('attr-'))
sel=runpy.run_path(str(root/'experiments/attrscore-v2/prepare.py'));selected,selection=sel['select'](rows,previous,count=2,seed='agora-plan-ids-semantic-20260929')
for item in selected:
 row=item['row'];cid='reserved-'+str(item['row_index']);cases.append(dict(id=cid,group='attrscore_reserved',question=row['query'],claim=row['answer'],evidence=row['reference']));gold[cid]=sel['MAPPING'][row['label']];meta.append(dict(id=cid,source_row_index=item['row_index'],original_label=row['label'],gold_origin='external unchanged'))
for p,o in [(b/'inputs/cases.json',cases),(b/'gold.json',gold),(b/'cases-metadata.json',meta),(b/'selection.json',dict(selection,previous_count=len(previous),csv_sha256=hashlib.sha256(raw).hexdigest()))]:p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
(b/'freeze.json').write_text(json.dumps(dict(cases_sha256=hashlib.sha256((b/'inputs/cases.json').read_bytes()).hexdigest(),gold_sha256=hashlib.sha256((b/'gold.json').read_bytes()).hexdigest(),max_calls=12,provider='jev',timeout_seconds=90,retries=0),indent=2)+'\n')
print('Prepared',len(cases),'cases, prior exclusions',len(previous))
