import json,pathlib,sys
import worker
label=sys.argv[1];requests=json.loads(pathlib.Path(sys.argv[2]).read_text());done=[]
original=worker.execute
def execute(*args,**kwargs):
 kwargs['memory']='26G';return original(*args,**kwargs)
worker.execute=execute
status=worker.ROOT/'results'/('worker-capture-pool-'+label+'.json')
for request in requests:
 job=request['job'];job['worker']=label
 worker.write(status,{'worker':'capture-pool-'+label,'total':len(requests),'completed':len(done),'current':job,'updated_at':worker.now()})
 r=worker.run_case(job,label);done.append({'id':job['id'],'status':r['status']})
 print(json.dumps(done[-1]),flush=True)
worker.write(status,{'worker':'capture-pool-'+label,'total':len(requests),'completed':len(done),'results':done,'finished_at':worker.now()})
