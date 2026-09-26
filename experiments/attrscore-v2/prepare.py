"""24 held-aside cases; exclude prior question, answer and reference identities."""
from pathlib import Path
import csv,hashlib,json,shutil
from agora.evidence import query_evidence
from agora.source import FileSourceAdapter,digest

BASE=Path(__file__).resolve().parent
MAPPING={'Attributable':'supported','Contradictory':'contradicted','Extrapolatory':'insufficient'}

def normalized(text):
    return ' '.join(text.split()).casefold()

def select(rows,previous,count=8,seed='agora-attrscore-pilot-02'):
    used={k:{normalized(r[k]) for r in previous if normalized(r[k])} for k in ('query','answer','reference')}
    original={k:set(v) for k,v in used.items()}
    eligible=[]; excluded=[]
    for index,row in enumerate(rows):
        if row['label'] not in MAPPING: raise ValueError('unknown_label')
        if any(normalized(row[k]) and normalized(row[k]) in original[k] for k in used):
            excluded.append({'row_index':index,'reason':'prior_question_answer_or_reference'});continue
        if not row['answer'].strip() or not row['reference'].strip() or len(row['answer'])>6000 or len(row['reference'].encode())>12000 or len(row['query'])>2000:
            excluded.append({'row_index':index,'reason':'consumer_bounds'});continue
        identity=digest(json.dumps([row['query'],row['answer'],row['reference']],ensure_ascii=False).encode())
        eligible.append({'row_index':index,'row':row,'identity':identity,'rank':digest((seed+identity).encode())})
    selected=[];collisions=[]
    for label in MAPPING:
        picked=0
        for item in sorted((x for x in eligible if x['row']['label']==label),key=lambda x:x['rank']):
            row=item['row']
            if any(normalized(row[k]) and normalized(row[k]) in used[k] for k in used):
                collisions.append({'row_index':item['row_index'],'reason':'duplicate_with_selected'});continue
            selected.append(item)
            for k in used:
                if normalized(row[k]): used[k].add(normalized(row[k]))
            picked+=1
            if picked==count:break
        if picked!=count: raise ValueError('insufficient_distinct_cases:'+label)
    return sorted(selected,key=lambda x:x['rank']),{'seed':seed,'total_rows':len(rows),'eligible_after_prior_and_bounds':len(eligible),'excluded':excluded,'selection_collisions':collisions,'selected':len(selected),'per_class':count,'deduplication':'nonempty whitespace-normalized casefold question, answer OR reference; against prior 12 and within new sample; not semantic/topic deduplication'}

def main():
    prior=BASE.parent/'attrscore-v1/inputs'
    inp=BASE/'inputs';inp.mkdir(exist_ok=False)
    for n in ('AttrEval-GenSearch.csv','download.json','README.md'):
        shutil.copyfile(prior/n,inp/n)
    metadata=json.loads((inp/'download.json').read_text())
    raw=inp/'AttrEval-GenSearch.csv'
    assert digest(raw.read_bytes())==metadata['files'][raw.name]['sha256']
    rows=list(csv.DictReader(raw.open()))
    previous_cases=json.loads((prior/'pilot-01/cases.json').read_text())
    previous=[rows[c['source_row_index']] for c in previous_cases]
    (inp/'previous-exposure.json').write_text(json.dumps(previous,indent=2))
    selected,selection=select(rows,previous)
    selection.update(revision=metadata['revision'],csv_sha256=digest(raw.read_bytes()),language='original English',gold='original external labels unchanged; not labels for relevance or recommendation')
    out=inp/'pilot-02';out.mkdir()
    cases=[];gold={}
    for i,item in enumerate(selected,1):
        cid=f'case-{i:02}';row=item['row'];source=out/(cid+'.txt');source.write_text(row['reference'])
        question=row['query'] or 'Assess whether the supplied reference supports the answer.'
        response={'parts':[{'id':'answer','status':'answered','claims':[{'text':row['answer'],'quotes':[row['reference']]}],'missing':[]}]}
        c=query_evidence(FileSourceAdapter(source,item['identity']),digest(source.read_bytes()),question,[{'id':'answer','question':question}],lambda s,u:{'finish_reason':'stop','content':json.dumps(response)},response_language='en',content_budget=12000)
        assert c['execution_status']=='complete'
        c['artifact_origin']='external dataset fixture; not GLM generation'
        (out/(cid+'.json')).write_text(json.dumps(c,indent=2))
        cases.append({'id':cid,'candidate':cid+'.json','source':cid+'.txt','identity':item['identity'],'source_row_index':item['row_index']})
        gold[cid]={'label':row['label'],'support':MAPPING[row['label']]}
    (out/'cases.json').write_text(json.dumps(cases,indent=2));(out/'gold.json').write_text(json.dumps(gold,indent=2));(out/'selection.json').write_text(json.dumps(selection,indent=2))
    print(json.dumps(selection,indent=2))

if __name__=='__main__': main()
