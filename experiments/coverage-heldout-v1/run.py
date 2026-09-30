import json,hashlib,importlib.util
from pathlib import Path
BASE=Path(__file__).resolve().parent
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
if __name__=='__main__':
 f=json.loads((BASE/'freeze.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(BASE/'inputs/cases.json')==f['cases_sha256'];assert sha(BASE.parent/'reviewer-coverage-glm-v1/run.py')==f['configuration_sha256'];assert sha(BASE.parent/'reviewer-separated-v1/run.py')==f['criteria_source_sha256'];prior=module('coverage',BASE.parent/'reviewer-coverage-glm-v1/run.py');m=module('transport',BASE.parent/'reviewer-comparison-v1/run.py');m.BASE=BASE/'inputs';m.payload=prior.payload;m.label=prior.label;m.main()
