"""Explicit consumer of recovery proposals; one attempt, no admission or retry."""
import json
from pathlib import Path
from types import SimpleNamespace
from . import coverage_recovery as recovery
from .coverage_cli import bounded, digest
from .evidence import query_evidence
from .source import FileSourceAdapter
from .transform import unique_object
from .plan_generation import live_provider


def validate(args):
    raw=bounded(args.proposal,8388608)
    if digest(raw)!=args.proposal_sha256:raise ValueError('proposal_hash_mismatch')
    plan=json.loads(raw,object_pairs_hook=unique_object)
    if not isinstance(plan,dict) or plan.get('schema')!=recovery.VERSION:raise ValueError('invalid_recovery_proposal')
    if plan.get('status')!='proposed' or plan.get('stop_reason')!='explicit_execution_required':raise ValueError('proposal_not_executable')
    settings=SimpleNamespace(**vars(args))
    for key,value in dict(query=plan['queries'],query_origin=plan['query_origin'],budget=plan['total_budget'],top_k=plan['search_plan']['top_k'],following=plan['following_paragraphs']).items():setattr(settings,key,value)
    rebuilt=recovery.build(bounded(args.source,160000),bounded(args.candidate,8388608),bounded(args.rubric,262144),bounded(args.review,8388608),settings)
    rebuilt['implementation_sha256']=digest(Path(recovery.__file__).read_bytes())
    if json.loads(json.dumps(rebuilt))!=plan:raise ValueError('proposal_reproduction_mismatch')
    return plan


def generate(args,provider):
    plan=validate(args)
    if args.response_language not in ('es','en'):raise ValueError('invalid_response_language')
    result=query_evidence(FileSourceAdapter(Path(args.source),plan['envelope']['source']['source_id']),args.source_sha256,args.question,[dict(id=args.part_id,question=args.question)],provider,ranges=plan['ranges'],content_budget=plan['total_budget'],prompt_budget=100000,citation_mode='ids',response_language=args.response_language,max_unit_bytes=4096)
    result.update(recovery_proposal_sha256=args.proposal_sha256,parent_candidate_sha256=args.candidate_sha256,parent_review_sha256=args.review_sha256,answer_scope='selected_passages_only',global_completeness='not_established',memory_admission='not_performed')
    return result


def add_command(sub):
    p=sub.add_parser('generate-recovery',help='Generar un derivado desde una propuesta de recuperación verificada.')
    for name in ('source','source-sha256','candidate','candidate-sha256','rubric','rubric-sha256','review','review-sha256','part-id','question','proposal','proposal-sha256','out'):p.add_argument('--'+name,required=True)
    p.add_argument('--response-language',choices=('es','en'),default='es')
    mode=p.add_mutually_exclusive_group(required=True);mode.add_argument('--live',action='store_true');mode.add_argument('--response')


def run(args,read):
    out=Path(args.out);out.mkdir(mode=0o700,parents=False,exist_ok=False)
    attempts=0
    def save(name,value):
        with (out/name).open('w',encoding='utf-8') as handle:json.dump(value,handle,ensure_ascii=False,indent=2);handle.write('\n')
    def provider(system,user):
        nonlocal attempts
        if attempts:raise ValueError('request_budget_exceeded')
        save('request.json',dict(system=system,user=user));attempts+=1
        save('result.json',dict(execution_status='attempted',http_attempts=attempts if args.live else 0,memory_admission='not_performed'))
        response=live_provider(system,user,max_tokens=4096,json_object=True) if args.live else read(args.response)
        save('response.json',response);return response
    try:result=generate(args,provider)
    except (ValueError,KeyError,TypeError,OSError) as exc:result=dict(execution_status='rejected',diagnostic=type(exc).__name__)
    result.update(http_attempts=attempts if args.live else 0,execution_origin='live_provider' if args.live else 'supplied_response_replay',request_config=dict(model='glm-5.3-flash',max_output_tokens=4096,timeout_seconds=90,max_calls=1,retries=0),implementation_sha256=digest(Path(__file__).read_bytes()))
    save('result.json',result)
    return dict(status=result['execution_status'],diagnostics=result.get('diagnostics',[]),diagnostic=result.get('diagnostic'),http_attempts=result['http_attempts'],output=str(out/'result.json'))
