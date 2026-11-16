return Def.ActorFrame {
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
}