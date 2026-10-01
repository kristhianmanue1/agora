"""Verify review bindings and propose an explicit next act. Never dispatch."""
import json
from .coverage_cli import bounded,digest
from .scoped_rubric import prepare,assess,VERSION
from .fidelity_cli import request,assess as assess_fidelity,VERSION as FIDELITY
from .transform import unique_object
from .subquestions import merge_ranges

def add_command(sub):
 p=sub.add_parser('reading-route',help='Decidir siguiente acción explícita desde revisiones vinculadas; sin ejecutar.')
 for n in ('source','source-sha256','candidate','candidate-sha256','rubric','rubric-sha256','review','review-sha256','fidelity','fidelity-sha256','question','part-id','out'):p.add_argument('--'+n,required=True)
 p.add_argument('--can-expand',action='store_true',help='El llamador declara que existe otra lectura; no garantiza ganancia.')
def run(args,write_new):
 raw=bounded(args.candidate,8388608);source=bounded(args.source,160000);rubric=bounded(args.rubric,262144)
 _,rub=prepare(source,raw,rubric,args);candidate=json.loads(raw,object_pairs_hook=unique_object)
 def load(path,expected):
  data=bounded(path,8388608)
  if digest(data)!=expected:raise ValueError('review_hash_mismatch')
  return json.loads(data,object_pairs_hook=unique_object)
 review=load(args.review,args.review_sha256);fidelity=load(args.fidelity,args.fidelity_sha256)
 if review.get('schema')!=VERSION or fidelity.get('schema')!=FIDELITY:raise ValueError('unsupported_review_schema')
 for k in ('source_sha256','candidate_sha256','rubric_sha256','question','part_id'):
  if review.get(k)!=getattr(args,k):raise ValueError('review_binding_mismatch')
 if fidelity.get('candidate_sha256')!=args.candidate_sha256:raise ValueError('fidelity_binding_mismatch')
 if review.get('status')!='complete' or fidelity.get('status')!='complete':decision='stop_inconclusive_review'
 else:
  labels=assess(review['response'],[r['id'] for r in rub['requirements']])
  if labels!=review['requirements']:raise ValueError('review_response_mismatch')
  body=request(candidate)
  if fidelity['request']!=body:raise ValueError('fidelity_request_mismatch')
  supported=assess_fidelity(fidelity['response'],body)
  if supported!=fidelity['label']:raise ValueError('fidelity_response_mismatch')
  if supported!='supported':decision='requires_fidelity_inspection'
  elif any(r['status'] in ('uncertain','contradicted') for r in labels):decision='requires_coverage_inspection'
  elif all(r['status']=='covered' for r in labels):decision='candidate_ready_for_explicit_review'
  else:decision='expand' if args.can_expand else 'insufficient_evidence'
 gaps=[]
 if review.get('status')=='complete':
  missing={r['id'] for r in review['requirements'] if r['status']=='missing'}
  for item in rub['requirements']:
   if item['id'] in missing:
    e=item['evidence'];present=any(a<=e['start_byte'] and e['end_byte']<=b for a,b in merge_ranges([(s['start_byte'],s['end_byte']) for s in candidate['envelope']['spans']]))
    gaps.append(dict(id=item['id'],reference_in_read_context=present,kind='answer_omission_of_supplied_reference' if present else 'reference_not_in_read_context'))
 result=dict(gaps=gaps,gap_basis='Exact supplied reference ranges; equivalent evidence elsewhere not assessed',schema='agora/reading-route/v1-experimental',decision=decision,candidate_sha256=args.candidate_sha256,review_sha256=args.review_sha256,fidelity_sha256=args.fidelity_sha256,can_expand_basis='caller_declared',memory_admission='not_performed',provider_calls=0)
 write_new(args.out,result);return result
