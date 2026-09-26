"""Freeze one known control and three deterministic document-disjoint real cases."""
from pathlib import Path
import hashlib,json,shutil
from agora.qasper import render,eligible
b=Path(__file__).resolve().parent;root=b.parents[1];out=b/'inputs';out.mkdir(exist_ok=False)
old=root/'experiments/evidence-contract-v1/inputs'
for n in ('G1.txt','G1-aspects.json','G1-selection.json'):shutil.copyfile(old/n,out/n)
control=json.loads((old/'cases.json').read_text())[0];cases=[control];refs={'G1':json.loads((old/'criteria.json').read_text())['G1']}
q=root/'experiments/qasper-v1';excluded={'1810.13414','1911.10742'}
for sample in ('pilot-01','pilot-02'):excluded.update(c['source_id'].split(':',1)[1] for c in json.loads((q/'prepared'/sample/'model_inputs/cases.json').read_text()))
raw=(q/'inputs/test.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==json.loads((q/'inputs/provenance.json').read_text())['test.json']['sha256']
for pid,paper in sorted(json.loads(raw).items()):
 if pid in excluded:continue
 src,paragraphs=render(paper)
 if not 16000<=len(src)<=32000:continue
 for qa in sorted(paper['qas'],key=lambda x:x['question_id']):
  if eligible(qa,paragraphs)[0]!='answerable':continue
  cid=f'R{len(cases)}';(out/(cid+'.txt')).write_bytes(src)
  (out/(cid+'-aspects.json')).write_text(json.dumps([{'id':'answer','question':qa['question']}]))
  cases.append({'id':cid,'source':cid+'.txt','aspects':cid+'-aspects.json','question':qa['question'],'paper_id':pid,'question_id':qa['question_id'],'kind':'real source; full-source input; public question and references'})
  refs[cid]={'title':paper['title'],'annotations':qa['answers'],'source_sha256':hashlib.sha256(src).hexdigest()};break
 if len(cases)==4:break
assert len(cases)==4
(out/'cases.json').write_text(json.dumps(cases,indent=2));(out/'references.json').write_text(json.dumps(refs,indent=2))
(out/'provenance.json').write_text(json.dumps({'selection':'sorted paper ID then question ID; answerable eligible, 16-32 KB; exclude earlier pilots and known examples','dataset_sha256':hashlib.sha256(raw).hexdigest(),'attribution':'QASPER v0.3, Dasigi et al., NAACL 2021; CC-BY 4.0 dataset','language':'same Spanish output in both modes; not official English F1 evaluation','references':'not included in provider input','limitations':'public contamination unknown; producer reviewed references; no independent adjudicator'},indent=2))
print('Prepared G1 and three document-disjoint real sources.')
