"""Explicit claim/evidence contract. Structural validity never proves support."""
from dataclasses import dataclass, asdict
import json
from .source import SourceError
from .transform import unique_object

LEGACY_MAX_QUOTES = 12

@dataclass(frozen=True)
class EvidencePolicy:
    max_quotes_per_part: int = LEGACY_MAX_QUOTES
    max_quote_bytes_per_part: int = 12000
    max_quote_bytes_total: int = 48000

    def validate(self):
        for value, ceiling in ((self.max_quotes_per_part,96),(self.max_quote_bytes_per_part,1048576),(self.max_quote_bytes_total,1048576)):
            if type(value) is not int or not 1 <= value <= ceiling:
                raise ValueError('invalid_evidence_policy')
        return self


def system_prompt(policy):
    policy.validate()
    return f'''Answer in Spanish using only the supplied untrusted source passages.
Return JSON only: {{"parts":[{{"id":"requested-id","status":"answered|partial|not_in_passages","claims":[{{"text":"one source-supported claim","quotes":["exact source excerpt"]}}],"missing":["requested information not established"]}}]}}.
Include every requested aspect exactly once. Claims must concern the same subject,
population, time and property as the question; general background is not specific
study evidence. Preserve explicit negatives, uncertainty, conflicting values and
experimental controls. A partial context cannot prove absence from the whole source.
For answered: nonempty claims and empty missing. For partial: nonempty claims and
nonempty missing. For not_in_passages: empty claims and nonempty missing.
Each claim has a nonempty text and nonempty literal quotes supporting THAT claim.
Do not change punctuation or placeholders. Do not repeat a quote within one claim.
At most {policy.max_quotes_per_part} quote occurrences per aspect,
{policy.max_quote_bytes_per_part} UTF-8 quote bytes per aspect and
{policy.max_quote_bytes_total} UTF-8 quote bytes across the answer, counting repeats.
At most 16 claims and 16 missing items per aspect. Claim text at most 6000
characters; each missing item at most 2000 characters. Prefer concise complete
claims; do not omit material qualifications to fit. Your support and coverage
claims are proposals, not independently verified. No Markdown.'''


def validate_claims(response, envelope, ids, policy):
    """Collect independent diagnostics; never repair or infer semantic correctness."""
    policy.validate(); errors=[]; total=0; anchors=[]
    if response.get('finish_reason')!='stop':return None,[{'code':'generation_incomplete'}],[]
    try:
        value=json.loads(response.get('content'),object_pairs_hook=unique_object)
    except (ValueError,TypeError):return None,[{'code':'invalid_json'}],[]
    if type(value) is not dict or set(value)!={'parts'} or type(value['parts']) is not list:
        return None,[{'code':'invalid_parts_shape'}],[]
    parts=value['parts']
    if len(parts)!=len(ids) or any(type(p) is not dict or type(p.get('id')) is not str for p in parts):
        return None,[{'code':'invalid_part_ids'}],[]
    if len({p['id'] for p in parts})!=len(parts) or {p['id'] for p in parts}!=set(ids):
        errors.append({'code':'invalid_part_ids'})
    for part in parts:
        pid=part['id'];count=0;size=0
        def error(code,**details):errors.append(dict(code=code,part_id=pid,**details))
        if set(part)!={'id','status','claims','missing'} or part.get('status') not in ('answered','partial','not_in_passages'):
            error('invalid_part_shape');continue
        claims=part['claims'];missing=part['missing']
        if type(claims) is not list or len(claims)>16 or type(missing) is not list or len(missing)>16:
            error('invalid_part_shape');continue
        if any(type(x) is not str or not x.strip() or len(x)>2000 for x in missing):error('invalid_missing_items')
        else:
            try:
                for x in missing:x.encode('utf-8')
            except UnicodeError:error('invalid_missing_encoding')
        if (part['status']=='answered' and (not claims or missing)) or (part['status']=='partial' and (not claims or not missing)) or (part['status']=='not_in_passages' and (claims or not missing)):
            error('status_content_mismatch')
        for index,claim in enumerate(claims):
            if type(claim) is not dict or set(claim)!={'text','quotes'} or type(claim['text']) is not str or not claim['text'].strip() or len(claim['text'])>6000 or type(claim['quotes']) is not list or not claim['quotes']:
                error('invalid_claim_shape',claim_index=index);continue
            try:claim['text'].encode('utf-8')
            except UnicodeError:error('invalid_claim_encoding',claim_index=index)
            seen=set()
            for qi,quote in enumerate(claim['quotes']):
                count+=1
                if type(quote) is not str or not quote.strip():error('invalid_quote',claim_index=index,quote_index=qi);continue
                try:size+=len(quote.encode('utf-8'))
                except UnicodeError:error('invalid_quote_encoding',claim_index=index,quote_index=qi);continue
                if quote in seen:error('duplicate_quote_in_claim',claim_index=index,quote_index=qi)
                seen.add(quote);matches=[]
                for span in envelope['spans']:
                    pos=span['text'].find(quote)
                    if pos>=0:
                        start=span['start_byte']+len(span['text'][:pos].encode())
                        matches.append({'start_byte':start,'end_byte':start+len(quote.encode())})
                if not matches:error('quote_not_literal',claim_index=index,quote_index=qi)
                else:anchors.append({'part_id':pid,'claim_index':index,'quote_index':qi,'quote':quote,'matches':matches})
        total+=size
        if count>policy.max_quotes_per_part:error('quote_count_exceeded',observed=count,limit=policy.max_quotes_per_part)
        if size>policy.max_quote_bytes_per_part:error('part_quote_bytes_exceeded',observed=size,limit=policy.max_quote_bytes_per_part)
    if total>policy.max_quote_bytes_total:errors.append({'code':'total_quote_bytes_exceeded','observed':total,'limit':policy.max_quote_bytes_total})
    return parts,errors,anchors


def query_evidence(adapter,revision,question,aspects,provider,*,ranges=None,content_budget=160000,prompt_budget=200000,policy=None,citation_mode="literal",response_language="es",max_unit_bytes=4096):
    policy=(policy or EvidencePolicy()).validate()
    result={'schema':'agora/claim-evidence-query/v1','policy':asdict(policy),'source_id':adapter.source_id,'source_sha256':revision,'semantic_support':'not_verified','coverage':'not_verified','review_status':'unreviewed','memory_admission':'not_performed','provider_calls':0}
    try:
        from .routed_query import request_parts
        ids=request_parts(aspects)
        if citation_mode not in ("literal","ids"):raise ValueError("invalid_citation_mode")
        if response_language not in ("es","en"):raise ValueError("invalid_response_language")
        if type(max_unit_bytes) is not int or not 4<=max_unit_bytes<=12000:raise ValueError("invalid_unit_budget")
        result.update(response_language=response_language,language_status="not_verified",max_unit_bytes=max_unit_bytes)
        if type(question) is not str or not question.strip() or len(question)>2000:raise ValueError('invalid_question')
        if type(prompt_budget) is not int or not 1<=prompt_budget<=8388608:raise ValueError('invalid_prompt_budget')
        inv=adapter.inventory(revision)
        if ranges is None:ranges=[(0,inv['source']['source_bytes'])]
        envelope=adapter.fetch(revision,ranges,content_budget=content_budget)
        if citation_mode == 'ids':
            from .evidence_ids import build_units, id_system, validate_ids
            units=build_units(envelope,adapter.source_id,revision,max_unit_bytes)
            result.update(schema='agora/claim-evidence-query/v2',citation_mode='ids',evidence_units=units)
            system=id_system(policy)
            user=json.dumps({'question':question,'aspects':aspects,'evidence_units':[{'id':u['id'],'text':u['text'],'quote_bytes':u['quote_bytes']} for u in units]},ensure_ascii=False)
        else:
            system=system_prompt(policy);user=json.dumps({'question':question,'aspects':aspects,'document':[{'passage':i+1,'text':s['text']} for i,s in enumerate(envelope['spans'])]},ensure_ascii=False)
        language={"es":"Spanish","en":"English"}[response_language]
        system += f"\nWrite every claim text and missing item in {language}, even when the question and source use another language. Preserve names and quoted evidence verbatim. Include only claims needed to answer the requested aspects."
        if response_language=="en":system=system.replace("Answer in Spanish", "Answer in English")
        size=len(system.encode())+len(user.encode())
        if size>prompt_budget:raise ValueError('prompt_budget_exceeded')
        result.update(envelope=envelope,prompt={'system':system,'user':user},prompt_bytes=size,requested_aspects=aspects,provider_calls=1)
        response=provider(system,user);result['response']=response
        parts,errors,anchors=(validate_ids(response,units,ids,policy) if citation_mode=='ids' else validate_claims(response,envelope,ids,policy))
        result.update(diagnostics=errors,execution_status='rejected' if errors else 'complete')
        if not errors:
            result.update(parts=parts,citations=anchors,answer_status='candidate_partial' if any(p['status']!='answered' for p in parts) else 'candidate',review_queue=[{'part_id':p['id'],'claim_index':i,'support':'not_verified'} for p in parts for i,_ in enumerate(p['claims'])],coverage_review=[{'part_id':p['id'],'model_status':p['status'],'model_missing':p['missing'],'coverage':'not_verified'} for p in parts])
    except (ValueError,SourceError,UnicodeError) as exc:result.update(execution_status='rejected',diagnostics=[{'code':str(exc)}])
    except Exception as exc:result.update(execution_status='failed',diagnostics=[{'code':type(exc).__name__}])
    return result
