"""Fetch fixed upstream evaluation files only; refuse overwrite, never run remote code."""
from pathlib import Path
import hashlib,json,urllib.request
b=Path(__file__).resolve().parent/'inputs';b.mkdir(exist_ok=True)
revision='467dcdd2cd31f9b5e8625491f3bdf7af90943a8d';files={}
for name in ('README.md','AttrEval-GenSearch.csv'):
 p=b/name
 if p.exists():raise ValueError('refuse_overwrite')
 url=f'https://huggingface.co/datasets/osunlp/AttrScore/resolve/{revision}/{name}'
 with urllib.request.urlopen(url,timeout=30) as response:data=response.read(10000001)
 if len(data)>10000000:raise ValueError('download_too_large')
 p.write_bytes(data);files[name]={'url':url,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
(b/'download.json').write_text(json.dumps({'dataset':'osunlp/AttrScore','revision':revision,'license_declared_in_dataset_card':'apache-2.0','files':files},indent=2))
