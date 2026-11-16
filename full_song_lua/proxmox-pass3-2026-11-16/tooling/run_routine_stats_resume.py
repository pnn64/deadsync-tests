import datetime,hashlib,json,os,pathlib,shutil,subprocess
ROOT=pathlib.Path('/opt/song-lua-audit');REPO=ROOT/'input-deadsync';OUT=ROOT/'pass3-routine-stats-resume'
assert not OUT.exists();OUT.mkdir()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
previous=json.loads((ROOT/'pass3-routine-stats-fix/source-proof.json').read_text())
for name,expected in previous['source_normalized_sha256'].items():assert sha(REPO/name)==expected,name
files=json.loads((ROOT/'routine-stats-resume-text.json').read_text())
for name,e in files.items():
 if e['before_sha256'] is None:assert not (REPO/name).exists(),name
 else:assert sha(REPO/name)==e['before_sha256'],name
for name,e in files.items():
 if sha(REPO/name)!=e['after_sha256']:(REPO/name).write_text(e['text'])
 assert sha(REPO/name)==e['after_sha256']
proof={'base_runner':previous,'deadsync_committed_base':'56e841e6e85d5ce8ebbd39e382b73803cb4f254b','source_normalized_sha256':{n:e['after_sha256'] for n,e in files.items()},'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(OUT/'source-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
env=dict(os.environ,PATH='/home/parity/.cargo/bin:'+os.environ['PATH'],CARGO_TARGET_DIR=str(ROOT/'deadsync/target'),CARGO_PROFILE_RELEASE_LTO='false',CARGO_PROFILE_RELEASE_CODEGEN_UNITS='16',CARGO_PROFILE_RELEASE_DEBUG='1',CARGO_PROFILE_RELEASE_STRIP='none',RUSTFLAGS='-C force-frame-pointers=yes')
checks=[('gameplay-tests',['cargo','test','--locked','--release','-j','6','-p','deadsync-gameplay','--lib','--','--test-threads=2']),
 ('routine-statistics-tests',['cargo','test','--locked','--release','-j','6','-p','deadsync-song-lua','--features','test-support','--test','statistics','--','--test-threads=2']),
 ('native-gameplay-tests',['cargo','test','--locked','--release','-j','6','--test','song_lua_itgmania_semantic_parity','native_gameplay::','--','--test-threads=2'])]
for label,args in checks:
 print(label,flush=True)
 with (OUT/(label+'.log')).open('w') as log:subprocess.run(args,cwd=REPO,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
with (OUT/'build-artifacts.jsonl').open('w') as log:subprocess.run(['cargo','rustc','--locked','--release','--test','full_song_lua','-j','6','--message-format=json-render-diagnostics'],cwd=REPO,env=env,stdout=log,check=True)
rows=[json.loads(line) for line in (OUT/'build-artifacts.jsonl').read_text().splitlines() if line.startswith('{')]
binary=next(r['executable'] for r in rows if r.get('target',{}).get('name')=='full_song_lua' and r.get('executable'))
runner=ROOT/'bin/full_song_lua-pass3-routine-stats';shutil.copy2(binary,runner)
for name,e in files.items():assert sha(REPO/name)==e['after_sha256']
proof.update(finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),runner_sha256=sha(runner))
(OUT/'build-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({'runner_sha256':proof['runner_sha256']}),flush=True)
