"""Prepare asymmetric routine charts to observe team statistics independently."""
import hashlib,json,pathlib,wave
OUT=pathlib.Path(__file__).resolve().parent/'routine-stats-controls';OUT.mkdir(exist_ok=True)
lua='''local function emit(phase, player)
 local stage=STATSMAN:GetCurStageStats()
 local team=stage:GetRoutineStageStats()
 local p1=stage:GetPlayerStageStats(PLAYER_1)
 local p2=stage:GetPlayerStageStats(PLAYER_2)
 assert(team==stage:GetRoutineStageStats() and team~=p1 and team~=p2)
 local function values(stats)
  return {actual=stats:GetActualDancePoints(), possible=stats:GetPossibleDancePoints(),
   combo=stats:GetCurrentCombo(), maximum=stats:MaxCombo(), percent=stats:GetPercentDancePoints(),
   w1=stats:GetTapNoteScores('TapNoteScore_W1'), miss=stats:GetTapNoteScores('TapNoteScore_Miss')}
 end
 MESSAGEMAN:Broadcast('RoutineStatistics', {phase=phase,player=player,
  team=values(team),p1=values(p1),p2=values(p2)})
end
return Def.ActorFrame {
 OnCommand=function(self) self:sleep(30);emit('start') end,
 JudgmentMessageCommand=function(self,params) emit('judgment',params.Player) end
}
'''
jobs=[]
for game,columns in [('dance',8),('pump',10)]:
 folder=OUT/game;folder.mkdir(exist_ok=True)
 # P1 has two notes, P2 has three, including a simultaneous row at beat 1.
 def part(notes):
  return ',\n'.join('\n'.join(''.join('1' if notes.get(beat)==column else '0' for column in range(columns)) for beat in range(measure*4,measure*4+4)) for measure in range(2))
 source=f'#VERSION:0.83;#TITLE:Routine statistics {game};#MUSIC:silence.wav;#BPMS:0=120;#FGCHANGES:0=default.lua=1=0=0=1;\n#NOTEDATA:;#STEPSTYPE:{game}-routine;#DESCRIPTION:Asymmetric owners;#DIFFICULTY:Edit;#METER:1;#NOTES:\n'+part({1:0,4:1})+'\n&\n'+part({1:columns-1,3:columns-2,6:columns-1})+'\n;\n'
 (folder/'control.ssc').write_text(source,encoding='utf8',newline='\n');(folder/'default.lua').write_text(lua,encoding='utf8',newline='\n')
 with wave.open(str(folder/'silence.wav'),'wb') as audio:
  audio.setnchannels(1);audio.setsampwidth(1);audio.setframerate(8000);audio.writeframes(bytes([128])*8000*8)
 jobs.append({'id':f'routine-stats-{game}','source_simfile':f'__pass3_controls/routine-stats/{game}/control.ssc',
  'title':f'{game} routine team and player statistics','game':game,'style':'routine','difficulty':'Edit','chart_index':1,
  'simfile_sha256':hashlib.sha256((folder/'control.ssc').read_bytes()).hexdigest(),'gc_mode':'automatic','capture_fps':60,
  'max_events':250000,'capture_timeout':180,'replay_timeout':180,'stage_memory':'6G',
  'player_options':'default' if game=='pump' else None,'run_role':'native-routine-statistics-control'})
(OUT/'jobs.json').write_text(json.dumps(jobs,indent=2)+'\n')
print('Prepared two asymmetric native routine controls; not yet executed.')
