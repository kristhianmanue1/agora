import json,hashlib
from pathlib import Path
B=Path(__file__).resolve().parent;load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=load(B/'freeze.json');rows=[];tokens=0;elapsed=0;calls=0
for case in f['cases']:
 cid=case['id'];folder=B/'runs-glm'/cid;c=load(folder/'candidate.json');g=load(folder/'response.json');rc=load(folder/'receipt.json');tokens+=g['usage']['total_tokens'];elapsed+=rc['elapsed_seconds'];calls+=1
 row=dict(id=cid,document_id=case['document_id'],source_bytes=case['source_bytes'],structural_status=c['execution_status'],candidate_sha256=sha(folder/'candidate.json'),generation_response=g,generation_receipt=rc)
 if c['execution_status']=='complete':
  r=load(B/('runs-review-'+cid)/'result.json');j=load(B/'runs-fidelity'/f'{cid}.json');tokens+=r['response']['usage']['total_tokens']+sum(j['response']['usage'].values());elapsed+=load(folder/'review-receipt.json')['elapsed_seconds']+j['elapsed_seconds'];calls+=2
  claims=c['parts'][0]['claims'];row.update(quote_uses=sum(len(x['quotes']) for x in claims),quote_bytes=sum(len(q.encode()) for x in claims for q in x['quotes']),coverage={x['id']:x['status'] for x in r.get('requirements',[])},expected=case['expected'],coverage_response=r['response'],fidelity={k:v['choice'] for k,v in j['response']['answers'].items()},fidelity_response=j['response'],coverage_result_sha256=sha(B/('runs-review-'+cid)/'result.json'),fidelity_journal_sha256=sha(B/'runs-fidelity'/f'{cid}.json'))
 rows.append(row)
result=dict(status='completed_with_fidelity_finding',http_calls=calls,total_tokens=tokens,elapsed_seconds=round(elapsed,3),rows=rows,product_changes=False,promotion='not_promoted',finding='Case 2 C3 cites a general applications paragraph but introduces two concrete examples located in other source units. True-in-source is not the same as established-by-attached-evidence.',limits='Two locally reserved cases; producer rubrics from benchmark annotations; GLM coverage and separate Jev fidelity advice, no human adjudication. No control arm for causal attribution, no selective reading savings.')
(B/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(tokens=tokens,seconds=round(elapsed,3),calls=calls,cases=[{k:r[k] for k in ('id','quote_uses','quote_bytes','coverage','fidelity')} for r in rows]),indent=2))
