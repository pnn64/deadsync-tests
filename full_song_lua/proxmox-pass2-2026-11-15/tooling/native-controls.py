import concurrent.futures, hashlib, json, os, pathlib, subprocess, wave
root=pathlib.Path('/opt/song-lua-audit')
out=root/'pass2-controls-v2';out.mkdir(exist_ok=True)
cases={
 'observer': '''return Def.Actor { OnCommand=function(self)
 self:effectclock('music'); assert(self:GetSecsIntoEffect()==0); self:x(self:GetSecsIntoEffect())
 self:aux(4); assert(self:getaux()==4)
 local options=GAMESTATE:GetPlayerState(PLAYER_1):GetPlayerOptions('ModsLevel_Song')
 options:Boost(0.5,true):Reverse(0.25,true)
 assert(PREFSMAN:GetPreference('LastSeenVideoDriver')~='')
 end }''',
 'syntax-error': 'return Def.Actor {}\nlocal invalid = 1\n',
 'load-error': "error('pass2 deliberate top-level load error')\nreturn Def.Actor {}",
}
def run(item):
 name,source=item;folder=out/name;folder.mkdir(exist_ok=True)
 song=folder/'song';song.mkdir(exist_ok=True)
 (song/'control.sm').write_text('#TITLE:Pass2 '+name+';\n#MUSIC:silence.wav;\n#OFFSET:0.825;\n#BPMS:0=120;\n#FGCHANGES:0=default.lua=1=0=0=1;\n#NOTES:dance-single::Challenge:1:0,0,0,0,0:\n1000\n0000\n0000\n1000\n;\n')
 (song/'default.lua').write_text(source)
 with wave.open(str(song/'silence.wav'),'wb') as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(8000);w.writeframes(b'\0\0'*8000*3)
 tmp=folder/'tmp';tmp.mkdir(exist_ok=True)
 command=[root/'bin/itgmania-harness-rs','song-lua-trace',song/'control.sm','--itgmania-bin',root/'harness/vendor/itgmania/ITGmania-harness-trace','--fallback-theme','Harness Simply Love','--headless','--style','single','--until-gameplay-end','--capture-fps','60','--max-events','100000','--timeout','120','--keep-run-dir','--out',folder/'native.json']
 with (folder/'capture.log').open('w') as log:
  result=subprocess.run(list(map(str,command)),env=dict(os.environ,TMPDIR=str(tmp)),stdout=log,stderr=subprocess.STDOUT,timeout=150)
 record={'name':name,'exit':result.returncode,'expected_success':name=='observer','command':list(map(str,command)),'log':(folder/'capture.log').read_text()[-3000:]}
 traces=list(tmp.glob('itgmania-harness-rs/song-lua-*/Save/itgmania-harness/song-lua-trace.json'))
 if traces:
  trace=json.loads(traces[0].read_text());record.update(script_errors=trace.get('script_errors'),completion=trace.get('completion'),preferences=trace.get('input',{}).get('preferences'),events=[e for e in trace['events'] if e.get('operation') in ['Actor.getaux','PlayerOptions.Boost','PlayerOptions.Reverse']])
 (folder/'result.json').write_text(json.dumps(record,indent=2)+'\n')
 return record
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(run,cases.items()))
(out/'native-controls.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps([{'name':r['name'],'exit':r['exit'],'errors':r.get('script_errors')} for r in results]),flush=True)
assert all((r['exit']==0)==r['expected_success'] for r in results)
