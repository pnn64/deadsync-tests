local showAFTs = true
if not string.find(string.lower(PREFSMAN:GetPreference('VideoRenderers')), 'opengl')
or string.find(string.lower(PREFSMAN:GetPreference('VideoRenderers')), 'd3d')
and string.find(string.lower(PREFSMAN:GetPreference('VideoRenderers')), 'opengl') 
and string.find(string.lower(PREFSMAN:GetPreference('VideoRenderers')), 'd3d') < 
string.find(string.lower(PREFSMAN:GetPreference('VideoRenderers')), 'opengl') then
	showAFTs = false
end

local sw = SCREEN_WIDTH
local sh = SCREEN_HEIGHT
local scx = SCREEN_CENTER_X
local scy = SCREEN_CENTER_Y
local dw = PREFSMAN:GetPreference('DisplayWidth')
local dh = PREFSMAN:GetPreference('DisplayHeight')
local zr = sw/dw
local rz = dw/sw
local comboProxies = {}

local static, aft_screenTex, blur, aft_blurTex, distort, pauseText, snow, overexpose
local staticSize = SCREEN_HEIGHT/20
local halfStaticSize = staticSize * 0.5
local blurSteps = 2
local blurDecay = 0.7
local blurTotal = 1
local distortionCount = 3
local rowsPerDistortion = 7
local distortMinDuration = 1
local distortRndDuration = 4
local distortMinMinWidth = 0.02
local distortRndMinWidth = 0.02
local distortMinAddWidth = 0.01
local distortRndAddWidth = 0.03
local distortRndTravel = 0.1
local distortMinIntensity = 0.04
local distortRndIntensity = 0.08
local maxSnow = 30
local snowPerWeight = 0.025 * SCREEN_WIDTH
local snowWhenPaused = 20
local snowMinWidth = 0.035 * SCREEN_WIDTH
local snowAddWidth = 0.045 * SCREEN_WIDTH

local vhs = 1
local lastAFTBeat = -1
local exposure = 0

local checked = false

-- EASING --
local path = GAMESTATE:GetCurrentSong():GetSongDir()..'lua/'
loadfile(path..'easing.lua')()
loadfile(path..'modhelpers.lua')()
loadfile(path.."mods.lua")()

local function Plr(pn)
	if GAMESTATE:IsPlayerEnabled(pn-1) then
		return SCREENMAN:GetTopScreen():GetChild('PlayerP'..pn)
	else
		return nil
	end
end
function GetJud(pn)
	return _G['jud'..pn]
end
function GetCom(pn)
	return _G['com'..pn]
end

function mod_do(str,pn)
	if pn then
		if GAMESTATE:IsPlayerEnabled(pn-1) then
			taronuke_mods(str,pn)
		end
	else
		for pn=1,2 do
			if GAMESTATE:IsPlayerEnabled(pn-1) then
				taronuke_mods(str,pn)
			end
		end
	end
end

-- ALIASES --
--These make it so the syntax for the table entries matches the syntax for the nITG template.
--If you want to prefix all your calls with "modhelpers.", "ease.", etc., then you won't need this and can remove this section.
local linear, inQuad, outQuad, inOutQuad, outInQuad, inCubic, outCubic, inOutCubic, outInCubic, inQuart,outQuart, inOutQuart, outInQuart, inQuint, outQuint, inOutQuint, outInQuint, inSine, outSine, inOutSine,outInSine, inExpo, outExpo, inOutExpo, outInExpo, inCirc, outCirc, inOutCirc, outInCirc, inElastic,outElastic, inOutElastic, outInElastic, inBack, outBack, inOutBack, outInBack, inBounce, outBounce,inOutBounce, outInBounce = ease.linear, ease.inQuad, ease.outQuad, ease.inOutQuad, ease.outInQuad,ease.inCubic, ease.outCubic, ease.inOutCubic, ease.outInCubic, ease.inQuart, ease.outQuart,ease.inOutQuart, ease.outInQuart, ease.inQuint, ease.outQuint, ease.inOutQuint, ease.outInQuint,ease.inSine, ease.outSine, ease.inOutSine, ease.outInSine, ease.inExpo, ease.outExpo, ease.inOutExpo,ease.outInExpo, ease.inCirc, ease.outCirc, ease.inOutCirc, ease.outInCirc, ease.inElastic,ease.outElastic, ease.inOutElastic, ease.outInElastic, ease.inBack, ease.outBack, ease.inOutBack,ease.outInBack, ease.inBounce, ease.outBounce, ease.inOutBounce, ease.outInBounce

local perframe, mod_insert, mod2_insert, mod_ease, mod_perframe, mod_message, mod_blacklist, simple_m0d, simple_m0d2, simple_m0d3, mod_wiggle, mod_spring, mod_springt, mod_springt2, mod_spring_adjustable, mod_onebeat, switcfino_add, switcfino_reset, mod_sugarkiller, modulo, reverseRotation, randomXD, mod_bounce, ease_wiggle, ease_wiggleAbs = modhelpers.perframe, modhelpers.mod_insert, modhelpers.mod2_insert, modhelpers.mod_ease, modhelpers.mod_perframe, modhelpers.mod_message, modhelpers.mod_blacklist, modhelpers.simple_m0d, modhelpers.simple_m0d2, modhelpers.simple_m0d3, modhelpers.mod_wiggle, modhelpers.mod_spring, modhelpers.mod_springt, modhelpers.mod_springt2, modhelpers.mod_spring_adjustable, modhelpers.mod_onebeat, modhelpers.switcfino_add, modhelpers.switcfino_reset, modhelpers.mod_sugarkiller, modhelpers.modulo,modhelpers.reverseRotation, modhelpers.randomXD, modhelpers.mod_bounce, modhelpers.ease_wiggle, modhelpers.ease_wiggleAbs

local m = mod_insert
local m2 = mod_message
local me = mod_ease
local mb = mod_bounce
			
local l = 'len'
local e = 'end'



init_modsp1 = ''
init_modsp2 = ''

mod_plr = {}

mod_firstSeenBeat = GAMESTATE:GetSongBeat() --necessary to prevent long freezes


local diffName = {}
local poptions = {GAMESTATE:GetPlayerState(0):GetPlayerOptions('ModsLevel_Song'), GAMESTATE:GetPlayerState(1):GetPlayerOptions('ModsLevel_Song')}
local playerscrolldir = {}
local playerspeed = {}
local playermini = {}
local playerminisize = {}
local playermirror = {}
local soptions = GAMESTATE:GetSongOptions('ModsLevel_Song')
local rate = 1
local xmu,sic = string.find(soptions,'xMusic')
if xmu then
	local begin = xmu-1
	while begin > 0 and string.match(string.sub(soptions,begin,begin),'[.%d]') do
		begin = begin - 1
	end
	local rateString = string.sub(soptions, begin + 1, xmu - 1)
	rate = tonumber(rateString)
end
local bpm = 125 * rate
for pn = 1,2 do
	if GAMESTATE:IsPlayerEnabled(pn-1) then
		diffName[pn] = GAMESTATE:GetCurrentSteps(pn-1):GetDifficulty()
		if poptions[pn] then
			playerscrolldir[pn] = (poptions[pn]:Reverse() == 0 and 1 or -1)
			playermirror[pn] = poptions[pn]:Mirror()
			playermini[pn] = poptions[pn]:Mini() * 100
			playerminisize[pn] = (200-playermini[pn])/200
			
			local xm = poptions[pn]:XMod()
			local cm = poptions[pn]:CMod() or poptions[pn]:MMod()
			if cm then
				playerspeed[pn] = cm / bpm
			else
				playerspeed[pn] = xm
			end
			local tiltCompensation = poptions[pn]:Tilt() or 0
			playerspeed[pn] = playerspeed[pn] * math.cos(tiltCompensation * math.pi / 6)
			-- speed limit
			if playerspeed[pn] * playerminisize[pn] > 3.5 then
				playerspeed[pn] = 3.5 / playerminisize[pn]
			end
		end
	end
end

local pp = {}

local restepDenote, currentRestep = {}, {}

-- preprocessing functions
local function getRot(panel)
	if panel == 1 then return math.pi * 0.5 end
	if panel == 2 then return 0 end
	if panel == 3 then return math.pi end
	return -math.pi * 0.5
end
local function getNote(newBlock, newStep, prevBlock, prevStep, panelIndex, lastNote, noteBeat)
	local tNewStep = newBlock[2][newStep]
	local tPrevStep = prevBlock[2][prevStep]
	local newPanel = tNewStep[panelIndex] or tNewStep[1]
	local prevPanel = tPrevStep[panelIndex] or tPrevStep[1]
	local xOff = (newPanel - prevPanel) * 64
	local yOff = (newStep - prevStep) * 16
	local prevRot, newRot = getRot(prevPanel), getRot(newPanel)
	local rzOff = newRot - prevRot
	if rzOff < -(math.pi * 0.5) then
		rzOff = rzOff + math.pi * 2
	end
	if rzOff > math.pi then
		rzOff = rzOff - math.pi * 2
	end
	local swapBeat = math.max(prevBlock[1] + (prevStep - 10) * 0.25, newBlock[1] + (newStep - 2) * 0.25)
	return { beat = swapBeat, xOff = lastNote.xOff + xOff, yOff = lastNote.yOff + yOff, rzOff = lastNote.rzOff + rzOff }
end

for pn = 1,2 do
	if GAMESTATE:IsPlayerEnabled(pn-1) then
		currentRestep[pn] = 1
		restepDenote[pn] = {
			{ resetAt = 1.5, { 0 }, { 2 }, { 4 } },
			{ resetAt = 1.5, { 8 }, { 10 }, { 12 } },
			{ resetAt = 1.5, { 16 }, { 18 }, { 20 } },
			{ resetAt = 1.5, { 24 }, { 26 }, { 28 } },
			{ resetAt = 1.5, { 32, { {}, {}, {}, {2}, {}, {3}, {2} } },
							 { 34, { {}, {}, {}, {3}, {}, {2}, {3} } },
							 { 36, { {}, {}, {}, {2}, {}, {3}, {2} } },
			},
			{ resetAt = 1.5, { 40, { {}, {}, {}, {2}, {}, {3}, {2} } },
							 { 42, { {}, {}, {}, {3}, {}, {2}, {3} } },
							 { 44, { {}, {}, {}, {2}, {}, {3}, {2} } },
			},
			{ resetAt = 1.5, { 79.5, { {2}, {3}, {1}, {}, {3}, {1}, {2,4} } },
							 { 81.5, { {3}, {3}, {1}, {}, {2}, {1}, {3,4} } },
							 { 83.5, { {2}, {length=0.75,3}, {1}, {}, {2}, {4}, {1,3} } },
							 { 85.5, { {2}, {2}, {length=0.5,3}, {}, {1}, {length=0.75,4}, {1,3} } },
			},
			{ resetAt = 1.5, { 87.5, { {2}, {3}, {1}, {}, {2}, {1}, {3,4} } },
							 { 89.5, { {2}, {2}, {1}, {}, {3}, {1}, {2,4} } },
							 { 91.5, { {3}, {length=0.75,2}, {1}, {}, {3}, {4}, {1,2} } },
			},
			{ resetAt = 1.5, { 95.5, { {3}, {2}, {4}, {}, {3}, {4}, {1,2} } },
							 { 97.5, { {3}, {length=0.75,3}, {4}, {}, {2}, {1}, {3,4} } },
							 { 99.5, { {2}, {length=0.75,2}, {1}, {}, {3}, {4}, {1,2} } },
							 { 101.5, { {3}, {3}, {length=0.5,2}, {}, {1}, {length=0.75,4}, {1,3} } },
			},
			{ resetAt = 1.5, { 103.5, { {2}, {2}, {1}, {}, {3}, {1}, {2,4} } },
							 { 105.5, { {3}, {length=0.75,3}, {1}, {}, {2}, {4}, {1,3} } },
							 { 107.5, { {2}, {2}, {4}, {}, {1}, {3}, {1,2} } },
			},
			{ resetAt = 1.75, { 111.25, { {}, {4}, {3}, {2}, {1}, {3}, {3}, {2,4} } },
							  { 113.25, { {}, {4}, {1}, {3}, {1}, {2}, {2}, {3,4} } },
							  { 115.25, { {}, {2}, {2}, {1}, {4}, {3}, {3}, {1,2} } },
							  { 117.25, { {}, {1}, {4}, {3}, {4}, {2}, {2}, {1,3} } },
							  { 119.25, { {length=0.75,4}, {2}, {}, {1}, {4}, {3}, {3}, {1,2} } },
							  { 121.25, { {}, {1}, {4}, {3}, {4}, {2}, {2}, {1,3} } },
							  { 123.25, { {}, {2}, {2}, {4}, {2}, {2}, {1}, {3,4} } },
							  { 125.25, { {}, {4}, {1}, {2}, {3}, {3}, {1}, {2,4} } },
							  { 127.25, { {length=0.75,1}, {3}, {}, {4}, {1}, {2}, {2}, {3,4} } },
							  { 129.25, { {}, {4}, {1}, {2}, {1}, {3}, {3}, {2,4} } },
							  { 131.25, { {}, {3}, {3}, {1}, {4}, {2}, {2}, {1,3} } },
							  { 133.25, { {}, {1}, {4}, {2}, {4}, {3}, {3}, {1,2} } },
							  { 135.25, { {length=0.75,4}, {3}, {}, {1}, {4}, {2}, {2}, {1,3} } },
							  { 137.25, { {}, {1}, {4}, {2}, {4}, {3}, {3}, {1,2} } },
							  { 139.25, { {}, {3}, {3}, {4}, {1}, {2}, {2}, {3,4} } },
							  { 141.25, { {}, {1}, {2}, {1,3}, {}, {4}, {2}, {3,4} } },
			},
			{ resetAt = 1.5, { 176, { {4}, {}, {}, {1}, {}, {}, {1} } },
							 { 178, { {1}, {}, {}, {4}, {}, {}, {4} } },
							 { 180, { {4}, {}, {}, {1}, {}, {}, {1} } },
			},
			{ resetAt = 1.5, { 184, { {1}, {}, {}, {4}, {}, {}, {4} } },
							 { 186, { {4}, {}, {}, {1}, {}, {}, {1} } },
							 { 188, { {1}, {}, {}, {4}, {}, {}, {4} } },
			},
			{ resetAt = 1.5, { 192, { {4}, {}, {}, {1}, {}, {1}, {} } },
							 { 194, { {1}, {}, {}, {4}, {}, {4}, {} } },
							 { 196, { {4}, {}, {}, {1}, {}, {1}, {} } },
			},
			{ resetAt = 1.5, { 200, { {4}, {}, {}, {1}, {}, {1}, {} } },
							 { 202, { {1}, {}, {}, {4}, {}, {4}, {} } },
							 { 204, { {4}, {}, {}, {1}, {}, {1}, {} } },
			},

		}
		
		-- preprocessing
		for crd = 1,#restepDenote[pn] do
			local trd = restepDenote[pn][crd]
			if trd and trd[1][2] then
				trd.notesByCol = {}
				for cblock = 1,#trd do
					local tblock = trd[cblock]
					for cstep = 1,#tblock[2] do
						local tstep = tblock[2][cstep]
						for p = 1,2 do
							if tstep[p] then
								local lastNote = { beat = 9999, xOff = 0, yOff = 0, rzOff = 0 }
								local tnote = { length=tstep.length, beat=tblock[1] + 0.25 * (cstep - 1), endBeat=(tblock[1] + 0.25 * (cstep - 1))+(tstep.length or 0), lastNote }
								if cblock > 1 then
									local dstep = cstep
									local dblock = cblock
									for rblock = cblock-1,1,-1 do
										local trblock = trd[rblock]
										local tdblock = trd[rblock+1]
										if trblock[2][dstep] and trblock[2][dstep][1] then
											lastNote = getNote(trblock, dstep, tdblock, dstep, p, lastNote, tnote.beat)
											tnote[#tnote+1] = lastNote
										elseif trblock[2][dstep-2] and trblock[2][dstep-2][1] then
											lastNote = getNote(trblock, dstep - 2, tdblock, dstep, p, lastNote, tnote.beat)
											tnote[#tnote+1] = lastNote
											dstep = dstep - 2
										elseif trblock[2][dstep+2] and trblock[2][dstep+2][1] then
											lastNote = getNote(trblock, dstep + 2, tdblock, dstep, p, lastNote, tnote.beat)
											tnote[#tnote+1] = lastNote
											dstep = dstep + 2
										else
											-- and you may ask yourself, well, how did I get here?
										end
									end
								end
								if not trd.notesByCol[tstep[p]] then
									trd.notesByCol[tstep[p]] = {}
								end
								trd.notesByCol[tstep[p]][#(trd.notesByCol[tstep[p]])+1] = tnote
							end
						end
					end
				end
			end
		end
	end
end

---------------------------------------------------------------------------------------
----------------------Begin tables 'n stuff--------------------------------------------
---------------------------------------------------------------------------------------

--beat based mods
--{beat_start, beat_end, mods, len_or_end, player_number}
mods = {
	{0,9999,'*1000 overhead, *1000 no beat, *1000 no drunk, *1000 no tipsy, *1000 no invert, *1000 no flip, *1000 no split, *1000 no alternate, *1000 no cross, *1000 no sudden','end'},
	playerspeed[1] and {0,9999,'*1000000 '..playerspeed[1]..'x','end',1} or nil,
	playerspeed[2] and {0,9999,'*1000000 '..playerspeed[2]..'x','end',2} or nil,
	{195.5,205,'*1000 200 sudden','end'},
}
			
--this is both a message broadcaster and a function runner
--if you put {beat,'String'}, then 'String' is broadcast as a message on that beat
--if you put {beat,function() somecode end}, then function() is run at that beat
--see example on beat 32

curaction = 1
--{beat,thing,persists}
mod_actions = {


	
}
			
--beat-based ease mods
--{time_start, time_end, mod_start, mod_end, mod, len_or_end, ease_type, player_number, sustaintime, optional_param1, optional_param2}
--valid ease types are:
	--linear
	--inQuad    outQuad    inOutQuad    outInQuad
	--inCubic   outCubic   inOutCubic   outInCubic
	--inQuart   outQuart   inOutQuart   outInQuart
	--inQuint   outQuint   inOutQuint   outInQuint
	--inSine    outSine    inOutSine    outInSine
	--inExpo    outExpo    inOutExpo    outInExpo
	--inCirc    outCirc    inOutCirc    outInCirc
	--inElastic outElastic inOutElastic outInElastic    --can take 2 optional parameters - amplitude & period
	--inBack    outBack    inOutBack    outInBack       --can take 1 optional parameter  - spring amount
	--inBounce  outBounce  inOutBounce  outInBounce
	
mods_ease = {
	-- EXAMPLE TWEEN: from beat 0 to 4, make rotationz go from 360 to 0 with the inOutBack tween
	--{0,4,360,0,'rotationz','end',inOutBack},
}



mod_perframes = {
	
}

function mpf(s,e,f)
	table.insert(mod_perframes,{s,e,f})
end

local randomCounter = 0
function randomXD()
	randomCounter = randomCounter + 1
	return modulo(math.sin(randomCounter * 3229.3) * 43758.5453, 1)
end

local function setVHS(value)
	vhs = value
end
local function setExposure(value)
	exposure = value
end

local function clapEmoji(beat,strength,linger)
	if not strength then
		strength = 100
	end
	local endVal = linger and ((strength > 0 and (strength - 100) or (strength + 100)) * 0.5) or 0
	local holdTime = linger and 1.625 or 0.5
	me(beat,0.375,strength,endVal,'drunk',l,outCirc)
	me(beat,0.375,strength,endVal,'tipsy',l,outCirc)
	me(beat+0.375,holdTime,endVal,endVal,'drunk',l,outCirc)
	me(beat+0.375,holdTime,endVal,endVal,'tipsy',l,outCirc)
	if linger then
		print(strength..', '..endVal)
	end
end

local flipflop = 100
for i = 17,45,2 do
	clapEmoji(i,flipflop)
	flipflop = -flipflop
end
clapEmoji(46,flipflop)
clapEmoji(47,-flipflop)

for i = 81,85,2 do
	clapEmoji(i,flipflop)
	flipflop = -flipflop
end
me(85.5,0.5,0,flipflop,'drunk',l,inCirc)
me(86,0.75,flipflop,-flipflop,'drunk',l,inQuad)
me(86.75,0.75,-flipflop,0,'drunk',l,inOutSine)
me(85.5,0.5,0,flipflop,'tipsy',l,inCirc)
me(86,0.75,flipflop,-flipflop,'tipsy',l,inQuad)
me(86.75,0.75,-flipflop,0,'tipsy',l,inOutSine)
for i = 89,93,2 do
	clapEmoji(i,flipflop)
	flipflop = -flipflop
end
me(93.5,0.5,0,flipflop,'drunk',l,inCirc)
me(94,0.75,flipflop,-flipflop*0.5,'drunk',l,inQuad)
me(94.75,0.75,-flipflop*0.5,0,'drunk',l,inOutSine)
me(93.5,0.5,0,flipflop,'tipsy',l,inCirc)
me(94,0.75,flipflop,-flipflop*0.5,'tipsy',l,inQuad)
me(94.75,0.75,-flipflop*0.5,0,'tipsy',l,inOutSine)
for i = 97,101,2 do
	clapEmoji(i,flipflop)
	flipflop = -flipflop
end
me(101.5,0.5,0,flipflop,'drunk',l,inCirc)
me(102,0.75,flipflop,-flipflop,'drunk',l,inQuad)
me(102.75,0.75,-flipflop,0,'drunk',l,inOutSine)
me(101.5,0.5,0,flipflop,'tipsy',l,inCirc)
me(102,0.75,flipflop,-flipflop,'tipsy',l,inQuad)
me(102.75,0.75,-flipflop,0,'tipsy',l,inOutSine)
for i = 105,109,2 do
	clapEmoji(i,flipflop)
	flipflop = -flipflop
end

clapEmoji(110,flipflop)
for i = 111,119,2 do
	flipflop = -flipflop
	clapEmoji(i,flipflop)
end
me(119.25,0.25,0,-flipflop*1.5,'drunk',l,inQuad)
me(119.5,0.5,-flipflop*1.5,0,'drunk',l,inOutSine)
me(119.25,0.25,0,-flipflop*0.5,'tipsy',l,inQuad)
me(119.5,0.5,-flipflop*0.5,0,'tipsy',l,inOutSine)
for i = 121,127,2 do
	clapEmoji(i,flipflop)
	flipflop = -flipflop
end
me(127.25,0.25,0,flipflop*1.5,'drunk',l,inQuad)
me(127.5,0.5,flipflop*1.5,0,'drunk',l,inOutSine)
me(127.25,0.25,0,flipflop*0.5,'tipsy',l,inQuad)
me(127.5,0.5,flipflop*0.5,0,'tipsy',l,inOutSine)
for i = 129,135,2 do
	flipflop = -flipflop
	clapEmoji(i,flipflop)
end
me(135.25,0.25,0,flipflop*1.5,'drunk',l,inQuad)
me(135.5,0.5,flipflop*1.5,0,'drunk',l,inOutSine)
me(135.25,0.25,0,flipflop*0.5,'tipsy',l,inQuad)
me(135.5,0.5,flipflop*0.5,0,'tipsy',l,inOutSine)
for i = 137,141,2 do
	clapEmoji(i,flipflop)
	flipflop = -flipflop
end
clapEmoji(142,-flipflop)
clapEmoji(143,flipflop)
for i = 177,205,2 do
	flipflop = -flipflop
	clapEmoji(i,flipflop)
end
for i = 209,239,2 do
	flipflop = -flipflop
	if flipflop < 0 then
		flipflop = flipflop + 5
	else
		flipflop = flipflop - 5
	end
	clapEmoji(i,flipflop,true)
end

me(47,1,1,3,setVHS,l,inCubic)
me(48,1,3,3,setVHS,l,linear)
me(47.5,0.5,0,25,'drunk',l,inQuad)
me(47.5,0.5,0,25,'tipsy',l,inQuad)

me(48,53.5,25,25,'drunk',e,linear)
me(53.5,0.5,25,-50,'drunk',l,inQuad)
me(54,0.75,-50,50,'drunk',l,inQuad)
me(54.75,1.25,50,25,'drunk',l,outQuad)
me(48,53.5,25,25,'tipsy',e,linear)
me(53.5,0.5,25,-50,'tipsy',l,inQuad)
me(54,0.75,-50,50,'tipsy',l,inQuad)
me(54.75,1.25,50,25,'tipsy',l,outQuad)

me(56,61.5,25,25,'drunk',e,linear)
me(61.5,0.5,25,-50,'drunk',l,inQuad)
me(62,0.75,-50,50,'drunk',l,inQuad)
me(62.75,1.25,50,25,'drunk',l,outQuad)
me(56,61.5,25,25,'tipsy',e,linear)
me(61.5,0.5,25,-50,'tipsy',l,inQuad)
me(62,0.75,-50,50,'tipsy',l,inQuad)
me(62.75,1.25,50,25,'tipsy',l,outQuad)

me(64,69.5,25,25,'drunk',e,linear)
me(69.5,0.5,25,-50,'drunk',l,inQuad)
me(70,0.75,-50,50,'drunk',l,inQuad)
me(70.75,1.25,50,25,'drunk',l,outQuad)
me(64,69.5,25,25,'tipsy',e,linear)
me(69.5,0.5,25,-50,'tipsy',l,inQuad)
me(70,0.75,-50,50,'tipsy',l,inQuad)
me(70.75,1.25,50,25,'tipsy',l,outQuad)

me(72,76,25,25,'drunk',e,linear)
me(76,3,25,0,'drunk',l,outQuad)
me(72,76,25,25,'tipsy',e,linear)
me(76,3,25,0,'tipsy',l,outQuad)

me(76,3.5,3,1.3,setVHS,l,outQuad)
me(79.5,0.5,1.3,1.3,setVHS,l,linear)

me(108,4,1.3,1,setVHS,l,outQuad)
me(112,0.5,1,1,setVHS,l,linear)

me(143.5,0.5,1,2.5,setVHS,l,inQuad)
me(144,176,2.5,1,setVHS,e,outQuad)

me(143.5,0.5,0,50,'drunk',l,inQuad)
me(144,175.5,50,25,'drunk',e,outQuad)
me(175.5,0.5,25,0,'drunk',l,inQuad)
me(143.5,0.5,0,50,'tipsy',l,inQuad)
me(144,175.5,50,25,'tipsy',e,outQuad)
me(175.5,0.5,25,0,'tipsy',l,inQuad)

me(176,1,1,1,setVHS,l,linear)
me(206,2,1,1.75,setVHS,l,inQuad)
me(208,239.5,1.75,5,setVHS,e,inCirc)
me(239.5,0.5,5,0,setVHS,l,inQuad)

for i = 49.75,73.75,4 do
	if i ~= 61.75 then
		me(i,0.25,0.3,0,setExposure,l,outCirc)
		me(i+0.25,1,0,0,setExposure,l,linear)
	end
end
for i = 119.5,135.5,8 do
	me(i-0.5,0.5,0,0.7,setExposure,l,inQuad)
	me(i,0.5,0.7,0,setExposure,l,inOutSine)
	me(i+0.5,1,0,0,setExposure,l,linear)
end

for pn = 1,2 do
	if playermini[pn] then
		me(143.5,0.5,playermini[pn],200-(200-playermini[pn])*0.25,'mini',l,inCirc,pn)
		me(144,172,200-(200-playermini[pn])*0.25,200-(200-playermini[pn])*0.95,'mini',e,inQuad,pn)
		me(172,174,200-(200-playermini[pn])*0.95,playermini[pn],'mini',e,outQuad,pn)

		me(208,239.5,playermini[pn],200-(200-playermini[pn])*0.5,'mini',e,inQuad,pn)

		me(195.5,8,395 * playerspeed[pn] * playerminisize[pn] - 100, 85 * playerspeed[pn] * playerminisize[pn] - 100,'suddenoffset',l,linear,pn)
		me(203.5,1.5,85 * playerspeed[pn] * playerminisize[pn] - 100, 150,'suddenoffset',l,linear,pn)
	end
end



local distortPaths = {{}, {}, {}}
local function distortWidthAt(distortPath, beat)
	local center = (distortPath.startBeat + distortPath.endBeat) * 0.5
	local amount
	if beat < center then
		amount = (beat - distortPath.startBeat) / (center - distortPath.startBeat)
	else
		amount = (distortPath.endBeat - beat) / (distortPath.endBeat - center)
	end
	return distortPath.maxWidth * amount + distortPath.minWidth * (1 - amount)
end
local function distortMinAt(distortPath, beat)
	beat = math.min(beat, distortPath.endBeat)
	beat = math.max(beat, distortPath.startBeat)
	local amount = (beat - distortPath.startBeat) / (distortPath.endBeat - distortPath.startBeat)
	return distortPath.endY * amount + distortPath.startY * (1 - amount) - distortWidthAt(distortPath, beat)
end
local function distortMaxAt(distortPath, beat)
	beat = math.min(beat, distortPath.endBeat)
	beat = math.max(beat, distortPath.startBeat)
	local amount = (beat - distortPath.startBeat) / (distortPath.endBeat - distortPath.startBeat)
	return distortPath.endY * amount + distortPath.startY * (1 - amount) + distortWidthAt(distortPath, beat)
end
local function distortIntensityAt(distortPath, beat)
	beat = math.min(beat, distortPath.endBeat)
	beat = math.max(beat, distortPath.startBeat)
	local center = (distortPath.startBeat + distortPath.endBeat) * 0.5
	local amount
	if beat < center then
		amount = (beat - distortPath.startBeat) / (center - distortPath.startBeat)
	else
		amount = (distortPath.endBeat - beat) / (distortPath.endBeat - center)
	end
	return distortPath.intensity * amount
end

if showAFTs then
	local function generateDistortPath(pathSet)
		local blocked = {}
		local path = {}
		path.startBeat = distortPaths[pathSet][1] and distortPaths[pathSet][#(distortPaths[pathSet])].endBeat or -1 + randomXD()
		path.endBeat = path.startBeat + distortMinDuration + distortRndDuration * randomXD()
		path.intensity = distortMinIntensity + distortRndIntensity * randomXD()
		for i = 1,3 do
			if i ~= pathSet and distortPaths[i][1] then
				blocked[i > pathSet and i - 1 or i] = { startMin = distortMinAt(distortPaths[i][#distortPaths[i]], path.startBeat),
														endMin = distortMinAt(distortPaths[i][#distortPaths[i]], path.endBeat),
														startMax = distortMaxAt(distortPaths[i][#distortPaths[i]], path.startBeat),
														endMax = distortMaxAt(distortPaths[i][#distortPaths[i]], path.endBeat),
														midMin = distortMinAt(distortPaths[i][#distortPaths[i]], (path.startBeat + path.endBeat) * 0.5),
														midMax = distortMaxAt(distortPaths[i][#distortPaths[i]], (path.startBeat + path.endBeat) * 0.5) }
			end
		end
		if not blocked[1] then
			path.minWidth = distortMinMinWidth + distortRndMinWidth * randomXD()
			path.maxWidth = path.minWidth + distortMinAddWidth + distortRndAddWidth * randomXD()
			path.startY = 0.45
			path.endY = 0.55
		elseif not blocked[2] then
			path.minWidth = distortMinMinWidth + distortRndMinWidth * randomXD()
			path.maxWidth = path.minWidth + distortMinAddWidth + distortRndAddWidth * randomXD()
			path.startY = 0.2
			path.endY = 0.3
		else
			if blocked[1].startMin > blocked[2].startMin then
				local temp = blocked[1]
				blocked[1] = blocked[2]
				blocked[2] = temp
			end
			local startZones = { { minY = 0, maxY = blocked[1].startMin, width = blocked[1].startMin },
								 { minY = blocked[1].startMax, maxY = blocked[2].startMin, width = blocked[2].startMin - blocked[1].startMax },
								 { minY = blocked[2].startMax, maxY = 1, width = 1 - blocked[2].startMax } }
			local endZones = { { minY = 0, maxY = blocked[1].endMin, width = blocked[1].endMin },
							   { minY = blocked[1].endMax, maxY = blocked[2].endMin, width = blocked[2].endMin - blocked[1].endMax },
							   { minY = blocked[2].endMax, maxY = 1, width = 1 - blocked[2].endMax } }
			local startRandom = randomXD() * (startZones[1].width + startZones[2].width + startZones[3].width)
			local startRandomLocal = startRandom
			local startRandomZone = 1
			while startRandomLocal > startZones[startRandomZone].width do
				startRandomLocal = startRandomLocal - startZones[startRandomZone].width
				startRandomZone = startRandomZone + 1
			end
			local endRandom = randomXD() * (endZones[1].width + endZones[2].width + endZones[3].width)
			local endRandomLocal = endRandom
			local endRandomZone = 1
			while endRandomLocal > endZones[endRandomZone].width do
				endRandomLocal = endRandomLocal - endZones[endRandomZone].width
				endRandomZone = endRandomZone + 1
			end
			if startRandomZone ~= endRandomZone then
				if startZones[startRandomZone].width + endZones[startRandomZone].width > startZones[endRandomZone].width + endZones[endRandomZone].width then
					endRandomZone = startRandomZone
					endRandomLocal = randomXD() * endZones[endRandomZone].width
				else				
					startRandomZone = endRandomZone
					startRandomLocal = randomXD() * startZones[startRandomZone].width
				end
			end
			
			for i = 1,3 do
				path.startY = startZones[startRandomZone].minY + startRandomLocal
				path.endY = endZones[endRandomZone].minY + endRandomLocal
				local dist = math.abs(path.endY - path.startY)
				if dist * dist > randomXD() * 0.1 then
					if path.endY > path.startY then
						local push = randomXD() * 0.5
						local remain = startZones[startRandomZone].width - startRandomLocal
						startRandomLocal = startRandomLocal + push * remain
						
						push = randomXD() * 0.5
						endRandomLocal = endRandomLocal * (1 - push)
					else
						local push = randomXD() * 0.5
						local remain = endZones[endRandomZone].width - endRandomLocal
						endRandomLocal = endRandomLocal + push * remain
						
						push = randomXD() * 0.5
						startRandomLocal = startRandomLocal * (1 - push)
					end
				end
			end
			local midY = (path.startY + path.endY) * 0.5

			path.minWidth = distortMinMinWidth + distortRndMinWidth * randomXD()
			path.minWidth = math.min(path.minWidth, path.startY - startZones[startRandomZone].minY)
			path.minWidth = math.min(path.minWidth, startZones[startRandomZone].maxY - path.startY)
			path.minWidth = math.min(path.minWidth, path.endY - endZones[endRandomZone].minY)
			path.minWidth = math.min(path.minWidth, endZones[endRandomZone].maxY - path.endY)
			
			path.maxWidth = path.minWidth + distortMinAddWidth + distortRndAddWidth * randomXD()
			if startRandomZone == 1 then
				path.maxWidth = math.min(path.maxWidth, midY)
				path.maxWidth = math.min(path.maxWidth, blocked[1].midMin - midY)
			elseif startRandomZone == 2 then
				path.maxWidth = math.min(path.maxWidth, midY - blocked[1].midMax)
				path.maxWidth = math.min(path.maxWidth, blocked[2].midMin - midY)
			else
				path.maxWidth = math.min(path.maxWidth, midY - blocked[2].midMax)
				path.maxWidth = math.min(path.maxWidth, 1 - midY)
			end
		end
		distortPaths[pathSet][#(distortPaths[pathSet])+1] = path
	end
	for i = 1,3 do
		generateDistortPath(i)
	end
	while distortPaths[1][#(distortPaths[1])].endBeat < 244 or distortPaths[2][#(distortPaths[2])].endBeat < 244 or distortPaths[3][#(distortPaths[3])].endBeat < 244 do
		local lowest = 1
		for i = 2,3 do
			if distortPaths[i][#(distortPaths[i])].endBeat < distortPaths[lowest][#(distortPaths[lowest])].endBeat then
				lowest = i
			end
		end
		generateDistortPath(lowest)
	end
end

local function Update(self)
	if GAMESTATE:GetSongBeat()>=0 and not checked then
		--name players, judgment and combo
		for pn=1,2 do
			_G['P'..pn] = SCREENMAN:GetTopScreen():GetChild('PlayerP'..pn) or nil
			if _G['P'..pn] then
				_G['jud'..pn] = _G['P'..pn]:GetChild('Judgment')
				_G['com'..pn] = _G['P'..pn]:GetChild('Combo')
			end
			
		end
		
		-- one time setup for AFT stuff
		if showAFTs then
			for i,v in ipairs(blur) do
				for ii,vv in ipairs(v) do
					if i == blurSteps+1 and ii == blurSteps+1 then
						vv:diffuse(1/blurTotal, 1/blurTotal, 1/blurTotal, 1)
					else
						vv:diffusealpha(math.pow(blurDecay,math.abs(blurSteps+1-i) + math.abs(blurSteps+1-ii)) / blurTotal)
					end
				end
			end
		end
		
		screen = SCREENMAN:GetTopScreen()
		checked = true --let this only run once
	end

	local beat = GAMESTATE:GetSongBeat()
	
	for pn = 1,2 do
		if comboProxies[pn] then
			local p = Plr(pn)
			local c = p:GetChild('Combo')
			comboProxies[pn]:visible(Plr(pn):GetChild('Combo'):GetVisible())
		end
	end
	
	local pause = false

	local sway = 0
	if beat >= 48 and beat < 49.75 then
		sway = (beat - 48) / 1.75
		sway = sway * sway
	elseif beat >= 49.75 and beat < 75.75 then
		sway = math.mod(beat - 49.75,4)
		if sway < 2 then
			sway = sway * 0.5
			sway = 1 - 2 * sway * sway * sway
		else
			sway = (sway - 2) * 0.5
			sway = -1 + 2 * sway * sway * sway
		end
	elseif beat >= 75.75 and beat < 77 then
		sway = (77 - beat) * 0.8
		sway = -sway * sway
	elseif beat >= 144 and beat < 145 then
		sway = 0.5 - 0.5 * math.cos((beat - 144) * math.pi)
	elseif beat >= 145 and beat < 173 then
		sway = math.sin(beat * 0.5 * math.pi)
	elseif beat >= 173 and beat < 174 then
		sway = 0.5 + 0.5 * math.cos((beat - 173) * math.pi)
	elseif beat >= 208 and beat < 209 then
		sway = beat - 208
		sway = sway * sway
	elseif beat >= 209 then
		sway = math.mod(beat - 209,4)
		if sway < 2 then
			sway = sway * 0.5
			sway = 1 - 2 * sway * sway * sway
		else
			sway = (sway - 2) * 0.5
			sway = -1 + 2 * sway * sway * sway
		end
	end

	for pn=1,2 do
		if playerspeed[pn] then
			mod_do('*10000 '..(10 * sway * playerspeed[pn] * playerminisize[pn])..' dizzy',pn)
		end
	
		local xbonus, ybonus = 0,0
		if beat >= 77 and beat < 79 then
			local angle = (beat - 77) * 0.5
			angle = math.pi - math.pi * math.cos(angle * angle * math.pi)
			xbonus = 32 - 32 * math.cos(angle)
			ybonus = 32 * math.sin(angle)
		end
		-- holds are the worst thing in the world
		if restepDenote[pn] then
			while restepDenote[pn][currentRestep[pn]] and restepDenote[pn][currentRestep[pn]][#(restepDenote[pn][currentRestep[pn]])][1] < beat and (restepDenote[pn][currentRestep[pn]].resetAt < 1.6 or restepDenote[pn][currentRestep[pn]][#(restepDenote[pn][currentRestep[pn]])][1] + 0.25 < beat) do
				currentRestep[pn] = currentRestep[pn] + 1
				local plr = SCREENMAN:GetTopScreen():GetChild('PlayerP'..pn)
				local nf = plr:GetChild('NoteField')
				for col = 1,4 do
					local ca = nf:GetColumnActors()[col]
					if ca then
						ca:GetPosHandler():SetSplineMode('NoteColumnSplineMode_Disabled')
						ca:GetRotHandler():SetSplineMode('NoteColumnSplineMode_Disabled')
						ca:GetZoomHandler():SetSplineMode('NoteColumnSplineMode_Disabled')
						local pspl = ca:GetPosHandler():GetSpline()
						local rspl = ca:GetRotHandler():GetSpline()
						local zspl = ca:GetZoomHandler():GetSpline()
						pspl:SetSize(1)
						pspl:SetPoint(1, {0, 0, 0} )
						pspl:Solve()
						rspl:SetSize(1)
						rspl:SetPoint(1, {0, 0, 0} )
						rspl:Solve()
						zspl:SetSize(1)
						zspl:SetPoint(1, {1, 1, 1} )
						zspl:Solve()
					end
				end
			end
			if restepDenote[pn][currentRestep[pn]] then
				thisRestep = restepDenote[pn][currentRestep[pn]]
				local plr = SCREENMAN:GetTopScreen():GetChild('PlayerP'..pn)
				local nf = plr:GetChild('NoteField')

				local perLoopOffset = 128 * playerspeed[pn]
				local baseOffset = 0
				local startLoop = 0
				while thisRestep[startLoop + 1] and thisRestep[startLoop + 1][1] < beat and (startLoop > 0 or thisRestep.resetAt < 1.6 or thisRestep[startLoop + 1][1] + 0.25 < beat) do
					startLoop = startLoop + 1
				end
				if startLoop > 0 then
					pause = true
					baseOffset = perLoopOffset * 0.5 * (beat - restepDenote[pn][currentRestep[pn]][startLoop][1])
					if thisRestep.resetAt > 1.6 then
						baseOffset = baseOffset - 16 * playerspeed[pn]
					end
				end
				
				for col = 1,4 do
					local ca = nf:GetColumnActors()[col]
					if ca then
						ca:GetPosHandler():SetSplineMode('NoteColumnSplineMode_Offset')
						ca:GetPosHandler():SetBeatsPerT(0.025)
						ca:GetRotHandler():SetSplineMode('NoteColumnSplineMode_Offset')
						ca:GetRotHandler():SetBeatsPerT(0.025)
						ca:GetZoomHandler():SetSplineMode('NoteColumnSplineMode_Position')
						ca:GetZoomHandler():SetBeatsPerT(0.025)
						local pspl = ca:GetPosHandler():GetSpline()
						local rspl = ca:GetRotHandler():GetSpline()
						local zspl = ca:GetZoomHandler():GetSpline()
						local size = math.round(500/(playerspeed[pn]*playerminisize[pn]))
						pspl:SetSize(size)
						rspl:SetSize(size)
						zspl:SetSize(size)
						local effectiveStartLoop = startLoop > 0 and startLoop or 1
						local currentLoop = effectiveStartLoop
						local currentNote = 1
						local nbc = thisRestep.notesByCol and thisRestep.notesByCol[col]
						local endBeat = thisRestep[#thisRestep][1] + 1.875
						if nbc and nbc[#nbc].length and nbc[#nbc].beat + nbc[#nbc].length > endBeat then
							endBeat = nbc[#nbc].beat + nbc[#nbc].length + 0.125
						end
						for point=1,size do
							local pointBeat = beat + 0.025 * (point - 1)
							while thisRestep[currentLoop + 1] and thisRestep[currentLoop + 1][1] - (2 - thisRestep.resetAt) * 0.5 < pointBeat do
								currentLoop = currentLoop + 1
							end
							if point == 1 then
								if startLoop > 0 and beat < thisRestep[currentLoop][1] then
									local endBeat = thisRestep[currentLoop][1]
									local fullDist = thisRestep.resetAt * 64 * playerspeed[pn]
									local resetLength = 2 - thisRestep.resetAt
									local resetPortion = (endBeat - beat) / resetLength
									resetPortion = resetPortion * resetPortion
									pspl:SetPoint(point, {xbonus, (resetPortion * fullDist) * playerscrolldir[pn] + ybonus, 0.0001 } )
								elseif beat > thisRestep[currentLoop][1] + thisRestep.resetAt then
									local endBeat = thisRestep[currentLoop + 1][1]
									local fullDist = thisRestep.resetAt * 64 * playerspeed[pn]
									local resetLength = 2 - thisRestep.resetAt
									local resetPortion = (endBeat - beat) / resetLength
									resetPortion = resetPortion * resetPortion
									pspl:SetPoint(point, {xbonus, (resetPortion * fullDist) * playerscrolldir[pn] + ybonus, 0.0001 } )
								else
									pspl:SetPoint(point, {xbonus, baseOffset * playerscrolldir[pn] + ybonus, 0.0001 } )
								end
								rspl:SetPoint(point, {0, 0, 0} )
								zspl:SetPoint(point, {1, 1, 1} )
							else
								local xOff, yOff, rzOff, zoomVal, bonusFlip = 0, 0, 0, 1, 1
								if nbc and nbc[1] then
									while nbc[currentNote+1] and pointBeat > (nbc[currentNote].endBeat + nbc[currentNote+1].beat)*0.5 do
										currentNote = currentNote + 1
									end
									if nbc[currentNote] and not nbc[currentNote+1] and pointBeat > (nbc[currentNote].endBeat + endBeat)*0.5 then
										currentNote = currentNote + 1
									end
									if nbc[currentNote] then
										local currentPhase = 1
										while nbc[currentNote][currentPhase+1] and beat < nbc[currentNote][currentPhase+1].beat do
											currentPhase = currentPhase + 1
										end
										local thisPhase = nbc[currentNote][currentPhase]
										if nbc[currentNote][currentPhase+1] and beat < nbc[currentNote][currentPhase+1].beat + 0.5 then
											local prevPhase = nbc[currentNote][currentPhase+1]
											local amount = 1 - (beat - nbc[currentNote][currentPhase+1].beat) * 2
											amount = 1 - (amount * amount)
											if pointBeat < endBeat then
												xOff = thisPhase.xOff * amount + prevPhase.xOff * (1 - amount)
												rzOff = thisPhase.rzOff * amount + prevPhase.rzOff * (1 - amount)
											end
											yOff = (thisPhase.yOff * amount + prevPhase.yOff * (1 - amount)) * playerspeed[pn]
											if nbc[currentNote].length then
												if currentPhase > 1 then
													amount = 0
												end
												yOff = yOff - (pointBeat - nbc[currentNote].beat) * 64 * playerspeed[pn] * (1 - amount) * playerscrolldir[pn]
												-- holds on reverse are the worster thing in the world
												if playerscrolldir[pn] < 0 then
													yOff = yOff - 12 * playerspeed[pn] * nbc[currentNote].length * playerspeed[pn] * (1 - amount)
												end
											end
										else
											yOff = thisPhase.yOff * playerspeed[pn]
											if pointBeat < endBeat then
												xOff, rzOff = thisPhase.xOff, thisPhase.rzOff
												if nbc[currentNote].length and currentPhase > 1 then
													yOff = yOff - (pointBeat - nbc[currentNote].beat) * 64 * playerspeed[pn] * playerscrolldir[pn]
													zoomVal = 0
												end
											end
										end
									end
								end
								local xOffSlice = math.mod(xOff + 512, 128)
								if xOffSlice > 32 and xOffSlice < 96 then
									bonusFlip = -1
								end
								pspl:SetPoint(point, {xOff + xbonus * bonusFlip, (baseOffset - (currentLoop - effectiveStartLoop) * perLoopOffset + yOff) * playerscrolldir[pn] + ybonus * bonusFlip, 0.0001 * point} )
								rspl:SetPoint(point, {0, 0, rzOff} )
								zspl:SetPoint(point, {zoomVal, zoomVal, zoomVal} )
							end
						end
						pspl:Solve()
						rspl:Solve()
						zspl:Solve()
					end
					xbonus = -xbonus
					ybonus = -ybonus
				end
			end
		end
	end
	
	if beat > lastAFTBeat + 0.0868 then
		lastAFTBeat = beat

		local evhs = pause and (vhs + vhs) or vhs
		evhs = math.pow(1.5,evhs) * 0.6

		if showAFTs then
			local waver = math.sin(beat*0.123) * 0.1 + 0.3
			for i,v in ipairs(static) do
				local bw = math.random(2)-1
				local alpha = math.random()
				alpha = alpha * alpha
				v:diffuse(bw,bw,bw,alpha*evhs*0.1)
				local w = math.random()
				w = w * w * 0.2
				local h = math.random()
				h = h * h * 0.2
				local x = math.random() * (1 - w)
				local y = math.random() * (1 - h)
				v:croptop(y)
				v:cropbottom(1-y-h)
				v:cropleft(x)
				v:cropright(1-x-w)
			end
			for i,v in ipairs(blur) do
				for ii,vv in pairs(v) do
					if i ~= blurSteps+1 or ii ~= blurSteps+1 then
						vv:x(dw*0.5+(i-blurSteps-1)*waver*rz*evhs)
						vv:y(dh*0.5+(ii-blurSteps-1)*waver*rz*evhs)
					end
				end
			end
			local orderedDistorts = {}
			for i=1,3 do
				local counter = 1
				while distortPaths[i][counter] and distortPaths[i][counter].endBeat < beat do
					counter = counter + 1
				end
				local path = distortPaths[i][counter]
				if path then
					counter = 1
					while orderedDistorts[counter] and distortMinAt(orderedDistorts[counter], beat) < distortMinAt(path, beat) do
						counter = counter + 1
					end
					for ii = #orderedDistorts, counter, -1 do
						orderedDistorts[ii+1] = orderedDistorts[ii]
					end
					orderedDistorts[counter] = path
				end
			end
			for i = 1,4 do
				for yu = 1,2 do
					distort[i][yu]:croptop(i > 1 and distortMaxAt(orderedDistorts[i-1], beat) or 0)
					distort[i][yu]:cropbottom(i < 4 and 1 - distortMinAt(orderedDistorts[i], beat) or 0)
				end
			end
			for i = 1,3 do
				local minY = distortMinAt(orderedDistorts[i], beat)
				local maxY = distortMaxAt(orderedDistorts[i], beat)
				local width = maxY - minY
				for ii = 1,7 do
					local d = distort[7 * i + ii - 3]
					local stripTop = (minY * (8 - ii) + maxY * (ii - 1)) / 7
					local stripBottom = (minY * (7 - ii) + maxY * ii) / 7
					local stripCenter = (stripTop + stripBottom) * 0.5
					local skewAmount = distortIntensityAt(orderedDistorts[i], beat) * evhs * 2
					local offset = skewAmount * width * SCREEN_HEIGHT * -0.25
					
					if ii == 1 then
						offset = offset * 0.125
						skewAmount = skewAmount * -0.5
					elseif ii == 2 then 
						offset = offset * 0.5
						skewAmount = -skewAmount
					elseif ii == 3 then 
						offset = offset * 0.875						
						skewAmount = skewAmount * -0.5
					elseif ii == 4 then
						skewAmount = 0
					elseif ii == 5 then 
						offset = offset * 0.875						
						skewAmount = skewAmount * 0.5						
					elseif ii == 6 then 
						offset = offset * 0.5
					else
						offset = offset * 0.125
						skewAmount = skewAmount * 0.5						
					end
					
					for yu = 1,2 do
						d[yu]:x(offset - skewAmount * (stripCenter - 0.5) * SCREEN_HEIGHT - evhs * waver * (yu-1) * 5)
						d[yu]:skewx(skewAmount)
						d[yu]:croptop(stripTop)
						d[yu]:cropbottom(1-stripBottom)
					end
				end
			end
			if exposure > 0 then
				overexpose:visible(1)
				overexpose:diffusealpha(exposure)
			else
				overexpose:visible(0)
			end
		end
		
		pauseText:visible(pause)
		
		local snowLines = { { y = .123 + .089 * math.sin(beat * 0.0456), h = .045 + .012 * math.sin(beat * 0.0367), w = .3 + .2 * math.sin(beat * 0.321) },
							{ y = .456 + .234 * math.sin(beat * 0.1789), h = .123 + .045 * math.sin(beat * 0.0678), w = .2 + .1 * math.sin(beat * 0.345) },
							{ y = .876 + .123 * math.sin(beat * 0.0594), h = .067 + .023 * math.sin(beat * 0.1458), w = .3 + .2 * math.sin(beat * 0.432) } }

		for i = 1,3 do
			snowLines[i].w = snowLines[i].w * snowLines[i].h
		end
		local totalWeight = snowLines[1].w + snowLines[2].w + snowLines[3].w
		local snowCount = totalWeight * snowPerWeight * evhs
		if pause then
			snowCount = snowCount * snowWhenPaused
		end
		snowCount = math.min(math.floor(snowCount), maxSnow)
		for i = 1,maxSnow do
			if i <= snowCount then
				local weightCheck = math.random() * totalWeight
				local selectedLine = 1
				while weightCheck > snowLines[selectedLine].w do
					weightCheck = weightCheck - snowLines[selectedLine].w
					selectedLine = selectedLine + 1
				end
				
				local yOff = math.random()
				if math.random() >= 0.5 then
					yOff = yOff * yOff
				else
					yOff = yOff * -yOff
				end
				local snowY = (snowLines[selectedLine].y + snowLines[selectedLine].h * yOff) * SCREEN_HEIGHT - SCREEN_CENTER_Y
				local snowX = math.random() * SCREEN_WIDTH - SCREEN_CENTER_X
				local snowW = snowMinWidth + snowAddWidth * math.random()
				
				for bw = 1,2 do
					snow[i][bw]:visible(1)
					snow[i][bw]:x(snowX)
					snow[i][bw]:y(snowY)
					snow[i][bw]:zoomx(snowW)
					snow[i][bw]:diffusealpha(math.random() * (pause and 0.35 or 0.1) * bw)
				end
			else
				snow[i][1]:visible(0)
				snow[i][2]:visible(0)
			end
		end
	end
	
	if beat > 239.5 then
		local amount = (beat - 239.5) * 2
		amount = math.min(amount,1)
		amount = 1 - amount * amount
		if showAFTs then
			for pn = 1,2 do
				if pp[pn] then
					pp[pn]:zoom(amount * rz)
				end
			end
		else
			for pn = 1,2 do
				if Plr(pn) then
					Plr(pn):zoom(amount)
				end
			end
		end
	end

---------------------------------------------------------------------------------------
----------------------Begin table handlers---------------------------------------------
---------------------------------------------------------------------------------------
	
	disable = false
	if disable ~= true and beat > mod_firstSeenBeat+0.1 and checked then
		
		-----------------------
		-- Player mod resets --
		-----------------------
		for i=1,2 do
			--mod_do('clearall',i)
		end
		
		------------------------------------------------------------------------------
		-- custom mod reader by TaroNuke edited by WinDEU and re-stolen by TaroNuke --
		------------------------------------------------------------------------------
		for i,v in pairs(mods) do
			if v and table.getn(v) > 3 and v[1] and v[2] and v[3] and v[4] then
				if beat >=v[1] then
					if (v[4] == 'len' and beat <=v[1]+v[2]) or (v[4] == 'end' and beat <=v[2]) then
						if table.getn(v) == 5 then
							mod_do(v[3],v[5])
						else
							mod_do(v[3])
						end
					end
				end
			else
				v[1] = 0
				v[2] = 0
				v[3] = ''
				v[4] = 'error'
				SCREENMAN:SystemMessage('Bad mod in beat-based table (line '..i..')')
			end
		end
		
		--------------------------------------------------------------------------------------
		-- i dont know who this reader is but he looks like he is made out of EASE HAHAHAHA --
		-- original code by exschwasion, bastardized by taro for cmod support and less 'if' --
		--------------------------------------------------------------------------------------
		for i,v in pairs(mods_ease) do
			if v and table.getn(v) > 6 and v[1] and v[2] and v[3] and v[4] and v[5] and v[6] and v[7] then
				if beat >=v[1] then
					local mod = v[5]
					if (v[6] == 'len' and beat <=v[1]+v[2]) or (v[6] == 'end' and beat <=v[2]) then
						
						local duration = v[2]
						if v[6] == 'end' then duration = v[2] - v[1] end
						local curtime = beat - v[1]
						local diff = v[4] - v[3]
						local startstrength = v[3]
						local curve = v[7]
						
						local strength = curve(curtime, startstrength, diff, duration, v[10], v[11]) --extra parameters for back and elastic eases :eyes:
						
						if type(mod) == 'function' then
							mod(strength)
						else
							local modstr = v[5] == 'xmod' and strength..'x' or (v[5] == 'cmod' and 'C'..strength or strength..' '..v[5])
							mod_do('*10000 '..modstr,v[8]);
						end
						
					elseif (v[9] and ((v[6] == 'len' and beat <=v[1]+v[2]+v[9]) or (v[6] == 'end' and beat <=v[9]))) then
						local strength = v[4]
						if type(mod) == 'function' then
							mod(strength)
						else
							local modstr = v[5] == 'xmod' and strength..'x' or (v[5] == 'cmod' and 'C'..strength or strength..' '..v[5])
							mod_do('*10000 '..modstr,v[8]);
						end
						
					end
				end
			else
				SCREENMAN:SystemMessage('Bad mod in beat-based ease table (line '..i..')')
			end
		end
		
		--------------------
		-- Perframe stuff --
		--------------------
		
		----------------------------------------
		-- HBLBHCBLBJGBHL DO THIS EVERY FRAME --
		----------------------------------------
		
		if table.getn(mod_perframes)>0 then
			for i=1,table.getn(mod_perframes) do
				local a = mod_perframes[i]
				if beat > a[1] and beat < a[2] then
					a[3](beat)
				end
			end
		end
		
		---------------------------------------
		-- ACTION RPGS AINT GOT SHIT ON THIS --
		---------------------------------------
		while curaction<=table.getn(mod_actions) and GAMESTATE:GetSongBeat()>=mod_actions[curaction][1] do
			if mod_actions[curaction][3] or GAMESTATE:GetSongBeat() < mod_actions[curaction][1]+2 then
				if type(mod_actions[curaction][2]) == 'function' then
					mod_actions[curaction][2]()
				elseif type(mod_actions[curaction][2]) == 'string' then
					MESSAGEMAN:Broadcast(mod_actions[curaction][2])
				end
			end
			curaction = curaction+1
		end
		
	end
	
---------------------------------------------------------------------------------------
----------------------END DON'T TOUCH IT KIDDO-----------------------------------------
---------------------------------------------------------------------------------------
	
end

local t = Def.ActorFrame{
	InitCommand=function(self)
		self:x(scx)
		self:y(scy)
		self:SetUpdateFunction(Update)
	end,
	Def.Quad{ InitCommand= cmd(visible,false), OnCommand= cmd(sleep,1000), },
}
if showAFTs then
	aft_screenTex = Def.ActorFrameTexture{
		Name = "ScreenTex",
		InitCommand=function(self)
			self:SetTextureName( "ScreenTex" )
			self:SetWidth(dw);
			self:SetHeight(dh);
			self:EnableAlphaBuffer(false);
			self:Create();
		end,
		OnCommand=function(self)
			self:visible(true);
			self:Draw();
		end,
		Def.Quad{ OnCommand=cmd(x,dw*0.5;y,dh*0.5;zoomto,dw,dh;diffuse,0,0,0,1), },
		Def.ActorProxy{ Name = "ProxyUL"; OnCommand=function(self) self:x(0); self:y(0) self:SetTarget(SCREENMAN:GetTopScreen():GetChild('Underlay')); self:zoom(rz); end },
		Def.ActorFrame{
			Name = "FrameProxyP1";
			OnCommand=function(self)
				local p = SCREENMAN:GetTopScreen():GetChild('PlayerP1')
				if p then
					self:x(p:GetX()/sw*dw);
					self:y(dh*.5);
				end
			end,
			Def.ActorProxy{ Name = "ProxyP1C"; OnCommand=function(self)
				self:x(0);
				self:y(0);
				self:zoom(rz);
				local p = SCREENMAN:GetTopScreen():GetChild('PlayerP1');
				if p then
					self:SetTarget(p:GetChild('Combo'));
					comboProxies[1] = self;
				end
			end },
			Def.ActorProxy{ Name = "ProxyP1N"; OnCommand=function(self)
				self:x(0);
				self:y(0);
				self:zoom(rz);
				local p = SCREENMAN:GetTopScreen():GetChild('PlayerP1');
				if p then
					self:SetTarget(p:GetChild('NoteField'));
					pp[1] = self;
				end
			end },
			Def.ActorProxy{ Name = "ProxyP1J"; OnCommand=function(self)
				self:x(0);
				self:y(0);
				self:zoom(rz);
				local p = SCREENMAN:GetTopScreen():GetChild('PlayerP1');
				if p then
					self:SetTarget(p:GetChild('Judgment'));
				end
			end }
		},
		Def.ActorFrame{
			Name = "FrameProxyP2";
			OnCommand=function(self)
				local p = SCREENMAN:GetTopScreen():GetChild('PlayerP2')
				if p then
					self:x(p:GetX()/sw*dw);
					self:y(dh*.5);
				end
			end,
			Def.ActorProxy{ Name = "ProxyP2C"; OnCommand=function(self)
				self:x(0);
				self:y(0);
				self:zoom(rz);
				local p = SCREENMAN:GetTopScreen():GetChild('PlayerP2');
				if p then
					self:SetTarget(p:GetChild('Combo'));
					comboProxies[2] = self;
				end
			end },
			Def.ActorProxy{ Name = "ProxyP2N"; OnCommand=function(self)
				self:x(0);
				self:y(0);
				self:zoom(rz);
				local p = SCREENMAN:GetTopScreen():GetChild('PlayerP2');
				if p then
					self:SetTarget(p:GetChild('NoteField'));
					pp[2] = self;
				end
			end },
			Def.ActorProxy{ Name = "ProxyP2J"; OnCommand=function(self)
				self:x(0);
				self:y(0);
				self:zoom(rz);
				local p = SCREENMAN:GetTopScreen():GetChild('PlayerP2');
				if p then
					self:SetTarget(p:GetChild('Judgment'));
				end
			end },
		},
		Def.ActorProxy{ Name = "ProxyOL"; OnCommand=function(self) self:x(0); self:y(0) self:SetTarget(SCREENMAN:GetTopScreen():GetChild('Overlay')); self:zoom(rz); end },
	};
	local icount = 1
	static = {}
	for ix = 1,math.round(SCREEN_WIDTH/staticSize) do
		for iy = 1,math.round(SCREEN_HEIGHT/staticSize) do
			local i = icount
			local ix = ix
			local iy = iy
			aft_screenTex[#aft_screenTex+1] = Def.Quad{
				Name = "Static"..i,
				InitCommand=function(self)
					static[i] = self;
				end,
				OnCommand = cmd(zoom,staticSize*rz;x,(ix*staticSize-halfStaticSize)*rz;y,(iy*staticSize-halfStaticSize)*rz),
			}
			icount = icount + 1
		end
	end
	t[#t+1] = aft_screenTex
	
	aft_blurTex = Def.ActorFrameTexture{
		Name = "BlurTex",
		InitCommand=function(self)
			self:SetTextureName( "BlurTex" )
			self:SetWidth(dw);
			self:SetHeight(dh);
			self:EnableAlphaBuffer(true);
			self:Create();
		end,
		OnCommand=function(self)
			self:visible(true);
			self:Draw();
		end,
	};
	blur = {}
	icount = 2
	for ix = 1,blurSteps*2+1 do
		blur[ix] = {}
	end
	aft_blurTex[#aft_blurTex+1] = Def.Sprite{
		Name = "Blur1";
		Texture = "ScreenTex";
		InitCommand=function(self)
			blur[blurSteps+1][blurSteps+1] = self
		end;
		OnCommand=cmd(x,dw*0.5;y,dh*0.5;zoomto,dw,dh);
	}
	for ix = 1,blurSteps*2+1 do
		for iy = 1,blurSteps*2+1 do
			if ix ~= blurSteps+1 or iy ~= blurSteps+1 then
				local ix = ix
				local iy = iy
				local i = icount
				blurTotal = blurTotal + math.pow(blurDecay,math.abs(blurSteps+1-ix) + math.abs(blurSteps+1-iy))
				aft_blurTex[#aft_blurTex+1] = Def.Sprite{
					Name = "Blur"..i;
					Texture = "ScreenTex";
					InitCommand=function(self)
						blur[ix][iy] = self
					end;
					OnCommand=cmd(x,dw*0.5;y,dh*0.5;zoomto,dw,dh;blend,'add');
				};
				icount = icount + 1
			end
		end
	end
	t[#t+1] = aft_blurTex
	t[#t+1] = Def.Quad{
		Name = "Blackout";
		OnCommand=cmd(zoomto,SCREEN_WIDTH,SCREEN_HEIGHT;diffuse,0,0,0,1);
	}
	blurTotal = blurTotal * .9
	
	distort = {}
	for i = 1,distortionCount*(rowsPerDistortion+1)+1 do
		distort[i] = {}
		local i = i
		t[#t+1] = Def.Sprite{
			Name = "DistortionY"..i;
			Texture = "BlurTex";
			InitCommand=function(self)
				distort[i][1] = self
			end;
			OnCommand=cmd(zoomto,SCREEN_WIDTH,SCREEN_HEIGHT;diffuse,1,1,0,1);
		}
	end
	for i = 1,distortionCount*(rowsPerDistortion+1)+1 do
		local i = i
		t[#t+1] = Def.Sprite{
			Name = "DistortionU"..i;
			Texture = "BlurTex";
			InitCommand=function(self)
				distort[i][2] = self
			end;
			OnCommand=cmd(zoomto,SCREEN_WIDTH,SCREEN_HEIGHT;diffuse,0,0,1,1;blend,'add');
		}
	end
	
	t[#t+1] = Def.Sprite{
		Name = "Overexpose";
		Texture = "ScreenTex";
		InitCommand=function(self)
			overexpose = self;
		end;
		OnCommand=cmd(zoomto,SCREEN_WIDTH,SCREEN_HEIGHT;blend,'add';visible,0);
	}
end
snow = {}
for i = 1,maxSnow do
	snow[i] = {}
	t[#t+1] = Def.Quad{
		Name="SnowB"..i,
		InitCommand=function(self)
			snow[i][1] = self
		end;
		OnCommand=cmd(zoomy,2;fadeleft,1;diffuse,0,0,0,1;visible,0),
	}
	t[#t+1] = Def.Quad{
		Name="SnowW"..i,
		InitCommand=function(self)
			snow[i][2] = self;
		end;
		OnCommand=cmd(zoomy,2;faderight,1;visible,0),
	}
end
t[#t+1] = Def.Sprite{
	Name="PauseText",
	Texture = "pause",
	InitCommand=function(self)
		pauseText = self
	end;
	OnCommand=cmd(x,80 - SCREEN_CENTER_X;y,35 - SCREEN_CENTER_Y;zoom,1.2;blend,'add'),
}


return t