"""Budget-aware routing and explicit answer parts. Never starts a traversal."""
import json
from .source import SourceError, integer
from .query import SYSTEM as BASE_SYSTEM, validate_answer
from .transform import TransformError, normalize_output, unique_object
from .traversal_query import verify_traversal
from .evidence import LEGACY_MAX_QUOTES

SYSTEM = BASE_SYSTEM + """
Cover every explicitly requested item in each part;
when facts conflict preserve both with attribution. Do not replace an enumeration
of components with only its final component. Group adjacent evidence only when
it is a literal substring of one passage. Do not invent or silently drop part ids.
Use not_in_document for a part not supported by the supplied passages. A valid
format is not proof of semantic completeness."""


def request_parts(parts):
    if type(parts) is not list or not 1<=len(parts)<=8:
        raise SourceError('invalid_parts')
    ids=[]
    for part in parts:
        if type(part) is not dict or set(part)!={'id','question'}:
            raise SourceError('invalid_parts')
        for key,limit in (('id',64),('question',2000)):
            value=part[key]
            if type(value) is not str or not value.strip() or len(value)>limit:
                raise SourceError('invalid_parts')
            value.encode('utf-8')
        ids.append(part['id'])
    if len(set(ids))!=len(ids):raise SourceError('duplicate_part_ids')
    return ids


CONCISE_RULES = """
Put only the shortest complete direct answer in answer (at most 1000 characters).
Put a brief source-grounded justification in explanation (1 to 2000 characters).
Keep all requested items, units, conditions and unresolved conflicts in answer;
never hide a material qualifier only in explanation. Do not truncate silently.
Use only the quotes necessary to support answer and explanation, at most {LEGACY_MAX_QUOTES}.
Check that evidence concerns the SAME subject, dataset, experiment, population,
time and property as the question. A general background method does not establish
which method a particular study used. A programme's intended scope is not an
observed evaluation result. Results for another group cannot answer this group.
If the requested conclusion is not established, use not_in_document, answer="",
quotes=[], and explain the missing link without asserting the requested conclusion.
Do not answer Yes or Partially and then retract it with a caveat. For partial
retrieval, this means not established in the supplied passages, not absent from
the entire original source. Explicit negative statements about the same subject
CAN support an answer. Conflicting direct evidence CAN support reporting both
values without resolving them. Explanation is not an independently verified audit.
All five fields are mandatory even on abstention. The top level MUST be an
object with the single key parts, never a bare array. Complete abstention example:
{"parts":[{"id":"requested-id","status":"not_in_document","answer":"",
 "explanation":"The requested fact is not established in the supplied passages.","quotes":[]}]}
Use the actual requested ids (one entry for each) and write explanation in the
requested language. Return only the complete JSON object, without Markdown.
"""

CONCISE_RULES = CONCISE_RULES.replace("{LEGACY_MAX_QUOTES}", str(LEGACY_MAX_QUOTES))


def response_system(language, answer_profile="legacy"):
    if answer_profile not in ("legacy", "concise-v1"):
        raise SourceError("unsupported_answer_profile")
    if language not in ("es", "en"):
        raise SourceError("unsupported_response_language")
    system = SYSTEM if language == "es" else SYSTEM.replace("in Spanish", "in English", 1)
    if answer_profile == "concise-v1":
        system = system.replace("id, status, answer, quotes.", "id, status, answer, explanation, quotes.", 1)
        system += CONCISE_RULES
    return system


def prompt(question,parts,envelope,language="es",answer_profile="legacy"):
    user=json.dumps({'question':question,'parts':parts,
                    'document':[{'passage':i+1,'text':s['text']} for i,s in enumerate(envelope['spans'])]},ensure_ascii=False)
    return user,len(response_system(language,answer_profile).encode())+len(user.encode())


def validate_profile_answer(response, document, ids, profile):
    if profile == "legacy":return validate_answer(response,document,ids)
    if response.get('finish_reason') != 'stop':raise TransformError('answer_generation_incomplete')
    content,operation=normalize_output(response.get('content'))
    try:
        parsed=json.loads(content,object_pairs_hook=unique_object)
        if type(parsed) is not dict or set(parsed)!={'parts'}:raise ValueError()
        parts=parsed['parts']
        if type(parts) is not list or len(parts)!=len(ids):raise ValueError()
        stripped=[];explanations=[]
        for part in parts:
            if type(part) is not dict or set(part)!={'id','status','answer','explanation','quotes'}:raise ValueError()
            explanation=part['explanation']
            if type(explanation) is not str or not explanation.strip() or len(explanation)>2000:raise ValueError()
            explanation.encode('utf-8')
            if type(part['answer']) is not str or len(part['answer'])>1000:raise ValueError()
            explanations.append(explanation)
            stripped.append({k:v for k,v in part.items() if k!='explanation'})
        clean,_=validate_answer(dict(response,content=json.dumps({'parts':stripped})),document,ids)
        return [dict(p,explanation=e) for p,e in zip(clean,explanations)],operation
    except (ValueError,TypeError,UnicodeError) as exc:
        if isinstance(exc,TransformError):raise
        raise TransformError('invalid_concise_answer_shape') from exc


def query_routed(adapter,revision,question,parts,provider,*,full_source_budget=32768,
                 prompt_budget=65536,traversal_data=None,traversal_hash=None,response_language="es",answer_profile="legacy"):
    result={'schema':'agora/routed-query/v0.2','response_language':response_language,'source_id':adapter.source_id,
            'source_sha256':revision,'question':question,'requested_parts':parts,
            'provider_calls':0,'routing_policy':'full-source-if-fits-else-verified-traversal/v0.1',
            'semantic_support':'not_verified','global_completeness':'not_established',
            'review_status':'unreviewed','memory_admission':'not_performed'}
    try:
        system=response_system(response_language,answer_profile)
        if answer_profile != "legacy":
            result.update(schema="agora/routed-query/v0.3",answer_profile=answer_profile)
        ids=request_parts(parts)
        if type(question) is not str or not question.strip() or len(question)>2000:
            raise SourceError('invalid_question')
        question.encode('utf-8')
        integer(full_source_budget,1,4194304,'invalid_full_source_budget')
        integer(prompt_budget,1,8388608,'invalid_prompt_budget')
        inventory=adapter.inventory(revision);size=inventory['source']['source_bytes']
        result.update(source_bytes=size,budgets={'full_source_bytes':full_source_budget,'prompt_bytes':prompt_budget})
        envelope=None;reason='full_source_budget_exceeded'
        if size<=full_source_budget:
            candidate=adapter.fetch(revision,[(0,size)],content_budget=full_source_budget)
            user,count=prompt(question,parts,candidate,response_language,answer_profile)
            if count<=prompt_budget:envelope=candidate
            else:reason='full_prompt_budget_exceeded'
        if envelope is not None:
            result.update(route='full_source',route_reason='full_source_and_prompt_fit',pending_ranges=[])
        else:
            result.update(route_reason=reason,route='traversal_required')
            if traversal_data is None:
                result.update(execution_status='complete',answer_status='traversal_required')
                return result
            saved=verify_traversal(adapter,revision,question,traversal_data,traversal_hash)
            result.update(route='verified_traversal',traversal_sha256=traversal_hash,
                          pending_ranges=saved['pending_ranges'],traversal_status=saved['traversal_status'],
                          receipt_provenance='caller_supplied_not_authenticated',
                          part_relevance_to_traversal_question='caller_declared_not_verified')
            if saved['traversal_status']!='full':
                result.update(execution_status='complete',answer_status='blocked_partial_traversal');return result
            ranges=[]
            for e in sorted(saved['evidence'],key=lambda e:(e['start_byte'],e['end_byte'])):
                if ranges and e['start_byte']<=ranges[-1][1]:ranges[-1][1]=max(ranges[-1][1],e['end_byte'])
                else:ranges.append([e['start_byte'],e['end_byte']])
            if not ranges:
                result.update(execution_status='complete',answer_status='no_retained_evidence');return result
            envelope=adapter.fetch(revision,ranges,content_budget=1048576)
            user,count=prompt(question,parts,envelope,response_language,answer_profile)
            if count>prompt_budget:raise SourceError('retained_prompt_budget_exceeded')
        result.update(envelope=envelope,prompt={'system':system,'user':user},prompt_bytes=count)
        result['provider_calls']=1
        response=provider(system,user);result['response']=response
        answers,operation=validate_profile_answer(response,'\n'.join(s['text'] for s in envelope['spans']),ids,answer_profile)
        anchors=[]
        for part in answers:
            for quote in part['quotes']:
                matches=[]
                for span in envelope['spans']:
                    pos=span['text'].find(quote)
                    if pos>=0:
                        start=span['start_byte']+len(span['text'][:pos].encode())
                        matches.append({'start_byte':start,'end_byte':start+len(quote.encode())})
                if not matches:raise TransformError('quote_outside_literal_passage')
                anchors.append({'part_id':part['id'],'quote':quote,'matches':matches})
        result.update(execution_status='complete',
                      answer_status='candidate_partial' if any(p['status']=='not_in_document' for p in answers) else 'candidate',parts=answers,
                      unanswered_parts=[p['id'] for p in answers if p['status']=='not_in_document'],
                      citations=anchors,normalization=operation)
    except Exception as exc:
        result.update(execution_status='rejected' if isinstance(exc,(SourceError,TransformError,ValueError)) else 'failed',
                      diagnostic=str(exc) if isinstance(exc,(SourceError,TransformError)) else type(exc).__name__)
    return result
