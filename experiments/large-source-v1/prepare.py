"""Freeze a large real source and producer-defined factual criteria before calls."""
from pathlib import Path
import json,hashlib
from agora.qasper import render
b=Path(__file__).resolve().parent;root=b.parents[1];q=root/'experiments/qasper-v1'
raw=(q/'inputs/test.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==json.loads((q/'inputs/provenance.json').read_text())['test.json']['sha256']
pid='1810.13414'
for sample in ('pilot-01','pilot-02'):
 cases=json.loads((q/'prepared'/sample/'model_inputs/cases.json').read_text())
 assert all(c['source_id']!='qasper:'+pid for c in cases)
p=json.loads(raw)[pid];source,paragraphs=render(p)
out=b/'inputs';out.mkdir(exist_ok=False);(out/'source.txt').write_bytes(source)
cases=[{'id':'M1','question':'Which three ontologies were used in the experiments, how did semi-auto compare with manual and auto in the joint experiments, and what specific weakness affected m-piro?'}, {'id':'G1','question':'Give an end-to-end overview of the proposed NaturalOWL methods: natural language names and sentence plans extracted from the Web, ranking and human selection, evaluation outcome, remaining manual resources, and the limits of full automation and language coverage.'}]
criteria={'M1':{'ontologies':'Wine, m-piro, Disease','comparison':'manual best; semi-auto close, often no detected significant difference; auto much lower','weakness':'m-piro semantic correctness/clarity degraded by sentence plans with too few seeds'},'G1':{'names':'Web noun phrases similar to OWL identifiers; rank by alignment and add linguistic annotations','plans':'Web templates from ontology seeds, annotations, Maximum Entropy scoring','selection':'human chooses among top five vs automatic top one','result':'semi-auto nearly manual; fully automatic inadequate','remaining_manual':'other linguistic resources, especially text plans, manually authored in all four configurations','language':'languages other than English remain future work'}}
refs={}
for i in (4,8,14,17,19):
 refs[str(i)]={'section':p['full_text'][i]['section_name'],'paragraphs':[x for x in paragraphs if x['text'] in p['full_text'][i]['paragraphs'] and x['text']]}
for name,value in [('cases.json',cases),('criteria.json',criteria),('references.json',refs),('provenance.json',{'paper_id':pid,'title':p['title'],'source_bytes':len(source),'source_sha256':hashlib.sha256(source).hexdigest(),'dataset_sha256':hashlib.sha256(raw).hexdigest(),'attribution':'QASPER v0.3, Dasigi et al., NAACL 2021; CC-BY 4.0 dataset','method':'qasper.render; original text and placeholders preserved','questions':'producer-written; not official QASPER scoring; not independent holdout','selection':'largest rendered document in local test corpus; absent from pilot-01/02'})]:
 (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
print('Prepared',len(source),'bytes; two tasks; factual criteria frozen before calls.')
