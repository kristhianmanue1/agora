import json,hashlib
from pathlib import Path
from memos.mem_reader.utils import parse_json_result
r=Path('/tmp/memos-long-reserved-v2')
x=json.loads((r/'extraction-candidate.json').read_text())
positive=parse_json_result('{"summary":"synthetic"}')
negative=parse_json_result('{"summary":"synthetic",}')
actual=parse_json_result(x['content'])
result={'actual_finish_reason':x['finish_reason'],'actual_content_sha256':hashlib.sha256(x['content'].encode()).hexdigest(),'actual_parser_return':actual,'synthetic_valid_return':positive,'synthetic_trailing_comma_return':negative,'provider_calls':0,'diagnosis':'Trailing comma in generated JSON; parser returns empty mapping without raising; API reports success with zero memories','product_changed':False}
assert positive=={'summary':'synthetic'} and negative=={} and actual=={}
(r/'parser-probe.json').write_text(json.dumps(result,indent=2)+'\n')
