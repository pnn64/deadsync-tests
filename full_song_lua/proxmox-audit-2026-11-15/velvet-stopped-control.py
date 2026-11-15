import json,pathlib,time
import worker
root=worker.ROOT;status=root/'results/worker-velvet-control.json'
worker.write(status,{'worker':'velvet-control','total':1,'completed':0,'waiting':True})
while True:
    main=root/'results/worker-15.json';recheck=root/'results/video-recheck-15.json'
    if main.exists() and recheck.exists() and json.loads(main.read_text()).get('finished_at') and json.loads(recheck.read_text()).get('finished_at'):break
    time.sleep(10)
job=json.loads((root/'velvet-stopped-control-job.json').read_text())
worker.write(status,{'worker':'velvet-control','total':1,'completed':0,'current':job,'updated_at':worker.now()})
result=worker.run_case(job,'15')
worker.write(status,{'worker':'velvet-control','total':1,'completed':1,'finished_at':worker.now(),'result':result['status']})
print(json.dumps({'control':job['id'],'status':result['status']}),flush=True)
