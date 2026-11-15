import concurrent.futures,hashlib,json,pathlib,subprocess,time,os
from remote import run,ssh,WORK
fleet=json.loads((WORK/'fleet.json').read_text())
rows=json.loads((WORK/'all-results.json').read_text())+json.loads((WORK/'extra-results.json').read_text())
rows={r['id']:r for r in rows if r['status'] in ['pass','parity_failure']}
order=[1312,1301,1311,1308,1306,1307,1304,1309,1310,1313]
if os.environ.get('FINAL_VM_IDS'):order=list(map(int,os.environ['FINAL_VM_IDS'].split(',')))
proof=json.loads((WORK/'final-validation-source-snapshot.json').read_text())
binary=WORK/'full_song_lua-final-validation';digest=hashlib.file_digest(binary.open('rb'),'sha256').hexdigest()
receipts=[]
for vmid in order:
 vm=next(r for r in fleet if r['vmid']==vmid);ip=vm['ip']
 jobs=[r for r in rows.values() if r['ip']==ip]
 if not jobs:continue
 subprocess.run(['ssh','-o','BatchMode=yes','root@192.168.1.79','qm','start',str(vmid)],check=True)
 for _ in range(60):
  try:run('print("ready")',ip=ip,capture_output=True,timeout=15);break
  except subprocess.SubprocessError:time.sleep(2)
 else:raise RuntimeError('VM did not become ready')
 remote_bin='/opt/song-lua-audit/bin/full_song_lua-final-validation'
 with binary.open('rb') as f:subprocess.run(ssh(ip)+['tee',remote_bin],stdin=f,stdout=subprocess.DEVNULL,check=True)
 code="import pathlib,json,hashlib,subprocess; r=pathlib.Path('/opt/song-lua-audit'); b=r/'bin/full_song_lua-final-validation';assert hashlib.file_digest(b.open('rb'),'sha256').hexdigest()=="+repr(digest)+";b.chmod(0o755)\n"
 for name,content in [('final-validation-source-snapshot.json',json.dumps(proof)),('final-jobs-light.json',json.dumps(jobs)),('final-replay-worker.py',(WORK/'final-replay-worker.py').read_text())]:
  code+="(r/"+repr(name)+").write_text("+repr(content)+")\n"
 code+="subprocess.run(['sudo','systemd-run','--unit=song-lua-final-replays','--collect','--property=User=parity','--property=Group=parity','--setenv=HOME=/home/parity','/usr/bin/python3',str(r/'final-replay-worker.py'),str(r/'final-jobs-light.json')],check=True)"
 run(code,ip=ip,capture_output=True)
 print('Final replays started',vmid,len(jobs),flush=True)
 while True:
  out=run("import pathlib,json,subprocess;p=pathlib.Path('/opt/song-lua-audit/pass2-final-results');print(json.dumps({'active':subprocess.run(['systemctl','is-active','--quiet','song-lua-final-replays']).returncode==0,'results':[json.loads(f.read_text()) for f in p.glob('*/result.json')]}))",ip=ip,capture_output=True)
  state=json.loads(out.stdout)
  for r in state['results']:r.update(ip=ip,vmid=vmid,result_directory='pass2-final-results')
  (WORK/('final-results-'+str(vmid)+'.json')).write_text(json.dumps(state['results'],indent=2)+'\n')
  if not state['active']:break
  time.sleep(20)
 assert len(state['results'])==len(jobs) and all(r.get('finished_at') for r in state['results'])
 print('Final results',vmid,[(r['id'],r['status'],r.get('comparison',{}).get('mismatch_count')) for r in state['results']],flush=True)
 subprocess.run(['ssh','-o','BatchMode=yes','root@192.168.1.79','qm','shutdown',str(vmid),'--timeout','40'],check=True)
 receipts.append({'vmid':vmid,'runner_sha256':digest,'jobs':len(jobs),'stopped':True})
 (WORK/'final-light-completion.json').write_text(json.dumps(receipts,indent=2)+'\n')
