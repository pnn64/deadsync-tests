"""Restore the published GameState snapshot and resume a terminal validation."""
import hashlib,json,pathlib,subprocess
from remote import WORK,run,ssh
IP='192.168.1.10';store=pathlib.Path('C:/GitHub/deadsync/tests/fixtures')
relative='regression-expectations/deadsync-song-lua/a21e50006934c942.snap'
data=subprocess.check_output(['git','show','HEAD:'+relative],cwd=store)
source=WORK/'pump-game-pinned-expectation.snap';source.write_bytes(data)
receipt={'tests_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=store,text=True).strip(),
 'path':relative,'sha256':hashlib.sha256(data).hexdigest(),
 'previous_normalized_sha256':'7976c286d9fb035c7bb86b76158a6c0d42bedbba1b2f71a0d4d6ba267432b2fe',
 'reason':'Guest retained the old UnjoinPlayer(false) expectation; restore the already published snapshot, without regenerating expectations.'}
subprocess.run(['scp',*ssh(IP)[1:-1],str(source),'parity@'+IP+':/opt/song-lua-audit/'+source.name],check=True)
script='''import subprocess,pathlib,json,hashlib
root=pathlib.Path('/opt/song-lua-audit');out=root/'pass3-pump-game-results';receipt=RECEIPT
state=subprocess.check_output(['systemctl','show','song-lua-pass3-pump-game','-p','ActiveState','-p','ExecMainStatus','-p','InvocationID'],text=True)
assert 'ActiveState=failed' in state and 'ExecMainStatus=1' in state and 'f3493db1ae884cf2a4b71f99e62aeaad' in state,state
assert not (out/'build-proof.json').exists()
target=root/'deadsync-pass3/tests/fixtures'/receipt['path'];old=target.read_bytes()
assert hashlib.sha256(old.replace(b'\\r\\n',b'\\n')).hexdigest()==receipt['previous_normalized_sha256']
data=(root/'pump-game-pinned-expectation.snap').read_bytes();assert hashlib.sha256(data).hexdigest()==receipt['sha256']
assert not (out/'unit-tests-stale-expectation.log').exists()
(out/'unit-tests.log').rename(out/'unit-tests-stale-expectation.log')
(out/'previous-game-state-expectation.snap').write_bytes(old)
target.write_bytes(data)
(out/'expectation-restoration.json').write_text(json.dumps(receipt,indent=2)+'\\n')
'''.replace('RECEIPT',repr(receipt))
run(script,ip=IP)
source=(WORK/'run_pump_game_fix.py').read_text()
source=source.replace('assert not OUT.exists();OUT.mkdir()',"assert OUT.exists() and (OUT/'expectation-restoration.json').exists() and not (OUT/'build-proof.json').exists()")
source=source.replace("subprocess.run(['git','apply','--check',str(patch)],cwd=REPO,check=True)\nsubprocess.run(['git','apply',str(patch)],cwd=REPO,check=True)","subprocess.run(['git','apply','--reverse','--check',str(patch)],cwd=REPO,check=True)")
resume=WORK/'run_pump_game_resume.py';resume.write_text(source)
subprocess.run(['scp',*ssh(IP)[1:-1],str(resume),'parity@'+IP+':/opt/song-lua-audit/'+resume.name],check=True)
result=run('sudo systemd-run --unit=song-lua-pass3-pump-game-resume --property=User=parity --property=Group=parity --property=MemoryMax=7G --property=MemorySwapMax=0 --property=StandardOutput=append:/opt/song-lua-audit/logs/pass3-pump-game-resume.log --property=StandardError=append:/opt/song-lua-audit/logs/pass3-pump-game-resume.log --working-directory=/opt/song-lua-audit /usr/bin/python3 /opt/song-lua-audit/run_pump_game_resume.py',ip=IP,language='bash',capture_output=True)
receipt['launch']=result.stderr.strip();(WORK/'pump-game-resume.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
