"""Auditoría local posterior; no cambia gold ni dicta soporte semántico."""
import hashlib
import json
from pathlib import Path
import sys

def audit(root):
    frozen=json.loads((root/'freeze.json').read_text())
    intact=all(hashlib.sha256((root/name).read_bytes()).hexdigest()==value for name,value in frozen.items())
    calls=json.loads((root/'calls.json').read_text())
    scores=json.loads((root/'scores.json').read_text())
    mismatches=[dict(case=r['case'],stage=r['stage'],mode=r['mode'],failed=[k for k,v in r['checks'].items() if not v]) for r in scores if not r['joint_correct']]
    pairs=[]
    for case in sorted({c['case'] for c in calls}):
        group=[(i+1,c) for i,c in enumerate(calls) if c['case']==case]
        for stage in (0,1):
            entries={c['mode']:json.loads((root/f'request-{i:02}.json').read_text()) for i,c in group if c['stage']==stage and (root/f'request-{i:02}.json').exists()}
            if len(entries)!=2:continue
            a=json.loads(entries['full']['messages'][1]['content']);b=json.loads(entries['tracked']['messages'][1]['content'])
            previous=b.pop('previous_assessment');baseline_previous=a.pop('previous_assessment')
            pairs.append(dict(case=case,stage=stage,same_inputs_except_previous=a==b,same_system=entries['full']['messages'][0]==entries['tracked']['messages'][0],baseline_without_history=baseline_previous is None,tracked_history_present=previous is not None))
    return dict(frozen_files_verified=intact,pairs=pairs,mismatches=mismatches,
                metrics={mode:{key:sum(r['mode']==mode and r['checks'][key] for r in scores) for key in ('status','relation','values','affected')} for mode in ('full','tracked')},
                semantic_support='requires_manual_assessment',automatic_admission=False)

if __name__=='__main__':print(json.dumps(audit(Path(sys.argv[1])),ensure_ascii=False,indent=2))
