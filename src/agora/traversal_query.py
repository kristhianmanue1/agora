"""Explicit query over a structurally replayed traversal; one new model call."""
import json
from .source import SourceError, digest, encode_record
from .transform import unique_object
from .traversal import walk
from .passages import query_passages


def verify_traversal(adapter, revision, question, record_data, record_hash):
    if type(record_data) is not bytes or len(record_data)>8388608 or digest(record_data)!=record_hash:
        raise SourceError('traversal_hash_or_size_mismatch')
    saved=json.loads(record_data,object_pairs_hook=unique_object)
    if saved['schema']!='agora/source-traversal/v0.1' or saved['execution_status']!='complete':
        raise SourceError('traversal_not_successful')
    if saved['source_id']!=adapter.source_id or saved['source_sha256']!=revision or saved['question']!=question:
        raise SourceError('traversal_identity_or_question_mismatch')
    budgets=saved['budgets'];units=saved['inventory']['units']
    unit_bytes=units[0]['end_byte']-units[0]['start_byte']
    # UTF-8 boundary adjustment can shorten a unit by up to three bytes.
    # Try the bounded compatible widths, requiring exact reconstruction.
    reconstructed=None
    for width in range(max(4,unit_bytes),min(65536,unit_bytes+3)+1):
        index=0
        def replay_provider(*args):
            nonlocal index
            response=saved['ledger'][index]['response'];index+=1
            return response
        replay=walk(adapter,revision,question,replay_provider,unit_bytes=width,
            max_calls=budgets['max_calls'],total_prompt_budget=budgets['total_prompt_bytes'],
            per_prompt_budget=budgets['per_prompt_bytes'],retained_budget=budgets['retained_bytes'])
        if encode_record({key:saved[key] for key in replay})==encode_record(replay):
            reconstructed=replay;break
    if reconstructed is None:raise SourceError('traversal_replay_mismatch')
    return reconstructed


def query_traversal(adapter, revision, question, record_data, record_hash, provider,
                    *, prompt_budget=65536):
    result={'schema':'agora/traversal-query/v0.1','question':question,
            'source_id':adapter.source_id,'source_sha256':revision,
            'traversal_sha256':record_hash,'provider_calls':0,
            'semantic_support':'not_verified','global_completeness':'not_established',
            'review_status':'unreviewed','memory_admission':'not_performed'}
    try:
        reconstructed=verify_traversal(adapter,revision,question,record_data,record_hash)
        result.update(traversal_binding='source_and_record_replayed',
                      receipt_provenance='caller_supplied_not_authenticated',
                      traversal_status=reconstructed['traversal_status'],
                      pending_ranges=reconstructed['pending_ranges'],
                      evidence=reconstructed['evidence'],
                      prior_provider_calls=reconstructed['provider_calls'])
        if reconstructed['traversal_status']!='full':
            result.update(execution_status='complete',answer_status='blocked_partial_traversal')
            return result
        ranges=[]
        for e in sorted(reconstructed['evidence'],key=lambda e:(e['start_byte'],e['end_byte'])):
            if ranges and e['start_byte']<=ranges[-1][1]:ranges[-1][1]=max(ranges[-1][1],e['end_byte'])
            else:ranges.append([e['start_byte'],e['end_byte']])
        if not ranges:
            result.update(execution_status='complete',answer_status='no_retained_evidence')
            return result
        answer=query_passages(adapter,revision,question,provider,mode='reference',ranges=ranges,
                              content_budget=1048576,prompt_budget=prompt_budget)
        result['answer_result']=answer
        result.update(execution_status=answer['execution_status'],
                      answer_status=answer.get('answer_status','generation_failed'),
                      provider_calls=answer['provider_calls'])
    except Exception as exc:
        result.update(execution_status='rejected',diagnostic=str(exc) if isinstance(exc,SourceError) else type(exc).__name__)
    return result
