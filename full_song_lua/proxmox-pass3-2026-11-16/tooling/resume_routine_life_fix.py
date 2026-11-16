import datetime,hashlib,json,os,pathlib,shutil,subprocess
ROOT=pathlib.Path('/opt/song-lua-audit');REPO=ROOT/'input-deadsync';OUT=ROOT/'pass3-routine-life-fix'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
proof=json.loads((OUT/'source-proof.json').read_text())
for name,expected in proof['source_normalized_sha256'].items():assert sha(REPO/name)==expected,name
assert not (OUT/'build-proof.json').exists()
game=(OUT/'gameplay-tests.log').read_text();semantic=(OUT/'semantic-tests.log').read_text()
assert '844 passed; 0 failed' in game
assert '302 passed; 9 failed; 94 ignored' in semantic
proof['validation']={'gameplay':{'passed':844,'failed':0},'semantic':{'passed':302,'failed':9,'ignored':94},
 'semantic_limitation':'Eight failures need unavailable committed archive fixtures (including poisoned fixture cache); short_glow_matches_native has six small numeric mismatches. Baseline comparison pending; original log retained.'}
env=dict(os.environ,PATH='/home/parity/.cargo/bin:'+os.environ['PATH'],CARGO_TARGET_DIR=str(ROOT/'deadsync/target'),CARGO_PROFILE_RELEASE_LTO='false',CARGO_PROFILE_RELEASE_CODEGEN_UNITS='16',CARGO_PROFILE_RELEASE_DEBUG='1',CARGO_PROFILE_RELEASE_STRIP='none',RUSTFLAGS='-C force-frame-pointers=yes')
with (OUT/'build-artifacts.jsonl').open('w') as log:
 subprocess.run(['cargo','rustc','--locked','--release','--test','full_song_lua','-j','6','--message-format=json-render-diagnostics'],cwd=REPO,env=env,stdout=log,check=True)
rows=[json.loads(line) for line in (OUT/'build-artifacts.jsonl').read_text().splitlines() if line.startswith('{')]
binary=next(r['executable'] for r in rows if r.get('target',{}).get('name')=='full_song_lua' and r.get('executable'))
runner=ROOT/'bin/full_song_lua-pass3-routine-life';shutil.copy2(binary,runner)
for name,expected in proof['source_normalized_sha256'].items():assert sha(REPO/name)==expected,name
proof.update(finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),runner_sha256=sha(runner))
(OUT/'build-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps({'runner_sha256':proof['runner_sha256']}),flush=True)
subprocess.run(['python3',str(ROOT/'run_routine_life_replays.py')],check=True)
