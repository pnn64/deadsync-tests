import json,pathlib,sys
import worker
label=sys.argv[1];request=json.loads(pathlib.Path(sys.argv[2]).read_text())
job=request['job'];job['worker']=label
original=worker.execute
def execute(*args,**kwargs):
    kwargs['memory']='26G'
    return original(*args,**kwargs)
worker.execute=execute
status=worker.ROOT/'results'/('worker-pool-'+label+'.json')
worker.write(status,{'worker':'pool-'+label,'total':1,'completed':0,'current':job,'updated_at':worker.now()})
result=worker.run_case(job,label)
worker.write(status,{'worker':'pool-'+label,'total':1,'completed':1,'finished_at':worker.now(),'results':[{'id':job['id'],'status':result['status']}]})
print(json.dumps({'pool':label,'id':job['id'],'status':result['status']}),flush=True)
