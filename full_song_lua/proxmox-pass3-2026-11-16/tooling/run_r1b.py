"""Guest 1401: consume the recorded inactive-side controller input and recompare."""
import json,os,pathlib,shutil,subprocess,sys,time
import zstandard
ROOT=pathlib.Path('/opt/song-lua-audit');REPO=ROOT/'deadsync-pass3'
for _ in range(720):
    state=subprocess.check_output(['systemctl','show','song-lua-pass3-r1','-p','ActiveState','-p','ExecMainStatus'],text=True)
    if 'ActiveState=active' not in state and 'ActiveState=activating' not in state:break
    time.sleep(5)
else:raise RuntimeError('r1 is still active; do not rebuild its running runner')
assert 'ActiveState=inactive' in state and 'ExecMainStatus=0' in state,state
old=ROOT/'pass3-r1-inputs/deadsync-r1.patch';new=ROOT/'deadsync-r1b.patch'
subprocess.run(['git','apply','--reverse','--check',str(old)],cwd=REPO,check=True)
subprocess.run(['git','apply','--reverse',str(old)],cwd=REPO,check=True)
subprocess.run(['git','apply','--check',str(new)],cwd=REPO,check=True)
subprocess.run(['git','apply',str(new)],cwd=REPO,check=True)
env=dict(os.environ,PATH='/home/parity/.cargo/bin:'+os.environ['PATH'],CARGO_TARGET_DIR=str(ROOT/'deadsync/target'),
    CARGO_PROFILE_RELEASE_LTO='false',CARGO_PROFILE_RELEASE_CODEGEN_UNITS='16',CARGO_PROFILE_RELEASE_DEBUG='1',
    CARGO_PROFILE_RELEASE_STRIP='none',RUSTFLAGS='-C force-frame-pointers=yes')
OUT=ROOT/'pass3-r1b-results';OUT.mkdir(exist_ok=True)
with (OUT/'build-artifacts.jsonl').open('w') as f:
    subprocess.run(['cargo','rustc','--locked','--release','--test','full_song_lua','-j','2','--message-format=json-render-diagnostics'],cwd=REPO,env=env,stdout=f,check=True)
rows=[json.loads(line) for line in (OUT/'build-artifacts.jsonl').read_text().splitlines() if line.startswith('{')]
binary=next(r['executable'] for r in rows if r.get('target',{}).get('name')=='full_song_lua' and r.get('executable'))
runner=ROOT/'bin/full_song_lua-pass3-r1b';shutil.copy2(binary,runner)
sys.path.insert(0,str(ROOT));import worker_pass2 as w
w.RESULTS=OUT
proof={'previous':json.loads((ROOT/'pass3-r1-proof.json').read_text()),'deadsync_patch_sha256':w.sha(new),'runner_sha256':w.sha(runner)}
w.write(OUT/'build-proof.json',proof)
for ident in ['join-inactive-r1','3effbc28e93b70bc','7c462fc586e600b3']:
    original=ROOT/'pass3-r1-results'/ident/'result.json'
    source=json.loads(original.read_text())
    candidates=[a for a in source['artifacts'] if '/candidate/' in a['file'] or '/accepted/' in a['file']]
    if not candidates:
        w.write(OUT/(ident+'-native-failure.json'),source);continue
    artifact=candidates[0];archive=ROOT/'pass3-r1-results'/artifact['file'];assert w.sha(archive)==artifact['sha256']
    case=OUT/ident;case.mkdir(exist_ok=True);candidate=case/(artifact['uncompressed_sha256']+'.tar')
    with archive.open('rb') as src,candidate.open('wb') as dst:zstandard.ZstdDecompressor().copy_stream(src,dst)
    assert w.sha(candidate)==artifact['uncompressed_sha256']
    result={'id':ident,'source_simfile':source['source_simfile'],'source_snapshot':proof,'native_capture':str(original),'started_at':w.now()}
    result['replay']=w.execute(case,'r1b-replay',[runner,'--archive',candidate,'--report',case/'report.json'],900,memory='6G')
    if (case/'report.json').exists():
        result['comparison']=w.document_summary(case/'report.json',report=True)
        result['status']='pass' if result['replay']['exit']==0 and result['comparison']['archive_accepted'] else 'parity_failure'
        if result['status']=='pass':
            result['pack']=w.execute(case,'r1b-pack',[ROOT/'bin/itgmania-harness-pass3-r1','song-lua-pack',candidate,'--report',case/'report.json','--out',case/'accepted'],900,memory='6G')
            assert result['pack']['exit']==0
        result['report']=w.compress(case/'report.json',remove=True)
    else:result['status']='replay_error'
    result['finished_at']=w.now();w.write(case/'result.json',result)
    print(json.dumps({'id':ident,'status':result['status'],'mismatches':result.get('comparison',{}).get('mismatch_count')}),flush=True)
    assert candidate.resolve().is_relative_to(OUT.resolve());candidate.unlink()
