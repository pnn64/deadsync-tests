import concurrent.futures,collections,json,subprocess
from remote import run,WORK
locations=[('192.168.1.23','pass2-resource-results'),('192.168.1.34','pass2-resource-results'),('192.168.1.37','pass2-subscriber-results'),('192.168.1.49','pass2-controls-b-results'),('192.168.1.49','pass2-controls-c-results'),('192.168.1.49','pass2-controls-d-results')]
locations += [('192.168.1.23','pass2-james-results'),('192.168.1.34','pass2-james-results')]
running={r['vmid'] for r in json.loads(subprocess.check_output(['ssh','-o','BatchMode=yes','root@192.168.1.79','pvesh','get','/nodes/x79d8d/qemu','--output-format','json'])) if r['status']=='running'}
ip_ids={r['ip']:r['vmid'] for r in json.loads((WORK/'fleet.json').read_text())};ip_ids['192.168.1.49']=1316
previous=json.loads((WORK/'extra-results.json').read_text()) if (WORK/'extra-results.json').exists() else []
def inspect(location):
 ip,directory=location
 if ip_ids[ip] not in running:return [r for r in previous if r['ip']==ip and r['result_directory']==directory]
 code="import pathlib,json;p=pathlib.Path('/opt/song-lua-audit')/"+repr(directory)+";print(json.dumps([json.loads(f.read_text()) for f in p.glob('*/result.json')]))"
 data=json.loads(run(code,ip=ip,capture_output=True,timeout=30).stdout)
 for r in data:r.update(ip=ip,result_directory=directory)
 return data
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=sum(pool.map(inspect,locations),[])
(WORK/'extra-results.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps([{'id':r['id'],'status':r['status'],'mismatches':r.get('comparison',{}).get('mismatch_count'),'name':r['source_simfile']} for r in results],indent=2))
