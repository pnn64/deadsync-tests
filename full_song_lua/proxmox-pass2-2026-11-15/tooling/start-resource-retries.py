import concurrent.futures,json,subprocess,time
from remote import run,WORK
rows=[r for r in json.loads((WORK/'fleet.json').read_text()) if r['worker'] in ['02','03']]
primary=json.loads((WORK/'all-results.json').read_text())
jobs=[]
for result in primary:
 if result['status'] in ['capture_resource_limit','replay_resource_limit']:
  job=dict(result['profile']);job.update(id=job['id']+'-memory26',stage_memory='26G',run_role='memory-budget-retry',max_events=6000000,capture_timeout=1800,replay_timeout=2400);jobs.append(job)
ultimate=next(dict(r['profile']) for r in primary if r['source_simfile'].startswith('DS ULTIMATE'))
ultimate.update(id=ultimate['id']+'-fixed60',stage_memory='26G',run_role='fixed-update-control',fixed_update_fps=60,max_events=6000000,capture_timeout=1800,replay_timeout=2400)
groups=[[ultimate]+jobs[::2],jobs[1::2]]
for row in rows:
 run('''import subprocess
assert subprocess.run(['systemctl','is-active','--quiet','song-lua-pass2-worker-WORKER']).returncode!=0
assert not subprocess.check_output(['pgrep','-f','^/opt/song-lua-audit/bin/'],text=True) if subprocess.run(['pgrep','-f','^/opt/song-lua-audit/bin/'],capture_output=True).returncode==0 else True
'''.replace('WORKER',row['worker']),ip=row['ip'],capture_output=True)
code='''import subprocess,json,pathlib
for vmid in [1302,1303]:
 config=json.loads(subprocess.check_output(['pvesh','get',f'/nodes/x79d8d/qemu/{vmid}/config','--output-format','json'],text=True))
 assert config['name'].startswith('deadsync-lua-pass2-')
 subprocess.run(['qm','shutdown',str(vmid),'--timeout','90'],check=True)
 assert subprocess.check_output(['qm','status',str(vmid)],text=True).strip()=='status: stopped'
 subprocess.run(['qm','set',str(vmid),'--memory','32768'],check=True)
 subprocess.run(['qm','start',str(vmid)],check=True)
'''
run(code,ip='192.168.1.79',user='root')
def start(pair):
 row,jobs=pair
 script='''import json,pathlib,worker_pass2 as worker
root=worker.ROOT
worker.RESULTS=root/'pass2-resource-results';worker.RESULTS.mkdir(exist_ok=True)
jobs=JOBS
for i,job in enumerate(jobs):
 worker.write(worker.RESULTS/'status.json',{'completed':i,'total':len(jobs),'current':job})
 result=worker.run_case(job,'memory26')
 print(json.dumps({'id':result['id'],'status':result['status'],'mismatches':result.get('comparison',{}).get('mismatch_count')}),flush=True)
worker.write(worker.RESULTS/'status.json',{'completed':len(jobs),'total':len(jobs),'finished':True})
'''.replace('JOBS',repr(jobs))
 code='''import pathlib,subprocess
p=pathlib.Path('/opt/song-lua-audit/pass2-resource-retry.py');p.write_text(SCRIPT)
assert int([line for line in pathlib.Path('/proc/meminfo').read_text().splitlines() if line.startswith('MemTotal:')][0].split()[1])>30000000
subprocess.run(['sudo','systemd-run','--unit=song-lua-pass2-resource-retry','--collect','--property=User=parity','--property=Group=parity','--property=RuntimeMaxSec=21600','--working-directory=/opt/song-lua-audit','python3',str(p)],check=True)
'''.replace('SCRIPT',repr(script))
 for attempt in range(20):
  try:run(code,ip=row['ip'],capture_output=True,timeout=30);return {**row,'jobs':jobs}
  except subprocess.CalledProcessError:time.sleep(3)
 raise RuntimeError(row)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:receipts=list(pool.map(start,zip(rows,groups)))
(WORK/'resource-retries.json').write_text(json.dumps(receipts,indent=2)+'\n')
print('Resource retries running: '+str([len(j) for j in groups]),flush=True)
