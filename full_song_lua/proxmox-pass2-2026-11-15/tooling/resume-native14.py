import pathlib,json,hashlib,subprocess,sys,ijson
from ijson.common import ObjectBuilder
r=pathlib.Path('/opt/song-lua-audit');sys.path.insert(0,str(r))
case=r/'pass2-results/67053c6979c0becb'
raw=next(case.glob('tmp/*/*/Save/itgmania-harness/song-lua-trace.json'))
fields={'input','display','capabilities','completion','script_errors','source_simfile','command_observer','error'}
meta={};active=None;depth=0;builder=None
with raw.open('rb') as f:
 for prefix,event,value in ijson.parse(f,use_float=True):
  if active is not None:
   builder.event(event,value)
   if event in ('start_map','start_array'):depth+=1
   elif event in ('end_map','end_array'):depth-=1
   if depth==0:meta[active]=builder.value;active=None
  elif prefix=='events' and event=='start_array':break
  elif prefix in fields or '.' not in prefix and prefix.startswith('dropped_'):
   if event in ('start_map','start_array'):active=prefix;depth=1;builder=ObjectBuilder();builder.event(event,value)
   elif event not in ('map_key','end_map','end_array'):meta[prefix]=value
assert not meta.get('error') and meta['script_errors']==[]
assert meta['completion']['reason']=='gameplay-exit' and meta['completion']['stage_committed'] is True
assert all(v==0 for k,v in meta.items() if k.startswith('dropped_'))
assert meta['input']['native_source']['revision']=='008bfcfef57a107eaafe08b4de7d9d42c6dd1e2f'
assert meta['input']['native_source']['modified_src'] is False
assert meta['display']['video_renderers']=='null'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
receipt={'phase_interrupted':'capture postprocessing after completed native trace publication','raw_sha256':sha(raw),'native_metadata':meta}
archive=r/'pass2-interrupted/67053c6979c0becb-host-oom';archive.parent.mkdir(exist_ok=True)
assert case.resolve().is_relative_to(r) and archive.resolve().is_relative_to(r) and not archive.exists()
relative=raw.relative_to(case);case.rename(archive);raw=archive/relative
case.mkdir();prepared=case/'recorded-with-provenance.json'
jobs=json.loads((r/'pass2-jobs/jobs-14.json').read_text());job=jobs[0]
assert job['id']==case.name
extra={'source_simfile':str(r/'Songs'/job['source_simfile']),
       'command_observer':{'dynamic_commands':True,'capture_binary_sha256':sha(r/'bin/itgmania-harness-rs')}}
# These two fields are the exact provenance assignments made by capture_in.
# Native observations are unchanged. song-lua-analyze parses then serializes the
# object, eliminating any overridden original key before archive validation.
with raw.open('rb') as src,prepared.open('wb') as dst:
 tail=b''
 while block:=src.read(4*1024*1024):
  data=tail+block
  if len(data)>128:dst.write(data[:-128]);tail=data[-128:]
  else:tail=data
 end=tail.rstrip();assert end.endswith(b'}')
 dst.write(end[:-1]+b','+json.dumps(extra,separators=(',',':')).encode()[1:]+b'\n')
receipt.update(preserved_attempt=str(archive),raw_trace=str(raw),provenance_assignments=extra,prepared_sha256=sha(prepared),recovery_jobs=len(jobs))
job['recorded_native_trace']=str(prepared);job['capture_recovery']=receipt
source=(r/'worker_pass2.py').read_text()
line="        result['stages']['capture']=execute(case,'capture',command,job.get('capture_timeout',900)+90)"
replacement="""        if job.get('recorded_native_trace'):
            result['capture_recovery']=job['capture_recovery']
            result['stages']['capture']=execute(case,'capture-resume',[HARNESS,'song-lua-analyze',job['recorded_native_trace'],'--out',trace/'native.json'],900)
            if (case/'capture-resume.log').exists():shutil.copyfile(case/'capture-resume.log',case/'capture.log')
        else:
            result['stages']['capture']=execute(case,'capture',command,job.get('capture_timeout',900)+90)"""
assert source.count(line)==1
(r/'worker_recover.py').write_text(source.replace(line,replacement))
(r/'pass2-jobs/jobs-14-recovery.json').write_text(json.dumps(jobs,indent=2))
(r/'worker14-recovery.json').write_text(json.dumps(receipt,indent=2)+'\n')
subprocess.run(['sudo','systemd-run','--unit=song-lua-pass2-worker-14-recovery','--collect','--property=User=parity','--property=Group=parity','--setenv=HOME=/home/parity','/usr/bin/python3',str(r/'worker_recover.py'),str(r/'pass2-jobs/jobs-14-recovery.json'),'--worker','14'],check=True)
print(json.dumps(receipt))
