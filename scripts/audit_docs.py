"""Inventory tracked Markdown, local links and Python module references; no network."""
import hashlib,json,re,subprocess
from pathlib import Path
from urllib.parse import unquote
ROOT=Path(__file__).resolve().parents[1]
files=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','*.md'],cwd=ROOT,text=True).splitlines()
records=[]
for name in sorted(set(files)):
    p=ROOT/name;raw=p.read_bytes();text=raw.decode('utf-8')
    links=[]
    for target in re.findall(r'\]\(([^)]+)\)',text):
        value=unquote(target.split('#')[0].strip('<>'))
        if not value or '://' in value or value.startswith('mailto:'):continue
        dest=p.parent/value
        links.append(dict(target=value,exists=dest.exists()))
    modules=sorted(set(re.findall(r'\b(?:-m\s+)(agora\.[a-zA-Z0-9_]+)',text)))
    module_checks=[dict(module=m,exists=(ROOT/'src'/Path(*m.split('.'))).with_suffix('.py').exists()) for m in modules]
    records.append(dict(path=name,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),
        scope='experiment_record' if name.startswith('experiments/') else 'decision_or_historical' if re.match(r'\d{4}-',name) else 'guidance_or_report',
        local_links=links,python_modules=module_checks))
result=dict(scope='all tracked and nonignored Markdown; complete text scanned mechanically; no external-link or historical-result revalidation',documents=len(records),bytes=sum(r['bytes'] for r in records),missing_links=sum(not l['exists'] for r in records for l in r['local_links']),missing_modules=sum(not m['exists'] for r in records for m in r['python_modules']),records=records)
print(json.dumps(result,ensure_ascii=False,indent=2))
