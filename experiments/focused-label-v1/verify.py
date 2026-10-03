"""Validate frozen sources, receipts and accounting; not semantic adjudication."""
import argparse,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);args=p.parse_args();base=Path(__file__).parent
raw=args.source.read_bytes();total=0;calls=0
for stage in ['initial','repair']:
 folder=base/stage;case=json.loads((folder/'case.json').read_text());freeze=json.loads((folder/'freeze.json').read_text())
 assert hashlib.sha256(raw).hexdigest()==case['source_sha256']
 assert hashlib.sha256((folder/'case.json').read_bytes()).hexdigest()==freeze['case_sha256']
 for r in case['ranges']:
  piece=raw[r['start_byte']:r['end_byte']]
  assert piece.decode()==r['text'] and hashlib.sha256(piece).hexdigest()==r['sha256']
 for effort in freeze['efforts']:
  d=json.loads((folder/(effort+'-receipt.json')).read_text())
  assert d['http_attempts']==1 and d['implementation_unchanged']
  assert d['source_sha256']==case['source_sha256']
  assert d['answer_scope']=='selected_passages' and d['requires_expansion']
  assert d['semantic_support']=='not_verified' and not d['document_absence_established']
  assert d['request_config']['max_output_tokens']==freeze['max_output_tokens']
  assert d['request_config'].get('reasoning_effort','default')==effort
  for c in d.get('citations',[]):
   for m in c['matches']:assert raw[m['start_byte']:m['end_byte']].decode()==c['quote']
  total+=d['response']['usage']['total_tokens'];calls+=d['http_attempts']
a=json.loads((base/'assessment.json').read_text());assert total==a['total_tokens'] and calls==a['http_attempts']
print(json.dumps({'integrity':'verified','semantic_validity':'not_certified','http_calls_executed':0,'recorded_tokens':total,'recorded_calls':calls}))
