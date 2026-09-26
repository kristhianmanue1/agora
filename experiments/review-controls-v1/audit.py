"""Offline evidence checks and replay; does not call a provider."""
from pathlib import Path
import hashlib, json
from agora.evidence_review import review_evidence
from score import scores

b=Path(__file__).resolve().parent; root=b.parents[1]; out=b/'runs/glm-01'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
frozen=json.loads((out/'freeze.json').read_text())
assert all(sha(out/n)==h for n,h in frozen.items())
for name in ('worker.py','run.py','prepare.py','score.py','audit.py'):
    assert sha(b/name)==sha(out/name)
for p in (out/'code/agora').glob('*.py'): assert sha(p)==sha(root/'src/agora'/p.name)
cases=json.loads((out/'inputs/pilot-01/cases.json').read_text())
gold=json.loads((out/'inputs/pilot-01/gold.json').read_text())
rows=json.loads((out/'execution.json').read_text())
assert len({(x['case'],x['version']) for x in rows})==len(rows)<=24
predictions={v:{} for v in ('v1','v2')}; observations=[]
for case in cases:
    cid=case['id']; candidate=json.loads((out/'inputs/pilot-01'/case['candidate']).read_text())
    assert sha(b/'inputs/pilot-01'/case['candidate'])==sha(out/'inputs/pilot-01'/case['candidate'])
    question=json.loads(candidate['prompt']['user'])['question']
    claim=candidate['parts'][0]['claims'][0]
    reference=(out/'inputs/pilot-01'/case['source']).read_text()
    assert claim['quotes']==[reference]
    for v in predictions:
        ledger=[x for x in rows if x['case']==cid and x['version']==v]
        if not ledger: continue
        f=out/v/cid/'result.json'
        if not f.exists():
            predictions[v][cid]='failed'; continue
        assert sha(f)==ledger[0]['sha256']
        r=json.loads(f.read_text()); request=json.loads(f.with_name('request.json').read_text())
        assert request['model']=='glm-5.3-flash' and request['max_tokens']==8192 and request['temperature']==0
        assert request['messages']==[{'role':'system','content':r['prompt']['system']},{'role':'user','content':r['prompt']['user']}]
        sent=json.loads(r['prompt']['user'])
        assert set(sent)=={'response_language','question','aspects','claims','missing'}
        assert sent['question']==question
        assert sent['claims']==[{'part_id':'answer','claim_index':0,'text':claim['text'],'quotes':[reference]}]
        assert sent['aspects']==[{'id':'answer','question':question}]
        assert sent['missing']==[{'part_id':'answer','items':[]}]
        replay=review_evidence(candidate,lambda s,u:r['response'],response_language='en',review_version=v)
        for key in ('schema','candidate_sha256','execution_status','assessment','diagnostics','recommendation'):
            assert replay.get(key)==r.get(key),(cid,v,key)
        if r['execution_status']=='complete':
            a=r['assessment']; c=a['claims'][0]
            prediction={'support':c['support'],'relevance':c['relevance'],'language':a['language'],'recommendation':r['recommendation']}
        else: prediction='failed'
        predictions[v][cid]=prediction
        observations.append({'case':cid,'version':v,'expected':gold[cid]['expected'],'observed':prediction,'status':r['execution_status'],'diagnostics':r.get('diagnostics')})
metrics={}
for v in predictions:
    used=[x for x in rows if x['version']==v]
    metrics[v]=dict(scores(gold,predictions[v]),calls=len(used),tokens=sum(x['tokens'] or 0 for x in used),
                    unknown_usage=sum(x['tokens'] is None for x in used),seconds=round(sum(x['seconds'] for x in used),3))
report={'freeze_and_local_replay_verified':True,'calls':len(rows),'metrics':metrics,'observations':observations,
        'claims':'diagnostic controls only; attribution textual not authentication; needs_adjudication is not approval'}
(out/'audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
