"""Exercise authored player/chart guards with fresh, unchanged song captures."""
import json,time
import worker
root=worker.ROOT;status=root/'results/worker-coverage-controls.json'
while not json.loads((root/'results/worker-entrypoint-probes.json').read_text()).get('finished_at'):time.sleep(10)
original_execute=worker.execute
def execute(*args,**kwargs):
 kwargs['memory']='26G'
 return original_execute(*args,**kwargs)
worker.execute=execute
jobs=json.loads((root/'coverage-control-jobs.json').read_text());done=[]
for job in jobs:
 worker.write(status,{'worker':'coverage-controls','total':len(jobs),'completed':len(done),'current':job,'updated_at':worker.now()})
 result=worker.run_case(job,'large')
 done.append({'id':result['id'],'status':result['status']})
 print(json.dumps(done[-1]),flush=True)
worker.write(status,{'worker':'coverage-controls','total':len(jobs),'completed':len(done),'finished_at':worker.now(),'results':done})
