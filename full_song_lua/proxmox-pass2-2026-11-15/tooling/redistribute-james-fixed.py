import json
from remote import WORK,run
job=next(j for j in json.loads((WORK/'jobs.json').read_text()) if j['id']=='ee72a53d84d7fc88-fixed60')
run("import pathlib;r=pathlib.Path('/opt/song-lua-audit');assert not (r/'pass2-james-fixed-followup.py').exists()",ip='192.168.1.23')
code="""import pathlib,json,datetime
p=pathlib.Path('/opt/song-lua-audit/pass2-results/ee72a53d84d7fc88-fixed60/result.json');assert not p.exists()
p.parent.mkdir(exist_ok=True)
p.write_text(json.dumps({'id':'ee72a53d84d7fc88-fixed60','source_simfile':'james/james.ssc','status':'delegated','finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'delegated_to':{'vmid':1302,'ip':'192.168.1.23','result_directory':'pass2-results'},'reason':'Unstarted fixed-frame diagnostic moved to worker 1302 after its final replay queue, with its existing 26 GiB stage limit. This receipt is not a result.'}))
"""
run(code,ip='192.168.1.48')
job.update(original_worker=job['worker'],worker='02-followup-heavy',stage_memory='26G')
script="""import json,subprocess,time
import worker_pass2 as w
while subprocess.run(['systemctl','is-active','--quiet','song-lua-final-await-active']).returncode==0:time.sleep(10)
job=JOB
w.write(w.RESULTS/'worker-02-followup-heavy.json',{'total':1,'completed':0,'current':job})
row=w.run_case(job,'02-followup-heavy');print(json.dumps({'id':row['id'],'status':row['status']}),flush=True)
w.write(w.RESULTS/'worker-02-followup-heavy.json',{'total':1,'completed':1,'finished':True})
final=[]
if row['status'] in ['pass','parity_failure']:
 row.update(result_directory='pass2-results',final_memory='26G');final.append(row)
p=w.ROOT/'final-jobs-followup.json';p.write_text(json.dumps(final))
subprocess.run(['python3',str(w.ROOT/'final-replay-worker.py'),str(p)],check=True)
""".replace('JOB',repr(job))
code="""import pathlib,subprocess
r=pathlib.Path('/opt/song-lua-audit');p=r/'pass2-james-fixed-followup.py';p.write_text(SCRIPT)
subprocess.run(['sudo','systemd-run','--unit=song-lua-pass2-james-fixed-followup','--collect','--property=User=parity','--property=Group=parity','--working-directory='+str(r),'/usr/bin/python3',str(p)],check=True)
""".replace('SCRIPT',repr(script))
run(code,ip='192.168.1.23')
(WORK/'james-fixed-redistribution.json').write_text(json.dumps(job,indent=2)+'\n')
print('Queued James SSC fixed-frame diagnostic on worker 1302 at 26 GiB, after its final replay queue.')
