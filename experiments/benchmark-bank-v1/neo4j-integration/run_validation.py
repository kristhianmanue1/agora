import os, subprocess, secrets, time, json, pathlib, datetime
root=pathlib.Path('/tmp/aria-neo4j-integration'); root.mkdir(exist_ok=True)
name='aria-neo4j-validation-'+secrets.token_hex(4)
password=secrets.token_hex(20)
env=os.environ.copy(); env['NEO4J_AUTH']='neo4j/'+password
result={'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'container':name,'image':'neo4j:5.26.6','backend':'Neo4jGraphDB; not Community+Qdrant','provider_calls':0}
try:
    result['image_id']=subprocess.check_output(['docker','image','inspect','neo4j:5.26.6','--format','{{.Id}}'],text=True).strip()
    subprocess.run(['docker','run','-d','--name',name,'-p','127.0.0.1:17687:7687','--tmpfs','/data','--tmpfs','/logs','-e','NEO4J_AUTH','-e','NEO4J_server_memory_heap_initial__size=256m','-e','NEO4J_server_memory_heap_max__size=512m', 'neo4j:5.26.6'],env=env,check=True,stdout=subprocess.DEVNULL)
    from neo4j import GraphDatabase
    for attempt in range(45):
        try:
            with GraphDatabase.driver('bolt://127.0.0.1:17687',auth=('neo4j',password)) as driver: driver.verify_connectivity()
            break
        except Exception:
            if attempt==44: raise RuntimeError('Disposable Neo4j did not become ready')
            time.sleep(2)
    env.update(NEO4J_INTEGRATION_TESTS='1',NEO4J_URI='bolt://127.0.0.1:17687',NEO4J_USER='neo4j',NEO4J_PASSWORD=password,NEO4J_DB_NAME='neo4j',PYTHONPATH='/tmp/memos-validation-worktree/src:/tmp/aria-bench-tools/lib/python3.11/site-packages',MEMOS_BASE_PATH='/tmp/memos-validation-state',PYTEST_DISABLE_PLUGIN_AUTOLOAD='1')
    cmd=['/Users/krisnova/www/memOs/.venv/bin/python','-B','-m','pytest','tests/mem_feedback','tests/graph_dbs/test_neo4j_keyword_feedback.py','tests/graph_dbs/test_neo4j_vector_search.py','tests/graph_dbs/test_search_return_fields.py','-p','pytest_asyncio.plugin','-q','-rs','-o','addopts=']
    with (root/'pytest.log').open('w') as log:
        proc=subprocess.run(cmd,cwd='/tmp/memos-validation-worktree',env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180)
    result['pytest_exit_code']=proc.returncode
    result['command']=cmd
finally:
    clean=subprocess.run(['docker','rm','-f','-v',name],capture_output=True,text=True)
    result['cleanup_exit_code']=clean.returncode
    result['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    (root/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
