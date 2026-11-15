import hashlib,json,pathlib,subprocess,os
from remote import WORK,run,ssh
binary=WORK/'full_song_lua-final-validation';digest=hashlib.file_digest(binary.open('rb'),'sha256').hexdigest()
proof=(WORK/'final-validation-source-snapshot.json').read_text()
locations=[('192.168.1.23','26G',['song-lua-pass2-resource-retry','song-lua-pass2-james-retry'],['pass2-results','pass2-resource-results']),
 ('192.168.1.34','26G',['song-lua-pass2-resource-retry','song-lua-pass2-james-retry'],['pass2-results','pass2-resource-results']),
 ('192.168.1.36','42G',['song-lua-pass2-heavy-extra'],['pass2-results']),
 ('192.168.1.48','50G',['song-lua-pass2-worker-15'],['pass2-results']),
 ('192.168.1.49','12G',[],['pass2-controls-b-results','pass2-controls-c-results','pass2-controls-d-results']),
 ('192.168.1.47','50G',['song-lua-pass2-worker-14-recovery'],['pass2-results'])]
for ip,memory,wait_units,directories in locations:
 if os.environ.get('FINAL_QUEUE_IPS') and ip not in os.environ['FINAL_QUEUE_IPS'].split(','):continue
 if ip!='192.168.1.49':
  with binary.open('rb') as f:subprocess.run(ssh(ip)+['tee','/opt/song-lua-audit/bin/full_song_lua-final-validation'],stdin=f,stdout=subprocess.DEVNULL,check=True)
 wrapper='''import pathlib,subprocess,json,time
r=pathlib.Path('/opt/song-lua-audit')
while any(subprocess.run(['systemctl','is-active','--quiet',u]).returncode==0 for u in WAIT):time.sleep(15)
jobs={}
for directory in DIRS:
 for p in (r/directory).glob('*/result.json'):
  row=json.loads(p.read_text()); key=row['id'].removesuffix('-memory26')
  if row['status'] not in ['pass','parity_failure'] or row['id'].startswith('pass2-pilot-'):continue
  if row['source_simfile'].startswith('__pass2_controls/') and row['id'] not in ['feedback-apollo-v2','feedback-megalovania-v2','roll-long-frame','join-reload-v3']:continue
  row.update(result_directory=directory,final_memory=MEMORY);jobs[key]=row
p=r/'final-jobs-active.json';p.write_text(json.dumps(list(jobs.values())))
subprocess.run(['python3',str(r/'final-replay-worker.py'),str(p)],check=True)
'''.replace('WAIT',repr(wait_units)).replace('DIRS',repr(directories)).replace('MEMORY',repr(memory))
 code="import pathlib,subprocess,hashlib;r=pathlib.Path('/opt/song-lua-audit');b=r/'bin/full_song_lua-final-validation';assert hashlib.file_digest(b.open('rb'),'sha256').hexdigest()=="+repr(digest)+";b.chmod(0o755)\n"
 for name,value in [('final-validation-source-snapshot.json',proof),('final-replay-worker.py',(WORK/'final-replay-worker.py').read_text()),('final-await-active.py',wrapper)]:code+='(r/'+repr(name)+').write_text('+repr(value)+')\n'
 code+="subprocess.run(['sudo','systemd-run','--unit=song-lua-final-await-active','--collect','--property=User=parity','--property=Group=parity','--setenv=HOME=/home/parity','/usr/bin/python3',str(r/'final-await-active.py')],check=True)"
 run(code,ip=ip,capture_output=True)
 print('Queued final comparisons',ip,memory,flush=True)
