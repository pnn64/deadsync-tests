local function emit(phase, player)
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
