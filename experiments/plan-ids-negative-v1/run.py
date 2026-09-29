import importlib.util,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2];base=root/'experiments/plan-ids-negative-v1'
freeze=json.loads((base/'freeze.json').read_text());assert hashlib.sha256((base/'inputs/cases.json').read_bytes()).hexdigest()==freeze['cases_sha256'];assert not (base/'runs').exists()
path=root/'experiments/reviewer-comparison-v2/run.py';spec=importlib.util.spec_from_file_location('ids_review_transport',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.engine.BASE=base/'inputs';m.engine.payload=m.payload;m.engine.main()
