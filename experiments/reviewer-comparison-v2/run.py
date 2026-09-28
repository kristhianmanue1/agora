"""Reuse frozen transport with matched question context; no product defaults change."""
import importlib.util,json
from pathlib import Path
BASE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('reviewer_v1_transport',BASE.parent/'reviewer-comparison-v1/run.py')
engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
original_payload=engine.payload

def payload(provider,case):
 url,body=original_payload(provider,case)
 state=json.dumps({k:case[k] for k in ('question','evidence','claim')},ensure_ascii=False)
 if provider=='jev':body['state']=state
 else:body['messages'][1]['content']=state
 return url,body
if __name__=='__main__':
 engine.BASE=BASE/'inputs';engine.payload=payload;engine.main()
