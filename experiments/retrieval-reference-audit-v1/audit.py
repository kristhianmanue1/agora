"""Reproduce provenance checks; semantic judgments are explicit producer annotations."""
import json,hashlib,collections
from pathlib import Path
R=Path(__file__).resolve().parents[2];B=Path(__file__).resolve().parent;P=R/'experiments/retrieval-answer-ids-v1';O=R/'experiments/retrieval-answer-paired-v1'
load=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dataset_path=R/'experiments/qasper-v1/inputs/test.json';dataset=load(dataset_path);prior=load(P/'result.json');cases={x['id']:x for x in load(P/'inputs/review-02/cases.json')};freeze=load(P/'freeze.json')
assert sha(P/'inputs/review-02/cases.json')==load(P/'review-freeze-02.json')['cases_sha256']
annotations=load(B/'annotations.json');records=[]
for row in prior['records']:
 cid=row['id']
 if cid not in cases:continue
 question=next(q for q in dataset[row['document_id']]['qas'] if q['question_id']==row['question_id']);envpath=O/'inputs'/f"{row['previous_id']}-envelope.json";assert sha(envpath)==freeze['envelope_sha256'][row['previous_id']];env=load(envpath);source_path=O/'inputs'/f"{row['document_id']}.txt";source=source_path.read_text();assert sha(source_path)==load(O/'freeze.json')['sources'][row['document_id']]
 refs=[]
 for a in question['answers']:
  answer=a['answer'];ev=[]
  for text in answer.get('evidence',[]):
   ev.append(dict(sha256=hashlib.sha256(text.encode()).hexdigest(),literal_in_full_source=text in source,literal_in_delivered_span=any(text in s['text'] for s in env['spans'])))
  refs.append(dict(annotation_id=a.get('annotation_id'),answer={k:answer.get(k) for k in ('unanswerable','yes_no','free_form_answer','extractive_spans')},evidence_checks=ev))
 annotation=annotations[row['document_id']][row['method']];records.append(dict(id=cid,document_id=row['document_id'],method=row['method'],question=question['question'],references=refs,producer_assessment=annotation,jev_labels=row['review']['labels'],candidate_sha256=hashlib.sha256(json.dumps(cases[cid]['answer'],sort_keys=True).encode()).hexdigest()))
assert len(records)==20 and len({x['id'] for x in records})==20
summary=dict(candidates=20,reference_answer_coverage=dict(collections.Counter(x['producer_assessment']['coverage'] for x in records)),jev_complete=sum(x['jev_labels']['coverage']=='complete' for x in records),jev_complete_reference_incomplete=[x['id'] for x in records if x['jev_labels']['coverage']=='complete' and x['producer_assessment']['coverage']=='incomplete'],by_method={m:dict(collections.Counter(x['producer_assessment']['coverage'] for x in records if x['method']==m)) for m in ('equal','shared')})
result=dict(schema='agora/producer-reference-audit/v1',method='Producer semantic comparison with external annotations and source evidence; not official QASPER score, independent adjudication or complete claim-fidelity audit',dataset_sha256=sha(dataset_path),protected_input_hashes={str(p.relative_to(R)):sha(p) for p in (P/'result.json',P/'validation.json',P/'inputs/review-02/cases.json')},summary=summary,records=records)
(B/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary))
