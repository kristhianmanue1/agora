import json,sys,subprocess
from pathlib import Path
from an_kla.canonical import digest_json
B=Path(__file__).resolve().parent;R=B.parents[1];out=B/'runs/ankla';out.mkdir(parents=True)
f=json.loads((B/'fixtures.json').read_text());issuer=dict(kind='model',id='codex-fixture-author',profile='synthetic-comparison/v1')
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
for condition in ('record','source'):
 root=out/condition;root.mkdir();index=0
 def cli(args,name):
  proc=subprocess.run([sys.executable,'-m','an_kla','--no-update-check','--project-root',str(root)]+args,capture_output=True,text=True)
  save(root/(name+'.json'),dict(exit_code=proc.returncode,stdout=proc.stdout,stderr=proc.stderr))
  if proc.returncode:raise SystemExit('AN-KLA stopped; inspect '+name)
  return json.loads(proc.stdout)
 cli(['init'],'init')
 for c in f['cases']:
  status=cli(['status'],c['id']+'-status');revision=status['revision']
  p=dict(schema='an-kla/write-proposal-v1',base_revision=revision,stream='facts',operation='add',requested_representation='summary',record=dict(id='test-'+c['id'],payload=dict(text=c[condition],fixture=True)),lineage=dict(derived_from_retrieval=False,refs=[]))
  a=dict(schema='an-kla/write-authority-v1',proposal_sha256=digest_json(p),base_revision=revision,authority_class='model_derived',issuer=dict(kind='model',id=issuer['id'],configuration_fingerprint=digest_json(issuer)),evidence=[],scope=dict(streams=['facts'],representations=['summary'],operations=['add']))
  pp=root/(c['id']+'-proposal.json');ap=root/(c['id']+'-authority.json');plan=root/(c['id']+'-plan.json');save(pp,p);save(ap,a)
  planning=cli(['plan-write','--proposal',str(pp),'--authority',str(ap)],c['id']+'-planning');save(plan,planning)
  cli(['commit-write-plan','--expected-current',revision,'--proposal',str(pp),'--authority',str(ap),'--planning-result',str(plan)],c['id']+'-commit')
 cli(['verify'],'verify')
 for c in f['cases']:cli(['retrieve','--query',c['query'],'--budget','8192'],c['id']+'-retrieve')
 print(condition,'complete',flush=True)
