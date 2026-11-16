import datetime,hashlib,json,os,pathlib,subprocess
ROOT=pathlib.Path('/opt/song-lua-audit');REPO=ROOT/'input-deadsync';OUT=ROOT/'pass3-routine-life-fix'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
changes=json.loads((ROOT/'routine-life-text.json').read_text())
before=json.loads((ROOT/'routine-life-baseline-text.json').read_text())
proof=json.loads((OUT/'build-proof.json').read_text())
assert not (OUT/'glow-baseline-validation.json').exists()
for n,e in changes.items():assert sha(REPO/n)==e['after_sha256'],n
env=dict(os.environ,PATH='/home/parity/.cargo/bin:'+os.environ['PATH'],CARGO_TARGET_DIR=str(ROOT/'deadsync/target'),CARGO_PROFILE_RELEASE_LTO='false',CARGO_PROFILE_RELEASE_CODEGEN_UNITS='16',CARGO_PROFILE_RELEASE_DEBUG='1',CARGO_PROFILE_RELEASE_STRIP='none',RUSTFLAGS='-C force-frame-pointers=yes')
command=['cargo','test','--locked','--release','-j','6','--test','song_lua_itgmania_semantic_parity','short_glow_matches_native','--','--exact','--nocapture']
result={'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidate_runner_sha256':proof['runner_sha256'],
 'baseline_commit':'ea8f44d9b88e8094afadebe4ab2a6c22af34882c','preserved_user_patch_sha256':'f362069247b6129a8a3a035c439fcbf77fd89c878feae29ee22c02d5475166c0',
 'baseline_source_sha256':{n:e['before_sha256'] for n,e in changes.items()},'candidate_source_sha256':{n:e['after_sha256'] for n,e in changes.items()},'command':command}
def run(label):
 with (OUT/(label+'.log')).open('w') as log:
  code=subprocess.run(command,cwd=REPO,env=env,stdout=log,stderr=subprocess.STDOUT).returncode
 text=(OUT/(label+'.log')).read_text()
 result[label]={'exit':code,'mismatches':[line for line in text.splitlines() if line.startswith('Monitor at ')]}
 print(label,code,flush=True)
run('glow-candidate')
try:
 for n,e in changes.items():
  (REPO/n).write_text(before[n]);assert sha(REPO/n)==e['before_sha256']
 run('glow-baseline')
finally:
 for n,e in changes.items():
  (REPO/n).write_text(e['text']);assert sha(REPO/n)==e['after_sha256']
result['identical_failures']=result['glow-candidate']==result['glow-baseline'] and len(result['glow-baseline']['mismatches'])==6
result['candidate_sources_restored']=True
result['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
(OUT/'glow-baseline-validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result),flush=True)
