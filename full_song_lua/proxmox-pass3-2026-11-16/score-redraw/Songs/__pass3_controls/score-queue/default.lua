return Def.ActorFrame {
 OnCommand=function(self)
  self:sleep(30)
  local score=SCREENMAN:GetTopScreen():GetChild('Underlay'):GetChild('P1Score')
  assert(score and score:GetName()=='P1Score')
  for i=1,75 do score:playcommand('JudgmentMessage') end
  MESSAGEMAN:Broadcast('ScoreQueueBurst',{calls=75})
 end
}
