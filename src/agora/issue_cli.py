"""Explicit issue preparation, evaluation, recovery and host-repair CLI."""
import argparse
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
from .issue_runtime import ROOT,flow,derived

WORKSPACE='agora/issues-workspace/v1-experimental'
def read(path):
    value=json.loads(Path(path).read_text(encoding='utf-8'),object_pairs_hook=flow.storage.protocol.unique)
    if not isinstance(value,dict):raise ValueError('json_object_required')
    return value
def write_new(path,value):
    with Path(path).open('x',encoding='utf-8') as handle:
        handle.write(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def summary(result):
    return dict(revision_sha256=result['revision_sha256'],assessment_status=result['assessment']['status'],admission=result['admission'])
def transport(request,workspace):
    if not os.environ.get('ZAI_API_KEY'):raise ValueError('provider_key_missing')
    # The recovery engine has reserved an operation before reaching this function.
    with tempfile.TemporaryDirectory(prefix='request-',dir=workspace) as directory:
        path=Path(directory)/'request.json';write_new(path,request)
        proc=subprocess.run([sys.executable,str(ROOT/'experiments/review-invariance-v1/transport_diagnostic.py'),str(path),'180'],capture_output=True,text=True,timeout=190)
        response=json.loads(proc.stdout)
        if proc.returncode:raise ValueError('provider_transport_failed')
        return response

def parser():
    p=argparse.ArgumentParser(description='Pendientes y derivados trazables. Experimental; no admisión automática.')
    p.add_argument('--workspace',type=Path,required=True)
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('init',help='Crear workspace nuevo; nunca migrar uno existente.')
    s=sub.add_parser('seed',help='Incorporar evaluación inicial suministrada explícitamente.')
    s.add_argument('--issue',required=True);s.add_argument('--input',type=Path,required=True);s.add_argument('--response',type=Path,required=True)
    s=sub.add_parser('prepare',help='Preparar una fuente contra la revisión esperada.')
    s.add_argument('--issue',required=True);s.add_argument('--expected-head',required=True);s.add_argument('--source',type=Path,required=True);s.add_argument('--as-of',required=True);s.add_argument('--out',type=Path,required=True)
    s=sub.add_parser('evaluate',help='Evaluar con respuesta conservada o una llamada GLM explícita.')
    s.add_argument('--operation',required=True);s.add_argument('--prepared',type=Path,required=True)
    choice=s.add_mutually_exclusive_group(required=True);choice.add_argument('--response',type=Path,help='Replay local; no se afirma ejecución del proveedor.');choice.add_argument('--live',action='store_true',help='Una llamada glm-5.3-flash, 8192 tokens máximo de salida, sin retry.')
    s=sub.add_parser('inspect',help='Consultar operación o historial.')
    choice=s.add_mutually_exclusive_group(required=True);choice.add_argument('--operation');choice.add_argument('--issue');choice.add_argument('--derivation')
    s.add_argument('--details',action='store_true',help='Incluir contenido y evidencia almacenados.')
    s=sub.add_parser('recover',help='Finalizar respuesta conservada o devolver resultado; nunca llamar al proveedor.')
    s.add_argument('--operation',required=True)
    s=sub.add_parser('repair-propose',help='Crear plan explícito ligado al original; sin incorporar.')
    s.add_argument('--operation',required=True);s.add_argument('--expected-head',required=True);s.add_argument('--out',type=Path,required=True)
    s=sub.add_parser('repair-apply',help='Incorporar derivado separado, sin cambiar la respuesta original.')
    s.add_argument('--derivation',required=True);s.add_argument('--plan',type=Path,required=True);s.add_argument('--expected-plan-sha256',required=True)
    s=sub.add_parser('retrieve-subquestions',help='Preparar subpreguntas y cobertura por rangos declarados; sin proveedor.')
    for name in ('source','source-id','source-sha256','spec','out'):
        s.add_argument('--'+name,required=True)
    s.add_argument('--budget',type=int,default=12000)
    s.add_argument('--top-k',type=int,default=1)
    from .expansion_cli import add_commands
    add_commands(sub)
    return p

def run(args):
    workspace=args.workspace.resolve()
    if args.command=='init':
        workspace.mkdir(mode=0o700,parents=False,exist_ok=False)
        store=flow.Store(workspace/'issues.sqlite3',create=True);store.close()
        store=derived.Store(workspace/'derivations.sqlite3',create=True);store.close()
        write_new(workspace/'workspace.json',dict(schema=WORKSPACE))
        return dict(status='initialized',workspace=str(workspace))
    if read(workspace/'workspace.json')!={'schema':WORKSPACE}:raise ValueError('incompatible_workspace')
    if args.command=='retrieve-subquestions':
        from .subquestions import prepare_subquestions
        from .source import FileSourceAdapter
        report=prepare_subquestions(FileSourceAdapter(args.source,args.source_id),args.source_sha256,read(args.spec),args.budget,args.top_k)
        write_new(args.out,report)
        return dict(status='prepared',output=args.out,delivered_bytes=report['delivered_bytes'],global_completeness=report['global_completeness'],questions=[{k:q[k] for k in ('id','candidate_status','reference_coverage','missing_reference_ranges')} for q in report['questions']],provider_calls=0)
    from .expansion_cli import COMMANDS, run as run_expansion
    if args.command in COMMANDS:
        return run_expansion(args,workspace,write_new)
    store=flow.Store(workspace/'issues.sqlite3')
    try:
        if args.command=='seed':
            data=read(args.input);response=read(args.response)
            if response.get('finish_reason')!='stop':raise ValueError('incomplete_response')
            candidate=flow.encode(flow.storage.protocol.prepare_candidate(response['content'],data))
            head=store.append(args.issue,None,data,response['content'],candidate,dict(kind='supplied_response',response_sha256=flow.digest(response),provider_execution_verified=False))
            return dict(status='seeded',issue=args.issue,head=head,admission='not_admitted')
        if args.command=='prepare':
            prepared=flow.flow.prepare(store,args.issue,args.expected_head,read(args.source),args.as_of)
            write_new(args.out,prepared)
            return dict(status='prepared',package_sha256=prepared['sha256'],output=str(args.out))
        if args.command=='evaluate':
            prepared=read(args.prepared)
            existing=flow.inspect(store,args.operation)
            if args.live:
                if existing is None and not os.environ.get('ZAI_API_KEY'):raise ValueError('provider_key_missing')
                provider=lambda request:dict(transport(request,workspace),execution_origin='live_provider')
            else:
                response=read(args.response)
                # Preserve declared provider metadata but mark execution as replay.
                response=dict(response,execution_origin='supplied_response_replay')
                if existing is not None and 'response' in existing and flow.encode(existing['response'])!=flow.encode(response):raise ValueError('replay_response_conflict')
                provider=lambda request:response
            result=flow.evaluate(store,args.operation,prepared,provider)
            op=flow.inspect(store,args.operation)
            return dict(status='committed',operation=args.operation,execution_origin=op['response'].get('execution_origin','provider_or_unknown'),**summary(result))
        if args.command=='recover':
            result=flow.finalize(store,args.operation)
            return dict(status='recovered',operation=args.operation,provider_called=False,**summary(result))
        if args.command=='inspect':
            if args.operation:
                op=flow.inspect(store,args.operation)
                if op is None:raise ValueError('unknown_operation')
                if args.details:return dict(status='observed',operation=op)
                response=op.get('response',{})
                return dict(status='observed',operation=args.operation,operation_state=op['state'],request_sha256=op['request_hash'],response_origin=response.get('execution_origin','provider_or_unknown'),result=summary(op['result']) if op.get('result') else None)
            if args.issue:
                history=store.history(args.issue)
                if not history:raise ValueError('unknown_issue')
                if args.details:return dict(status='observed',history=history)
                return dict(status='observed',issue=args.issue,revisions=len(history),head=history[-1]['digest'],assessment_status=history[-1]['record']['assessment']['status'])
            ledger=derived.Store(workspace/'derivations.sqlite3')
            try:result=ledger.get(args.derivation)
            finally:ledger.close()
            if result is None:raise ValueError('unknown_derivation')
            return dict(status='observed',derivation=result if args.details else dict(id=result['id'],digest=result['digest'],kind=result['record']['kind'],assessment_status=result['record']['assessment']['status'],source_operation_state=result['record']['source_operation_state'],admission='not_admitted'))
        if args.command=='repair-propose':
            snapshot=derived.capture(store,args.operation,args.expected_head)
            receipt=derived.repair.propose(snapshot['operation']['response']['content'])
            record=derived.derive(snapshot,receipt)
            plan=dict(schema='agora/repair-plan/v1-experimental',snapshot=snapshot,receipt=receipt)
            checksum=flow.digest(plan);write_new(args.out,dict(plan=plan,sha256=checksum))
            return dict(status='repair_proposed',plan_sha256=checksum,assessment_status=record['assessment']['status'],source_operation_state='response_ready')
        if args.command=='repair-apply':
            document=read(args.plan)
            if set(document)!={'plan','sha256'} or document['sha256']!=args.expected_plan_sha256 or flow.digest(document['plan'])!=document['sha256']:raise ValueError('repair_plan_mismatch')
            plan=document['plan']
            if set(plan)!={'schema','snapshot','receipt'} or plan['schema']!='agora/repair-plan/v1-experimental':raise ValueError('invalid_repair_plan')
            snapshot=plan['snapshot'];op=snapshot['operation']
            current=derived.capture(store,op['id'],snapshot['captured_head'])
            if flow.encode(current)!=flow.encode(snapshot):raise ValueError('repair_origin_changed')
            ledger=derived.Store(workspace/'derivations.sqlite3')
            try:result=ledger.put(args.derivation,snapshot,plan['receipt'])
            finally:ledger.close()
            return dict(status='derived',derivation=args.derivation,digest=result['digest'],kind='host_format_repair',source_operation_state='response_ready',assessment_status=result['record']['assessment']['status'],admission='not_admitted')
    finally:store.close()

def main(argv=None):
    args=parser().parse_args(argv);os.umask(0o077)
    try:result=run(args);code=0
    except (ValueError,KeyError,TypeError,OSError,sqlite3.Error,subprocess.SubprocessError) as exc:
        # Do not echo source text, provider bodies, keys, or arbitrary exception text.
        safe=str(exc) if type(exc) is ValueError and str(exc).replace('_','').isalnum() else type(exc).__name__
        result=dict(status='rejected',diagnostic=safe,command=args.command)
        code=2
    print(json.dumps(result,ensure_ascii=False));return code
if __name__=='__main__':raise SystemExit(main())
