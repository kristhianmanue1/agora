#!/usr/bin/env python3
"""Explicit generation or review of a relation; one provider invocation maximum."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from agora.relation_workflow import run,jev_provider
from agora.plan_generation import live_provider
from agora.transform import unique_object


def read_json(path):
    with path.open('rb') as stream:raw=stream.read(1048577)
    if len(raw)>1048576:raise ValueError('input_too_large')
    return json.loads(raw,object_pairs_hook=unique_object)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['generate','review'])
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--source-id',required=True)
    parser.add_argument('--expected-sha256',required=True)
    parser.add_argument('--question')
    parser.add_argument('--candidate',type=Path)
    parser.add_argument('--out',type=Path,required=True)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--response',type=Path)
    mode.add_argument('--live',choices=['glm','jev'])
    parser.add_argument('--contract-version',choices=['v1','v2'],help='Only for generate; review reads the candidate schema.')
    args=parser.parse_args()
    if args.contract_version and args.action!='generate':
        parser.error('--contract-version applies only to generate; review uses candidate schema')
    if args.action=='generate' and (not args.question or args.candidate or args.live=='jev'):
        parser.error('generate requires --question, no --candidate; live generator is glm')
    if args.action=='review' and (not args.candidate or args.question):
        parser.error('review requires --candidate and no --question')
    try:
        with args.source.open('rb') as stream:raw=stream.read(4194305)
        candidate=read_json(args.candidate) if args.candidate else None
        if args.action=='review' and type(candidate) is not dict:raise ValueError('invalid_candidate')
        response=read_json(args.response) if args.response else None
        args.out.mkdir(parents=True,exist_ok=False)
        marker={'execution_status':'started','origin':'live_provider' if args.live else 'supplied_response_replay','provider':args.live}
        (args.out/'result.json').write_text(json.dumps(marker)+'\n')
        def provider(system,user):
            if args.response:return response
            if args.live=='jev':return jev_provider(system,user)
            return live_provider(system,user,max_tokens=4096,json_object=True)
        result=run(raw,args.source_id,args.expected_sha256,provider,question=args.question,candidate=candidate,contract_version=args.contract_version or "v1")
        result.update(origin=marker['origin'],provider=args.live)
        (args.out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        # Output candidate only after successful structural validation; original is in result.
        if args.action=='generate' and result['execution_status']=='complete':
            (args.out/'candidate.json').write_text(json.dumps(result['assessment']['candidate'],ensure_ascii=False,indent=2)+'\n')
        print(json.dumps({'execution_status':result['execution_status'],'out':str(args.out),'admitted':False}))
        return 0 if result['execution_status']=='complete' else 2
    except (ValueError,OSError) as exc:
        print(json.dumps({'execution_status':'rejected','error':str(exc)}),file=sys.stderr)
        return 2

if __name__=='__main__':raise SystemExit(main())
