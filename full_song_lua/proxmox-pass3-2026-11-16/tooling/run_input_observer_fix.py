import datetime,hashlib,json,os,pathlib,shutil,subprocess
ROOT=pathlib.Path('/opt/song-lua-audit');OUT=ROOT/'pass3-input-observer-fix';assert not OUT.exists();OUT.mkdir()
native=ROOT/'routine-native';harness=ROOT/'routine-harness';patch=ROOT/'harness-input-observer.patch'
def sha(path):
 with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
proof=json.loads((ROOT/'pass3-native-routine-controls/source-proof.json').read_text())
assert sha(native/'ITGmania-harness-trace')==proof['native_binary_sha256']
status=subprocess.check_output(['git','status','--porcelain'],cwd=harness,text=True)
assert status==' T vendor/itgmania\n T vendor/simply-love\n',status
assert (harness/'vendor/itgmania').resolve()==native.resolve()
assert (harness/'vendor/simply-love').resolve()==(ROOT/'harness/vendor/simply-love').resolve()
shutil.copy2(native/'ITGmania-harness-trace',OUT/'ITGmania-before-input-fix')
shutil.copy2(patch,OUT/patch.name)
subprocess.run(['git','apply','--check',str(patch)],cwd=harness,check=True)
subprocess.run(['git','apply',str(patch)],cwd=harness,check=True)
proof.update(harness_patch_sha256=sha(patch),previous_native_binary_sha256=proof['native_binary_sha256'],
 started_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
(OUT/'source-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
env=dict(os.environ,PATH='/home/parity/.cargo/bin:'+os.environ['PATH'],CARGO_TARGET_DIR=str(ROOT/'harness/target'),
 CARGO_PROFILE_RELEASE_LTO='false',CARGO_PROFILE_RELEASE_CODEGEN_UNITS='16',ITGMANIA_HARNESS_TRACE_BIN=str(native/'ITGmania-harness-trace'))
test=['cargo','test','--locked','--release','-j','8','--bin','itgmania-harness-rs']
specific=test+['native_inputs_are_observed_once_with_or_without_lua_callbacks','--','--ignored','--nocapture']
with (OUT/'baseline-test.log').open('w') as log:
 baseline=subprocess.run(specific,cwd=harness,env=env,stdout=log,stderr=subprocess.STDOUT)
assert baseline.returncode!=0 and 'scripted input did not reach native screen input dispatch' in (OUT/'baseline-test.log').read_text()
proof['baseline_test_reproduced']=True
checks=[('configure',['cmake','-S',native,'-B',ROOT/'routine-native-build','-DCMAKE_BUILD_TYPE=Release','-DWITH_LTO=OFF',
 '-DCMAKE_PROJECT_INCLUDE='+str(harness/'native/trace_adapter.cmake')],ROOT),
 ('native-build',['cmake','--build',ROOT/'routine-native-build','--target','ITGmania','--parallel','8'],ROOT),
 ('unit-tests',test,harness),('native-input-test',specific,harness),
 ('harness-build',['cargo','build','--locked','--release','-j','8'],harness)]
for name,args,cwd in checks:
 with (OUT/(name+'.log')).open('w') as log:subprocess.run(list(map(str,args)),cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
runner=ROOT/'bin/itgmania-harness-pass3-input-fix';shutil.copy2(ROOT/'harness/target/release/itgmania-harness-rs',runner)
proof.update(finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),native_binary_sha256=sha(native/'ITGmania-harness-trace'),harness_binary_sha256=sha(runner))
(OUT/'build-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof),flush=True)
