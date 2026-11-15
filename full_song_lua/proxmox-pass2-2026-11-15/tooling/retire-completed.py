"""Preserve completed worker receipts and shut down only this pass's idle VMs."""
import datetime,json,subprocess,sys
from remote import WORK,run
vmid=int(sys.argv[1]);assert vmid in [1302,1305,1314,1315]
fleet=json.loads((WORK/'fleet.json').read_text());vm=next(r for r in fleet if r['vmid']==vmid)
ip=vm['ip']
code="""import pathlib,json,hashlib,subprocess
r=pathlib.Path('/opt/song-lua-audit')
units=subprocess.check_output(['systemctl','list-units','--no-legend','--plain','--state=active','song-lua-*']).decode()
assert not units.strip(),units
results={};verified=[]
for d in ['pass2-results','pass2-resource-results','pass2-final-results']:
 results[d]=[json.loads(p.read_text()) for p in (r/d).glob('*/result.json')]
 for row in results[d]:
  assert row['status']!='running',row['id']
  for a in row.get('artifacts',[]):
   p=r/d/a['file'];assert p.stat().st_size==a['bytes']
   with p.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==a['sha256']
   verified.append({'path':str(p),'sha256':a['sha256']})
expected={j['id'] for p in r.glob('final-jobs-*.json') for j in json.loads(p.read_text())}
assert expected=={r['id'] for r in results['pass2-final-results']}
print(json.dumps({'results':results,'verified':verified}))
"""
saved=json.loads(run(code,ip=ip,capture_output=True,timeout=600).stdout)
published={r['sha256'] for r in json.loads((WORK/'published-archives.json').read_text())}
for row in saved['results']['pass2-final-results']:
 if row['status']=='pass':
  assert all(a['sha256'] in published for a in row['artifacts'] if '/accepted/' in a['file']),row['id']
for directory,rows in saved['results'].items():
 for row in rows:row.update(ip=ip,vmid=vmid,result_directory=directory)
 if directory=='pass2-final-results':(WORK/f'final-results-{vmid}.json').write_text(json.dumps(rows,indent=2)+'\n')
 elif directory=='pass2-results':
  for row in rows:
   if row['id'].startswith('pass2-pilot-') or row['status']=='delegated':continue
   (WORK/'results'/(row['id']+'.json')).write_text(json.dumps(row,indent=2)+'\n')
 else:
  p=WORK/'extra-results.json';extra=json.loads(p.read_text())
  extra=[r for r in extra if not (r['ip']==ip and r['result_directory']==directory)]+rows
  p.write_text(json.dumps(extra,indent=2)+'\n')
saved.update(vmid=vmid,ip=ip,verified_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
(WORK/f'worker{vmid}-preservation.json').write_text(json.dumps(saved,indent=2)+'\n')
subprocess.run(['ssh','-o','BatchMode=yes','root@192.168.1.79','qm','shutdown',str(vmid),'--timeout','40'],check=True)
state=subprocess.check_output(['ssh','-o','BatchMode=yes','root@192.168.1.79','qm','status',str(vmid)]).decode().strip()
assert state=='status: stopped',state
print(json.dumps({'vmid':vmid,'status':state,'verified_artifacts':len(saved['verified'])}))
