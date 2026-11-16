"""Validate pump game/style metadata against the same retained native inputs."""
import json,os,pathlib,shutil,subprocess,sys
import zstandard
ROOT=pathlib.Path('/opt/song-lua-audit');REPO=ROOT/'deadsync-pass3';OUT=ROOT/'pass3-pump-game-results'
assert OUT.exists() and (OUT/'expectation-restoration.json').exists() and not (OUT/'build-proof.json').exists()
patch=ROOT/'deadsync-pump-game.patch'
subprocess.run(['git','apply','--reverse','--check',str(patch)],cwd=REPO,check=True)
env=dict(os.environ,PATH='/home/parity/.cargo/bin:'+os.environ['PATH'],CARGO_TARGET_DIR=str(ROOT/'deadsync/target'),
    CARGO_PROFILE_RELEASE_LTO='false',CARGO_PROFILE_RELEASE_CODEGEN_UNITS='16',CARGO_PROFILE_RELEASE_DEBUG='1',
    CARGO_PROFILE_RELEASE_STRIP='none',RUSTFLAGS='-C force-frame-pointers=yes')
with (OUT/'unit-tests.log').open('w') as log:
    subprocess.run(['cargo','test','--locked','--release','-j','2','-p','deadsync-song-lua','--features','test-support','--test','game_state','--','--nocapture'],cwd=REPO,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
with (OUT/'build-artifacts.jsonl').open('w') as log:
    subprocess.run(['cargo','rustc','--locked','--release','--test','full_song_lua','-j','2','--message-format=json-render-diagnostics'],
        cwd=REPO,env=env,stdout=log,check=True)
rows=[json.loads(line) for line in (OUT/'build-artifacts.jsonl').read_text().splitlines() if line.startswith('{')]
binary=next(r['executable'] for r in rows if r.get('target',{}).get('name')=='full_song_lua' and r.get('executable'))
runner=ROOT/'bin/full_song_lua-pass3-pump-game';shutil.copy2(binary,runner)
sys.path.insert(0,str(ROOT));import worker_pass2 as w
w.RESULTS=OUT
proof={'baseline':json.loads((ROOT/'pass3-pump-style-results/build-proof.json').read_text()),
    'source':json.loads((ROOT/'pump-game-validation.json').read_text()),'patch_sha256':w.sha(patch),'runner_sha256':w.sha(runner)}
w.write(OUT/'build-proof.json',proof)
for style in ['single','versus','double']:
    ident='style-pump-'+style;source=ROOT/'pass3-chart-selector-results'/ident
    original=json.loads((source/'result.json').read_text())
    assert original['status']=='replay_error' and original['native']['completion']['reason']=='gameplay-exit'
    case=OUT/(ident+'-game');case.mkdir()
    packed=next((source/'candidate').glob('*.tar.zst'))
    record=next(a for a in original['artifacts'] if pathlib.Path(a['file']).name==packed.name)
    assert w.sha(packed)==record['sha256']
    candidate=case/(original['candidate_sha256']+'.tar')
    with packed.open('rb') as src,candidate.open('wb') as dst:zstandard.ZstdDecompressor().copy_stream(src,dst)
    assert w.sha(candidate)==original['candidate_sha256']
    result={'id':case.name,'source_simfile':original['source_simfile'],'profile':original['profile'],
        'source_snapshot':proof,'native':original['native'],'native_capture':str(source/'result.json'),
        'capture_reused':True,'status':'running','started_at':w.now(),'stages':{},'candidate_sha256':original['candidate_sha256']}
    w.write(case/'result.json',result)
    result['stages']['replay']=w.execute(case,'replay',[runner,'--archive',candidate,'--report',case/'report.json'],180,memory='6G')
    if (case/'report.json').exists():
        result['comparison']=w.document_summary(case/'report.json',report=True)
        result['status']='pass' if result['stages']['replay']['exit']==0 and result['comparison']['archive_accepted'] else 'parity_failure'
        if result['status']=='pass':
            result['stages']['pack']=w.execute(case,'pack',[ROOT/'bin/itgmania-harness-pass3-chart-selector','song-lua-pack',candidate,
                '--report',case/'report.json','--out',case/'accepted'],180,memory='6G')
            if result['stages']['pack']['exit']!=0:result['status']='packaging_error'
        result['report']=w.compress(case/'report.json',remove=True)
    else:
        result['status']='replay_error';result['reason']=(case/'replay.log').read_text(errors='replace')[-8000:]
    result['finished_at']=w.now();w.write(case/'result.json',result)
    print(json.dumps({'id':result['id'],'status':result['status'],'mismatches':result.get('comparison',{}).get('mismatch_count')}),flush=True)
    assert candidate.resolve().is_relative_to(OUT.resolve());candidate.unlink()
