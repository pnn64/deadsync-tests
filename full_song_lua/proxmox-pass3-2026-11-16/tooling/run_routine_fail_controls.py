import json,pathlib,shutil,sys
ROOT=pathlib.Path('/opt/song-lua-audit');OUT=ROOT/'pass3-native-routine-fail'
assert not OUT.exists();OUT.mkdir()
sys.path.insert(0,str(ROOT));import worker_pass2 as w
w.RESULTS=OUT
proof=json.loads((ROOT/'pass3-input-clocks/build-proof.json').read_text())
harness=ROOT/'bin/itgmania-harness-pass3-input-clocks';native=ROOT/'routine-native/ITGmania-harness-trace'
assert w.sha(harness)==proof['harness_binary_sha256'] and w.sha(native)==proof['native_binary_sha256']
w.write(OUT/'source-proof.json',proof)
lua='''local function emit(phase, player)
 local stage=STATSMAN:GetCurStageStats()
 local team=stage:GetRoutineStageStats()
 local p1=stage:GetPlayerStageStats(PLAYER_1)
 local p2=stage:GetPlayerStageStats(PLAYER_2)
 assert(team==stage:GetRoutineStageStats() and team~=p1 and team~=p2)
 local function values(stats)
  return {actual=stats:GetActualDancePoints(),possible=stats:GetPossibleDancePoints(),
   current_possible=stats:GetCurrentPossibleDancePoints(),failed=stats:GetFailed(),
   combo=stats:GetCurrentCombo(),maximum=stats:MaxCombo(),percent=stats:GetPercentDancePoints(),
   w1=stats:GetTapNoteScores('TapNoteScore_W1'),miss=stats:GetTapNoteScores('TapNoteScore_Miss')}
 end
 MESSAGEMAN:Broadcast('RoutineFailure',{phase=phase,player=player,team=values(team),p1=values(p1),p2=values(p2)})
end
return Def.ActorFrame {
 OnCommand=function(self)
  self:sleep(30);emit('start')
  local p1_failed=false;local team_failed=false
  self:SetUpdateFunction(function(self)
   local seconds=GAMESTATE:GetCurMusicSeconds()
   if seconds>0.25 and not p1_failed then
    STATSMAN:GetCurStageStats():GetPlayerStageStats(PLAYER_1):FailPlayer()
    p1_failed=true;emit('p1-failed')
   end
   if seconds>1.25 and not team_failed then
    STATSMAN:GetCurStageStats():GetRoutineStageStats():FailPlayer()
    team_failed=true;emit('team-failed')
   end
   if seconds>3.5 then emit('finished');self:SetUpdateFunction(nil) end
  end)
 end,
 JudgmentMessageCommand=function(self,params) emit('judgment',params.Player) end
}
'''
for game in ['dance','pump']:
 origin=ROOT/'Songs/__pass3_controls/routine-manual'/game
 dest=ROOT/'Songs/__pass3_controls/routine-fail'/game
 assert not dest.exists();dest.mkdir(parents=True)
 for name in ['silence.wav','inputs.json']:shutil.copy2(origin/name,dest/name)
 (dest/'control.ssc').write_text((origin/'control.ssc').read_text().replace('Routine statistics '+game,'Routine failure '+game))
 (dest/'default.lua').write_text(lua)
 job={'id':'routine-fail-'+game,'game':game,'style':'routine','difficulty':'Edit','chart_index':1,
  'source_simfile':str((dest/'control.ssc').relative_to(ROOT/'Songs')),'autoplay':False,'player_options':'default',
  'input_script':str((dest/'inputs.json').relative_to(ROOT/'Songs')),'title':'Routine failure '+game}
 case=OUT/job['id'];case.mkdir()
 result={'id':job['id'],'profile':job,'source_simfile':job['source_simfile'],'source_snapshot':proof,
  'control_sha256':{p.name:w.sha(p) for p in dest.iterdir()},'status':'running','started_at':w.now(),'stages':{}}
 w.write(case/'result.json',result)
 command=[harness,'song-lua-trace',dest/'control.ssc','--itgmania-bin',native,'--fallback-theme','Harness Simply Love',
  '--headless','--game',game,'--style','routine','--difficulty','Edit','--chart-index','1','--until-gameplay-end',
  '--capture-fps','60','--max-events','250000','--player-options','default','--autoplay','0','--input-script',dest/'inputs.json',
  '--timeout','180','--out',case/'native.json']
 result['stages']['capture']=w.execute(case,'capture',command,270,memory='3G')
 if result['stages']['capture']['exit']==0:
  result['native']=w.document_summary(case/'native.json');trace=json.loads((case/'native.json').read_text())
  result['samples']=[e['args'][1] for e in trace['events'] if e.get('operation')=='MessageManager.Broadcast' and e.get('args',[None])[0]=='RoutineFailure']
  assert trace['harness_version']=='0.1.103' and trace['completion']['reason']=='gameplay-exit'
  assert [s['phase'] for s in result['samples'] if s['phase']!='judgment']==['start','p1-failed','team-failed','finished'],result['samples']
  result['status']='native_capture_pass';result['trace_sha256']=w.sha(case/'native.json')
  result['native_artifact']=w.compress(case/'native.json',remove=False)
 else:result.update(status='native_capture_error',reason=(case/'capture.log').read_text(errors='replace')[-8000:])
 result['finished_at']=w.now();w.write(case/'result.json',result)
 print(json.dumps({'id':result['id'],'status':result['status'],'samples':result.get('samples'),'reason':result.get('reason')}),flush=True)
