"""Retry the retained clean SM capture at the SSC worker's 50 GiB budget."""
import json,subprocess
from remote import WORK,run,ssh
row=json.loads((WORK/'results/272cbdbb21a302b2.json').read_text())
assert row['status']=='replay_resource_limit'
assert row['native']['completion']['reason']=='gameplay-exit' and row['native']['script_errors']==[]
a=next(a for a in row['artifacts'] if '/candidate/' in a['file'])
src='/opt/song-lua-audit/pass2-results/'+a['file']
dest='/opt/song-lua-audit/pass2-imported-results/'+a['file']
code="import pathlib;r=pathlib.Path('/opt/song-lua-audit');assert not (r/'final-paint-sm-memory50.py').exists();p=pathlib.Path("+repr(dest)+");assert p.is_relative_to(r/'pass2-imported-results');p.parent.mkdir(parents=True,exist_ok=True)"
run(code,ip='192.168.1.47')
source=subprocess.Popen(ssh('192.168.1.36')+['cat',src],stdout=subprocess.PIPE)
try:
 copied=subprocess.run(ssh('192.168.1.47')+['tee',dest],stdin=source.stdout,stdout=subprocess.DEVNULL)
finally:source.stdout.close()
assert copied.returncode==source.wait()==0
run("import pathlib,hashlib;p=pathlib.Path("+repr(dest)+");assert p.stat().st_size=="+str(a['bytes'])+";assert hashlib.file_digest(p.open('rb'),'sha256').hexdigest()=="+repr(a['sha256']),ip='192.168.1.47')
row.update(result_directory='pass2-imported-results',final_memory='50G')
script="""import pathlib,json,subprocess,time
r=pathlib.Path('/opt/song-lua-audit')
while subprocess.run(['systemctl','is-active','--quiet','song-lua-final-await-active']).returncode==0:time.sleep(10)
p=r/'final-jobs-paint-sm.json';p.write_text(json.dumps([ROW]))
subprocess.run(['python3',str(r/'final-replay-worker.py'),str(p)],check=True)
""".replace('ROW',repr(row))
code="""import pathlib,subprocess
r=pathlib.Path('/opt/song-lua-audit');p=r/'final-paint-sm-memory50.py';p.write_text(SCRIPT)
subprocess.run(['sudo','systemd-run','--unit=song-lua-final-paint-sm-memory50','--collect','--property=User=parity','--property=Group=parity','--working-directory='+str(r),'/usr/bin/python3',str(p)],check=True)
""".replace('SCRIPT',repr(script))
run(code,ip='192.168.1.47')
receipt={'id':row['id'],'original_capture_ip':'192.168.1.36','original_capture_archive':src,'replay_ip':'192.168.1.47','imported_archive':dest,'compressed_sha256':a['sha256'],'bytes':a['bytes'],'original_replay_memory':'42G','final_replay_memory':'50G','native_capture_regenerated':False,'reason':'Retest the same clean fresh native capture with the final runner and the larger budget already used for the SSC variant.'}
(WORK/'paint-sm-resource-retry.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('Queued final Paint SM replay at 50 GiB after the SSC final check; imported capture hash verified.')
