"""Explicit, revision-checked consumer of subquestion plans; no admission."""
import json
import os
from pathlib import Path
import urllib.request
from .source import FileSourceAdapter, digest, SourceError
from .subquestions import prepare_subquestions
from .passages import query_passages
from .transform import unique_object
from .__main__ import ENDPOINT


def generate(source, plan_bytes, expected_hash, question, provider, citation_mode="literal"):
    if citation_mode not in ("literal", "ids"):
        raise ValueError("invalid_citation_mode")
    if len(plan_bytes) > 8*1024*1024 or digest(plan_bytes) != expected_hash:
        raise ValueError('plan_hash_or_size_mismatch')
    plan = json.loads(plan_bytes, object_pairs_hook=unique_object)
    strategies = {'agora/subquestions-plan/v1-experimental':'paragraphs-equal',
                  'agora/subquestions-plan/v2-experimental':'functions-adaptive'}
    from .structured_plan import VERSION as STRUCTURED,prepare as prepare_structured
    if plan.get('schema') not in (*strategies,STRUCTURED):
        raise ValueError('unsupported_subquestions_plan')
    adapter = FileSourceAdapter(source, plan['source_id'])
    spec = dict(schema='agora/subquestions-input/v1-experimental',questions=[
        {k:q[k] for k in ('id','query','reference_ranges')} for q in plan['questions']])
    if plan['schema']==STRUCTURED:
        rebuilt=prepare_structured(adapter,plan['source_sha256'],spec,plan['structure'],plan['budget_bytes'],plan['top_k'])
    else:
        rebuilt = prepare_subquestions(adapter,plan['source_sha256'],spec,plan['budget_bytes'],plan['top_k'],strategies[plan['schema']])
    # JSON arrays deserialize as lists; compare in the serialized contract domain.
    if json.loads(json.dumps(rebuilt)) != plan:
        raise ValueError('plan_reproduction_mismatch')
    if not plan['envelope']:
        return dict(execution_status='complete',answer_status='no_supplied_evidence',provider_calls=0,
                    plan_sha256=expected_hash,global_completeness='not_established',memory_admission='not_performed')
    ranges = [(s['start_byte'],s['end_byte']) for s in plan['envelope']['spans']]
    scoped_question = ('Responde sólo sobre los fragmentos suministrados. La selección es parcial; '
                       'no presentes la respuesta como exhaustiva del documento.\n'+question)
    if citation_mode == 'ids':
        from .evidence import query_evidence
        result = query_evidence(adapter,plan['source_sha256'],scoped_question,
            [dict(id='P1',question=scoped_question)],provider,ranges=ranges,
            content_budget=plan['budget_bytes'],prompt_budget=65536,citation_mode='ids')
    else:
        result = query_passages(adapter,plan['source_sha256'],scoped_question,provider,'reference',
                                ranges=ranges,content_budget=plan['budget_bytes'],prompt_budget=65536)
    result.update(plan_sha256=expected_hash,plan_schema=plan['schema'],
                  global_completeness='not_established',answer_scope='selected_passages_only',
                  reference_coverage=[{k:q[k] for k in ('id','reference_coverage','missing_reference_ranges')} for q in plan['questions']])
    return result


def live_provider(system, user, *, max_tokens=8192, json_object=False):
    key=os.environ.get('ZAI_API_KEY') or os.environ.get('SKOPOS_LLM_API_KEY')
    if not key:raise ValueError('provider_key_missing')
    payload=dict(model='glm-5.3-flash',messages=[dict(role='system',content=system),dict(role='user',content=user)],max_tokens=max_tokens,temperature=0)
    if json_object:payload["response_format"]={"type":"json_object"}
    request=urllib.request.Request(ENDPOINT,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+key})
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,*args,**kwargs):return None
    with urllib.request.build_opener(NoRedirect()).open(request,timeout=90) as response:
        raw=response.read(1048577)
    if len(raw)>1048576 or key.encode() in raw:raise ValueError('invalid_provider_response')
    data=json.loads(raw);choice=data['choices'][0]
    return dict(content=choice['message']['content'],finish_reason=choice.get('finish_reason'),
                requested_model='glm-5.3-flash',reported_model=data.get('model'),usage=data.get('usage'),response_id=data.get('id'))


def run(args, read):
    # Reserve a new local output directory before any network effect. No retry.
    out=Path(args.out);out.mkdir(parents=False,exist_ok=False)
    attempts=0
    origin='live_provider' if args.live else 'supplied_response_replay'
    response=read(args.response) if args.response else None
    def provider(system,user):
        nonlocal attempts
        if attempts:raise ValueError('request_budget_exceeded')
        attempts+=1
        return live_provider(system,user) if args.live else response
    modules=('structured_plan.py','structure_selection.py','qasper.py','plan_generation.py','subquestions.py','function_retrieval.py','passages.py','source.py','query.py','transform.py','evidence.py','evidence_ids.py','routed_query.py')
    hashes={n:digest(Path(__file__).with_name(n).read_bytes()) for n in modules}
    try:
        result=generate(args.source,Path(args.plan).read_bytes(),args.expected_plan_sha256,args.question,provider,args.citation_mode)
    except (ValueError,KeyError,TypeError,OSError) as exc:
        result=dict(execution_status='rejected',diagnostic=type(exc).__name__)
    result.update(execution_origin=origin,http_attempts=attempts if args.live else 0,
                  request_config=dict(citation_mode=args.citation_mode,model='glm-5.3-flash',max_output_tokens=8192,timeout_seconds=90,max_calls=1),
                  implementation_hashes=hashes)
    result['implementation_unchanged']=hashes=={n:digest(Path(__file__).with_name(n).read_bytes()) for n in modules}
    if not result['implementation_unchanged']:result.update(execution_status='rejected',diagnostic='implementation_changed_during_run')
    (out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return dict(status=result['execution_status'],answer_status=result.get('answer_status'),diagnostic=result.get('diagnostic'),diagnostics=result.get('diagnostics',[]),http_attempts=result['http_attempts'],output=str(out/'result.json'))
