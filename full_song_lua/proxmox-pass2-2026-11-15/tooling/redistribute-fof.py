import json,time,subprocess
from remote import WORK,run
job=next(j for j in json.loads((WORK/'jobs.json').read_text()) if j['id']=='e115c0f3019c18b4')
run("""import subprocess,json,pathlib
c=json.loads(subprocess.check_output(['pvesh','get','/nodes/x79d8d/qemu/1315/config','--output-format','json']))
assert c['name'].startswith('deadsync-lua-pass2-') and int(c['memory'])==57344
available=int(next(s.split()[1] for s in pathlib.Path('/proc/meminfo').read_text().splitlines() if s.startswith('MemAvailable:')))*1024
assert available>72*1024**3,available
assert subprocess.check_output(['qm','status','1315']).decode().strip()=='status: stopped'
subprocess.run(['qm','start','1315'],check=True)
""",ip='192.168.1.79',user='root')
for _ in range(30):
 try:run('print("ready")',ip='192.168.1.48',capture_output=True,timeout=15);break
 except subprocess.SubprocessError:time.sleep(2)
else:raise RuntimeError('worker did not restart')
run("import pathlib;r=pathlib.Path('/opt/song-lua-audit');assert not (r/'pass2-fof-followup.py').exists();assert not (r/'pass2-results/e115c0f3019c18b4/result.json').exists()",ip='192.168.1.48')
run("""import pathlib,json,datetime
p=pathlib.Path('/opt/song-lua-audit/pass2-results/e115c0f3019c18b4/result.json');assert not p.exists()
p.parent.mkdir(exist_ok=True)
p.write_text(json.dumps({'id':'e115c0f3019c18b4','source_simfile':'fof_guys/fof.ssc','status':'delegated','finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'delegated_to':{'vmid':1315,'ip':'192.168.1.48','result_directory':'pass2-results'},'reason':'Unstarted followup moved to the idle fresh worker 1315 with its original 50 GiB stage limit, after memory headroom verification. This receipt is not a result.'}))
""",ip='192.168.1.36')
job.update(original_worker=job['worker'],worker='15-fof-heavy',stage_memory='50G')
script="""import json,subprocess
import worker_pass2 as w
job=JOB
w.write(w.RESULTS/'worker-15-fof-heavy.json',{'total':1,'completed':0,'current':job})
row=w.run_case(job,'15-fof-heavy');print(json.dumps({'id':row['id'],'status':row['status']}),flush=True)
w.write(w.RESULTS/'worker-15-fof-heavy.json',{'total':1,'completed':1,'finished':True})
final=[]
if row['status'] in ['pass','parity_failure']:
 row.update(result_directory='pass2-results',final_memory='50G');final.append(row)
p=w.ROOT/'final-jobs-fof.json';p.write_text(json.dumps(final))
subprocess.run(['python3',str(w.ROOT/'final-replay-worker.py'),str(p)],check=True)
""".replace('JOB',repr(job))
code="""import pathlib,subprocess
r=pathlib.Path('/opt/song-lua-audit');p=r/'pass2-fof-followup.py';p.write_text(SCRIPT)
subprocess.run(['sudo','systemd-run','--unit=song-lua-pass2-fof-followup','--collect','--property=User=parity','--property=Group=parity','--working-directory='+str(r),'/usr/bin/python3',str(p)],check=True)
""".replace('SCRIPT',repr(script))
run(code,ip='192.168.1.48')
(WORK/'fof-redistribution.json').write_text(json.dumps(job,indent=2)+'\n')
print('Started fof on the idle fresh worker 1315 with a 50 GiB stage limit.')
