"""Validate exact native chart selection, then capture and replay duplicate Edit controls."""
import json,os,pathlib,shutil,subprocess,sys
ROOT=pathlib.Path('/opt/song-lua-audit');INPUT=ROOT/'chart-selector-inputs';OUT=ROOT/'pass3-chart-selector-results'
assert not OUT.exists(), 'Never overwrite or repeat an existing run'
state=subprocess.run(['systemctl','show','song-lua-pass3-pause-fix-resume','-p','ActiveState'],capture_output=True,text=True).stdout
assert 'ActiveState=active' not in state and 'ActiveState=activating' not in state,state
patches=[(ROOT/'harness-pass3',INPUT/'harness.patch'),(ROOT/'deadsync-pass3',INPUT/'deadsync.patch')]
for repo,patch in patches:subprocess.run(['git','apply','--check',str(patch)],cwd=repo,check=True)
OUT.mkdir()
for repo,patch in patches:subprocess.run(['git','apply',str(patch)],cwd=repo,check=True)
env=dict(os.environ,PATH='/home/parity/.cargo/bin:'+os.environ['PATH'],CARGO_TARGET_DIR=str(ROOT/'harness/target'),
    ITGMANIA_HARNESS_TRACE_BIN=str(ROOT/'harness/vendor/itgmania/ITGmania-harness-trace'))
def checked(args,repo,name):
    with (OUT/name).open('w') as log:
        subprocess.run(args,cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
for selection in ['trace_selects_an_exact_native_chart','generated_config_has_stable_runtime_contract']:
    checked(['cargo','test','--locked','--release','-j','2','--bin','itgmania-harness-rs',selection],ROOT/'harness-pass3',selection+'.log')
checked(['cargo','test','--locked','--release','-j','2','--bin','itgmania-harness-rs',
    'native_chart_index_selects_duplicate_difficulties_and_rejects_mismatches','--','--ignored','--nocapture'],ROOT/'harness-pass3','native-selector.log')
checked(['cargo','build','--locked','--release','-j','2'],ROOT/'harness-pass3','harness-build.log')
harness=ROOT/'bin/itgmania-harness-pass3-chart-selector'
shutil.copy2(ROOT/'harness/target/release/itgmania-harness-rs',harness)
env.update(CARGO_TARGET_DIR=str(ROOT/'deadsync/target'),CARGO_PROFILE_RELEASE_LTO='false',
    CARGO_PROFILE_RELEASE_CODEGEN_UNITS='16',CARGO_PROFILE_RELEASE_DEBUG='1',CARGO_PROFILE_RELEASE_STRIP='none',RUSTFLAGS='-C force-frame-pointers=yes')
for selection in ['native_starting_chart_checks_identity_and_maps_catalog_to_payload',
    'native_double_session_selects_double_steps_and_runs_eight_column_scene','native_reload_starts_with_the_requested_style']:
    checked(['cargo','test','--locked','--release','-j','2','--test','song_lua_itgmania_semantic_parity',selection,'--','--nocapture'],ROOT/'deadsync-pass3',selection+'.log')
with (OUT/'build-artifacts.jsonl').open('w') as log:
    subprocess.run(['cargo','rustc','--locked','--release','--test','full_song_lua','-j','2','--message-format=json-render-diagnostics'],
        cwd=ROOT/'deadsync-pass3',env=env,stdout=log,check=True)
rows=[json.loads(line) for line in (OUT/'build-artifacts.jsonl').read_text().splitlines() if line.startswith('{')]
binary=next(r['executable'] for r in rows if r.get('target',{}).get('name')=='full_song_lua' and r.get('executable'))
runner=ROOT/'bin/full_song_lua-pass3-chart-selector';shutil.copy2(binary,runner)
sys.path.insert(0,str(ROOT));import worker_pass2 as w
proof={'baseline':json.loads((ROOT/'pass3-pause-fix-results/build-proof.json').read_text()),
    'selection_source':json.loads((INPUT/'source.json').read_text()),
    'patches':{p.name:w.sha(p) for _,p in patches},
    'harness_sha256':w.sha(harness),'runner_sha256':w.sha(runner)}
w.write(OUT/'build-proof.json',proof);w.write(ROOT/'pass2-source-snapshot.json',proof)
w.RESULTS=OUT;w.HARNESS=harness;w.RUNNER=runner
folder=ROOT/'Songs/__pass3_controls/chart-selector';folder.mkdir(parents=True,exist_ok=False)
for name in ['control.sm','control.ssc','default.lua','silence.wav']:shutil.copy2(INPUT/name,folder/name)
execute=w.execute
def selected_execute(case,stage,command,timeout,*args,**kwargs):
    if stage=='capture':command=[*command,'--game','dance','--chart-index','2']
    return execute(case,stage,command,timeout,*args,**kwargs)
w.execute=selected_execute
for extension in ['sm','ssc']:
    simfile=folder/f'control.{extension}'
    job={'id':'chart-selector-'+extension,'source_simfile':str(simfile.relative_to(ROOT/'Songs')),
        'title':'Second Edit chart selector control','style':'single','difficulty':'Edit','game':'dance','chart_index':2,
        'gc_mode':'automatic','capture_fps':60,'max_events':250000,'capture_timeout':180,'replay_timeout':180,
        'simfile_sha256':w.sha(simfile),'stage_memory':'6G','run_role':'exact-native-chart-control'}
    r=w.run_case(job,'1401')
    print(json.dumps({'id':r['id'],'status':r['status'],'mismatches':r.get('comparison',{}).get('mismatch_count')}),flush=True)
