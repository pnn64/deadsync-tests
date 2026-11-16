"""Guest 1401: build the roster-input fix, test it, and freshly recapture Anxiety."""
import hashlib,json,os,pathlib,shutil,subprocess,sys,traceback,wave
ROOT=pathlib.Path('/opt/song-lua-audit');INPUT=ROOT/'pass3-r1-inputs'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(args,repo,env=None):subprocess.run(args,cwd=repo,env=env,check=True)
try:
    for directory,name in [('harness-pass3','harness-r1.patch'),('deadsync-pass3','deadsync-r1.patch')]:
        run(['git','apply','--check',str(INPUT/name)],ROOT/directory)
        run(['git','apply',str(INPUT/name)],ROOT/directory)
    env=dict(os.environ,PATH='/home/parity/.cargo/bin:'+os.environ['PATH'],CARGO_TARGET_DIR=str(ROOT/'harness/target'))
    run(['cargo','test','--locked','--release','--bin','itgmania-harness-rs','song_lua_runtime::tests::update_clocks_allow_reload_music_reset','-j','2'],ROOT/'harness-pass3',env)
    run(['cargo','build','--locked','--release','-j','2'],ROOT/'harness-pass3',env)
    shutil.copy2(ROOT/'harness/target/release/itgmania-harness-rs',ROOT/'bin/itgmania-harness-pass3-r1')
    env.update(CARGO_TARGET_DIR=str(ROOT/'deadsync/target'),CARGO_PROFILE_RELEASE_LTO='false',
               CARGO_PROFILE_RELEASE_CODEGEN_UNITS='16',CARGO_PROFILE_RELEASE_DEBUG='1',CARGO_PROFILE_RELEASE_STRIP='none',RUSTFLAGS='-C force-frame-pointers=yes')
    run(['cargo','test','--locked','--release','--test','song_lua_itgmania_semantic_parity','native_capture_rejects_incomplete_or_failed_traces','-j','2'],ROOT/'deadsync-pass3',env)
    with (ROOT/'logs/pass3-r1-artifacts.jsonl').open('w') as out:
        subprocess.run(['cargo','rustc','--locked','--release','--test','full_song_lua','-j','2','--message-format=json-render-diagnostics'],
            cwd=ROOT/'deadsync-pass3',env=env,stdout=out,check=True)
    artifacts=[json.loads(line) for line in (ROOT/'logs/pass3-r1-artifacts.jsonl').read_text().splitlines() if line.startswith('{')]
    executables=[row['executable'] for row in artifacts if row.get('reason')=='compiler-artifact' and row.get('target',{}).get('name')=='full_song_lua' and row.get('executable')]
    assert len(executables)==1
    shutil.copy2(executables[0],ROOT/'bin/full_song_lua-pass3-r1')
    proof={'baseline':json.loads((ROOT/'pass3-build-proof.json').read_text()),
           'patches':{name:sha(INPUT/name) for name in ['harness-r1.patch','deadsync-r1.patch']},
           'binaries':{name:sha(ROOT/'bin'/name) for name in ['itgmania-harness-pass3-r1','full_song_lua-pass3-r1']}}
    (ROOT/'pass3-r1-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    # The old reusable worker's provenance field reads this filename. Replace
    # it only in this fresh worker with the actual revision-plus-patch receipt.
    (ROOT/'pass2-source-snapshot.json').write_text(json.dumps(proof,indent=2)+'\n')
    sys.path.insert(0,str(ROOT));import worker_pass2 as w
    w.RESULTS=ROOT/'pass3-r1-results';w.RESULTS.mkdir(exist_ok=True)
    w.HARNESS=ROOT/'bin/itgmania-harness-pass3-r1';w.RUNNER=ROOT/'bin/full_song_lua-pass3-r1'
    folder=ROOT/'Songs/__pass3_controls/join-inactive';folder.mkdir(parents=True,exist_ok=True)
    sim=folder/'control.sm'
    sim.write_text('#TITLE:Inactive player input control;\n#MUSIC:silence.wav;\n#OFFSET:0.825;\n#BPMS:0=120;\n#FGCHANGES:0=default.lua=1=0=0=1;\n#NOTES:dance-single::Challenge:1:0,0,0,0,0:\n1000\n0000\n0000\n1000\n;\n')
    with wave.open(str(folder/'silence.wav'),'wb') as file:
        file.setnchannels(1);file.setsampwidth(2);file.setframerate(8000);file.writeframes(b'\0\0'*8000*3)
    (folder/'default.lua').write_text('''return Def.Actor { OnCommand=function(self)
 assert(GAMESTATE:GetPlayerState(PLAYER_2):GetPlayerOptions('ModsLevel_Preferred'):PlayerAutoPlay()==1)
 if not GAMESTATE:IsSideJoined(PLAYER_2) then
  GAMESTATE:JoinPlayer(PLAYER_2)
  SCREENMAN:SetNewScreen('ScreenGameplay')
  return
 end
 assert(#GAMESTATE:GetEnabledPlayers()==2)
 local screen=SCREENMAN:GetTopScreen()
 local p1,p2=screen:GetChild('PlayerP1'),screen:GetChild('PlayerP2')
 assert(p1 and p2)
 self:x(p1:GetX()):y(p2:GetX())
 assert(GAMESTATE:GetCurrentSteps(PLAYER_1)==GAMESTATE:GetCurrentSteps(PLAYER_2))
end }''')
    control=dict(id='join-inactive-r1',source_simfile=str(sim.relative_to(ROOT/'Songs')),title='Inactive player input control',
        style='single',difficulty='Challenge',gc_mode='automatic',capture_fps=60,max_events=100000,capture_timeout=120,replay_timeout=120,
        simfile_sha256=sha(sim),stage_memory='6G',run_role='inactive-player-profile-control')
    jobs=[control]+json.loads((INPUT/'anxiety-jobs.json').read_text())
    for job in jobs:
        print('Starting fresh r1 case',job['id'],flush=True)
        result=w.run_case(job,'1401')
        print(json.dumps({'id':job['id'],'status':result['status'],'mismatches':result.get('comparison',{}).get('mismatch_count')}),flush=True)
    (ROOT/'logs/pass3-r1.exit').write_text('0\n')
except BaseException:
    (ROOT/'logs/pass3-r1.exit').write_text('1\n');traceback.print_exc();raise
