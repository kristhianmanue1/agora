"""Offline QASPER v0.3 preparation and prediction export; never calls a model."""
import argparse
import hashlib
import json
from pathlib import Path


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def render(paper):
    chunks=[]; paragraphs=[]; offset=0
    def add(text, is_paragraph=False):
        nonlocal offset
        if not isinstance(text,str): raise ValueError('invalid_text')
        raw=text.encode('utf-8')
        if is_paragraph:
            paragraphs.append({'text':text,'start_byte':offset,'end_byte':offset+len(raw)})
        chunks.append(raw+b'\n\n');offset+=len(raw)+2
    add(paper['title']);add(paper['abstract'],True)
    for section in paper['full_text']:
        add(section['section_name'] or '')
        for paragraph in section['paragraphs']: add(paragraph,True)
    return b''.join(chunks),paragraphs


def eligible(qa, paragraphs):
    annotations=[a['answer'] for a in qa['answers']]
    if not annotations: return None,'no_annotations'
    states={a['unanswerable'] for a in annotations}
    if len(states)!=1 or not all(type(a['unanswerable']) is bool for a in annotations):
        return None,'answerability_disagreement'
    if states=={True}:return 'unanswerable',None
    for a in annotations:
        if not a['evidence']:return None,'no_evidence'
        for evidence in a['evidence']:
            if 'FLOAT SELECTED' in evidence:return None,'visual_evidence'
            if sum(p['text'].strip()==evidence.strip() for p in paragraphs)!=1:
                return None,'unmapped_or_ambiguous_evidence'
        if not (a['extractive_spans'] or a['free_form_answer'] or type(a['yes_no']) is bool):
            return None,'invalid_answer'
    return 'answerable',None


def prepare(dataset, out, *, answerable=8, unanswerable=4, max_source_bytes=65536):
    if any(type(x) is not int or x<1 for x in (answerable,unanswerable,max_source_bytes)):
        raise ValueError('invalid_sample_limits')
    raw=dataset.read_bytes()
    if len(raw)>67108864:raise ValueError('dataset_too_large')
    data=json.loads(raw); candidates=[]; excluded=[]; seen=set()
    for pid,paper in sorted(data.items()):
        source,paragraphs=render(paper)
        for qa in paper['qas']:
            qid=qa['question_id']
            if qid in seen:raise ValueError('duplicate_question_id')
            seen.add(qid)
            kind,reason=eligible(qa,paragraphs)
            if len(source)>max_source_bytes:reason='source_budget_exceeded'
            if not isinstance(qa['question'],str) or not 1<=len(qa['question'].strip())<=2000:
                reason='question_length'
            if reason:excluded.append({'question_id':qid,'reason':reason});continue
            candidates.append((qid,pid,kind,qa,source,paragraphs))
    selected=[];used=set();counts={'answerable':0,'unanswerable':0}
    # Fixed stratum order, sorted original IDs, one question per document.
    for kind,target in [('answerable',answerable),('unanswerable',unanswerable)]:
        for row in sorted(candidates):
            if counts[kind]==target:break
            if row[2]!=kind or row[1] in used:continue
            selected.append(row);used.add(row[1]);counts[kind]+=1
        if counts[kind]!=target:raise ValueError('insufficient_eligible_documents')
    out.mkdir(parents=True,exist_ok=False)
    inputs=out/'model_inputs';refs=out/'references'
    inputs.mkdir();refs.mkdir();cases=[];gold={};mapping={}
    for index,(qid,pid,kind,qa,source,paragraphs) in enumerate(selected):
        name=f'case-{index+1:02d}'
        (inputs/(name+'.txt')).write_bytes(source)
        parts=[{'id':'answer','question':qa['question']}]
        write_json(inputs/(name+'-parts.json'),parts)
        cases.append({'id':name,'question_id':qid,'source_id':'qasper:'+pid,
                      'source':name+'.txt','sha256':sha(source),
                      'question':qa['question'],'parts':name+'-parts.json','response_language':'en'})
        gold[pid]={**data[pid],'qas':[qa]}
        mapping[name]={'question_id':qid,'stratum':kind,'paragraphs':paragraphs}
    write_json(inputs/'cases.json',cases)
    write_json(refs/'gold.json',gold);write_json(refs/'paragraphs.json',mapping)
    write_json(refs/'selection.json',{'policy':'qid-sorted-answerable-first-one-paper/v1',
                                    'counts':counts,'excluded':excluded,
                                    'eligible_questions':len(candidates),'max_source_bytes':max_source_bytes,
                                    'dataset_sha256':sha(raw),'split':'test','version':'0.3',
                                    'scope':'diagnostic subset; not official full-test score',
                                    'development':'synthetic fixtures only; no model-output selection'})
    manifest={str(p.relative_to(out)):sha(p.read_bytes()) for p in out.rglob('*') if p.is_file()}
    write_json(out/'freeze.json',manifest)
    return counts


def verify(prepared):
    manifest=json.loads((prepared/'freeze.json').read_text())
    for name,digest in manifest.items():
        path=prepared/name
        if path.resolve().is_relative_to(prepared.resolve()) is False:raise ValueError('invalid_manifest_path')
        if sha(path.read_bytes())!=digest:raise ValueError('freeze_mismatch')


def export_predictions(prepared, results, output):
    verify(prepared)
    cases=json.loads((prepared/'model_inputs/cases.json').read_text())
    mapping=json.loads((prepared/'references/paragraphs.json').read_text())
    rows=[];missing=[]
    for case in cases:
        path=results/case['id']/'result.json'
        if not path.exists():missing.append(case['id']);continue
        r=json.loads(path.read_text())
        if r.get('execution_status')!='complete' or r.get('answer_status') not in ('candidate','candidate_partial'):
            missing.append(case['id']);continue
        if (r.get('source_sha256')!=case['sha256'] or r.get('question')!=case['question']
            or r.get('source_id')!=case['source_id'] or r.get('response_language')!='en'):
            raise ValueError('result_case_mismatch')
        if len(r['parts'])!=1 or r['parts'][0]['id']!='answer':raise ValueError('result_parts_mismatch')
        part=r['parts'][0];evidence=[]
        if any(c.get('part_id')!='answer' for c in r['citations']):raise ValueError('citation_part_mismatch')
        if [c['quote'] for c in r['citations']]!=part['quotes']:raise ValueError('citation_quotes_mismatch')
        source=(prepared/'model_inputs'/case['source']).read_bytes()
        for citation in r['citations']:
            for match in citation['matches']:
                start,end=match['start_byte'],match['end_byte']
                if not 0<=start<end<=len(source) or source[start:end].decode()!=citation['quote']:
                    raise ValueError('citation_mismatch')
                for p in mapping[case['id']]['paragraphs']:
                    if start<p['end_byte'] and end>p['start_byte'] and p['text'] not in evidence:
                        evidence.append(p['text'])
        if part['status']=='not_in_document':
            if part['answer'] or part['quotes'] or evidence:raise ValueError('invalid_abstention')
            answer='Unanswerable'
        elif part['status']=='answer':answer=part['answer']
        else:raise ValueError('invalid_status')
        rows.append({'question_id':case['question_id'],'predicted_answer':answer,'predicted_evidence':evidence})
    with output.open('x',encoding='utf-8') as stream:
        for row in rows:stream.write(json.dumps(row,ensure_ascii=False)+'\n')
    return {'exported':len(rows),'missing_or_failed':missing,
            'evidence_metric':'cited paragraphs; not all retrieved paragraphs'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('prepare');p.add_argument('--dataset',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--answerable',type=int,default=8);p.add_argument('--unanswerable',type=int,default=4)
    p.add_argument('--max-source-bytes',type=int,default=65536)
    p=sub.add_parser('export');p.add_argument('--prepared',type=Path,required=True);p.add_argument('--results',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    if args.command=='prepare': result=prepare(args.dataset,args.out,answerable=args.answerable,unanswerable=args.unanswerable,max_source_bytes=args.max_source_bytes)
    else:result=export_predictions(args.prepared,args.results,args.out)
    print(json.dumps(result))

if __name__=='__main__':main()
