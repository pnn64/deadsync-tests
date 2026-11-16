local function emit(phase, player)
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
