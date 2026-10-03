"""Isolated public-CLI transition and command-gate checks; no real operations."""
import json,sys,subprocess,uuid
from pathlib import Path
from datetime import datetime,timezone
from an_kla.canonical import digest_json
B=Path(__file__).resolve().parent;O=Path(sys.argv[1]).resolve();O.mkdir();root=O/'memory';root.mkdir();issuer=dict(kind='model',id='codex-lab-fixture',profile='ankla-transitions/v1')
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def cli(args,name,project=root,ok=True):
 p=subprocess.run([sys.executable,'-B','-m','an_kla','--no-update-check','--project-root',str(project)]+args,capture_output=True,text=True)
 d=dict(args=args,exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr);save(O/(name+'.json'),d)
 if ok and p.returncode:raise RuntimeError(name+': '+p.stderr)
 return json.loads(p.stdout) if p.returncode==0 else d
cli(['init'],'init')
def status(name):return cli(['status'],name)['revision']
def plan_record(ident,text,name,supersedes=None):
 rev=status(name+'-status');p=dict(schema='an-kla/write-proposal-v1',base_revision=rev,stream='facts',operation='supersede' if supersedes else 'add',requested_representation='summary',record=dict(id=ident,payload=dict(text=text)),lineage=dict(derived_from_retrieval=False,refs=[]))
 if supersedes:p['supersedes']=supersedes
 a=dict(schema='an-kla/write-authority-v1',proposal_sha256=digest_json(p),base_revision=rev,authority_class='model_derived',issuer=dict(kind='model',id=issuer['id'],configuration_fingerprint=digest_json(issuer)),evidence=[],scope=dict(streams=['facts'],representations=['summary'],operations=['add','supersede']))
 pp=O/(name+'-proposal.json');ap=O/(name+'-authority.json');plan=O/(name+'-plan.json');save(pp,p);save(ap,a)
 result=cli(['plan-write','--proposal',str(pp),'--authority',str(ap)],name+'-planning');save(plan,result)
 return rev,pp,ap,plan

def write(ident,text,name,supersedes=None):
 rev,pp,ap,plan=plan_record(ident,text,name,supersedes)
 return cli(['commit-write-plan','--expected-current',rev,'--proposal',str(pp),'--authority',str(ap),'--planning-result',str(plan)],name+'-commit')
write('schedule-v1','Schedule day Tuesday. Draft.', 'initial');old=status('initial-revision')
write('schedule-v2','Schedule day Wednesday. Replaces Tuesday.', 'replacement','schedule-v1')
retrieved=cli(['retrieve','--query','Schedule day','--budget','8192'],'supersede-retrieve');assert [x['id'] for x in retrieved['selected']]==['schedule-v2']
history=cli(['inventory','--revision',old,'--streams','facts'],'old-inventory');assert 'schedule-v1' in json.dumps(history)
cli(['verify','--revision',old],'old-verify')
parent=cli(['checkpoint','show'],'checkpoint-before')['checkpoint_digest']
ws=dict(schema='an-kla/working-state-v2',objective=dict(provenance='caller_asserted',value='Validate synthetic schedule handoff'),phase=dict(provenance='caller_asserted',value='review_pending'),next_step=dict(provenance='caller_asserted',value='Ask operator to review; no action approved'),decisions=[],blockers=[],evidence=[],source_state=dict(profile='none/v1',head=dict(provenance='unavailable',value=None),branch=dict(provenance='unavailable',value=None),dirty_digest=dict(provenance='unavailable',value=None)),captured_at=dict(provenance='caller_asserted',value=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')),supersedes_checkpoint=parent)
wp=O/'working-state.json';save(wp,ws);a=cli(['checkpoint','plan','--input',str(wp),'--emit-authority-template'],'checkpoint-template');assert a['authority_class']=='model_derived';a['issuer']=dict(kind='model',id=issuer['id'],configuration_fingerprint=digest_json(issuer));ap=O/'checkpoint-authority.json';save(ap,a)
plan=cli(['checkpoint','plan','--input',str(wp),'--authority',str(ap)],'checkpoint-planning');cp=O/'checkpoint-plan.json';save(cp,plan);revision=status('checkpoint-base')
committed=cli(['checkpoint','commit','--plan',str(cp),'--expected-current',revision,'--transaction-id',str(uuid.uuid4())],'checkpoint-commit');assert committed['committed']
shown=cli(['checkpoint','show'],'checkpoint-after');assert shown['checkpoint']['working_state']==ws
resumed=cli(['resume','--query','schedule','--budget','16384'],'resume');assert 'Ask operator to review; no action approved' in json.dumps(resumed)
current=status('before-stale-checkpoint')
stale=cli(['checkpoint','commit','--plan',str(cp),'--expected-current',revision,'--transaction-id',str(uuid.uuid4())],'stale-checkpoint',ok=False);assert stale['exit_code']!=0 and status('after-stale-checkpoint')==current
rev,pp,ap,plan=plan_record('stale-candidate','Should not be committed after revision changes.','stale-write')
write('advance','Independent synthetic revision advance.','advance')
current=status('before-stale-write');bad=cli(['commit-write-plan','--expected-current',rev,'--proposal',str(pp),'--authority',str(ap),'--planning-result',str(plan)],'stale-write-rejected',ok=False);assert bad['exit_code']!=0 and status('after-stale-write')==current
cli(['verify'],'final-verify')
# Separate fresh stores; positive exact command configured before invocation.
for mode in ('denied','allowed'):
 project=O/mode;project.mkdir();cli(['init'],mode+'-init',project)
 marker=project/'marker.txt';cmd=[sys.executable,'-c','from pathlib import Path; import sys; Path(sys.argv[1]).write_text("executed")',str(marker)]
 if mode=='allowed':save(project/'.an-kla/attest-whitelist.json',dict(schema='an-kla/attest-whitelist-v1',entries=[dict(argv=cmd)]))
 result=cli(['attest','run','--timeout','5','--']+cmd,mode+'-action',project,ok=mode=='allowed')
 if mode=='denied':assert result['exit_code']!=0 and 'attest_command_not_allowed' in result['stderr'] and not marker.exists()
 else:
  assert marker.read_text()=='executed'
  altered=cmd[:-1]+[str(project/'other-marker.txt')];negative=cli(['attest','run','--timeout','5','--']+altered,'altered-action',project,ok=False);assert negative['exit_code']!=0 and not (project/'other-marker.txt').exists()
print('PASS supersede historical preservation; checkpoint/resume; stale writes rejected; denied/allowed/altered command marker checks')

save(O/"result.json",dict(supersede_current_excludes_old=True,historical_revision_verified=True,checkpoint_roundtrip=True,resume_contains_next_step=True,stale_checkpoint_rejected_without_revision_change=True,stale_write_rejected_without_revision_change=True,denied_marker_absent=True,positive_marker_executed=True,altered_argument_marker_absent=True,scope="AN-KLA CLI and attest whitelist laboratory only; not a general sandbox, hostile-host defense or deployed integration"))
