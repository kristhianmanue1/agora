"""Source-bound relation candidates; structural validation is not entailment."""
import copy
import hashlib
from .evidence_ids import build_units

FIELDS = ('system', 'task', 'version', 'input', 'evaluation')
SCHEMA = 'agora/relation-candidate/v1'
FIELDS_V2 = ('system', 'task', 'software_version', 'model_configuration', 'input', 'evaluation')


def fields_for(schema):
    if schema == SCHEMA:
        return FIELDS
    if schema == 'agora/relation-candidate/v2':
        return FIELDS_V2
    raise ValueError('unsupported_schema')


def evidence(raw, source_id):
    if type(raw) is not bytes or len(raw) > 4 * 1024 * 1024:
        raise ValueError('invalid_source_size')
    if type(source_id) is not str or not source_id.strip() or len(source_id) > 256:
        raise ValueError('invalid_source_id')
    revision = hashlib.sha256(raw).hexdigest()
    units = build_units({'spans': [{'start_byte': 0, 'text': raw.decode('utf-8')}]}, source_id, revision)
    return {'source_id': source_id, 'source_sha256': revision, 'units': units}


def template(raw, source_id, *, contract_version="v1"):
    bundle = evidence(raw, source_id)
    schema = 'agora/relation-candidate/' + contract_version
    names = fields_for(schema)
    return {'schema': schema, 'source_id': source_id, 'source_sha256': bundle['source_sha256'],
            'fields': {field: {'text': None, 'evidence_ids': []} for field in names},
            'relation_evidence_ids': []}


def validate(raw, source_id, candidate):
    """Resolve IDs against the actual source; never mark a relation supported."""
    bundle = evidence(raw, source_id)
    if type(candidate) is not dict or set(candidate) != {'schema', 'source_id', 'source_sha256', 'fields', 'relation_evidence_ids'}:
        raise ValueError('invalid_candidate_shape')
    names = fields_for(candidate['schema'])
    if candidate['source_id'] != source_id or candidate['source_sha256'] != bundle['source_sha256']:
        raise ValueError('source_identity_mismatch')
    fields = candidate['fields']
    if type(fields) is not dict or set(fields) != set(names):
        raise ValueError('invalid_fields')
    units = {unit['id']: unit for unit in bundle['units']}

    def resolve(ids):
        if type(ids) is not list or len(ids) > 32:
            raise ValueError('invalid_evidence_ids')
        seen = set()
        for uid in ids:
            if type(uid) is not str or uid not in units:
                raise ValueError('unknown_evidence_id')
            if uid in seen:
                raise ValueError('duplicate_evidence_id')
            seen.add(uid)
        return [copy.deepcopy(units[uid]) for uid in ids]

    gaps, anchors = [], {}
    for name, value in fields.items():
        if type(value) is not dict or set(value) != {'text', 'evidence_ids'}:
            raise ValueError('invalid_field_shape')
        text = value['text']
        if text is not None and (type(text) is not str or not text.strip() or len(text) > 2000):
            raise ValueError('invalid_field_text')
        anchors[name] = resolve(value['evidence_ids'])
        if text is None and anchors[name]:
            raise ValueError('evidence_without_field_text')
        if text is None or not anchors[name]:
            gaps.append({'field': name, 'reason': 'missing_text' if text is None else 'missing_evidence'})
    anchors['relation'] = resolve(candidate['relation_evidence_ids'])
    if not anchors['relation']:
        gaps.append({'field': 'relation', 'reason': 'missing_link_evidence'})
    return {'schema': 'agora/relation-assessment/' + candidate['schema'].rsplit('/', 1)[1], 'candidate': copy.deepcopy(candidate),
            'status': 'needs_more_evidence' if gaps else 'requires_semantic_review',
            'gaps': gaps, 'anchors': anchors, 'semantic_support': 'not_verified',
            'admitted': False}
