local layout = ...
local target
local controller = Def.Quad{
    Name = "Controller",
    InitCommand = function(self) self:queuecommand("Update") end,
    OnCommand = function(self) self:visible(false) end,
    UpdateCommand = function(self)
        if GAMESTATE:GetSongBeat() >= 0.2 then
            target:x(GAMESTATE:GetSongBeat() * 100)
        end
        self:sleep(0.02):queuecommand("Update")
    end,
}
local visual = Def.Quad{
    Name = "Target",
    InitCommand = function(self) target = self; self:zoomto(20, 20) end,
}

if layout == "helper" then
    return Def.ActorFrame{
        Def.Actor{}, LoadActor("baked-child-helper.lua"), controller, visual,
    }
elseif layout == "sparse" then
    return Def.ActorFrame{
        [2] = Def.ActorFrame{[1000] = controller},
        [1000000] = visual,
    }
elseif layout == "children" then
    return Def.ActorFrame{children = {
        controller,
        Def.Actor{Condition = false, InitCommand = function() error("excluded child") end},
        visual,
    }}
end
return Def.ActorFrame{controller, visual}
