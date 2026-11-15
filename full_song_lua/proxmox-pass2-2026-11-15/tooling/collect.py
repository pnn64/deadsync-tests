import collections,concurrent.futures,json,pathlib,subprocess
from remote import run,WORK
fleet=json.loads((WORK/'fleet.json').read_text());dest=WORK/'results';dest.mkdir(exist_ok=True)
running={r['vmid'] for r in json.loads(subprocess.check_output(['ssh','-o','BatchMode=yes','root@192.168.1.79','pvesh','get','/nodes/x79d8d/qemu','--output-format','json'])) if r['status']=='running'}
def inspect(row):
 if row['vmid'] not in running:return {**row,'stopped':True}
 code='''import json,pathlib,shutil
p=pathlib.Path('/opt/song-lua-audit/pass2-results')
status=p/STATUS
results=[r for f in p.glob('*/result.json') if not f.parent.name.startswith('pass2-pilot-') and (r:=json.loads(f.read_text())).get('status')!='delegated']
print(json.dumps({'status':json.loads(status.read_text()) if status.exists() else {},'additional_workers':{f.name:json.loads(f.read_text()) for f in p.glob('worker-*-heavy.json')},'results':results,'disk_free':shutil.disk_usage(p).free}))
'''.replace('STATUS',repr('worker-'+row['worker']+'.json'))
 try:
  data=json.loads(run(code,ip=row['ip'],capture_output=True,timeout=30).stdout)
  for r in data['results']:
   r.update(vmid=row['vmid'],ip=row['ip'])
   (dest/(r['id']+'.json')).write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
  return {**row,**{k:v for k,v in data.items() if k!='results'}}
 except Exception as error:return {**row,'error':str(error)}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:state=list(pool.map(inspect,fleet))
results=[json.loads(p.read_text(encoding='utf-8')) for p in dest.glob('*.json')]
(WORK/'all-results.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
(WORK/'fleet-status.json').write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'results':dict(collections.Counter(r['status'] for r in results)),
 'workers':[{'worker':r['worker'],'completed':r.get('status',{}).get('completed'),
  'current':r.get('status',{}).get('current',{}).get('source_simfile'),
  'free_GiB':round(r['disk_free']/2**30,1) if 'disk_free' in r else None,
  'error':r.get('error')} for r in state]},indent=2))
