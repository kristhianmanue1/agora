"""Explicit model checks with conservative local aggregation, not a truth oracle."""
from .evidence_details import SYSTEM_DETAILS, validate_detail_row

SYSTEM_CHECKED_REVISION = "v3-r2"

SYSTEM_CHECKED = SYSTEM_DETAILS.replace(
    '"relevance":"relevant|extra|uncertain",',
    '"relevance":"relevant|extra|uncertain","relevance_reason":"explanation",'
).replace(
    '"quote_indices":[0],"reason":"explanation"',
    '"quote_indices":[0],"reason":"explanation","certainty":"preserved|overstated|uncertain","scope":"same|different|uncertain"'
) + '''
The JSON has a CLOSED schema. Each claim has ONLY part_id, claim_index,
relevance, relevance_reason, details. Each detail has ONLY text, support,
quote_indices, reason, certainty, scope. Put ALL commentary in the existing
reason or relevance_reason fields. Never add note, relevance_detail or other keys.

RELEVANCE compares the CLAIM with the QUESTION, not the quotation with the question.
A claim that answers the question may be relevant even when no quote supports it.
Explain this axis separately in relevance_reason. Do not label an unsupported
answer extra solely because the quotation is off topic. Do not demand external
source authentication: a literal restatement can be textually supported.

Evaluate SUPPORT from the fully resolved CLAIM and its own QUOTATIONS first.
Use the question only to resolve genuinely ambiguous references, never to supply
missing evidence or to decide whether an explicit assertion is true. For an
identical, self-contained claim and identical quotes, changing only the question
must not change support, certainty or scope; relevance may change independently.

DISTINGUISH TWO KINDS OF NEGATION:
- Negation of knowledge, mention, identification or reporting describes what the
  source does not establish. It does NOT deny the underlying event or property.
  Unknown, unspecified and not reported are insufficient evidence, not a negative
  finding. Do not assume a partial list or description is exhaustive.
- Negation of the event/property itself, an explicitly exhaustive incompatible
  account, or an incompatible value at the same scope can establish contradiction.
Before using contradicted, identify in the EXISTING reason field the proposition
that the quote actually denies. If it only denies that information is available,
use insufficient. Do not add any JSON fields for this check.

For EACH detail, judge certainty and scope in the context of the ENTIRE claim:
- certainty=preserved only when attribution, hedging, negation and exceptions are
  preserved. A source reporting that someone claimed X does not establish X as an
  unqualified fact. Use overstated when attribution or a material hedge is lost,
  or an exception is suppressed; uncertain when the comparison cannot be resolved.
- scope=same only when the quotation addresses the SAME subject, measurement,
  population, time and property as that detail IN THE CLAIM. An identical modifier
  attached to another number or subject is different, not support for this detail.
  Missing context is uncertain. Mere differences in numeric VALUES can contradict
  the same measurement; do not call these a different scope solely due to value.
- When the scope differs or is uncertain, neither support nor contradiction is
  established for this detail; local code downgrades the label to insufficient.
- A supported label cannot survive overstated or uncertain certainty; local code
  downgrades it to insufficient. Actual contradiction at the same scope remains.
These checks are your fallible judgments, not independently verified facts.
A correct overall judgment does not excuse a wrong label for any individual detail.
'''


def validate_checked_row(row, claim_text, quote_count):
    expected={'part_id','claim_index','relevance','relevance_reason','details'}
    if type(row) is not dict or set(row)!=expected:
        raise ValueError('invalid_claim_review')
    reason=row['relevance_reason']
    if type(reason) is not str or not reason.strip() or len(reason)>4000:
        raise ValueError('invalid_relevance_reason')
    if type(row['details']) is not list or not 1<=len(row['details'])<=32:
        raise ValueError('invalid_review_details')
    fields={'text','support','quote_indices','reason','certainty','scope'}
    core=[]
    for detail in row['details']:
        if type(detail) is not dict or set(detail)!=fields:
            raise ValueError('invalid_review_detail')
        if detail['certainty'] not in ('preserved','overstated','uncertain') or detail['scope'] not in ('same','different','uncertain'):
            raise ValueError('invalid_detail_check')
        core.append({k:detail[k] for k in ('text','support','quote_indices','reason')})
    base={k:row[k] for k in ('part_id','claim_index','relevance')}
    # First validate the raw labels and refs; flags never excuse invalid output.
    validate_detail_row(dict(base,details=core),claim_text,quote_count)
    changes=[]
    for i,(detail,checked) in enumerate(zip(core,row['details'])):
        blockers=[]
        if checked['scope']!='same': blockers.append('scope_not_established')
        if detail['support']=='supported' and checked['certainty']!='preserved': blockers.append('certainty_not_preserved')
        if blockers and detail['support']!='insufficient':
            detail['support']='insufficient'
            changes.append({'detail_index':i,'reasons':blockers})
    result=validate_detail_row(dict(base,details=core),claim_text,quote_count)
    for detail,raw in zip(result['details'],row['details']):
        detail.update(model_support=raw['support'],certainty=raw['certainty'],scope=raw['scope'])
    result.update(relevance_reason=reason,local_adjustments=changes,
                  aggregation='local_checked_details/v1',checks_provenance='model_reported_not_independently_verified')
    return result
