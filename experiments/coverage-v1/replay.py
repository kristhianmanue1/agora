"""Replay frozen L3 contexts with coverage preflight; no external requests."""
import hashlib
import json
from pathlib import Path
import shutil
from agora.source import FileSourceAdapter, digest, encode_record
from agora.coverage import assess_with_coverage


def main():
    root=Path(__file__).resolve().parents[2]
    old=root/'experiments/sufficiency-large-v1/runs/glm-01'
    manifest=json.loads((old/'freeze.json').read_text())
    assert all(digest((old/k).read_bytes())==v for k,v in manifest.items())
    execution=json.loads((old/'execution.json').read_text())
    hashes={r['case']:r['result_sha256'] for r in execution}
    out=root/'experiments/coverage-v1/runs/replay-01'
    out.mkdir(parents=True,exist_ok=False)
    shutil.copytree(root/'src/agora',out/'code/agora',ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copyfile(__file__,out/'replay.py')
    frozen={str(p.relative_to(out)):digest(p.read_bytes()) for p in out.rglob('*') if p.is_file()}
    (out/'freeze.json').write_text(json.dumps(frozen,indent=2)+'\n')
    adapter=FileSourceAdapter(old/'source.txt','large-synthetic-v1')
    sha=digest((old/'source.txt').read_bytes())
    rows=[]
    def forbidden(*args):raise AssertionError('provider_must_not_be_called')
    for mode in ('retrieve','reference'):
        name='L3-'+mode+'-judge'
        data=(old/name/'result.json').read_bytes()
        assert digest(data)==hashes[name]
        saved=json.loads(data)
        envelope=encode_record(saved['envelope'])
        result=assess_with_coverage(adapter,sha,saved['question'],envelope,digest(envelope),forbidden,scope='global')
        assert result['global_review_status']=='blocked_incomplete_context'
        assert result['provider_calls']==0
        rows.append({'case':name,'historical_result_sha256':digest(data),
                     'historical_model_decision':saved['judgment']['decision'],
                     'current_result':result})
    full=encode_record(adapter.fetch(sha,[(0,(old/'source.txt').stat().st_size)],content_budget=200000))
    limited=assess_with_coverage(adapter,sha,'Todas las fases',full,digest(full),forbidden,scope='global')
    assert limited['diagnostic']=='assessment_prompt_budget_exceeded'
    assert limited['provider_calls']==0
    rows.append({'case':'full_context_default_budget','current_result':limited})
    for name,h in frozen.items():assert digest((out/name).read_bytes())==h
    assert all(digest((root/'src'/Path(name).relative_to('code')).read_bytes())==h
               for name,h in frozen.items() if name.startswith('code/'))
    (out/'results.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'cases':len(rows),'http_calls':0,'frozen_code_files':len(frozen),
                      'results_sha256':digest((out/'results.json').read_bytes()),'out':str(out)}))

if __name__=='__main__':main()
