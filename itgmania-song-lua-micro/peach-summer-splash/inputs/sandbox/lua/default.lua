local baseBpm = 125 -- Set to your song's base BPM (used to convert CMod/MMod to XMod)
local poptions = {
	GAMESTATE:GetPlayerState(0):GetPlayerOptions('ModsLevel_Song'),
	GAMESTATE:GetPlayerState(1):GetPlayerOptions('ModsLevel_Song'),
}
local playerscrolldir = {}
local playerspeed = {}
local playermini = {}
local playerminisize = {}
-- Parse song rate from SongOptions (e.g. "1.2xMusic")
local soptions = GAMESTATE:GetSongOptions('ModsLevel_Song')
local rate = 1
local xmu = string.find(soptions, 'xMusic')
if xmu then
	local begin = xmu - 1
	while begin > 0 and string.match(string.sub(soptions, begin, begin), '[.%d]') do
		begin = begin - 1
	end
	local rateString = string.sub(soptions, begin + 1, xmu - 1)
	rate = tonumber(rateString) or 1
end
local receptorMetricY = {
	tonumber(THEME:GetMetric('Player', 'ReceptorArrowsYStandard')) or -140,
	tonumber(THEME:GetMetric('Player', 'ReceptorArrowsYReverse')) or 140,
}
local centerYOffset = (receptorMetricY[1] + receptorMetricY[2]) * 0.5
local resetLeadBeats = 0.125
local function scaleRange(x, l1, h1, l2, h2)
	return (h2 - l2) * (x - l1) / (h1 - l1) + l2
end
local function copyTransformsPlayer(dst, pp, nf, skew, tilt, reverse)
	skew = skew or 0
	tilt = tilt or 0
	local vpx = scaleRange(skew, 0.1, 1.0, pp:GetX(), SCREEN_CENTER_X)
	local vpy = pp:GetY() + centerYOffset
	local reverseMult = reverse and -1 or 1
	local tiltZoom, tiltYOff
	if tilt > 0 then
		tiltZoom = scaleRange(tilt, 0, 1, 1, 0.9)
		tiltYOff = scaleRange(tilt, 0, 1, 0, -45) * reverseMult
	else
		tiltZoom = scaleRange(tilt, 0, -1, 1, 0.9)
		tiltYOff = scaleRange(tilt, 0, -1, 0, -20) * reverseMult
	end
	dst:GetParent():x(pp:GetX()):y(pp:GetY()):z(pp:GetZ()):fov(45):vanishpoint(vpx, vpy)
	dst:x(nf:GetX())
		:y(nf:GetY() + tiltYOff)
		:z(nf:GetZ())
		:rotationx(nf:GetRotationX())
		:rotationy(nf:GetRotationY())
		:rotationz(nf:GetRotationZ())
		:zoomx(nf:GetZoomX() * tiltZoom)
		:zoomy(nf:GetZoomY() * tiltZoom)
		:zoomz(nf:GetZoomZ() * tiltZoom)
end
local function positionBar(bar, ps, yOff, height)
	local x1 = ArrowEffects.GetXPos(ps, 1, yOff)
	local x4 = ArrowEffects.GetXPos(ps, 4, yOff)
	local y = ArrowEffects.GetYPos(ps, 1, yOff)
	local z = ArrowEffects.GetZPos(ps, 1, yOff)
	local zoom = ArrowEffects.GetZoom(ps, yOff, 1)
	local width = math.abs(x4 - x1) + 64 * zoom
	bar:visible(true):xy((x1 + x4) * 0.5, y):z(z):zoomto(width, height * zoom)
end
for pn = 1, 2 do
	if GAMESTATE:IsPlayerEnabled(pn - 1) and poptions[pn] then
		playerscrolldir[pn] = (poptions[pn]:Reverse() == 0 and 1 or -1)
		playermini[pn] = poptions[pn]:Mini() * 100
		playerminisize[pn] = (200 - playermini[pn]) / 200
		local xm = poptions[pn]:XMod()
		local cm = poptions[pn]:CMod()
		local mm = poptions[pn]:MMod()
		if cm then
			playerspeed[pn] = cm / (baseBpm * rate)
		elseif mm then
			local maxBpm = baseBpm
			local steps = GAMESTATE:GetCurrentSteps(pn - 1)
			if steps then
				local actualMin, actualMax = steps:GetTimingData():GetActualBPM()
				if type(actualMin) == 'table' then
					actualMax = actualMin[2]
				end
				if actualMax and actualMax > 0 then
					maxBpm = actualMax
				end
			end
			playerspeed[pn] = mm / (maxBpm * rate)
		else
			playerspeed[pn] = xm
		end
		local tiltCompensation = poptions[pn]:Tilt() or 0
		playerspeed[pn] = playerspeed[pn] * math.cos(tiltCompensation * math.pi / 6)
		-- Clamp speed so the 2-beat wrap point always stays on-screen
		local metricY = playerscrolldir[pn] == 1 and receptorMetricY[1] or receptorMetricY[2]
		local receptorScreenY = SCREEN_CENTER_Y + metricY - 8 * playerscrolldir[pn]
		local maxScreenDist = (playerscrolldir[pn] == 1 and (SCREEN_HEIGHT - receptorScreenY) or receptorScreenY) - 40
		local maxSpeed = math.min(3.5, maxScreenDist / 128) / playerminisize[pn]
		if playerspeed[pn] > maxSpeed then
			playerspeed[pn] = maxSpeed
		end
		-- Clear CMod/MMod on both Song and Current levels so StepMania uses the exact XMod that matches the spline offsets,
		-- hide receptors (100% Dark), and hide missed notes past the receptors (-100% DrawSizeBack).
		local pstate = GAMESTATE:GetPlayerState(pn - 1)
		local modString = '*1000000 ' .. playerspeed[pn] .. 'x, 100% Dark, -100% DrawSizeBack'
		for _, level in ipairs({ 'ModsLevel_Song', 'ModsLevel_Current' }) do
			local po = pstate:GetPlayerOptions(level)
			if po then
				po:XMod(playerspeed[pn], 1000000)
				po:FromString(modString)
			end
		end
	end
end

local restepDenote, currentRestep = {}, {}
for pn = 1, 2 do
	if GAMESTATE:IsPlayerEnabled(pn - 1) then
		currentRestep[pn] = 1
		-- Define restep sections as { startBeat, endBeat } per player.
		restepDenote[pn] = {
			{ 0, 4 },
			{ 8, 12 },
			{ 16, 20 },
			{ 24, 28 },
			{ 32, 36 },
			{ 40, 44 },
			{ 79.5, 85.5 },
			{ 87.5, 91.5 },
			{ 95.5, 101.5 },
			{ 103.5, 107.5 },
			{ 111.25, 141.25 },
			{ 176, 180 },
			{ 184, 188 },
			{ 192, 196 },
			{ 200, 204 },
		}
	end
end
local bars = {}
local barsField = {}
local function Update(self)
	local beat = GAMESTATE:GetSongBeat()
	local screen = SCREENMAN:GetTopScreen()
	if not screen then return end
	for pn = 1, 2 do
		local plr = screen:GetChild('PlayerP' .. pn)
		local nf = plr and plr:GetChild('NoteField')
		if restepDenote[pn] and nf then
			while restepDenote[pn][currentRestep[pn]]
				and restepDenote[pn][currentRestep[pn]][2] - resetLeadBeats < beat
			do
				currentRestep[pn] = currentRestep[pn] + 1
				for col = 1, 4 do
					local ca = nf:GetColumnActors()[col]
					if ca then
						ca:GetPosHandler():SetSplineMode('NoteColumnSplineMode_Disabled')
						local pspl = ca:GetPosHandler():GetSpline()
						pspl:SetSize(1)
						pspl:SetPoint(1, {0, 0, 0})
						pspl:Solve()
					end
				end
			end
			local thisRestep = restepDenote[pn][currentRestep[pn]]
			local perLoopOffset = 128 * playerspeed[pn]
			local baseOffset = 0
			local startLoop = 0
			local effectiveStartLoop = 1
			local sectionStart, sectionEnd, endLoop
			if thisRestep then
				sectionStart = thisRestep[1]
				sectionEnd = thisRestep[2]
				endLoop = math.floor((sectionEnd - sectionStart) / 2 + 0.5) + 1
				if beat >= sectionStart - resetLeadBeats then
					startLoop = math.floor((beat - (sectionStart - resetLeadBeats)) / 2) + 1
					local loopStartBeat = sectionStart + (startLoop - 1) * 2 - resetLeadBeats
					baseOffset = perLoopOffset * 0.5 * (beat - loopStartBeat)
					effectiveStartLoop = startLoop
				end
			end
			local receptorOffset = baseOffset
			local posBeatsPerPoint = 0.03125
			local posSize = 75
			local zoomBeatsPerPoint = 0.0625
			local zoomSize = 41
			for col = 1, 4 do
				local ca = nf:GetColumnActors()[col]
				if ca then
					local pspl = ca:GetPosHandler():GetSpline()
					local zspl = ca:GetZoomHandler():GetSpline()
					ca:GetZoomHandler():SetSplineMode('NoteColumnSplineMode_Position')
					ca:GetZoomHandler():SetBeatsPerT(zoomBeatsPerPoint)
					zspl:SetSize(zoomSize)
					if thisRestep then
						ca:GetPosHandler():SetSplineMode('NoteColumnSplineMode_Offset')
						ca:GetPosHandler():SetBeatsPerT(posBeatsPerPoint)
						pspl:SetSize(posSize)
						for point = 1, posSize do
							local pointBeat = beat + posBeatsPerPoint * (point - 1)
							if point == 1 then
								pspl:SetPoint(point, {0, receptorOffset * playerscrolldir[pn], 0.0001})
							else
								local currentLoop = 1
								if pointBeat >= sectionEnd - resetLeadBeats then
									currentLoop = endLoop
								elseif pointBeat >= sectionStart - resetLeadBeats then
									currentLoop = math.floor((pointBeat - (sectionStart - resetLeadBeats)) / 2) + 1
								end
								local splineOffset = baseOffset - (currentLoop - effectiveStartLoop) * perLoopOffset
								pspl:SetPoint(point, {
									0,
									splineOffset * playerscrolldir[pn],
									0.0001 * point,
								})
							end
						end
						pspl:Solve()
					end
					for point = 1, zoomSize do
						local pointBeat = beat + zoomBeatsPerPoint * (point - 1)
						if point == 1 then
							zspl:SetPoint(point, {1, 1, 1})
						else
							local splineOffset = 0
							local currentLoop = 1
							if thisRestep then
								if pointBeat >= sectionEnd - resetLeadBeats then
									currentLoop = endLoop
								elseif pointBeat >= sectionStart - resetLeadBeats then
									currentLoop = math.floor((pointBeat - (sectionStart - resetLeadBeats)) / 2) + 1
								end
								splineOffset = baseOffset - (currentLoop - effectiveStartLoop) * perLoopOffset
							end
							local totalOffset = (pointBeat - beat) * 64 * playerspeed[pn] + splineOffset
							local zoomVal = 1
							if totalOffset > perLoopOffset then
								zoomVal = 0
							elseif thisRestep and currentLoop > 1 and pointBeat < sectionEnd + 1.875 then
								local passBeat = pointBeat - 2
								if beat <= passBeat then
									zoomVal = 0
								elseif beat < passBeat + 0.25 then
									local t = (beat - passBeat) * 4
									zoomVal = 1 - (1 - t) * (1 - t)
								end
							else
								local beatsPastBottom = (perLoopOffset - totalOffset) / (64 * playerspeed[pn])
								if beatsPastBottom < 0.25 then
									local t = beatsPastBottom * 4
									zoomVal = 1 - (1 - t) * (1 - t)
								end
							end
							zspl:SetPoint(point, {zoomVal, zoomVal, zoomVal})
						end
					end
					zspl:Solve()
				end
			end
			if bars[pn] and barsField[pn] then
				local pstate = GAMESTATE:GetPlayerState(pn - 1)
				copyTransformsPlayer(
					barsField[pn],
					plr,
					nf,
					poptions[pn]:Skew(),
					poptions[pn]:Tilt(),
					playerscrolldir[pn] < 0
				)
				positionBar(bars[pn].top, pstate, 0, 4)
				positionBar(bars[pn].bottom, pstate, perLoopOffset, 4)
				positionBar(bars[pn].receptors, pstate, receptorOffset, 2)
			end
		elseif bars[pn] then
			bars[pn].top:visible(false)
			bars[pn].bottom:visible(false)
			bars[pn].receptors:visible(false)
		end
	end
end
local af = Def.ActorFrame{
	InitCommand = function(self)
		self:SetUpdateFunction(Update)
	end,
	Def.Quad{
		InitCommand = cmd(visible, false),
		OnCommand = cmd(sleep, 1000),
	},
}
for pn = 1, 2 do
	if GAMESTATE:IsPlayerEnabled(pn - 1) then
		bars[pn] = {}
		af[#af + 1] = Def.ActorFrame{
			Name = 'BarsParentP' .. pn,
			Def.ActorFrame{
				Name = 'BarsFieldP' .. pn,
				InitCommand = function(self)
					barsField[pn] = self
				end,
				Def.Quad{
					InitCommand = function(self)
						self:visible(false):diffuse(1, 1, 1, 1)
						bars[pn].top = self
					end,
				},
				Def.Quad{
					InitCommand = function(self)
						self:visible(false):diffuse(1, 1, 1, 1)
						bars[pn].bottom = self
					end,
				},
				Def.Quad{
					InitCommand = function(self)
						self:visible(false):diffuse(1, 1, 1, 0.8)
						bars[pn].receptors = self
					end,
				},
			},
		}
	end
end
return af