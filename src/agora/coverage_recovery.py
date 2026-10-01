"""Explicit recovery proposal from rubric coverage; never dispatch or admission."""
import json
import re
from pathlib import Path
from . import coverage_cli as coverage, rubric_cli as rubric
from .source import FileSourceAdapter
from .subquestions import prepare_subquestions, merge_ranges
from .transform import unique_object

VERSION='agora/coverage-recovery-proposal/v1-experimental'
def build(source,candidate_bytes,rubric_bytes,review_bytes,args):
 if coverage.digest(review_bytes)!=args.review_sha256:raise ValueError('review_hash_mismatch')
 _,requirements=rubric.prepare(source,candidate_bytes,rubric_bytes,args)
 prior=json.loads(review_bytes,object_pairs_hook=unique_object)
 if not isinstance(prior,dict):raise ValueError('invalid_review')
 if prior.get('schema') not in (rubric.VERSION,'agora/rubric-review/v2-scoped-experimental') or prior.get('status')!='complete':raise ValueError('invalid_review')
 for key in ('source_sha256','candidate_sha256','rubric_sha256','part_id','question'):
  if prior.get(key)!=getattr(args,key):raise ValueError('review_binding_mismatch')
 if prior['schema']=='agora/rubric-review/v2-scoped-experimental':
  from .scoped_rubric import prepare as prepare_scoped
  prepare_scoped(source,candidate_bytes,rubric_bytes,args)
 labels=rubric.assess(prior['response'],[r['id'] for r in requirements['requirements']])
 if labels!=prior.get('requirements'):raise ValueError('review_response_mismatch')
 if type(args.budget) is not int or not 1<=args.budget<=160000 or type(args.top_k) is not int or not 1<=args.top_k<=8 or type(args.following) is not int or not 0<=args.following<=3:raise ValueError('invalid_recovery_budget')
 if type(args.query) is not list or not 1<=len(args.query)<=4 or any(type(q) is not str or not 1<=len(q.strip())<=2000 for q in args.query):raise ValueError('invalid_queries')
 if type(args.query_origin) is not str or not 1<=len(args.query_origin.strip())<=2000:raise ValueError('invalid_query_origin')
 candidate=json.loads(candidate_bytes,object_pairs_hook=unique_object);initial=[]
 for span in candidate['envelope']['spans']:
  a,b=span['start_byte'],span['end_byte']
  if type(a) is not int or type(b) is not int or not 0<=a<b<=len(source) or source[a:b].decode()!=span['text']:raise ValueError('invalid_initial_span')
  initial.append([a,b])
 if not initial:raise ValueError('empty_initial_context')
 initial=merge_ranges(initial);cost=lambda rs:sum(b-a for a,b in merge_ranges(rs))
 if cost(initial)>args.budget:raise ValueError('initial_context_exceeds_budget')
 missing=[x['id'] for x in labels if x['status']=='missing'];unresolved=[x['id'] for x in labels if x['status'] in ('contradicted','uncertain')]
 result=dict(schema=VERSION,status='requires_review',source_sha256=args.source_sha256,candidate_sha256=args.candidate_sha256,rubric_sha256=args.rubric_sha256,review_sha256=args.review_sha256,part_id=args.part_id,question=args.question,missing_requirement_ids=missing,unresolved_requirement_ids=unresolved,queries=args.query,query_origin=args.query_origin,query_origin_verification='caller_declared',initial_ranges=initial,ranges=initial,initial_bytes=cost(initial),delivered_bytes=cost(initial),new_bytes=0,total_budget=args.budget,following_paragraphs=args.following,provider_calls=0,admission='not_performed',semantic_completeness='not_established',rubric_text_added_to_queries=False)
 if unresolved:return dict(result,stop_reason='unresolved_review_requires_inspection')
 if not missing:return dict(result,status='no_expansion',stop_reason='no_missing_requirements_in_supplied_rubric')
 # Reuse retrieval; queries are explicit caller input, never rubric answers.
 adapter=FileSourceAdapter(Path(args.source).resolve(),candidate.get('source_id','local'))
 spec=dict(schema='agora/subquestions-input/v1-experimental',questions=[dict(id='Q'+str(i),query=q,reference_ranges=[]) for i,q in enumerate(args.query)])
 search=prepare_subquestions(adapter,args.source_sha256,spec,args.budget,args.top_k)
 text=source.decode();paragraphs=[]
 for m in re.finditer(r'[^\r\n]+(?:\r?\n(?!\r?\n)[^\r\n]+)*',text):
  a=len(text[:m.start()].encode());paragraphs.append([a,a+len(m.group().encode())])
 chosen=initial;skipped=[]
 for span in (search['envelope'] or {}).get('spans',[]):
  indices=[i for i,(a,b) in enumerate(paragraphs) if a<span['end_byte'] and b>span['start_byte']]
  if not indices:continue
  for pair in paragraphs[indices[0]:min(len(paragraphs),indices[-1]+1+args.following)]:
   proposal=merge_ranges(chosen+[pair])
   if cost(proposal)<=args.budget:chosen=proposal
   else:skipped.append(pair)
 result.update(search_plan=search,ranges=chosen,delivered_bytes=cost(chosen),new_bytes=cost(chosen)-cost(initial),skipped_ranges=merge_ranges(skipped))
 result['status']='proposed' if result['new_bytes'] else 'no_new_passages'
 result['stop_reason']='explicit_execution_required' if result['new_bytes'] else 'no_new_passages_within_budget'
 # Re-read through the adapter to bind offsets and contents to the supplied source.
 result['envelope']=adapter.fetch(args.source_sha256,[tuple(p) for p in chosen],content_budget=args.budget)
 return result

def add_command(sub):
 p=sub.add_parser('coverage-plan',help='Proponer recuperación ante requisitos omitidos; sin proveedor ni admisión.')
 for name in ('source','source-sha256','candidate','candidate-sha256','rubric','rubric-sha256','review','review-sha256','part-id','question','query-origin','out'):p.add_argument('--'+name,required=True)
 p.add_argument('--query',action='append',required=True)
 p.add_argument('--budget',type=int,default=12000);p.add_argument('--top-k',type=int,default=3);p.add_argument('--following',type=int,default=0,choices=range(4))

def run(args,write_new):
 result=build(coverage.bounded(args.source,160000),coverage.bounded(args.candidate,8388608),coverage.bounded(args.rubric,262144),coverage.bounded(args.review,8388608),args)
 result['implementation_sha256']=coverage.digest(Path(__file__).read_bytes())
 write_new(args.out,result)
 return {k:result[k] for k in ('status','missing_requirement_ids','unresolved_requirement_ids','initial_bytes','new_bytes','delivered_bytes','stop_reason','provider_calls')} | dict(output=args.out)
