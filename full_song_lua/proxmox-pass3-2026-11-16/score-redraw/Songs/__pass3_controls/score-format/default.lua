local function pack(...) return {n=select('#',...),...} end
local cases={
 {'missing',pack()}, {'nil',pack(nil)}, {'boolean',pack(false)}, {'table',pack({})},
 {'zero',pack(0)}, {'negative-zero',pack(-0)}, {'positive',pack(1.25)}, {'negative',pack(-2.25)},
 {'third',pack(1/3)}, {'numeric-string',pack(' 1.25 ')}, {'nan-string',pack('nan')},
 {'inf-string',pack('inf')}, {'nan-number',pack(0/0)}, {'inf-number',pack(math.huge)},
 {'hex-string',pack('0x10')}, {'invalid-string',pack(string.char(255))}
}
return Def.ActorFrame {OnCommand=function(self)
 self:sleep(30)
 for _,case in ipairs(cases) do
  local args=case[2];local ok,value=pcall(FormatPercentScore,unpack(args,1,args.n))
  MESSAGEMAN:Broadcast('ScoreFormat',{label=case[1],ok=ok,value=ok and value or nil})
 end
end}
