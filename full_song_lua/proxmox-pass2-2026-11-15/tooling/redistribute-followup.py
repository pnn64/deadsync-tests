import json
from remote import WORK,run
jobs=[j for j in json.loads((WORK/'jobs.json').read_text()) if j['id'] in ['7fa17005f2a1fbae','e115c0f3019c18b4']]
assert len(jobs)==2
run("import pathlib; r=pathlib.Path('/opt/song-lua-audit'); assert not (r/'pass2-followup-heavy.py').exists()",ip='192.168.1.36')
for job in jobs:
 code="""import pathlib,json,datetime
p=pathlib.Path('/opt/song-lua-audit/pass2-results')/ID/'result.json'
assert not p.exists(),str(p)
p.parent.mkdir(exist_ok=True)
p.write_text(json.dumps({'id':ID,'source_simfile':SOURCE,'status':'delegated','finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'delegated_to':{'vmid':1305,'ip':'192.168.1.36','result_directory':'pass2-results'},'reason':'Unstarted job moved to worker 1305 after its final replay queue; 42 GiB stage limit. This receipt is not a test result.'}))
""".replace('ID',repr(job['id'])).replace('SOURCE',repr(job['source_simfile']))
 run(code,ip='192.168.1.47')
 job.update(original_worker=job['worker'],worker='05-followup-heavy',stage_memory='42G')
script="""import json,pathlib,subprocess,time
import worker_pass2 as w
while subprocess.run(['systemctl','is-active','--quiet','song-lua-final-await-active']).returncode==0:time.sleep(10)
jobs=JOBS
final=[]
for i,job in enumerate(jobs):
 w.write(w.RESULTS/'worker-05-followup-heavy.json',{'total':len(jobs),'completed':i,'current':job})
 row=w.run_case(job,'05-followup-heavy')
 print(json.dumps({'id':row['id'],'status':row['status']}),flush=True)
 if row['status'] in ['pass','parity_failure']:
  row.update(result_directory='pass2-results',final_memory='42G');final.append(row)
w.write(w.RESULTS/'worker-05-followup-heavy.json',{'total':len(jobs),'completed':len(jobs),'finished':True})
p=w.ROOT/'final-jobs-followup.json';p.write_text(json.dumps(final))
subprocess.run(['python3',str(w.ROOT/'final-replay-worker.py'),str(p)],check=True)
""".replace('JOBS',repr(jobs))
code="""import pathlib,subprocess
r=pathlib.Path('/opt/song-lua-audit');p=r/'pass2-followup-heavy.py';p.write_text(SCRIPT)
subprocess.run(['sudo','systemd-run','--unit=song-lua-pass2-followup-heavy','--collect','--property=User=parity','--property=Group=parity','--working-directory='+str(r),'/usr/bin/python3',str(p)],check=True)
""".replace('SCRIPT',repr(script))
run(code,ip='192.168.1.36')
(WORK/'followup-redistribution.json').write_text(json.dumps(jobs,indent=2)+'\n')
print('Queued WAWW and fof on worker 1305 after its current final checks.')
