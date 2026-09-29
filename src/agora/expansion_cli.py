"""Additional commands for the existing issue CLI; explicit ledger creation."""
from . import expansion_review as review

COMMANDS={'review-init','review-import','review-inspect','review-recover','expand-prepare','expand-inspect','expand-evaluate'}

def add_commands(sub):
    sub.add_parser('review-init',help='Crear registro separado de revisiones; sin migración.')
    s=sub.add_parser('review-import',help='Conservar juicio inicial suministrado; no ejecutar proveedor.')
    s.add_argument('--review',required=True);s.add_argument('--input',required=True)
    s=sub.add_parser('review-inspect',help='Consultar revisión u operación de ampliación.')
    group=s.add_mutually_exclusive_group(required=True);group.add_argument('--review');group.add_argument('--operation')
    s.add_argument('--details',action='store_true')
    s=sub.add_parser('review-recover',help='Recuperar respuesta guardada; nunca llamar al proveedor.')
    s.add_argument('--operation',required=True)
    s=sub.add_parser('expand-prepare',help='Preparar pasajes con búsqueda léxica explícita.')
    for name in ('parent','expected-parent','source','source-id','source-sha256','out'):
        s.add_argument('--'+name,required=True)
    s.add_argument('--budget',type=int,default=4096);s.add_argument('--top-k',type=int,default=3)
    s=sub.add_parser('expand-inspect',help='Inspeccionar plan y revalidar fuente y padre.')
    s.add_argument('--plan',required=True);s.add_argument('--expected-plan-sha256',required=True);s.add_argument('--details',action='store_true')
    s=sub.add_parser('expand-evaluate',help='Crear revisión derivada sobre el plan exacto.')
    for name in ('review','plan','expected-plan-sha256'):
        s.add_argument('--'+name,required=True)
    s.add_argument('--provider',choices=('glm','jev'),required=True)
    group=s.add_mutually_exclusive_group(required=True);group.add_argument('--response');group.add_argument('--live',action='store_true')

def summary(record):
    r=record['record']
    return dict(review=record['id'],sha256=record['sha256'],support=r['support'],origin=r['origin'],parent=r['parent'],admission=r['admission'])

def run(args,workspace,write_new):
    ledger=review.Ledger(workspace/'reviews.sqlite3',create=args.command=='review-init')
    try:
        if args.command=='review-init':
            return dict(status='review_ledger_initialized')
        if args.command=='review-import':
            return dict(status='imported',**summary(review.import_review(ledger,args.review,review.read(args.input))))
        if args.command=='expand-prepare':
            document=review.prepare(ledger,args.parent,args.expected_parent,args.source,args.source_id,args.source_sha256,args.budget,args.top_k)
            write_new(args.out,document)
            return dict(status='expansion_prepared',plan_sha256=document['sha256'],retrieved_bytes=document['plan']['envelope']['delivered_bytes'],output=args.out)
        if args.command=='expand-inspect':
            document=review.read(args.plan);plan=review.validate_plan(ledger,document,args.expected_plan_sha256)
            if args.details:
                return dict(status='observed',document=document)
            return dict(status='observed',parent=plan['parent_id'],parent_sha256=plan['parent_sha256'],source_sha256=plan['source_sha256'],query=plan['query'],ranges=[{k:s[k] for k in ('start_byte','end_byte','sha256')} for s in plan['envelope']['spans']],retrieved_bytes=plan['envelope']['delivered_bytes'],evidence_bytes=len(plan['evidence'].encode()),evidence_sufficiency='unknown')
        if args.command=='expand-evaluate':
            response=review.read(args.response) if args.response else None
            result=review.evaluate(ledger,args.review,review.read(args.plan),args.expected_plan_sha256,args.provider,response=response,call=review.live if args.live else None)
            return dict(status='review_committed',**summary(result))
        if args.command=='review-recover':
            return dict(status='review_recovered',provider_called=False,**summary(review.finalize(ledger,args.operation)))
        record=ledger.get('reviews' if args.review else 'operations',args.review or args.operation)
        if record is None:
            raise ValueError('unknown_review_record')
        if args.details:
            return dict(status='observed',record=record)
        if args.review:
            return dict(status='observed',**summary(record))
        return dict(status='observed',operation=record['id'],state=record['record']['state'],sha256=record['sha256'])
    finally:
        ledger.close()
