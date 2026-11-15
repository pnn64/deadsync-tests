-- Reference: ITGmania 5c737928, bundled Lua 5.1 ltable.c/lstring.c.
-- Includes the actor-discovery and active-modifier maps used by song scripts.
function show(t)
    local out = {}
    for k,v in pairs(t) do out[#out+1] = tostring(k)..'='..tostring(v) end
    print(#t, table.concat(out, ','))
end
local children = {}
for _,name in ipairs({'quad','barrier','aft.base','aft.output','aft.basep2',
    'aft.outputp2','aft.finalbase','aft.finaloutput','songbackground'}) do
    children[name] = name
end
show(children)
local mods = {}
for _,name in ipairs({'ConfusionOffset','Tiny4','Tiny1','Tiny2','Tiny3','Reverse'}) do
    mods[name] = 1; show(mods)
end
mods.Tiny4 = nil; mods.Tiny2 = nil; show(mods)
mods.Boost = 2; mods.Tiny4 = 3; show(mods)
-- Collisions, deleted main nodes, surviving chain nodes, and resize reinsertion.
local t = {}
for i=1,48 do
    t['key'..i] = i
    if i % 3 == 0 then t['key'..(i-1)] = nil end
    if i % 4 == 0 then show(t) end
end
for k in pairs(t) do t[k] = nil end
show(t)
for i=48,1,-1 do t['key'..i] = i end
show(t)
-- Array density, SETLIST growth, false and fractional keys.
t = {}
for _,k in ipairs({7,2,12,1,4,3,8,6,5,20,0,-1,0.5}) do t[k] = k; show(t) end
t[false] = 'false'; t[true] = 'true'; t['named'] = 'field'; show(t)
t[2] = nil; t[5] = nil; t[9] = 9; show(t)
local function constructors()
    local a = {a=1,b=2,c=3,d=4,e=5,f=6,g=7,h=8,i=9,j=10,k=11,l=12,m=13,n=14,o=15,p=16,q=17}
    show(a)
    local b = {10,20,30, foo=1, bar=2, baz=3, [8]=80, [16]=160}
    show(b)
    b[6]=60; b[5]=50; b[4]=40; show(b)
    local function tail() return 3,4,5 end
    show({a=1, 1,2,tail()})
end
constructors()
assert(loadstring(string.dump(constructors)))()
-- A deleted iteration control remains valid until its node is reused.
t = {first=1,second=2,third=3}
local k = next(t); t[k] = nil
local n = next(t,k); print(n, t[n])
collectgarbage('collect'); show(children)
-- Repeated deletion/reuse crosses many collision-chain and array boundaries.
local seed, checksum = 7919, 0
local function random(n)
    seed = seed * 16807 % 2147483647
    return seed % n
end
t = {}
for i=1,10000 do
    local k = random(257)
    if k % 3 ~= 0 then k = 'field'..k end
    local v = random(5) == 0 and false or i
    if v == false then v = nil end
    t[k] = v
    if i % 20 == 0 then
        local out = {}
        for key,value in pairs(t) do out[#out+1] = tostring(key)..'='..value end
        local s = table.concat(out, ',')
        for j=1,#s do checksum = (checksum * 31 + s:byte(j)) % 2147483647 end
    end
end
print(checksum)
-- Relocation must preserve collectable keys/values and weak cleanup.
local strong, weak = {}, setmetatable({}, {__mode='kv'})
for i=1,1000 do
    local k, v = {}, {i}
    strong[k] = v; weak[k] = v
end
collectgarbage('collect')
local n = 0
for k,v in pairs(strong) do assert(weak[k] == v); n = n + 1 end
assert(n == 1000)
strong = nil
collectgarbage('collect'); collectgarbage('collect')
assert(next(weak) == nil)
