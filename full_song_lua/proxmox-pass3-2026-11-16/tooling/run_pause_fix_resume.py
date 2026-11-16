"""Build complete pause integration and replay targeted native references."""
import json,os,pathlib,shutil,subprocess,sys
import zstandard
ROOT=pathlib.Path('/opt/song-lua-audit');REPO=ROOT/'deadsync-pass3';OUT=ROOT/'pass3-pause-fix-results'
assert OUT.exists() and not (OUT/'build-proof.json').exists()
patch=ROOT/'deadsync-pause-runtime.patch'
assert (OUT/'expectation-restoration.json').exists()
env=dict(os.environ,PATH='/home/parity/.cargo/bin:'+os.environ['PATH'],CARGO_TARGET_DIR=str(ROOT/'deadsync/target'),
    CARGO_PROFILE_RELEASE_LTO='false',CARGO_PROFILE_RELEASE_CODEGEN_UNITS='16',CARGO_PROFILE_RELEASE_DEBUG='1',
    CARGO_PROFILE_RELEASE_STRIP='none',RUSTFLAGS='-C force-frame-pointers=yes')
checks=[['-p','deadlib-audio-core','-p','deadsync-audio-stream'],
        ['-p','deadsync-gameplay','--lib'],
        ['-p','deadsync-song-lua','--features','test-support','--test','top_screen'],
        ['-p','deadsync-song-lua','--features','test-support','--test','unit_live','pause'],
        ['-p','deadsync-song-lua','--features','test-support','--test','live_gameplay']]
for i,args in enumerate(checks[2:],start=2):
    with (OUT/f'check-{i+1}.log').open('w') as log:
        subprocess.run(['cargo','test','--locked','--release','-j','2',*args],cwd=REPO,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
with (OUT/'build-artifacts.jsonl').open('w') as log:
    subprocess.run(['cargo','rustc','--locked','--release','--test','full_song_lua','-j','2','--message-format=json-render-diagnostics'],cwd=REPO,env=env,stdout=log,check=True)
rows=[json.loads(line) for line in (OUT/'build-artifacts.jsonl').read_text().splitlines() if line.startswith('{')]
binary=next(r['executable'] for r in rows if r.get('target',{}).get('name')=='full_song_lua' and r.get('executable'))
runner=ROOT/'bin/full_song_lua-pass3-pause';shutil.copy2(binary,runner)
sys.path.insert(0,str(ROOT));import worker_pass2 as w
w.RESULTS=OUT
proof={'baseline':json.loads((ROOT/'pass3-gc-results/build-proof.json').read_text()),'pause_patch_sha256':w.sha(patch),
    'runner_sha256':w.sha(runner),'checks':checks}
w.write(OUT/'build-proof.json',proof)
jobs=json.loads((ROOT/'pause-replay-inputs/jobs.json').read_text())
for job in jobs:
    case=OUT/job['id'];case.mkdir();archive=ROOT/job['archive']
    assert w.sha(archive)==job['compressed_sha256']
    candidate=case/(job['fixture_sha256']+'.tar')
    with archive.open('rb') as src,candidate.open('wb') as dst:zstandard.ZstdDecompressor().copy_stream(src,dst)
    assert w.sha(candidate)==job['fixture_sha256']
    r={'id':job['id'],'primary_id':job.get('primary_id',job['id']),'source_simfile':job['source_simfile'],
       'source_snapshot':proof,'native_capture':job['native_capture'],'capture_reused':True,'status':'running','started_at':w.now()}
    w.write(case/'result.json',r)
    r['replay']=w.execute(case,'pause-replay',[runner,'--archive',candidate,'--report',case/'report.json'],1200,memory='6G')
    if (case/'report.json').exists():
        r['comparison']=w.document_summary(case/'report.json',report=True)
        r['status']='pass' if r['replay']['exit']==0 and r['comparison']['archive_accepted'] else 'parity_failure'
        if r['status']=='pass':
            r['pack']=w.execute(case,'pause-pack',[ROOT/'bin/itgmania-harness-pass3-r1','song-lua-pack',candidate,'--report',case/'report.json','--out',case/'accepted'],600,memory='6G')
            if r['pack']['exit']!=0:r['status']='packaging_error'
        r['report']=w.compress(case/'report.json',remove=True)
    else:r['status']='replay_error'
    r['finished_at']=w.now();w.write(case/'result.json',r)
    print(json.dumps({'id':r['id'],'status':r['status'],'mismatches':r.get('comparison',{}).get('mismatch_count')}),flush=True)
    assert candidate.resolve().is_relative_to(OUT.resolve());candidate.unlink()
