"""Synthetic Skopos -> packet -> Agora pilot; three paid calls at most."""
import hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]

def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    skopos=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve()
    out.mkdir(parents=True,exist_ok=False)
    shutil.copytree(ROOT/'src/agora',out/'code/agora',ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copytree(skopos/'experiments/meeting-source-v1',out/'skopos',ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copyfile(ROOT/'experiments/review-invariance-v1/transport_diagnostic.py',out/'transport.py')
    shutil.copyfile(BASE/'run.py',out/'run.py');shutil.copyfile(BASE/'README.md',out/'protocol.md')
    save(out/'versions.json',{name:subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip() for name,root in [('agora',ROOT),('skopos',skopos)]})
    sys.path[:0]=[str(out/'code'),str(out/'skopos')]
    from persistent import PersistentMeetingStore
    from export import export_packet
    from agora.source import FileSourceAdapter
    from agora.evidence import query_evidence
    from agora.split_review import review_split
    first={'source_id':'meeting-lumbre','revision':1,'supersedes':None,'complete':True,'segments':[
        {'id':'delivery','start_ms':0,'end_ms':10000,'speaker':'Nerea','text':'Entrega acordada: lunes 28 de septiembre de 2026; lote de 40 equipos.'},
        {'id':'owner','start_ms':10000,'end_ms':20000,'speaker':'Nerea','text':'Responsable de la entrega: Nerea. La entrega depende de completar la prueba de aceptación.'}]}
    save(out/'meeting-v1.json',first)
    store=PersistentMeetingStore(out/'meeting.sqlite')
    store.ingest(out/'meeting-v1.json')
    second=json.loads(json.dumps(first));second.update(revision=2,supersedes=sha(out/'meeting-v1.json'))
    second['segments'][0]['text']='Entrega acordada: martes 29 de septiembre de 2026; lote de 40 equipos.'
    save(out/'meeting-v2.json',second);store.ingest(out/'meeting-v2.json');store.close()
    store=PersistentMeetingStore(out/'meeting.sqlite')
    try:
        assert not store.search('lunes')
        packet=export_packet(store,['entrega'])
        assert packet['revision']==2
        save(out/'packet.json',packet);(out/'source.txt').write_bytes(packet['text'].encode())
        assert sha(out/'source.txt')==packet['content_sha256']
        question='¿Cuál es el plan vigente de entrega y qué presupuesto tiene?'
        aspects=[{'id':'delivery','question':'Indica fecha y cantidad de la entrega vigente.'},
                 {'id':'owner','question':'Identifica responsable y condición de la entrega.'},
                 {'id':'budget','question':'¿Qué presupuesto monetario está especificado?'}]
        save(out/'request.json',{'question':question,'aspects':aspects})
        frozen={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file() and p.suffix!='.sqlite'}
        save(out/'freeze.json',frozen);calls=[];stopped=False
        def provider(system,user):
            nonlocal stopped
            if stopped or len(calls)>=3:raise RuntimeError('call_budget_or_stop')
            assert all(sha(out/n)==h for n,h in frozen.items())
            ordinal=len(calls)+1;record={'ordinal':ordinal,'status':'attempted'}
            calls.append(record);save(out/'calls.json',calls)
            request=out/('request-%d.json'%ordinal)
            save(request,{'model':'glm-5.3-flash','temperature':0,'max_tokens':8192,'response_format':{'type':'json_object'},'messages':[{'role':'system','content':system},{'role':'user','content':user}]})
            started=time.monotonic()
            try:
                run=subprocess.run([sys.executable,str(out/'transport.py'),str(request),'90'],capture_output=True,text=True,timeout=100)
                response=json.loads(run.stdout);save(out/('response-%d.json'%ordinal),response)
                tokens=response.get('usage',{}).get('total_tokens')
                if run.returncode or type(tokens) is not int or tokens<0:raise RuntimeError('transport_or_unknown_usage')
                record.update(status='complete',tokens=tokens,reported_model=response.get('reported_model'))
                return response
            except Exception as exc:
                stopped=True;record.update(status='failed',error=type(exc).__name__);raise
            finally:
                record['seconds']=round(time.monotonic()-started,3);save(out/'calls.json',calls);print(json.dumps(record),flush=True)
        candidate=query_evidence(FileSourceAdapter(out/'source.txt',packet['source_id']),packet['content_sha256'],question,aspects,provider)
        save(out/'candidate.json',candidate)
        navigation=[]
        if candidate['execution_status']=='complete':
            for citation in candidate['citations']:
                quote=citation['quote'];matches=[]
                for span in packet['spans']:
                    if quote in span['text']:
                        original=store.fetch(packet['source_id'],packet['revision'],span['locator']['id'])
                        assert original['status']=='verified' and original['sha256']==packet['source_sha256']
                        assert quote in original['segment']['text']
                        matches.append(span['locator'])
                if not matches:raise ValueError('quote_not_mapped_to_original')
                navigation.append({'part_id':citation['part_id'],'claim_index':citation['claim_index'],'quote':quote,'locators':matches})
            save(out/'navigation.json',navigation)
            review=review_split(candidate,provider,provider);save(out/'review.json',review)
        else:review={}
        summary={'source_revision':packet['revision'],'old_term_excluded':not store.search('lunes'),
                 'candidate_status':candidate['execution_status'],'answer_status':candidate.get('answer_status'),
                 'review_status':review.get('execution_status','not_attempted'),
                 'review_recommendation':review.get('recommendation'),'verified_quote_count':len(navigation),
                 'calls':len(calls),'known_tokens':sum(c.get('tokens',0) for c in calls),
                 'unknown_usage_calls':sum('tokens' not in c for c in calls),
                 'admission':'not_performed','frozen_files_verified':all(sha(out/n)==h for n,h in frozen.items())}
        save(out/'summary.json',summary);print(json.dumps(summary),flush=True)
        return 2 if stopped or candidate['execution_status']!='complete' or review.get('execution_status')!='complete' else 0
    finally:store.close()

if __name__=='__main__':raise SystemExit(main())
