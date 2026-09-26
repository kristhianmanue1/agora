"""Bounded claim review with explicit coverage; never approves a candidate."""
import copy
from dataclasses import asdict, dataclass
import hashlib
import json
import time
from .evidence_review import review_evidence


def fingerprint(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=True).encode()).hexdigest()


@dataclass(frozen=True)
class ReviewBudget:
    max_calls: int = 6
    max_output_tokens_per_call: int = 8192
    max_output_tokens_total: int = 49152
    max_prompt_bytes_total: int = 120000
    max_seconds: int = 1200
    call_timeout_seconds: int = 180

    def validate(self):
        for field,ceiling in (('max_calls',128),('max_output_tokens_per_call',8192),
                              ('max_output_tokens_total',1048576),('max_prompt_bytes_total',8388608),
                              ('max_seconds',3600),('call_timeout_seconds',300)):
            value=getattr(self,field)
            if type(value) is not int or not 1<=value<=ceiling:raise ValueError('invalid_review_budget')
        return self


class _DispatchStopped(Exception):
    pass


def _plan(candidate):
    if candidate.get('execution_status')!='complete':raise ValueError('candidate_not_complete')
    if candidate.get('schema') not in ('agora/claim-evidence-query/v1','agora/claim-evidence-query/v2'):raise ValueError('unsupported_candidate_schema')
    parts=candidate.get('parts');seen=set();jobs=[]
    if type(parts) is not list or not 1<=len(parts)<=8:raise ValueError('invalid_candidate_parts')
    for pi,part in enumerate(parts):
        if type(part) is not dict or type(part.get('id')) is not str or not part['id'] or part['id'] in seen:raise ValueError('invalid_candidate_parts')
        seen.add(part['id']);claims=part.get('claims');missing=part.get('missing')
        if type(claims) is not list or len(claims)>16 or type(missing) is not list or any(type(x) is not str for x in missing):raise ValueError('invalid_candidate_parts')
        for claim in claims:
            if type(claim) is not dict or type(claim.get('text')) is not str or not claim['text'].strip() or type(claim.get('quotes')) is not list or not claim['quotes'] or any(type(q) is not str or not q.strip() for q in claim['quotes']):raise ValueError('invalid_candidate_claim')
        if not claims and not missing:raise ValueError('empty_candidate_part')
        for ci in range(len(claims)) if claims else [None]:
            jobs.append({'part_index':pi,'part_id':part['id'],'claim_index':ci,'kind':'claim' if ci is not None else 'missing_only'})
    return jobs


def project(candidate,job,original_hash):
    """Review-only projection. Text/quotes/missing copied; source answer untouched."""
    projected=copy.deepcopy(candidate);part=projected['parts'][job['part_index']]
    ci=job['claim_index'];part['claims']=[] if ci is None else [part['claims'][ci]]
    projected['parts']=[part]
    projected['citations']=[dict(a,claim_index=0) for a in candidate.get('citations',[]) if a['part_id']==job['part_id'] and a['claim_index']==ci]
    # Producer queue/coverage refers to the whole response; omit from this review view.
    projected.pop('review_queue',None);projected.pop('coverage_review',None)
    projected['review_projection']={'original_candidate_sha256':original_hash,'part_id':job['part_id'],
                                   'original_claim_index':ci,'projected_claim_index':0 if ci is not None else None,
                                   'purpose':'review_only_not_a_source_answer'}
    return projected


def review_candidate(candidate,provider,*,budget=None,response_language=None,clock=time.monotonic,on_result=None,review_version="v2"):
    """Provider must honor max_output_tokens and timeout_seconds keyword limits.

    Output tokens are reserved before dispatch, never refunded. Input is bounded
    in UTF-8 bytes, not guessed tokens. Unknown usage or transport failure stops
    further dispatch. Structural rejections remain visible; other jobs may proceed.
    on_result receives a detached snapshot after each job for durable logging.
    """
    if review_version not in ('v2','v3'):raise ValueError('invalid_review_version')
    budget=(budget or ReviewBudget()).validate();snapshot=copy.deepcopy(candidate)
    jobs=_plan(snapshot);original_hash=fingerprint(snapshot);started=clock()
    result={'schema':'agora/bounded-evidence-review/v1','review_version':review_version,'candidate_sha256':original_hash,
            'budget':asdict(budget),'execution_status':'incomplete','review_coverage':'incomplete',
            'semantic_coverage':'not_verified','adjudication':'not_performed','independence':'not_established',
            'recommendation':'review_incomplete','jobs':[],
            'ledger':{'calls':0,'reserved_output_tokens':0,'prompt_bytes':0,'reported_total_tokens':0,'unknown_usage_calls':0},
            'stop_reason':None}
    ledger=result['ledger'];stop=None
    for job in jobs:
        record=dict(job,status='not_reviewed',original_candidate_sha256=original_hash)
        if stop:
            record['reason']=stop;result['jobs'].append(record);continue
        projection=project(snapshot,job,original_hash);record['projection_sha256']=fingerprint(projection)
        dispatched=False;local_stop=None
        def bounded_provider(system,user):
            nonlocal dispatched,local_stop
            size=len(system.encode())+len(user.encode());remaining=budget.max_seconds-(clock()-started)
            for reason,blocked in (
                ('call_budget_exhausted',ledger['calls']>=budget.max_calls),
                ('output_budget_exhausted',ledger['reserved_output_tokens']+budget.max_output_tokens_per_call>budget.max_output_tokens_total),
                ('prompt_budget_exhausted',ledger['prompt_bytes']+size>budget.max_prompt_bytes_total),
                ('time_budget_exhausted',remaining<=0)):
                if blocked:local_stop=reason;raise _DispatchStopped(reason)
            dispatched=True;ledger['calls']+=1;ledger['reserved_output_tokens']+=budget.max_output_tokens_per_call;ledger['prompt_bytes']+=size
            return provider(system,user,max_output_tokens=budget.max_output_tokens_per_call,
                            timeout_seconds=min(budget.call_timeout_seconds,remaining))
        review=review_evidence(projection,bounded_provider,response_language=response_language,review_version=review_version)
        if dispatched:
            usage=review.get('response',{}).get('usage');tokens=usage.get('total_tokens') if isinstance(usage,dict) else None
            if type(tokens) is int and tokens>=0:ledger['reported_total_tokens']+=tokens
            else:ledger['unknown_usage_calls']+=1;stop='usage_unknown'
        if local_stop:
            record['reason']=local_stop;stop=local_stop
        else:
            record.update(status='reviewed' if review['execution_status']=='complete' else 'failed',review=review)
            if review['execution_status']=='failed':stop='provider_or_execution_failure'
        if clock()-started>budget.max_seconds:stop='time_budget_exhausted'
        result['jobs'].append(record);result['stop_reason']=stop
        if on_result:on_result(copy.deepcopy(result))
    completed=sum(j['status']=='reviewed' for j in result['jobs'])
    result.update(expected_jobs=len(jobs),reviewed_jobs=completed,stop_reason=stop,elapsed_seconds=round(clock()-started,3))
    if completed==len(jobs):result['review_coverage']='complete'
    if completed==len(jobs) and stop is None:
        result['execution_status']='complete'
        result['recommendation']='needs_revision' if any(j['review']['recommendation']=='needs_revision' for j in result['jobs']) else 'needs_adjudication'
    result['findings']=[{'part_id':j['part_id'],'claim_index':j['claim_index'],'recommendation':j['review']['recommendation']} for j in result['jobs'] if j['status']=='reviewed' and j['review']['recommendation']=='needs_revision']
    if on_result:on_result(copy.deepcopy(result))
    return result
