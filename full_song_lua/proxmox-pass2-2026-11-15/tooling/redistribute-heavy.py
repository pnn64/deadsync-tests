import json,subprocess,time
from remote import run,WORK
jobs=json.loads((WORK/'jobs.json').read_text())
chosen=[j for j in jobs if j['id'] in ['10fe9862c1cf88c3','272cbdbb21a302b2','7a0708216dd461ad','9a7dc9dd696c05ad']]
assert len(chosen)==4
run("import subprocess;assert subprocess.run(['systemctl','is-active','--quiet','song-lua-pass2-worker-05']).returncode!=0",ip='192.168.1.36')
run('''import subprocess,json
vmid=1305
c=json.loads(subprocess.check_output(['pvesh','get',f'/nodes/x79d8d/qemu/{vmid}/config','--output-format','json'],text=True));assert c['name'].startswith('deadsync-lua-pass2-')
if c.get('memory') != 49152:
 subprocess.run(['qm','shutdown',str(vmid),'--timeout','90'],check=True)
 assert subprocess.check_output(['qm','status',str(vmid)],text=True).strip()=='status: stopped'
 subprocess.run(['qm','set',str(vmid),'--memory','49152'],check=True)
 subprocess.run(['qm','start',str(vmid)],check=True)
''',ip='192.168.1.79',user='root')
for j in chosen:
 ip={'14':'192.168.1.47','15':'192.168.1.48'}[j['worker']]
 code=r'''import pathlib,json,datetime
root=pathlib.Path('/opt/song-lua-audit/pass2-results');p=root/ID/'result.json'
assert not p.exists(),str(p)
p.parent.mkdir(exist_ok=True)
p.write_text(json.dumps({'id':ID,'status':'delegated','source_simfile':SOURCE,'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'delegated_to':{'vmid':1305,'ip':'192.168.1.36','result_directory':'pass2-results'},'reason':'Queued job moved to a finished worker with 42 GiB stage memory; this receipt is not a test result.'},indent=2)+'\n')
'''.replace('ID',repr(j['id'])).replace('SOURCE',repr(j['source_simfile']))
 run(code,ip=ip)
 j.update(original_worker=j['worker'],worker='05-heavy',stage_memory='42G')
script='''import worker_pass2 as w,json
jobs=JOBS
for i,j in enumerate(jobs):
 w.write(w.RESULTS/'worker-05-heavy.json',{'total':len(jobs),'completed':i,'current':j})
 result=w.run_case(j,'05-heavy');print(json.dumps({'id':result['id'],'status':result['status']}),flush=True)
w.write(w.RESULTS/'worker-05-heavy.json',{'total':len(jobs),'completed':len(jobs),'finished':True})
'''.replace('JOBS',repr(chosen))
code='''import pathlib,subprocess
root=pathlib.Path('/opt/song-lua-audit');p=root/'pass2-heavy-extra.py';p.write_text(SCRIPT)
subprocess.run(['sudo','systemd-run','--unit=song-lua-pass2-heavy-extra','--collect','--property=User=parity','--property=Group=parity','--property=RuntimeMaxSec=21600','--working-directory='+str(root),'python3',str(p)],check=True)
'''.replace('SCRIPT',repr(script))
for attempt in range(20):
 try:run(code,ip='192.168.1.36');break
 except subprocess.CalledProcessError:time.sleep(3)
else:raise RuntimeError('worker 1305 did not restart')
(WORK/'heavy-redistribution.json').write_text(json.dumps(chosen,indent=2)+'\n')
print('Four queued heavy jobs moved to VM 1305, 42 GiB per stage.')
