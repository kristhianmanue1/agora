from pathlib import Path
import json,hashlib,datetime
root=Path('/Users/krisnova/www/aria/agora');p=Path(__file__).parent
sha=lambda b:hashlib.sha256(b).hexdigest()
plan=json.loads((root/'experiments/streaming-diagnosis-v1/manual-plan.json').read_text())
request=json.loads((root/'experiments/streaming-diagnosis-v1/request.json').read_text());raw=json.loads(request['state'])['paper'].encode()
assert sha(raw)==plan['source_sha256']
parts=[];mapping=[];offset=0
for span in plan['envelope']['spans']:
 piece=raw[span['start_byte']:span['end_byte']];assert piece.decode()==span['text']
 if parts:parts.append(b'\n\n');offset+=2
 mapping.append({'derived_range':[offset,offset+len(piece)],'original_range':[span['start_byte'],span['end_byte']],'text_sha256':sha(piece)})
 parts.append(piece);offset+=len(piece)
source=b''.join(parts);(p/'source.txt').write_bytes(source)
freeze={'frozen_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_id':'1907.12984-manual-chain','source_sha256':sha(source),'original_source_id':plan['source_id'],'original_source_sha256':sha(raw),'source_bytes':len(source),'selected_original_bytes':715,'mapping':mapping,'selection':'manual development case; not automatic retrieval','question':'Describe only the standard Transformer baseline used for translation comparison. Identify system, task, version, input granularity and evaluation supported by these passages. Preserve uncertainty; do not turn a full sentence into a full document, invent a software version, metric name or numerical result.','max_generator_calls':1,'max_reviewer_calls':1,'retries':0,'producer_checks':['sentence scope without whole-document expansion','no invented version or numerical metric','comparison concerns translation, not boundary detection'],'independent_adjudication':False}
(p/'freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
