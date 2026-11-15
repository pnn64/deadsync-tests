import concurrent.futures,json,subprocess
from remote import WORK,run
fleet=json.loads((WORK/'fleet.json').read_text())+[dict(vmid=1316,ip='192.168.1.49')]
running={r['vmid'] for r in json.loads(subprocess.check_output(['ssh','-o','BatchMode=yes','root@192.168.1.79','pvesh','get','/nodes/x79d8d/qemu','--output-format','json'])) if r['status']=='running'}
def collect(vm):
 if vm['vmid'] not in running:return
 try:
  rows=json.loads(run("import pathlib,json;r=pathlib.Path('/opt/song-lua-audit/pass2-final-results');print(json.dumps([json.loads(p.read_text()) for p in r.glob('*/result.json')]))",ip=vm['ip'],capture_output=True,timeout=30).stdout)
  for row in rows:row.update(ip=vm['ip'],vmid=vm['vmid'],result_directory='pass2-final-results')
  if rows:(WORK/('final-results-'+str(vm['vmid'])+'.json')).write_text(json.dumps(rows,indent=2)+'\n')
 except Exception as error:print(vm['vmid'],str(error))
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as p:list(p.map(collect,fleet))
rows=sum([json.loads(p.read_text()) for p in WORK.glob('final-results-*.json')],[])
(WORK/'final-results.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps([dict(id=r['id'],status=r['status'],mismatches=r.get('comparison',{}).get('mismatch_count')) for r in rows]))
