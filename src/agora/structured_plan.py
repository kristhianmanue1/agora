"""Opt-in QASPER structure enrichment with exact source and baseline preservation."""
import json
from .source import FileSourceAdapter,SourceError,digest
from .qasper import render
from .structure_selection import nodes,select
from .subquestions import prepare_subquestions,merge_ranges
VERSION='agora/subquestions-plan/v3-structured-experimental'
def prepare(adapter,revision,spec,structure,budget=20000,top_k=3):
    if not isinstance(structure,dict) or set(structure)!={'title','abstract','full_text'}:
        raise ValueError('invalid_source_structure')
    if not isinstance(structure['full_text'],list):raise ValueError('invalid_source_structure')
    for s in structure['full_text']:
        if not isinstance(s,dict) or set(s)!={'section_name','paragraphs'} or not isinstance(s['paragraphs'],list):raise ValueError('invalid_source_structure')
    base=prepare_subquestions(adapter,revision,spec,budget,top_k)
    if len(spec['questions'])!=1:raise ValueError('structured_single_question_required')
    raw,_=render(structure)
    if digest(raw)!=revision:raise ValueError('structure_source_mismatch')
    sections,size=nodes(structure)
    if size!=len(raw):raise ValueError('structure_size_mismatch')
    selected=select(raw,spec['questions'][0]['query'],sections,'headings-lists',budget)
    chosen=merge_ranges([(s['start_byte'],s['end_byte']) for s in (base['envelope'] or {}).get('spans',[])])
    skipped=[]
    for pair in selected['ranges']:
        proposed=merge_ranges(chosen+[pair])
        if sum(b-a for a,b in proposed)<=budget:chosen=proposed
        else:skipped.append(pair)
    result=dict(base);result.update(schema=VERSION,structure=structure,structure_sha256=digest(json.dumps(structure,sort_keys=True,ensure_ascii=False).encode()),allocation='preserve_lexical_then_add_source_structure',baseline_ranges=merge_ranges([(s['start_byte'],s['end_byte']) for s in (base['envelope'] or {}).get('spans',[])]),skipped_structure_ranges=skipped)
    result['envelope']=adapter.fetch(revision,chosen,content_budget=budget) if chosen else None
    result['delivered_bytes']=result['envelope']['delivered_bytes'] if chosen else 0
    for q in result['questions']:
        missing=[r for r in q['reference_ranges'] if not any(a<=r[0] and r[1]<=b for a,b in chosen)]
        q.update(missing_reference_ranges=missing,reference_coverage='unknown' if not q['reference_ranges'] else 'partial' if missing else 'covered')
    return result

def add_command(sub):
    p=sub.add_parser('retrieve-structured',help='Experimental: conservar selección léxica y añadir estructura QASPER verificada; cero llamadas.')
    for name in ('source','source-id','source-sha256','spec','structure','structure-sha256','out'):p.add_argument('--'+name,required=True)
    p.add_argument('--budget',type=int,default=20000);p.add_argument('--top-k',type=int,default=3)
def run(args,read,write_new):
    from .coverage_cli import bounded
    from .transform import unique_object
    raw=bounded(args.structure,1048576)
    if digest(raw)!=args.structure_sha256:raise ValueError('structure_hash_mismatch')
    structure=json.loads(raw,object_pairs_hook=unique_object)
    result=prepare(FileSourceAdapter(args.source,args.source_id),args.source_sha256,read(args.spec),structure,args.budget,args.top_k)
    write_new(args.out,result)
    return dict(status='prepared',schema=VERSION,delivered_bytes=result['delivered_bytes'],provider_calls=0,global_completeness='not_established',output=str(args.out))
