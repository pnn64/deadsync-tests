"""Guest 1402: validate the roll clock correction against unit and full-song tests."""
import hashlib,json,os,pathlib,shutil,subprocess,sys
ROOT=pathlib.Path('/opt/song-lua-audit');REPO=ROOT/'deadsync-pass3'
source='tests/song_lua_itgmania_semantic_parity/native_gameplay.rs'
old=ROOT/'pass3-afterdark-diagnostic'
current=subprocess.check_output(['git','diff','--binary','--',source],cwd=REPO)
assert hashlib.sha256(current).hexdigest()==json.loads((old/'result.json').read_text())['diagnostic_diff_sha256']
(REPO/source).write_bytes(subprocess.check_output(['git','show','HEAD:'+source],cwd=REPO))
for name in ['deadsync-r1.patch','deadsync-roll-clock.patch']:
    subprocess.run(['git','apply','--check',str(ROOT/name)],cwd=REPO,check=True)
    subprocess.run(['git','apply',str(ROOT/name)],cwd=REPO,check=True)
env=dict(os.environ,PATH='/home/parity/.cargo/bin:'+os.environ['PATH'],CARGO_TARGET_DIR=str(ROOT/'deadsync/target'),
    CARGO_PROFILE_RELEASE_LTO='false',CARGO_PROFILE_RELEASE_CODEGEN_UNITS='16',CARGO_PROFILE_RELEASE_DEBUG='1',
    CARGO_PROFILE_RELEASE_STRIP='none',RUSTFLAGS='-C force-frame-pointers=yes')
subprocess.run(['cargo','test','--locked','--release','-p','deadsync-gameplay','--lib','autoplay_roll','-j','2'],cwd=REPO,env=env,check=True)
OUT=ROOT/'pass3-roll-fix';OUT.mkdir(exist_ok=True)
with (OUT/'build-artifacts.jsonl').open('w') as f:
    subprocess.run(['cargo','rustc','--locked','--release','--test','full_song_lua','-j','2','--message-format=json-render-diagnostics'],cwd=REPO,env=env,stdout=f,check=True)
rows=[json.loads(line) for line in (OUT/'build-artifacts.jsonl').read_text().splitlines() if line.startswith('{')]
binary=next(r['executable'] for r in rows if r.get('target',{}).get('name')=='full_song_lua' and r.get('executable'))
runner=ROOT/'bin/full_song_lua-pass3-r2';shutil.copy2(binary,runner)
sys.path.insert(0,str(ROOT));import worker_pass2 as w
w.RESULTS=OUT
proof={'baseline':json.loads((ROOT/'pass3-build-proof.json').read_text()),'runner_sha256':w.sha(runner),
       'patches':{name:w.sha(ROOT/name) for name in ['deadsync-r1.patch','deadsync-roll-clock.patch']}}
w.write(OUT/'build-proof.json',proof)
candidate=old/'d059e57749d31496857e7c565a4c78c5bfb40c3a0c8222cbeacda344f547766c.tar'
assert w.sha(candidate)==candidate.stem
result={'started_at':w.now(),'source':proof,'capture_reused':str(candidate)}
result['replay']=w.execute(OUT,'roll-fix',[runner,'--archive',candidate,'--report',OUT/'report.json'],600,memory='6G')
if (OUT/'report.json').exists():
    result['comparison']=w.document_summary(OUT/'report.json',report=True)
    result['report']=w.compress(OUT/'report.json',remove=True)
result['finished_at']=w.now();w.write(OUT/'result.json',result)
print(json.dumps({'exit':result['replay']['exit'],'mismatches':result.get('comparison',{}).get('mismatch_count'),
    'accepted':result.get('comparison',{}).get('archive_accepted')}),flush=True)
