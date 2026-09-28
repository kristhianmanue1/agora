"""Score saved responses against frozen authored gold, including failures/missing."""
import argparse,collections,hashlib,json,statistics
from pathlib import Path
BASE=Path(__file__).resolve().parent
LABELS=('supported','contradicted','insufficient')
def score(directory,cases,gold):
 records=[];matrix={x:{y:0 for y in (*LABELS,'no_valid_output')} for x in LABELS}
 correct=0;unsafe=0;elapsed=[];tokens=collections.Counter();models=set();languages={x:{'correct':0,'total':0} for x in ('es','en')}
 for case in cases:
  path=directory/(case['id']+'.json');record=json.loads(path.read_text()) if path.exists() else {'status':'not_attempted'}
  expected=gold[case['id']];predicted=record.get('label') if record['status']=='completed' else 'no_valid_output'
  if predicted not in LABELS:predicted='no_valid_output'
  matrix[expected][predicted]+=1;correct+=predicted==expected;unsafe+=predicted=='supported' and expected!='supported'
  lang=languages[case['language']];lang['total']+=1;lang['correct']+=predicted==expected
  raw=record.get('response',{});usage=raw.get('usage') or {}
  for key,value in usage.items():
   if isinstance(value,int) and not isinstance(value,bool):tokens[key]+=value
  if raw.get('model'):models.add(raw['model'])
  if 'elapsed_seconds' in record:elapsed.append(record['elapsed_seconds'])
  records.append(dict(case_id=case['id'],expected=expected,predicted=predicted,status=record['status']))
 return dict(total=len(cases),completed=sum(r['status']=='completed' for r in records),correct=correct,false_support=unsafe,false_support_denominator=sum(x!='supported' for x in gold.values()),confusion_matrix=matrix,by_language=languages,reported_models=sorted(models),usage_totals=dict(tokens),sum_request_seconds=round(sum(elapsed),3),median_request_seconds=statistics.median(elapsed) if elapsed else None,cost_usd=None,cost_note='No verified per-request charge or tariff supplied; tokens are not dollars.',cases=records)
def main():
 p=argparse.ArgumentParser();p.add_argument('glm',type=Path);p.add_argument('jev',type=Path);args=p.parse_args()
 casebytes=(BASE/'cases.json').read_bytes();cases=json.loads(casebytes);gold=json.loads((BASE/'gold.json').read_text())
 for directory in (args.glm,args.jev):
  manifest=json.loads((directory/'manifest.json').read_text())
  if manifest['case_sha256']!=hashlib.sha256(casebytes).hexdigest():raise ValueError('case_manifest_mismatch')
 print(json.dumps(dict(schema='agora/reviewer-comparison/v1-experimental',cases_sha256=hashlib.sha256(casebytes).hexdigest(),gold_sha256=hashlib.sha256((BASE/'gold.json').read_bytes()).hexdigest(),glm=score(args.glm,cases,gold),jev=score(args.jev,cases,gold)),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
