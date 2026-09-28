"""Offline proposal only: does not mutate the failed provider operation."""
import importlib.util
import json
from pathlib import Path
from adapter import propose,verify,sha
BASE=Path(__file__).resolve().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
    historical=BASE.parent/'issue-flow-v4/result-glm-01.json'
    response=json.loads(historical.read_text())['original_response']
    if response['finish_reason']!='stop':raise ValueError('incomplete_original_response')
    flow=load('format_recovery',BASE.parent/'issue-flow-v4/recovery.py')
    protocol=flow.storage.protocol
    initial=json.loads((BASE.parent/'open-issues-v4/replay-fixtures.json').read_text())[0]
    data=json.loads(flow.encode(initial['input']))
    # Exact synthetic input used by the original run, reconstructed explicitly.
    data['previous_assessment']=protocol.validate(flow.encode(protocol.prepare_candidate(initial['original_content'],data)),data)
    text='Coordinación confirma: Nube se entrega el 2026-10-21. Lina sigue siendo responsable.'
    data['sources'].append(dict(id='new-confirmation',text=text,received_at='2026-10-09',sha256=sha(text)))
    data['as_of']='2026-10-09'
    receipt=propose(response['content']);verify(receipt)
    candidate=protocol.prepare_candidate(receipt['candidate_content'],data)
    result=protocol.validate(flow.encode(candidate),data)
    assert result['status']=='resolved'
    assert {k:v['observed_value'] for k,v in result['fields'].items()}=={'date':'2026-10-21','owner':'Lina'}
    report=dict(status='local_candidate_validated',real_model_calls=0,historical_operation_modified=False,original_response_file=str(historical.relative_to(BASE.parent)),original_report_sha256=sha(historical.read_text()),input_sha256=sha(flow.encode(data)),receipt=receipt,assessment=result,limitation='Explicit host repair candidate, not a new model response or committed issue revision.')
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
