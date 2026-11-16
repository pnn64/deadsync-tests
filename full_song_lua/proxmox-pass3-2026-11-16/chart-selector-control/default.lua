
return Def.ActorFrame { OnCommand=function(self)
    self:sleep(30)
    local selected = GAMESTATE:GetCurrentSteps(PLAYER_1)
    MESSAGEMAN:Broadcast('SelectedChart', {description=selected:GetDescription()})
end }
