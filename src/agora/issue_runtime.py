"""Checkout compatibility bridge to frozen experimental contracts.

Do not move these implementations silently: stored manifests bind their bytes.
"""
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

def load(name,path):
    if not path.is_file():raise ValueError('runtime_contract_unavailable')
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

flow=load('agora_issue_flow_v4',ROOT/'experiments/issue-flow-v4/recovery.py')
derived=load('agora_repair_store_v1',ROOT/'experiments/repair-store-v1/store.py')
