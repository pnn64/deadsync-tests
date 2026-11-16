-- Keep every key alive independently of the table. Lua 5.1 still converts
-- deleted collectable keys to dead keys while traversing the table during GC.
collectgarbage('stop')
local keys = {}
for i=1,12 do keys[i] = 'field'..i end
local function order(t)
    local out = {}
    for key in pairs(t) do out[#out+1] = key end
    return table.concat(out, ',')
end
local function run(gc)
    local t = {}
    for i=1,12 do t[keys[i]] = i end
    for i=1,12,2 do t[keys[i]] = nil end
    local cursor = next(t)
    t[cursor] = nil
    -- Move the cached next cursor elsewhere before using the deleted key.
    local other = next(t)
    if other then next(t, other) end
    if gc then collectgarbage('collect') end
    -- A deleted cursor remains valid even after its node becomes a dead key.
    local next_key = next(t, cursor)
    print(gc, cursor, next_key)
    for i=12,1,-1 do t[keys[i]] = i end
    print(order(t))
end
run(false)
run(true)
-- Weak-value cleanup also retires the key at the point its value is cleared.
local weak = setmetatable({}, {__mode='v'})
for i=1,12 do weak[keys[i]] = {} end
collectgarbage('collect')
assert(next(weak) == nil)
assert(pcall(next, weak, keys[2]))
for i=12,1,-1 do weak[keys[i]] = i end
print(order(weak))
-- Non-string collectable cursors remain usable without retaining the objects
-- through the dead nodes. Pointer-specific iteration order is not compared.
local objects = {{}, function() end, coroutine.create(function() end), newproxy()}
local t = {}
for _, key in ipairs(objects) do t[key] = true end
for _, key in ipairs(objects) do t[key] = nil end
collectgarbage('collect')
for _, key in ipairs(objects) do assert(pcall(next, t, key)) end
for _, key in ipairs(objects) do t[key] = true end
local count = 0
for key, value in pairs(t) do assert(value); count = count + 1 end
assert(count == #objects)
-- A revived object key must use its live node even if next() cached the old
-- deleted node before collection. Check against the table's actual traversal.
local anchors, map = {}, {}
for i=1,32 do local key = {}; anchors[i] = key; map[key] = i end
for i=1,64 do
    local key = next(map)
    map[key] = nil
    collectgarbage('collect')
    map[key] = i
    local actual = next(map, key)
    local found, expected = false, nil
    for item in pairs(map) do
        if found then expected = item; break end
        if item == key then found = true end
    end
    assert(found and actual == expected)
end
