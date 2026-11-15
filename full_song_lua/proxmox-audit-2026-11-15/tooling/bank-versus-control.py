"""Fresh native control for Bank Account's unconditional second-player proxies."""
import json,pathlib,time
import worker
status=worker.ROOT/'results/worker-bank-versus-control.json'
while True:
 p=worker.ROOT/'results/worker-02.json'
 if p.exists() and json.loads(p.read_text()).get('finished_at'):break
 time.sleep(10)
job=json.loads((worker.ROOT/'bank-versus-control-job.json').read_text())
worker.write(status,{'worker':'bank-versus-control','total':1,'completed':0,'current':job,'updated_at':worker.now()})
r=worker.run_case(job,'02')
worker.write(status,{'worker':'bank-versus-control','total':1,'completed':1,'finished_at':worker.now(),'results':[{'id':r['id'],'status':r['status']}]})
print(json.dumps({'id':r['id'],'status':r['status']}),flush=True)
