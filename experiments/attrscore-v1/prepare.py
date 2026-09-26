"""Fixed 12-case balanced development pilot, not an official benchmark score."""
from pathlib import Path
import csv,hashlib,json
from agora.evidence import query_evidence
from agora.source import FileSourceAdapter,digest
b=Path(__file__).resolve().parent;inp=b/'inputs';out=inp/'pilot-01';out.mkdir(exist_ok=False)
def h(text):return hashlib.sha256(text.encode()).hexdigest()
raw=inp/'AttrEval-GenSearch.csv';download=json.loads((inp/'download.json').read_text());assert digest(raw.read_bytes())==download['files'][raw.name]['sha256']
rows=list(csv.DictReader(raw.open()));mapping={'Attributable':'supported','Contradictory':'contradicted','Extrapolatory':'insufficient'}
seed='agora-attrscore-pilot-01';eligible=[];excluded=[]
for i,row in enumerate(rows):
 if row['label'] not in mapping:raise ValueError('unknown_label')
 reason=None
 if not row['answer'].strip() or not row['reference'].strip():reason='empty_answer_or_reference'
 elif len(row['answer'])>6000 or len(row['reference'].encode())>12000 or len(row['query'])>2000:reason='consumer_budget'
 if reason:excluded.append({'row_index':i,'reason':reason});continue
 identity=h(json.dumps([row['query'],row['answer'],row['reference']],ensure_ascii=False))
 eligible.append({'row_index':i,'row':row,'identity':identity,'rank':h(seed+identity)})
selected=[];questions=set();references=set()
for label in mapping:
 group=sorted((r for r in eligible if r['row']['label']==label),key=lambda r:r['rank']);picked=0
 for r in group:
  q=' '.join(r['row']['query'].split()).casefold();ref=h(r['row']['reference'])
  if (q and q in questions) or ref in references:continue
  selected.append(r);questions.add(q);references.add(ref);picked+=1
  if picked==4:break
 assert picked==4,label
selected.sort(key=lambda r:r['rank']);gold={};cases=[]
for i,item in enumerate(selected,1):
 cid=f'case-{i:02}';row=item['row'];source=out/(cid+'.txt');source.write_text(row['reference'])
 question=row['query'] or 'Assess whether the supplied reference supports the answer.'
 answer={'parts':[{'id':'answer','status':'answered','claims':[{'text':row['answer'],'quotes':[row['reference']]}],'missing':[]}]}
 candidate=query_evidence(FileSourceAdapter(source,item['identity']),digest(source.read_bytes()),question,[{'id':'answer','question':question}],lambda s,u:{'finish_reason':'stop','content':json.dumps(answer)},response_language='en',content_budget=12000)
 assert candidate['execution_status']=='complete',candidate
 candidate['artifact_origin']='dataset fixture; local structural validation, not GLM generation'
 (out/(cid+'.json')).write_text(json.dumps(candidate,indent=2))
 cases.append({'id':cid,'candidate':cid+'.json','source':cid+'.txt','identity':item['identity'],'source_row_index':item['row_index']})
 gold[cid]={'label':row['label'],'support':mapping[row['label']]}
(out/'cases.json').write_text(json.dumps(cases,indent=2));(out/'gold.json').write_text(json.dumps(gold,indent=2))
(out/'selection.json').write_text(json.dumps({'seed':seed,'selection':'4 per original class; rank sha256(seed + row identity); skip repeated normalized nonempty queries and exact references; final rank order; no truncation or translation','mapping':mapping,'total_rows':len(rows),'eligible':len(eligible),'excluded':excluded,'selected':len(cases),'revision':download['revision'],'csv_sha256':download['files'][raw.name]['sha256'],'language':'original English; not a Spanish evaluation','limitations':'small development pilot; public data contamination unknown; labels used only for stratification and scoring; not gold per-detail spans'},indent=2))
print(json.dumps({'total':len(rows),'eligible':len(eligible),'selected':len(cases),'excluded':excluded}))
