import json,pathlib,subprocess,time,hashlib
from remote import WORK,run,ssh
ip='192.168.1.34'
while True:
 state=json.loads(run("import subprocess,json;print(json.dumps({u:subprocess.run(['systemctl','is-active','--quiet',u]).returncode==0 for u in ['song-lua-pass2-resource-retry','song-lua-pass2-james-retry','song-lua-final-await-active']}))",ip=ip,capture_output=True).stdout)
 if not any(state.values()):break
 time.sleep(20)
code="""import pathlib,json,hashlib
r=pathlib.Path('/opt/song-lua-audit');results={};verified=[]
for d in ['pass2-results','pass2-final-results']:
 results[d]=[json.loads(p.read_text()) for p in (r/d).glob('*/result.json')]
 for row in results[d]:
  for a in row.get('artifacts',[]):
   p=r/d/a['file'];assert hashlib.file_digest(p.open('rb'),'sha256').hexdigest()==a['sha256'];verified.append({'path':str(p),'sha256':a['sha256']})
print(json.dumps({'results':results,'verified':verified}))
"""
saved=json.loads(run(code,ip=ip,capture_output=True,timeout=600).stdout)
(WORK/'worker1303-preservation.json').write_text(json.dumps(saved,indent=2)+'\n')
for directory,rows in saved['results'].items():
 for row in rows:row.update(ip=ip,vmid=1303,result_directory=directory)
 if directory=='pass2-final-results':(WORK/'final-results-1303.json').write_text(json.dumps(rows,indent=2)+'\n')
 else:
  for row in rows:
   if row['id'].startswith('pass2-pilot-'):continue
   (WORK/'results'/ (row['id']+'.json')).write_text(json.dumps(row,indent=2)+'\n')
subprocess.run(['ssh','-o','BatchMode=yes','root@192.168.1.79','qm','shutdown','1303','--timeout','40'],check=True)
subprocess.run(['ssh','-o','BatchMode=yes','root@192.168.1.79','qm','start','1314'],check=True)
ip='192.168.1.47'
for _ in range(60):
 try:run('print("ready")',ip=ip,capture_output=True,timeout=15);break
 except subprocess.SubprocessError:time.sleep(2)
else:raise RuntimeError('Worker 14 did not boot')
code='''import pathlib,json,shutil,subprocess
r=pathlib.Path('/opt/song-lua-audit');case=r/'pass2-results/67053c6979c0becb'
archive=r/'pass2-interrupted/67053c6979c0becb-host-oom';archive.parent.mkdir(exist_ok=True)
assert case.resolve().is_relative_to(r) and archive.resolve().is_relative_to(r)
assert (case/'traces/native.json').is_file() and not archive.exists()
case.rename(archive)
source=(r/'worker_pass2.py').read_text()
line="        result['stages']['capture']=execute(case,'capture',command,job.get('capture_timeout',900)+90)"
assert source.count(line)==1
replacement="""        if job.get('reused_capture'):
            original=pathlib.Path(job['reused_capture']);assert original.is_relative_to(ROOT/'pass2-interrupted')
            os.link(original,trace/'native.json')
            result['stages']['capture']={'exit':0,'reused_completed_capture':str(original),'sha256':sha(original),'reason':'host OOM interrupted archive creation after capture completion'}
        else:
            result['stages']['capture']=execute(case,'capture',command,job.get('capture_timeout',900)+90)"""
(r/'worker_recover.py').write_text(source.replace(line,replacement))
jobs=json.loads((r/'pass2-jobs/jobs-14.json').read_text())
jobs[0]['reused_capture']=str(archive/'traces/native.json')
(r/'pass2-jobs/jobs-14-recovery.json').write_text(json.dumps(jobs,indent=2))
subprocess.run(['sudo','systemd-run','--unit=song-lua-pass2-worker-14-recovery','--collect','--property=User=parity','--property=Group=parity','--setenv=HOME=/home/parity','/usr/bin/python3',str(r/'worker_recover.py'),str(r/'pass2-jobs/jobs-14-recovery.json'),'--worker','14'],check=True)
print(json.dumps({'preserved_attempt':str(archive),'recovery_jobs':len(jobs),'reused_capture':jobs[0]['reused_capture']}))
'''
receipt=json.loads(run(code,ip=ip,capture_output=True).stdout)
(WORK/'worker14-recovery.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt,flush=True)
