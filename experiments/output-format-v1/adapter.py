"""Strict JSON object or explicit single trailing-backtick repair proposal."""
import hashlib
import json
import math

SCHEMA='agora/output-format-candidate/v1-experimental'
POLICY='single-trailing-backtick/v1'
MAX_BYTES=1048576
WS=' \t\r\n'

def sha(text):return hashlib.sha256(text.encode('utf-8')).hexdigest()
def unique(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('duplicate_key')
        result[key]=value
    return result

def reject_constant(value):raise ValueError('nonfinite_number')

def finite(value):
    if isinstance(value,float) and not math.isfinite(value):raise ValueError('nonfinite_number')
    if isinstance(value,dict):
        for item in value.values():finite(item)
    elif isinstance(value,list):
        for item in value:finite(item)

def strict_object(text):
    try:
        value=json.loads(text,object_pairs_hook=unique,parse_constant=reject_constant)
        finite(value)
    except (json.JSONDecodeError,RecursionError) as exc:
        raise ValueError('invalid_json_object') from exc
    if type(value) is not dict:raise ValueError('object_required')
    return value

def propose(original):
    if type(original) is not str:raise ValueError('text_required')
    try:raw=original.encode('utf-8')
    except UnicodeEncodeError as exc:raise ValueError('invalid_unicode') from exc
    if len(raw)>MAX_BYTES:raise ValueError('output_too_large')
    start=len(original)-len(original.lstrip(WS))
    decoder=json.JSONDecoder(object_pairs_hook=unique,parse_constant=reject_constant)
    try:value,end=decoder.raw_decode(original,start)
    except (json.JSONDecodeError,RecursionError) as exc:raise ValueError('invalid_json_object') from exc
    if type(value) is not dict:raise ValueError('object_required')
    finite(value)
    suffix=original[end:]
    edits=[];candidate=original;status='unchanged'
    if suffix.strip(WS):
        if suffix.strip(WS)!='`':raise ValueError('ambiguous_trailing_content')
        offset=end+len(suffix)-len(suffix.lstrip(WS))
        candidate=original[:offset]+original[offset+1:]
        edits=[dict(operation='delete',start_byte=len(original[:offset].encode('utf-8')),end_byte=len(original[:offset+1].encode('utf-8')),removed='`')]
        status='repair_candidate'
    strict_object(candidate)
    return dict(schema=SCHEMA,policy=POLICY,status=status,original_content=original,original_sha256=sha(original),candidate_content=candidate,candidate_sha256=sha(candidate),edits=edits,admission='not_admitted')

def verify(receipt):
    if type(receipt) is not dict or type(receipt.get('original_content')) is not str:raise ValueError('invalid_receipt')
    expected=propose(receipt['original_content'])
    # JSON comparison distinguishes numeric offsets from booleans.
    if json.dumps(receipt,sort_keys=True,ensure_ascii=False,allow_nan=False)!=json.dumps(expected,sort_keys=True,ensure_ascii=False,allow_nan=False):
        raise ValueError('receipt_mismatch')
    return strict_object(receipt['candidate_content'])
