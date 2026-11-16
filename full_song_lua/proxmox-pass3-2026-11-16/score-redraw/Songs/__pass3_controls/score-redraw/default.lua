local score, phase
local function burst()
 for i=1,75 do score:playcommand('Judgment') end
end
return Def.ActorFrame {
 OnCommand=function(self)
  self:sleep(30)
  score=SCREENMAN:GetTopScreen():GetChild('Underlay'):GetChild('P1Score')
  assert(score and score:GetName()=='P1Score')
  score:playcommand('Judgment')
  score:stoptweening()
  score:x(0):linear(2):x(100)
  burst()
  phase=0
  self:SetUpdateFunction(function()
   local seconds=GAMESTATE:GetCurMusicSeconds()
   if phase==0 and seconds>0.2 then
    assert(score:GetTweenTimeLeft()>0 and score:GetX()>0 and score:GetX()<100)
    MESSAGEMAN:Broadcast('ScoreTweenPreserved',{text=score:GetText()})
    phase=1
   elseif phase==1 and seconds>1.2 then
    assert(score:GetText()=='50.00',score:GetText())
    score:playcommand('Judgment')
    score:stoptweening()
    burst()
    MESSAGEMAN:Broadcast('ScoreRedrawFirst',{text=score:GetText()})
    phase=2
   elseif phase==2 and seconds>3.2 then
    assert(score:GetText()=='100.00',score:GetText())
    assert(STATSMAN:GetCurStageStats():GetPlayerStageStats(PLAYER_1):GetActualDancePoints()==10)
    MESSAGEMAN:Broadcast('ScoreRedrawFinal',{text=score:GetText(),phase=phase})
    phase=3
   end
  end)
 end
}
