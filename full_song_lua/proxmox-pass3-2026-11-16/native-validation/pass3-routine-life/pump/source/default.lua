local function emit(phase)
 local screen=SCREENMAN:GetTopScreen()
 local stage=STATSMAN:GetCurStageStats()
 local meter1=screen:GetLifeMeter(PLAYER_1)
 local meter2=screen:GetLifeMeter(PLAYER_2)
 MESSAGEMAN:Broadcast('RoutineLife', {phase=phase,
  p1=stage:GetPlayerStageStats(PLAYER_1):GetCurrentLife(),
  p2=stage:GetPlayerStageStats(PLAYER_2):GetCurrentLife(),
  meter1=meter1:GetLife(),meter2=meter2:GetLife(),same_meter=meter1==meter2})
end
return Def.ActorFrame {
 OnCommand=function(self)
  self:sleep(30)
  emit('start')
  local phase=0
  self:SetUpdateFunction(function(self)
   local seconds=GAMESTATE:GetCurMusicSeconds()
   if phase==0 and seconds>0.5 then
    SCREENMAN:GetTopScreen():GetChild('PlayerP1'):SetLife(0.8)
    emit('p1-write');phase=1
   elseif phase==1 and seconds>1.5 then
    SCREENMAN:GetTopScreen():GetChild('PlayerP2'):SetLife(0.2)
    emit('p2-write');phase=2
   elseif phase==2 and seconds>2.5 then
    emit('finished');self:SetUpdateFunction(nil)
   end
  end)
 end,
}
