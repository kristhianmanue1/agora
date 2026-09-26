from pathlib import Path
import hashlib,json,shutil
from agora.qasper import render,eligible
from agora.evidence import query_evidence
from agora.source import FileSourceAdapter,digest
b=Path(__file__).resolve().parent;root=b.parents[1];out=b/'inputs';out.mkdir(exist_ok=False)
q=root/'experiments/qasper-v1';excluded={'1810.13414','1911.10742'}
for sample in ('pilot-01','pilot-02'):excluded.update(c['source_id'].split(':',1)[1] for c in json.loads((q/'prepared'/sample/'model_inputs/cases.json').read_text()))
excluded.update(c['paper_id'] for c in json.loads((root/'experiments/evidence-ids-v1/inputs/cases.json').read_text()) if 'paper_id' in c)
raw=(q/'inputs/test.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==json.loads((q/'inputs/provenance.json').read_text())['test.json']['sha256']
cases=[];refs={}
for pid,paper in sorted(json.loads(raw).items()):
 if pid in excluded:continue
 src,paragraphs=render(paper)
 if not 16000<=len(src)<=32000:continue
 for qa in sorted(paper['qas'],key=lambda x:x['question_id']):
  if eligible(qa,paragraphs)[0]!='answerable':continue
  cid=f'N{len(cases)+1}';(out/(cid+'.txt')).write_bytes(src)
  (out/(cid+'-aspects.json')).write_text(json.dumps([{'id':'answer','question':qa['question']}]))
  cases.append({'id':cid,'source':cid+'.txt','aspects':cid+'-aspects.json','question':qa['question'],'paper_id':pid,'question_id':qa['question_id']})
  refs[cid]={'title':paper['title'],'annotations':qa['answers']};break
 if len(cases)==2:break
assert len(cases)==2
(out/'cases.json').write_text(json.dumps(cases,indent=2));(out/'references.json').write_text(json.dumps(refs,indent=2))
old=root/'experiments/evidence-ids-v1/runs/glm-01/ids/R1/result.json';shutil.copyfile(old,out/'C-language.json')
text='Atlas scored 91%. Boreal was not evaluated.';p=out/'C-support.txt';p.write_text(text)
v={'parts':[{'id':'a','status':'answered','claims':[{'text':'Atlas obtuvo 91%.','quotes':['Atlas scored 91%.']},{'text':'Boreal obtuvo 91%.','quotes':['Atlas scored 91%.']},{'text':'Boreal fue evaluado.','quotes':['Boreal was not evaluated.']}],'missing':[]}]}
c=query_evidence(FileSourceAdapter(p,'synthetic'),digest(p.read_bytes()),'¿Qué resultados obtuvieron Atlas y Boreal?',[{'id':'a','question':'Resultados de Atlas y Boreal'}],lambda s,u:{'finish_reason':'stop','content':json.dumps(v)})
assert c['execution_status']=='complete';(out/'C-support.json').write_text(json.dumps(c,indent=2))
(out/'provenance.json').write_text(json.dumps({'dataset_sha256':hashlib.sha256(raw).hexdigest(),'attribution':'QASPER v0.3, Dasigi et al., NAACL 2021; CC-BY 4.0','selection':'sorted paper/question IDs; 16-32KB; eligible answerable; exclude earlier 24 pilot documents, prior ID cases and known examples','excluded_paper_ids':sorted(excluded),'controls':{'C-language':'expected mismatch Spanish requested; source artifact unchanged','C-support':['supported','insufficient','contradicted']},'references':'withheld from generation and review','limitations':'public contamination unknown; same model separate call is not independent adjudication'},indent=2))
print(json.dumps(cases))
