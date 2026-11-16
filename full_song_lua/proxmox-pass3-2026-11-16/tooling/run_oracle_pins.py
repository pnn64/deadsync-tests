import datetime,hashlib,json,os,pathlib,shutil,subprocess
ROOT=pathlib.Path('/opt/song-lua-audit');OUT=ROOT/'pass3-oracle-pins';assert not OUT.exists();OUT.mkdir()
harness=ROOT/'routine-harness';native=ROOT/'routine-native';theme=ROOT/'routine-theme'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
proof=json.loads((ROOT/'pass3-input-observer-fix/build-proof.json').read_text())
assert sha(native/'ITGmania-harness-trace')==proof['native_binary_sha256']
bundle=json.loads((ROOT/'oracle-pins-text.json').read_text())
for name,entry in bundle['files'].items():
 p=harness/name;assert sha(p)==entry['before_sha256'],name
for name,entry in bundle['files'].items():(harness/name).write_text(entry['text'])
link=harness/'vendor/simply-love';assert link.is_symlink() and link.resolve()==(ROOT/'harness/vendor/simply-love').resolve()
link.unlink();link.symlink_to(theme,target_is_directory=True)
for name,digest in bundle['production_sources'].items():assert sha(harness/name)==digest,name
proof.update(pin_text_bundle_sha256=sha(ROOT/'oracle-pins-text.json'),harness_version='0.1.102',
 started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_normalized_sha256=bundle['production_sources'])
(OUT/'source-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
env=dict(os.environ,PATH='/home/parity/.cargo/bin:'+os.environ['PATH'],CARGO_TARGET_DIR=str(ROOT/'harness/target'),
 CARGO_PROFILE_RELEASE_LTO='false',CARGO_PROFILE_RELEASE_CODEGEN_UNITS='16',ITGMANIA_HARNESS_TRACE_BIN=str(native/'ITGmania-harness-trace'))
test=['cargo','test','--locked','--release','-j','8','--bin','itgmania-harness-rs']
for name,args in [('unit-tests',test),('native-input-test',test+['native_inputs_are_observed_once_with_or_without_lua_callbacks','--','--ignored','--nocapture']),
 ('native-selector-test',test+['native_chart_index_selects_duplicate_difficulties_and_rejects_mismatches','--','--ignored','--nocapture']),
 ('harness-build',['cargo','build','--locked','--release','-j','8'])]:
 with (OUT/(name+'.log')).open('w') as log:subprocess.run(args,cwd=harness,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
runner=ROOT/'bin/itgmania-harness-pass3-oracle-pins';shutil.copy2(ROOT/'harness/target/release/itgmania-harness-rs',runner)
proof.update(finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),harness_binary_sha256=sha(runner))
(OUT/'build-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof),flush=True)
subprocess.run(['/usr/bin/python3',str(ROOT/'run_native_routine_manual_pinned.py')],check=True)
