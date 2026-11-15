"""Independent reduced native capture; unchanged product binaries."""
import json,pathlib,wave
import worker
root=worker.ROOT;folder=root/'Songs/__audit_controls/initial-effect-clock';folder.mkdir(parents=True,exist_ok=True)
sim=folder/'control.sm';sim.write_text('#TITLE:Initial effect clock;\n#MUSIC:silence.wav;\n#OFFSET:0.825;\n#BPMS:0=120;\n#FGCHANGES:0=default.lua=1=0=0=1;\n#NOTES:dance-single::Challenge:1:0,0,0,0,0:\n1000\n0000\n0000\n0000\n,\n0000\n0000\n0000\n1000\n;\n')
(folder/'default.lua').write_text('return Def.Actor { OnCommand=function(self) self:effectclock("music"); self:x(self:GetSecsIntoEffect()) end }\n')
with wave.open(str(folder/'silence.wav'),'wb') as w:
 w.setnchannels(1);w.setsampwidth(2);w.setframerate(8000);w.writeframes(b'\0\0'*8000*5)
job={'id':'initial-effect-clock-control','source_simfile':str(sim.relative_to(root/'Songs')),'title':'Initial effect clock','style':'single','difficulty':'Challenge','gc_mode':'automatic','capture_fps':60,'max_events':100000,'capture_timeout':120,'replay_timeout':120,'simfile_sha256':worker.sha(sim),'worker':'large'}
r=worker.run_case(job,'large');print(json.dumps({'id':r['id'],'status':r['status'],'comparison':r.get('comparison',{})}))
