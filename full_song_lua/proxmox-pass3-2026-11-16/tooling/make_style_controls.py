"""Build source-owned controls for every dance/pump style supported by gameplay."""
import hashlib,json,pathlib,wave
OUT=pathlib.Path(__file__).resolve().parent/'style-controls'
OUT.mkdir(exist_ok=True)
jobs=[]
for game,width in [('dance',4),('pump',5)]:
    folder=OUT/game;folder.mkdir(exist_ok=True)
    source='#VERSION:0.83;#TITLE:Native style selection control;#MUSIC:silence.wav;#BPMS:0=120;#FGCHANGES:0=default.lua=1=0=0=1;\n'
    def rows(lanes,columns):
        return '\n'.join(''.join('1' if column==c else '0' for c in range(lanes)) for column in columns)
    for style,lanes in [('single',width),('double',2*width),('couple',2*width),('routine',2*width)]:
        notes=rows(lanes,[None,0,None,lanes-1])+',\n'+rows(lanes,[None,1,None,lanes-2])
        if style=='routine':
            notes=rows(lanes,[None,0,None,None])+',\n'+rows(lanes,[None,1,None,None])+'\n&\n'+rows(lanes,[None,None,None,lanes-1])+',\n'+rows(lanes,[None,None,None,lanes-2])
        source+=f'#NOTEDATA:;#STEPSTYPE:{game}-{style};#DESCRIPTION:{style};#CHARTNAME:{style};#DIFFICULTY:Edit;#METER:1;#NOTES:\n{notes}\n;\n'
    (folder/'control.ssc').write_text(source,encoding='utf-8',newline='\n')
    with wave.open(str(folder/'silence.wav'),'wb') as audio:
        audio.setnchannels(1);audio.setsampwidth(1);audio.setframerate(8000);audio.writeframes(bytes([128])*8000*8)
    (folder/'default.lua').write_text('''return Def.ActorFrame {
 OnCommand=function(self)
  self:sleep(30)
  local screen=SCREENMAN:GetTopScreen()
  local function columns(name)
   local player=screen:GetChild(name)
   return player and #player:GetChild('NoteField'):GetColumnActors() or 0
  end
  MESSAGEMAN:Broadcast('StyleSelection', {
   game=GAMESTATE:GetCurrentGame():GetName(), style=GAMESTATE:GetCurrentStyle():GetName(),
   steps=GAMESTATE:GetCurrentSteps(PLAYER_1):GetStepsType(),
   players=#GAMESTATE:GetEnabledPlayers(), p1_columns=columns('PlayerP1'), p2_columns=columns('PlayerP2')})
 end,
 JudgmentMessageCommand=function(self,params)
  local stats=STATSMAN:GetCurStageStats():GetPlayerStageStats(params.Player)
  MESSAGEMAN:Broadcast('StyleJudgment', {player=params.Player,
   combo=stats:GetCurrentCombo(), actual=stats:GetActualDancePoints(), possible=stats:GetPossibleDancePoints()})
 end
}''',encoding='utf-8',newline='\n')
    digest=hashlib.sha256((folder/'control.ssc').read_bytes()).hexdigest()
    for style,index in [('single',1),('versus',1),('double',2),('couple',3),('routine',4)]:
        jobs.append({'id':f'style-{game}-{style}','source_simfile':f'__pass3_controls/styles/{game}/control.ssc',
            'title':f'{game} {style} gameplay control','game':game,'style':style,'difficulty':'Edit','chart_index':index,
            'simfile_sha256':digest,'gc_mode':'automatic','capture_fps':60,'max_events':250000,'capture_timeout':180,
            'replay_timeout':180,'player_options':'default' if game=='pump' else None,'stage_memory':'6G','run_role':'native-style-control'})
(OUT/'jobs.json').write_text(json.dumps(jobs,indent=2)+'\n')
print(f'Prepared {len(jobs)} native style controls without running them')
