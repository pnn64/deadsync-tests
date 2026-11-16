"""Build the native dead-key fix and replay both fresh KENPO reference runs."""
import hashlib,json,os,pathlib,shutil,subprocess,sys
ROOT=pathlib.Path('/opt/song-lua-audit');REPO=ROOT/'deadsync-pass3'
for name in ['deadsync-roll-clock.patch','deadsync-gc-dead-keys.patch']:
    subprocess.run(['git','apply','--check',str(ROOT/name)],cwd=REPO,check=True)
    subprocess.run(['git','apply',str(ROOT/name)],cwd=REPO,check=True)
env=dict(os.environ,PATH='/home/parity/.cargo/bin:'+os.environ['PATH'],CARGO_TARGET_DIR=str(ROOT/'deadsync/target'),
    CARGO_PROFILE_RELEASE_LTO='false',CARGO_PROFILE_RELEASE_CODEGEN_UNITS='16',CARGO_PROFILE_RELEASE_DEBUG='1',
    CARGO_PROFILE_RELEASE_STRIP='none',RUSTFLAGS='-C force-frame-pointers=yes')
subprocess.run(['cargo','test','--locked','--release','-p','deadlib-lua','--test','lua51_table_order','-j','2'],cwd=REPO,env=env,check=True)
OUT=ROOT/'pass3-gc-results';OUT.mkdir(exist_ok=True)
with (OUT/'build-artifacts.jsonl').open('w') as f:
    subprocess.run(['cargo','rustc','--locked','--release','--test','full_song_lua','-j','2','--message-format=json-render-diagnostics'],cwd=REPO,env=env,stdout=f,check=True)
rows=[json.loads(line) for line in (OUT/'build-artifacts.jsonl').read_text().splitlines() if line.startswith('{')]
binary=next(r['executable'] for r in rows if r.get('target',{}).get('name')=='full_song_lua' and r.get('executable'))
runner=ROOT/'bin/full_song_lua-pass3-gc';shutil.copy2(binary,runner)
sys.path.insert(0,str(ROOT));import worker_pass2 as w
import zstandard
w.RESULTS=OUT
proof={'baseline':json.loads((ROOT/'pass3-build-proof.json').read_text()),'runner_sha256':w.sha(runner),
       'patches':{name:w.sha(ROOT/name) for name in ['deadsync-roll-clock.patch','deadsync-gc-dead-keys.patch','deadsync-r1b.patch']}}
w.write(OUT/'build-proof.json',proof)
for source in sorted((ROOT/'pass3-order-results').glob('*/result.json')):
    previous=json.loads(source.read_text());case=OUT/previous['id'];case.mkdir(exist_ok=True)
    assert not (case/'result.json').exists()
    artifact=next(a for a in previous['artifacts'] if '/candidate/' in a['file'])
    archive=ROOT/'pass3-order-results'/artifact['file'];assert w.sha(archive)==artifact['sha256']
    candidate=case/(artifact['uncompressed_sha256']+'.tar')
    with archive.open('rb') as src,candidate.open('wb') as dst:zstandard.ZstdDecompressor().copy_stream(src,dst)
    assert w.sha(candidate)==artifact['uncompressed_sha256']
    r={'id':previous['id'],'primary_id':'a170dd312f720cd4','source_simfile':previous['source_simfile'],
       'source_snapshot':proof,'native_capture':str(source),'status':'running','started_at':w.now()}
    w.write(case/'result.json',r)
    r['replay']=w.execute(case,'gc-replay',[runner,'--archive',candidate,'--report',case/'report.json'],1200,memory='6G')
    if (case/'report.json').exists():
        r['comparison']=w.document_summary(case/'report.json',report=True)
        r['status']='pass' if r['replay']['exit']==0 and r['comparison']['archive_accepted'] else 'parity_failure'
        if r['status']=='pass':
            r['pack']=w.execute(case,'gc-pack',[ROOT/'bin/itgmania-harness-pass3-r1','song-lua-pack',candidate,'--report',case/'report.json','--out',case/'accepted'],600,memory='6G')
            if r['pack']['exit']!=0:r['status']='packaging_error'
        r['report']=w.compress(case/'report.json',remove=True)
    else:r['status']='replay_error'
    r['finished_at']=w.now();w.write(case/'result.json',r)
    print(json.dumps({'id':r['id'],'status':r['status'],'mismatches':r.get('comparison',{}).get('mismatch_count')}),flush=True)
    assert candidate.resolve().is_relative_to(OUT.resolve());candidate.unlink()
