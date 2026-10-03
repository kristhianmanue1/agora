import json,re,hashlib
from pathlib import Path
r=Path('/tmp/memos-long-reserved-v2');calls={}
for p in (r/'memos').glob('*.json'):
 x=json.loads(p.read_text());calls[x['trace']]={'file':p.name,'seconds':x['seconds'],'usage_events':[],'llm_timers':0}
for line in Path('/Users/krisnova/www/aria/llavero/.memos/logs/memos.log').open(errors='replace'):
 parts=line.split(' | ',2)
 if len(parts)<3 or parts[1] not in calls:continue
 row=calls[parts[1]]
 if '[TIMER_WITH_STATUS] OpenAI LLM took' in line:row['llm_timers']+=1
 if 'Response from OpenAI: ' in line:
  try:
   response=json.JSONDecoder().raw_decode(line.split('Response from OpenAI: ',1)[1])[0]
   row['usage_events'].append({'id':response.get('id'),'model':response.get('model'),'usage':response.get('usage')})
  except Exception:row['parse_error']=True
for row in calls.values():
 unique={e['id']:e for e in row['usage_events']};row['usage_events']=list(unique.values());row['reported_total_tokens']=sum((e['usage'] or {}).get('total_tokens',0) for e in unique.values())
(r/'memos-usage.json').write_text(json.dumps(list(calls.values()),indent=2))
def nodes(x):
 if isinstance(x,dict):
  if isinstance(x.get('memory'),str):yield x
  else:
   for k,v in x.items():
    if k!='metadata':yield from nodes(v)
 elif isinstance(x,list):
  for v in x:yield from nodes(v)
rows=[]
gold={x['id']:x['answers'] for x in json.load(open(r/'gold.json'))}
for c in json.load(open(r/'cases.json')):
 for q in c['questions']:
  a=json.load(open(r/'agora'/q['id']/'result.json'));m=json.load(open(r/'memos'/(q['id']+'-chat.json')))
  evidence=list(dict.fromkeys(e for answer in gold[q['id']] for e in answer['answer']['evidence'] if not e.startswith('FLOAT SELECTED:')))
  selected='\n'.join(s['text'] for s in a.get('envelope',{}).get('spans',[]))
  search=list(nodes(json.load(open(r/'memos'/(q['id']+'-search.json')))['response']))
  row={'id':q['id'],'question':q['question'],'agora_status':a['execution_status'],'agora_diagnostic':a.get('diagnostic'),'agora_answer':a.get('answer'),'agora_usage':a.get('response',{}).get('usage'),'agora_citations':a.get('citations',[]),'selected_bytes':sum(len(s['text'].encode()) for s in a.get('envelope',{}).get('spans',[])),'source_bytes':c['bytes'],'gold_text_evidence_count':len(evidence),'gold_evidence_in_full_source':sum(e in (r/c['source']).read_text() for e in evidence),'gold_evidence_in_agora_selection':sum(e in selected for e in evidence),'memos_answer':m['response']['data']['response'],'memos_retrieved_memories':[n['memory'] for n in search]}
  rows.append(row)
(r/'comparison.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
for row in rows:print(row['id'],'gold retrieved',row['gold_evidence_in_agora_selection'],'/',row['gold_text_evidence_count'],'MEMOS:',row['memos_answer'])
print('USAGE',[(c['file'],c['reported_total_tokens'],c['llm_timers']) for c in calls.values()])
