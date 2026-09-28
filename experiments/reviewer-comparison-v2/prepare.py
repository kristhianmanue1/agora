"""Freeze external held-aside cases and long-document evidence-scope controls."""
import csv,hashlib,json,runpy
from pathlib import Path
from agora.qasper import render
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def build():
 old=BASE.parent/'attrscore-v1/inputs'
 raw=(old/'AttrEval-GenSearch.csv').read_bytes();meta=json.loads((old/'download.json').read_text())
 assert sha(raw)==meta['files']['AttrEval-GenSearch.csv']['sha256']
 rows=list(csv.DictReader(raw.decode().splitlines()))
 previous=[]
 for file in (old/'pilot-01/cases.json',BASE.parent/'attrscore-v2/inputs/pilot-02/cases.json'):
  previous.extend(rows[c['source_row_index']] for c in json.loads(file.read_text()))
 selector=runpy.run_path(str(BASE.parent/'attrscore-v2/prepare.py'))
 selected,selection=selector['select'](rows,previous,count=8,seed='agora-reviewer-comparison-v2-20260928')
 cases=[];gold={};metadata=[]
 for item in selected:
  row=item['row'];cid='attr-'+str(item['row_index'])
  cases.append(dict(id=cid,language='en',group='attrscore',question=row['query'],claim=row['answer'],evidence=row['reference']))
  gold[cid]=selector['MAPPING'][row['label']]
  metadata.append(dict(id=cid,source_row_index=item['row_index'],original_label=row['label']))
 q=BASE.parent/'qasper-v1';qraw=(q/'inputs/test.json').read_bytes()
 assert sha(qraw)==json.loads((q/'inputs/provenance.json').read_text())['test.json']['sha256']
 papers=json.loads(qraw);used={'1810.13414'}
 for file in (q/'prepared').glob('*/model_inputs/cases.json'):
  used.update(c['source_id'].split(':',1)[1] for c in json.loads(file.read_text()))
 specs={
 '1811.00051':[
  ('The proposed ILP models rely on an external text planner rather than directly performing text planning.','supported','insufficient','A further limitation of our models'),
  ('The proposed ILP models directly perform text planning internally.','contradicted','insufficient','A further limitation of our models'),
  ('The experiments use three ontologies.','supported','supported','We experimented with three owl ontologies')],
 '1911.03977':[
  ('This review includes visual-and-language navigation among the applications it covers.','contradicted','insufficient','In this section, selected applications'),
  ('The review excludes visual-and-language navigation due to space limitations.','supported','insufficient','In this section, selected applications'),
  ('The review covers image captioning among its applications.','supported','supported','In this section, selected applications')]}
 docs=[]
 for pid,spec in specs.items():
  assert pid not in used
  paper=papers[pid];source,paragraphs=render(paper);text=source.decode();abstract=paper['abstract']
  docs.append(dict(paper_id=pid,title=paper['title'],bytes=len(source),sha256=sha(source),abstract_sha256=sha(abstract.encode())))
  for n,(claim,fullgold,shortgold,anchor) in enumerate(spec):
   refs=[p for p in paragraphs if p['text'].startswith(anchor)];assert refs
   for scope,evidence,expected in [('full',text,fullgold),('abstract',abstract,shortgold)]:
    cid=f'long-{pid}-{n}-{scope}'
    cases.append(dict(id=cid,language='en',group='large_'+scope,question='Is the claim supported by the supplied evidence?',claim=claim,evidence=evidence))
    gold[cid]=expected
    metadata.append(dict(id=cid,paper_id=pid,scope=scope,evidence_sha256=sha(evidence.encode()),evidence_bytes=len(evidence.encode()),reference_paragraph_sha256=sha(refs[0]['text'].encode()),gold_origin='producer-authored evidence-scope control, not official QASPER answer'))
 selection.update(prior_cases=len(previous),deduplication='question OR answer OR reference normalized against all 36 prior cases and current sample; not semantic deduplication',csv_sha256=sha(raw),revision=meta['revision'],qasper_sha256=sha(qraw),documents=docs,excluded_papers=sorted(used))
 return cases,gold,metadata,selection
if __name__=='__main__':
 cases,gold,meta,selection=build();(BASE/'inputs').mkdir(exist_ok=False)
 for path,data in [(BASE/'inputs/cases.json',cases),(BASE/'gold.json',gold),(BASE/'cases-metadata.json',meta),(BASE/'selection.json',selection)]:
  with path.open('x') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
 print('Prepared',len(cases),'cases: 24 external + 12 paired long-document controls')
