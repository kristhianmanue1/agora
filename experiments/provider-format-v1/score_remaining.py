"""Audit paired receipts without calling a provider or changing old results."""
import hashlib,json
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent/'runs/paired-02'
 freeze=json.loads((out/'freeze.json').read_text())
 assert all(sha(out/n)==h for n,h in freeze.items())
 for n,h in freeze.items():
  if n.startswith('code/agora/'):assert sha(root/'src/agora'/n.removeprefix('code/agora/'))==h
 execution=json.loads((out/'execution.json').read_text())
 expected=json.loads((out/'protocol.json').read_text())['expected_status'];scores={};details=[]
 for mode in ('default','json_object'):
  rows=[]
  for row in execution:
   if row['mode']!=mode:continue
   file=out/mode/row['case']/'result.json';assert sha(file)==row['result_sha256']
   r=json.loads(file.read_text());assert r['implementation_unchanged'] and r['http_attempts']==1
   assert r['request_config']['response_format']==mode
   if mode=='json_object':
    other=json.loads((out/'default'/row['case']/'result.json').read_text())
    assert r['prompt']==other['prompt'] and r['source_sha256']==other['source_sha256']
   try:
    value=json.loads(r.get('response',{}).get('content'));parsed=True
   except (ValueError,TypeError):value=None;parsed=False
   parts=value.get('parts') if isinstance(value,dict) else None
   shape=isinstance(parts,list) and len(parts)==1 and isinstance(parts[0],dict) and set(parts[0])=={'id','status','answer','explanation','quotes'} and set(value)=={'parts'}
   accepted=r['execution_status']=='complete'
   status=r.get('parts',[{}])[0].get('status')
   correct=accepted and status==expected[row['case']]
   quotes=[q for p in r.get('parts',[]) for q in p['quotes']]
   anchors=r.get('citations',[])
   for a in anchors:
    source=(out/'inputs'/f"{row['case']}.txt").read_bytes()
    assert all(source[m['start_byte']:m['end_byte']].decode()==a['quote'] for m in a['matches'])
   item=dict(row,json_parseable=parsed,required_fields_exact=shape,expected_status_match=correct,quotes=len(quotes),anchored_quotes=len(anchors),parts=r.get('parts'),raw_content=r.get('response',{}).get('content'))
   rows.append(item);details.append(item)
  scores[mode]={'calls':len(rows),'json_parseable':sum(x['json_parseable'] for x in rows),'required_fields_exact':sum(x['required_fields_exact'] for x in rows),'accepted':sum(x['status']=='complete' for x in rows),'expected_status_match':sum(x['expected_status_match'] for x in rows),'quotes':sum(x['quotes'] for x in rows),'anchored_quotes':sum(x['anchored_quotes'] for x in rows),'total_tokens':sum(x['tokens'] for x in rows if x['tokens'] is not None),'unknown_usage_calls':sum(x['tokens'] is None for x in rows),'seconds':round(sum(x['seconds'] for x in rows),3)}
 result={'scores':scores,'details':details,'campaign_complete':len(execution)==12,'integrity_verified':True,'paired_prompts_identical':True,'semantic_review':'pending; expected status match is not semantic fidelity'}
 target=out/'scores.json'
 with target.open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
 print(json.dumps(scores,indent=2))
if __name__=='__main__':main()
