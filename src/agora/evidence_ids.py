"""Source-bound evidence IDs; membership and literal provenance, not entailment."""
import copy
import hashlib
import json
import re
from .evidence import system_prompt, validate_claims
from .transform import unique_object


def build_units(envelope, source_id, revision, max_unit_bytes=4096):
    if type(max_unit_bytes) is not int or not 4<=max_unit_bytes<=12000:
        raise ValueError('invalid_unit_budget')
    units={}
    for span in envelope['spans']:
        text=span['text']
        for match in re.finditer(r'[^\r\n]+(?:\r?\n(?!\r?\n)[^\r\n]+)*',text):
            block=match.group();raw=block.encode();offset=span['start_byte']+len(text[:match.start()].encode())
            while raw:
                end=min(len(raw),max_unit_bytes)
                while end<len(raw) and raw[end]&0xC0==0x80:end-=1
                if end<len(raw):
                    candidates=[m.end() for m in re.finditer(rb'\s+',raw[:end]) if m.end()>=end//2]
                    if candidates:end=candidates[-1]
                piece=raw[:end];raw=raw[end:]
                start=offset;offset+=end
                if not piece.decode().strip():continue
                identity=json.dumps([source_id,revision,start,offset,piece.decode()],ensure_ascii=False).encode()
                uid='ev_'+hashlib.sha256(identity).hexdigest()[:24]
                unit={'id':uid,'start_byte':start,'end_byte':offset,'text':piece.decode(),'quote_bytes':len(piece)}
                if uid in units and units[uid]!=unit:raise ValueError('evidence_id_collision')
                units[uid]=unit
                if len(units)>4096:raise ValueError('evidence_unit_limit')
    return list(units.values())


def id_system(policy):
    prompt=system_prompt(policy)
    prompt=prompt.replace('"quotes":["exact source excerpt"]','"evidence_ids":["provided-unit-id"]')
    prompt=prompt.replace('nonempty literal quotes supporting THAT claim.','nonempty evidence_ids selecting whole provided units supporting THAT claim.')
    prompt=prompt.replace('Do not change punctuation or placeholders. Do not repeat a quote within one claim.','Use only IDs listed in evidence_units. Never invent an ID or output quote text.\nDo not repeat an ID within one claim. Each ID resolves to the entire unit text;\nall quote-byte budgets below apply to the resolved text, not the ID length.')
    return prompt


def validate_ids(response, units, expected_ids, policy):
    if response.get('finish_reason')!='stop':return None,[{'code':'generation_incomplete'}],[]
    try:value=json.loads(response.get('content'),object_pairs_hook=unique_object)
    except (ValueError,TypeError):return None,[{'code':'invalid_json'}],[]
    if type(value) is not dict or set(value)!={'parts'} or type(value['parts']) is not list:return None,[{'code':'invalid_parts_shape'}],[]
    by_id={u['id']:u for u in units};converted=copy.deepcopy(value);errors=[];refs={}
    for pi,p in enumerate(converted['parts']):
        if type(p) is not dict or type(p.get('claims')) is not list:
            errors.append({'code':'invalid_part_shape'});continue
        for ci,c in enumerate(p['claims']):
            if type(c) is not dict or set(c)!={'text','evidence_ids'} or type(c.get('evidence_ids')) is not list or not c['evidence_ids']:
                errors.append({'code':'invalid_claim_id_shape','part_index':pi,'claim_index':ci});continue
            requested=c.pop('evidence_ids');refs[(pi,ci)]=requested;c['quotes']=[];seen=set()
            for ri,uid in enumerate(requested):
                if type(uid) is not str or uid not in by_id:
                    errors.append({'code':'unknown_evidence_id','part_index':pi,'claim_index':ci,'reference_index':ri});continue
                if uid in seen:errors.append({'code':'duplicate_evidence_id','part_index':pi,'claim_index':ci,'reference_index':ri})
                seen.add(uid);c['quotes'].append(by_id[uid]['text'])
    if errors:return None,errors,[]
    expanded=dict(response,content=json.dumps(converted))
    parts,errors,_=validate_claims(expanded,{'spans':units},expected_ids,policy)
    if errors:return None,errors,[]
    anchors=[]
    for pi,p in enumerate(parts):
        for ci,c in enumerate(p['claims']):
            c['evidence_ids']=refs[(pi,ci)]
            for qi,uid in enumerate(c['evidence_ids']):
                u=by_id[uid]
                anchors.append({'part_id':p['id'],'claim_index':ci,'quote_index':qi,'evidence_id':uid,'quote':u['text'],'matches':[{'start_byte':u['start_byte'],'end_byte':u['end_byte']}]})
    return parts,[],anchors
