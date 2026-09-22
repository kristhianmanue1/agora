"""Local retrieval diagnostic against frozen passage ranges; no provider."""
import argparse
import hashlib
import json
from pathlib import Path
from agora.passages import prepare
from agora.source import FileSourceAdapter


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    base=Path(__file__).resolve().parent
    source=base/'source.txt'
    revision=hashlib.sha256(source.read_bytes()).hexdigest()
    adapter=FileSourceAdapter(source,'synthetic-comparison-v1')
    rows=[]
    for case in json.loads((base/'cases.json').read_text()):
        for mode in ('source','reference','retrieve'):
            options={'content_budget':20480 if mode=='source' else 1800,'prompt_budget':65536}
            if mode=='reference':options['ranges']=case['ranges']
            envelope,retrieval,user=prepare(adapter,revision,case['question'],mode,**options)
            spans=envelope['spans'] if envelope else []
            covered=[any(s['start_byte']<=start and end<=s['end_byte'] for s in spans)
                     for start,end in case['ranges']]
            rows.append({'case':case['id'],'mode':mode,'required_ranges_present':covered,
                         'all_reference_ranges_present':all(covered),
                         'delivered_bytes':envelope['delivered_bytes'] if envelope else 0,
                         'coverage':envelope['coverage'] if envelope else 'none',
                         'retrieval':retrieval,'semantic_support':'not_evaluated'})
    root=base.parents[1]
    paths=[base/'source.txt',base/'cases.json',base/'protocol.md',Path(__file__),
           root/'src/agora/passages.py',root/'src/agora/source.py',root/'src/agora/query.py']
    report={'schema':'agora/retrieval-diagnostic/v0.1','model_calls':0,
            'file_hashes':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
            'rows':rows,'limits':'Range coverage only. Does not establish semantic sufficiency or model quality.'}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open('x') as stream:json.dump(report,stream,ensure_ascii=False,indent=2)
    for row in rows:
        print(row['case'],row['mode'],row['all_reference_ranges_present'],row['delivered_bytes'])


if __name__=='__main__':main()
