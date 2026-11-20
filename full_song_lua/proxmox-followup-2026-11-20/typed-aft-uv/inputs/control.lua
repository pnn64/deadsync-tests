-- Native control: ActorMultiVertex keeps render-target UVs in backing space.
-- ActorFrameTexture allocates this 854x480 image in a 1024x512 texture.
local vertices = {
    {{0, 0, 0}, {1, 1, 1, 1}, {0, 0}},
    {{0, 64, 0}, {1, 1, 1, 1}, {0, 480 / 512}},
    {{128, 0, 0}, {1, 1, 1, 1}, {854 / 1024, 0}},
    {{128, 64, 0}, {1, 1, 1, 1}, {854 / 1024, 480 / 512}},
}

return Def.ActorFrame {
    Name = "TypedAftUvControl",
    OnCommand = function(self)
        -- Foreground::Update derives visibility duration from this tween time.
        self:sleep(6)
        local target = self:GetChild("Target")
        local mesh = self:GetChild("Mesh")
        target:SetSize(854, 480):SetTextureName("TypedAftUvTarget")
            :EnableAlphaBuffer(true):Create()
        local texture = target:GetTexture()
        assert(texture ~= nil, "native render target was created")
        assert(texture:GetImageWidth() == 854 and texture:GetImageHeight() == 480)
        assert(texture:GetTextureWidth() == 1024 and texture:GetTextureHeight() == 512)
        mesh:SetTexture(texture):SetVertices(vertices)
            :SetDrawState{Mode="DrawMode_QuadStrip", First=1, Num=-1}
        self:SetDrawFunction(function()
            target:Draw()
            mesh:Draw()
        end)
    end,
    Def.ActorFrameTexture {
        Name = "Target",
        Def.Quad {
            Name = "TargetFill",
            InitCommand = function(self)
                self:xy(427, 240):zoomto(854, 480):diffuse(0.25, 0.5, 0.75, 1)
            end,
        },
    },
    Def.ActorMultiVertex {
        Name = "Mesh",
        InitCommand = function(self) self:xy(100, 100) end,
    },
}
