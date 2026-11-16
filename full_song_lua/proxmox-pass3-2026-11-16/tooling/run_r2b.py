"""Guest 1402: combine the verified fixes and make a fresh After Dark capture."""
import json,os,pathlib,shutil,subprocess,sys,time
ROOT=pathlib.Path('/opt/song-lua-audit');REPO=ROOT/'deadsync-pass3'
for _ in range(1440):
    state=subprocess.check_output(['systemctl','show','song-lua-pass3-roll-fix','-p','ActiveState','-p','ExecMainStatus'],text=True)
    if state.splitlines() and 'ActiveState=active' not in state and 'ActiveState=activating' not in state:break
    time.sleep(5)
else:raise RuntimeError('roll fix still active; do not replace its runner')
assert 'ActiveState=inactive' in state and 'ExecMainStatus=0' in state,state
previous=json.loads((ROOT/'pass3-roll-fix/result.json').read_text())
assert previous['replay']['exit']==0 and previous['comparison']['archive_accepted'],previous['comparison'].get('mismatch_count')
subprocess.run(['git','apply','--check',str(ROOT/'inactive-autoplay-seed.patch')],cwd=REPO,check=True)
subprocess.run(['git','apply',str(ROOT/'inactive-autoplay-seed.patch')],cwd=REPO,check=True)
env=dict(os.environ,PATH='/home/parity/.cargo/bin:'+os.environ['PATH'],CARGO_TARGET_DIR=str(ROOT/'deadsync/target'),
    CARGO_PROFILE_RELEASE_LTO='false',CARGO_PROFILE_RELEASE_CODEGEN_UNITS='16',CARGO_PROFILE_RELEASE_DEBUG='1',
    CARGO_PROFILE_RELEASE_STRIP='none',RUSTFLAGS='-C force-frame-pointers=yes')
OUT=ROOT/'pass3-r2b-results';OUT.mkdir(exist_ok=True)
with (OUT/'build-artifacts.jsonl').open('w') as f:
    subprocess.run(['cargo','rustc','--locked','--release','--test','full_song_lua','-j','2','--message-format=json-render-diagnostics'],cwd=REPO,env=env,stdout=f,check=True)
rows=[json.loads(line) for line in (OUT/'build-artifacts.jsonl').read_text().splitlines() if line.startswith('{')]
binary=next(r['executable'] for r in rows if r.get('target',{}).get('name')=='full_song_lua' and r.get('executable'))
runner=ROOT/'bin/full_song_lua-pass3-r2b';shutil.copy2(binary,runner)
sys.path.insert(0,str(ROOT));import worker_pass2 as w
w.RESULTS=OUT;w.RUNNER=runner;w.HARNESS=ROOT/'bin/itgmania-harness-pass3-r1'
assert w.sha(w.HARNESS)==json.loads((ROOT/'pass3-r1-proof-from-1401.json').read_text())['binaries']['itgmania-harness-pass3-r1']
proof={'baseline':json.loads((ROOT/'pass3-build-proof.json').read_text()),'runner_sha256':w.sha(runner),
       'harness_sha256':w.sha(w.HARNESS),'roll_patch_sha256':w.sha(ROOT/'deadsync-roll-clock.patch'),
       'initial_roster_patch_sha256':w.sha(ROOT/'deadsync-r1.patch'),'inactive_seed_patch_sha256':w.sha(ROOT/'inactive-autoplay-seed.patch')}
w.write(OUT/'build-proof.json',proof);w.write(ROOT/'pass2-source-snapshot.json',proof)
job=json.loads((ROOT/'afterdark-job.json').read_text())
result=w.run_case(job,'1402')
print(json.dumps({'id':job['id'],'status':result['status'],'mismatches':result.get('comparison',{}).get('mismatch_count')}),flush=True)
