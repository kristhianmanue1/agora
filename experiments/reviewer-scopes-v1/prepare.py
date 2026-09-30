import json,hashlib,copy,random,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];B=R/'experiments/reviewer-scopes-v1';P=R/'experiments/retrieval-answer-ids-v1';O=R/'experiments/retrieval-answer-paired-v1';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
B.mkdir();(B/'inputs').mkdir();(B/'.gitignore').write_text('inputs/\nruns-*/\n');old={x['id']:x for x in load(P/'inputs/review-02/cases.json')};results=load(P/'result.json');key=[];cases=[]
selection=[('1909.11706','equal','scoped_abstention'),('1909.13466','equal','scoped_abstention'),('1909.13466','shared','scoped_abstention'),('1909.02322','equal','ambiguous_question'),('1909.02322','shared','ambiguous_question'),('1909.11706','shared','positive'),('2003.11531','equal','positive'),('1802.03052','equal','positive')]
for pid,method,group in selection:
 row=next(x for x in results['records'] if x['document_id']==pid and x['method']==method);c=old[row['id']];envpath=O/'inputs'/f"{row['previous_id']}-envelope.json";assert sha(envpath)==load(P/'freeze.json')['envelope_sha256'][row['previous_id']];env=load(envpath);cid='s'+hashlib.sha256(row['id'].encode()).hexdigest()[:10]
 case=dict(id=cid,task=c['task'],full_source=c['evidence'],delivered_passages=[s['text'] for s in env['spans']],answer=c['answer']);cases.append(case);key.append(dict(id=cid,original_id=row['id'],document_id=pid,method=method,group=group,previous_labels=row['review']['labels'],expected_fidelity='supported' if group in ('scoped_abstention','positive') else None,expected_coverage='omitted' if group=='scoped_abstention' else 'complete' if group=='positive' else None))
# Negative controls are producer-authored; actual candidate originals stay unchanged.
for basegroup,mutation in [('positive','false_absence'),('positive','false_claim')]:
 idx=5 if mutation=='false_absence' else 6;c=copy.deepcopy(cases[idx]);c['id']='s'+hashlib.sha256(mutation.encode()).hexdigest()[:10]
 if mutation=='false_absence':c['answer']=dict(status='not_in_passages',claims=[],missing=['The delivered passages contain no accuracy values for SVM or Random Forest, so their performance cannot be compared.'])
 else:c['answer']['claims'][0]['text']='They used the Banana Quantum Tagging model, not the Span-Attribute Tagging (SAT) model.'
 cases.append(c);key.append(dict(id=c['id'],original_id=key[idx]['original_id'],document_id=key[idx]['document_id'],method=key[idx]['method'],group=mutation,previous_labels=None,expected_fidelity='unsupported',expected_coverage='omitted'))
random.Random('scope-review-v1').shuffle(cases)
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
dump(B/'inputs/cases.json',cases);dump(B/'key.json',key);dump(B/'freeze.json',dict(code_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),cases_sha256=sha(B/'inputs/cases.json'),original_result_sha256=sha(P/'result.json'),max_calls=10,model='jev-1.13.0',timeout_seconds=90,retries=0,selection='3 scoped abstentions, both ambiguous candidates, 3 positive candidates, 2 synthetic negative controls',blinding='neutral IDs shuffled; no method, group, reference answers, prior labels, expectations or sibling response',limits='development cases selected after prior failures; producer labels, no independent adjudication; no controlled rerun of old prompt; new criteria and evidence shape; one draw; no promotion'))
print('Prepared 10 reviews; no generation')
