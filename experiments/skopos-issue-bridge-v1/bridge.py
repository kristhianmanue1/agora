"""Paquete Skopos experimental -> fuente local con vínculo de procedencia."""
import hashlib
import json

def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def convert(packet,received_at,fetch):
 if packet['schema']!='skopos/meeting-evidence-packet/v0' or packet['selection_complete']!='not_established' or type(packet['capture_complete_declared']) is not bool:raise ValueError('invalid_contract')
 if type(packet['revision']) is not int or packet['revision']<1 or not packet['spans']:raise ValueError('invalid_revision_or_spans')
 content=packet['text'].encode()
 if hashlib.sha256(content).hexdigest()!=packet['content_sha256']:raise ValueError('content_hash')
 expected=b'';seen=set()
 for span in packet['spans']:
  loc=span['locator']
  if loc['id'] in seen:raise ValueError('duplicate_locator')
  seen.add(loc['id'])
  start=span['start_byte'];end=span['end_byte'];raw=span['text'].encode()
  if type(start) is not int or type(end) is not int or start!=len(expected) or end!=start+len(raw) or content[start:end]!=raw:raise ValueError('invalid_span')
  original=fetch(packet['source_id'],packet['revision'],loc['id'])
  if original['status']!='verified' or original['sha256']!=packet['source_sha256']:raise ValueError('unverified_origin')
  if original['segment']!={**loc,'text':span['text']}:raise ValueError('native_locator_mismatch')
  expected+=raw+b'\n\n'
 if expected!=content:raise ValueError('unmapped_content')
 packet_hash=digest(packet)
 source=dict(id='skopos-packet:'+packet_hash,text=packet['text'],sha256=packet['content_sha256'],received_at=received_at)
 receipt=dict(packet_sha256=packet_hash,source_id=source['id'],original_source_id=packet['source_id'],revision=packet['revision'],source_sha256=packet['source_sha256'],capture_complete_declared=packet['capture_complete_declared'],selection_complete=packet['selection_complete'],spans=packet['spans'])
 return source,receipt

def locate(packet,quote):
 matches=[s['locator'] for s in packet['spans'] if quote and quote in s['text']]
 if not matches:raise ValueError('quote_not_in_native_segment')
 return matches
