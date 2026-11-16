"""Fresh pause control and Megalovania reference; no authored source edits."""
import json,pathlib,sys,time,wave,subprocess
ROOT=pathlib.Path('/opt/song-lua-audit');sys.path.insert(0,str(ROOT));import worker_pass2 as w
proof=json.loads((ROOT/'pass3-r2b-results/build-proof.json').read_text())
w.RUNNER=ROOT/'bin/full_song_lua-pass3-r2b';w.HARNESS=ROOT/'bin/itgmania-harness-pass3-r1'
w.RESULTS=ROOT/'pass3-pause-results';w.RESULTS.mkdir(exist_ok=True)
w.write(ROOT/'pass2-source-snapshot.json',{'combined_r2b_build':proof})
folder=ROOT/'Songs/__pass3_controls/pause-v2';folder.mkdir(parents=True,exist_ok=True)
sim=folder/'control.sm'
sim.write_text('#TITLE:Pause runtime control;\n#MUSIC:silence.wav;\n#OFFSET:0;\n#BPMS:0=120;\n#FGCHANGES:0=default.lua=1=0=0=1;\n#NOTES:dance-single::Challenge:1:0,0,0,0,0:\n'+',\n'.join(['1000\n0100\n0010\n0001']*5)+'\n;\n')
with wave.open(str(folder/'silence.wav'),'wb') as f:
    f.setnchannels(1);f.setsampwidth(2);f.setframerate(8000);f.writeframes(b'\0\0'*8000*11)
(folder/'default.lua').write_text('''local screen, started, paused_at
local phase=0
return Def.ActorFrame {
 OnCommand=function(self)
  self:sleep(30)
  screen=SCREENMAN:GetTopScreen()
  screen:addcommand('Pause',function() MESSAGEMAN:Broadcast('PauseObserved') end)
  screen:addcommand('Unpause',function() MESSAGEMAN:Broadcast('UnpauseObserved') end)
  self:SetUpdateFunction(function(self,dt)
   local music=GAMESTATE:GetCurMusicSeconds()
   local uptime=GetTimeSinceStart()
   if phase==0 and music>1 then
    phase=1;paused_at=uptime
    self:x(select('#',screen:PauseGame(true)))
    screen:PauseGame(true)
   elseif phase==1 and uptime-paused_at>0.75 then
    phase=2
    self:x(select('#',screen:PauseGame(false)))
    screen:PauseGame(false)
   elseif phase==2 and music>3 then
    phase=3;paused_at=uptime
    screen:PauseGame(true)
   elseif phase==3 and uptime-paused_at>0.5 then
    phase=4
    screen:PauseGame(false)
   end
   self:y(screen:IsPaused() and 1 or 0)
   self:z(STATSMAN:GetCurStageStats():GetGameplaySeconds())
   self:rotationx(screen:GetChild('PlayerP1'):GetTweenTimeLeft())
  end)
 end,
 Def.Actor {
  PauseObservedMessageCommand=function(self) self:x(self:GetX()+1) end,
  UnpauseObservedMessageCommand=function(self) self:y(self:GetY()+1) end,
 }
}
''')
control=dict(id='pause-runtime-control-v2',source_simfile=sim.relative_to(ROOT/'Songs').as_posix(),title='Pause runtime control',style='single',difficulty='Challenge',gc_mode='automatic',capture_fps=60,max_events=300000,capture_timeout=120,replay_timeout=180,simfile_sha256=w.sha(sim),stage_memory='6G',run_role='pause-runtime-control')
mega=ROOT/'Songs/Megalovania SM5 - [TaroNuke]/megalovania.sm'
job=dict(id='c3e0c410f04c30dd-pause-baseline',primary_id='c3e0c410f04c30dd',source_simfile=mega.relative_to(ROOT/'Songs').as_posix(),title='Megalovania',style='single',difficulty='Challenge',gc_mode='automatic',capture_fps=60,max_events=2000000,capture_timeout=900,replay_timeout=1200,simfile_sha256=w.sha(mega),stage_memory='6G',run_role='fresh-pause-baseline')
for job in (control,):
    assert not (w.RESULTS/job['id']/'result.json').exists()
    r=w.run_case(job,'1402')
    print(json.dumps({'id':r['id'],'status':r['status'],'mismatches':r.get('comparison',{}).get('mismatch_count')}),flush=True)
